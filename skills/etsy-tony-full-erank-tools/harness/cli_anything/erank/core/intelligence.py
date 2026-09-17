from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
import hashlib
import math
from statistics import mean
from typing import Any, Iterable

from PIL import Image, ImageFilter, ImageOps, ImageStat

from cli_anything.erank.core.analyzers import normalize_phrase, tokenize
from cli_anything.erank.core.models import Listing, parse_datetime, parse_tags
from cli_anything.erank.core.shop_search import normalize_shop


UNKNOWN_VALUES = {"", "unknown", "n/a", "na", "none", "null", "-", "< 20", "<20"}


def _optional_number(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if text.lower() in UNKNOWN_VALUES or text.startswith("<"):
        return None
    text = text.replace("$", "").replace("%", "").replace(",", "")
    try:
        return float(text)
    except ValueError:
        return None


def _pick(row: dict[str, Any], *keys: str) -> Any:
    lowered = {str(key).strip().lower().replace(" ", "_"): value for key, value in row.items()}
    for key in keys:
        normalized = key.strip().lower().replace(" ", "_")
        if normalized in lowered and lowered[normalized] not in (None, ""):
            return lowered[normalized]
    return None


def _clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def _iso_datetime(value: Any) -> datetime | None:
    parsed = parse_datetime(value)
    if parsed and parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc) if parsed else None


def true_profit(
    *,
    price: float,
    shipping_charged: float = 0,
    supplier_cost: float = 0,
    shipping_cost: float = 0,
    packaging_cost: float = 0,
    ad_cost: float = 0,
    production_minutes: float = 0,
    labor_rate_hourly: float = 0,
    return_rate: float = 0,
    breakage_rate: float = 0,
    weekly_orders: float = 0,
    weekly_capacity_minutes: float = 0,
    target_margin: float = 0,
    formula_multiplier: float | None = None,
    listing_fee: float = 0.20,
    transaction_fee_rate: float = 0.065,
    payment_fee_rate: float = 0.03,
    payment_fixed_fee: float = 0.25,
    offsite_ad_rate: float = 0,
) -> dict[str, Any]:
    values = {
        "price": price,
        "shipping_charged": shipping_charged,
        "supplier_cost": supplier_cost,
        "shipping_cost": shipping_cost,
        "packaging_cost": packaging_cost,
        "ad_cost": ad_cost,
        "production_minutes": production_minutes,
        "labor_rate_hourly": labor_rate_hourly,
        "return_rate": return_rate,
        "breakage_rate": breakage_rate,
        "weekly_orders": weekly_orders,
        "weekly_capacity_minutes": weekly_capacity_minutes,
        "target_margin": target_margin,
    }
    if any(value < 0 for value in values.values()):
        raise ValueError("Profit and capacity inputs must be non-negative.")
    if return_rate > 100 or breakage_rate > 100 or target_margin > 100:
        raise ValueError("Return, breakage, and target-margin percentages cannot exceed 100.")
    if formula_multiplier is not None and formula_multiplier <= 0:
        raise ValueError("Formula multiplier must be greater than zero.")

    revenue = price + shipping_charged
    labor_cost = production_minutes / 60 * labor_rate_hourly
    transaction_fee = revenue * transaction_fee_rate
    payment_fee = revenue * payment_fee_rate + payment_fixed_fee
    offsite_fee = revenue * offsite_ad_rate
    expected_loss = revenue * ((return_rate + breakage_rate) / 100)
    total_cost = (
        supplier_cost
        + shipping_cost
        + packaging_cost
        + ad_cost
        + labor_cost
        + listing_fee
        + transaction_fee
        + payment_fee
        + offsite_fee
        + expected_loss
    )
    profit = revenue - total_cost
    margin = profit / revenue * 100 if revenue else 0
    weekly_minutes = weekly_orders * production_minutes
    capacity_ok = weekly_capacity_minutes <= 0 or weekly_minutes <= weekly_capacity_minutes
    recommended_price = None
    formula_ok = True
    if formula_multiplier is not None:
        recommended_price = (supplier_cost + shipping_cost) * formula_multiplier
        formula_ok = price >= recommended_price
    margin_ok = margin >= target_margin
    return {
        "currency": "USD",
        "revenue": round(revenue, 2),
        "costs": {
            "supplier_cost": round(supplier_cost, 2),
            "shipping_cost": round(shipping_cost, 2),
            "packaging_cost": round(packaging_cost, 2),
            "labor_cost": round(labor_cost, 2),
            "ad_cost": round(ad_cost, 2),
            "expected_return_breakage_loss": round(expected_loss, 2),
        },
        "fees": {
            "listing_fee": round(listing_fee, 2),
            "transaction_fee": round(transaction_fee, 2),
            "payment_fee": round(payment_fee, 2),
            "offsite_ad_fee": round(offsite_fee, 2),
        },
        "total_cost": round(total_cost, 2),
        "profit": round(profit, 2),
        "margin_percent": round(margin, 2),
        "constraints": {
            "target_margin_percent": target_margin,
            "margin_ok": margin_ok,
            "weekly_production_minutes": round(weekly_minutes, 2),
            "weekly_capacity_minutes": weekly_capacity_minutes,
            "capacity_ok": capacity_ok,
            "formula_multiplier": formula_multiplier,
            "formula_recommended_price": round(recommended_price, 2) if recommended_price is not None else None,
            "formula_ok": formula_ok,
        },
        "decision": "VIABLE" if margin_ok and capacity_ok and formula_ok else "REVIEW",
    }


def _scale(values: list[float | None], invert: bool = False) -> list[float | None]:
    known = [value for value in values if value is not None]
    if not known:
        return [None for _ in values]
    low, high = min(known), max(known)
    scaled: list[float | None] = []
    for value in values:
        if value is None:
            scaled.append(None)
            continue
        score = 50.0 if high == low else (value - low) / (high - low) * 100
        scaled.append(100 - score if invert else score)
    return scaled


def opportunity_engine(rows: Iterable[dict[str, Any]], target_margin: float = 30) -> dict[str, Any]:
    materialized = [dict(row) for row in rows]
    if not materialized:
        return {"count": 0, "opportunities": [], "limitations": ["No opportunity rows were supplied."]}
    demand = [_optional_number(_pick(row, "demand", "search_volume", "avg_searches")) for row in materialized]
    competition = [_optional_number(_pick(row, "competition", "results")) for row in materialized]
    demand_scores = _scale(demand)
    competition_scores = _scale(competition, invert=True)
    results: list[dict[str, Any]] = []
    for index, row in enumerate(materialized):
        product = str(_pick(row, "product", "keyword", "name") or "").strip()
        growth = _optional_number(_pick(row, "growth", "trend", "growth_percent"))
        momentum = _optional_number(_pick(row, "competitor_momentum", "momentum", "sales_growth"))
        fit = _optional_number(_pick(row, "fit_score", "equipment_fit", "capability_fit"))
        required_equipment = {normalize_phrase(item) for item in parse_tags(_pick(row, "required_equipment", "equipment_required")) if normalize_phrase(item)}
        available_equipment = {normalize_phrase(item) for item in parse_tags(_pick(row, "available_equipment", "equipment_available")) if normalize_phrase(item)}
        equipment_missing = sorted(required_equipment - available_equipment) if required_equipment and available_equipment else []
        if fit is None and required_equipment and available_equipment:
            fit = 100.0 if not equipment_missing else max(0.0, 100 * (1 - len(equipment_missing) / len(required_equipment)))
        ip_risk = _optional_number(_pick(row, "ip_risk", "risk_score"))
        price = _optional_number(_pick(row, "price", "selling_price"))
        supplier = _optional_number(_pick(row, "supplier_cost", "item_cost"))
        shipping = _optional_number(_pick(row, "shipping_cost", "shipping"))
        production_minutes = _optional_number(_pick(row, "production_minutes", "minutes"))
        return_rate = _optional_number(_pick(row, "return_rate"))
        breakage_rate = _optional_number(_pick(row, "breakage_rate"))
        components: list[tuple[str, float, float]] = []
        if demand_scores[index] is not None:
            components.append(("demand", demand_scores[index], 0.25))
        if competition_scores[index] is not None:
            components.append(("competition", competition_scores[index], 0.15))
        if growth is not None:
            components.append(("growth", _clamp(50 + growth), 0.15))
        if momentum is not None:
            components.append(("competitor_momentum", _clamp(50 + momentum), 0.10))
        if fit is not None:
            components.append(("business_fit", _clamp(fit), 0.10))
        if ip_risk is not None:
            components.append(("risk", 100 - _clamp(ip_risk), 0.10))

        profit = None
        if None not in (price, supplier, shipping):
            profit = true_profit(
                price=price or 0,
                supplier_cost=supplier or 0,
                shipping_cost=shipping or 0,
                packaging_cost=_optional_number(_pick(row, "packaging_cost")) or 0,
                ad_cost=_optional_number(_pick(row, "ad_cost")) or 0,
                production_minutes=production_minutes or 0,
                labor_rate_hourly=_optional_number(_pick(row, "labor_rate_hourly")) or 0,
                return_rate=return_rate or 0,
                breakage_rate=breakage_rate or 0,
                weekly_orders=_optional_number(_pick(row, "weekly_orders")) or 0,
                weekly_capacity_minutes=_optional_number(_pick(row, "weekly_capacity_minutes")) or 0,
                target_margin=target_margin,
                formula_multiplier=_optional_number(_pick(row, "formula_multiplier")),
            )
            components.append(("profit", _clamp(profit["margin_percent"] * 2), 0.15))
        weight = sum(component[2] for component in components)
        score = sum(component[1] * component[2] for component in components) / weight if weight else 0
        coverage = weight / 1.0
        action = "SCALE" if score >= 70 and coverage >= 0.65 else "TEST" if score >= 55 and coverage >= 0.5 else "RESEARCH"
        if profit and profit["decision"] != "VIABLE" and action == "SCALE":
            action = "TEST"
        if profit and not profit["constraints"]["capacity_ok"]:
            action = "RESEARCH"
        if action == "SCALE" and (ip_risk is None or profit is None):
            action = "TEST"
        results.append(
            {
                "product": product,
                "score": round(score, 1),
                "action": action,
                "data_coverage": round(min(coverage, 1), 2),
                "components": {name: round(value, 1) for name, value, _ in components},
                "profit": profit,
                "equipment": {
                    "required": sorted(required_equipment),
                    "available": sorted(available_equipment),
                    "missing": equipment_missing,
                },
                "raw_metrics": {
                    "demand": _pick(row, "demand", "search_volume", "avg_searches"),
                    "competition": _pick(row, "competition", "results"),
                    "growth": _pick(row, "growth", "trend", "growth_percent"),
                    "competitor_momentum": _pick(row, "competitor_momentum", "momentum", "sales_growth"),
                },
                "missing_fields": [
                    name
                    for name, value in {
                        "demand": demand[index],
                        "competition": competition[index],
                        "growth": growth,
                        "competitor_momentum": momentum,
                        "business_fit": fit,
                        "ip_risk": ip_risk,
                        "price": price,
                        "supplier_cost": supplier,
                        "shipping_cost": shipping,
                    }.items()
                    if value is None
                ],
            }
        )
    results.sort(key=lambda item: (item["score"], item["data_coverage"]), reverse=True)
    return {
        "count": len(results),
        "opportunities": results,
        "method": "Weighted score over available evidence; missing and '< 20' values remain missing and weights are renormalized.",
    }


GENERIC_PRODUCT_WORDS = {
    "custom", "personalized", "handmade", "gift", "new", "set", "for", "with", "the", "and",
    "wood", "wooden", "small", "large", "modern", "vintage",
}


def _listing_family(listing: Listing) -> str:
    if listing.category:
        return listing.category.split(">")[-1].strip().lower()
    candidates = [token for token in tokenize(listing.title) if token not in GENERIC_PRODUCT_WORDS]
    if listing.tags:
        tag_tokens = [token for token in tokenize(listing.tags[0]) if token not in GENERIC_PRODUCT_WORDS]
        candidates = tag_tokens or candidates
    return " ".join(candidates[:2]) or "uncategorized"


def _keyword_intent(phrase: str) -> tuple[str, str]:
    tokens = set(tokenize(phrase))
    if tokens.intersection({"buy", "custom", "personalized", "personalised", "order", "sale", "gift"}):
        return "transactional", "conversion"
    if tokens.intersection({"best", "ideas", "compare", "versus", "vs", "reviews"}):
        return "commercial", "consideration"
    if tokens.intersection({"how", "guide", "tutorial", "tips", "what", "why"}):
        return "informational", "awareness"
    return "category", "discovery"


def cluster_listings(listings: Iterable[Listing], previous: Iterable[Listing] = ()) -> dict[str, Any]:
    groups: dict[str, list[Listing]] = defaultdict(list)
    previous_map = {item.listing_id: item for item in previous if item.listing_id}
    for listing in listings:
        groups[_listing_family(listing)].append(listing)
    clusters: list[dict[str, Any]] = []
    for family, items in groups.items():
        prices = [item.price for item in items if item.price > 0]
        tag_counts = Counter(normalize_phrase(tag) for item in items for tag in item.tags if normalize_phrase(tag))
        total_sales = sum(item.sales for item in items)
        growth = sum(max(item.sales - previous_map[item.listing_id].sales, 0) for item in items if item.listing_id in previous_map)
        new_listing_count = sum(bool(item.listing_id and item.listing_id not in previous_map) for item in items) if previous_map else 0
        sorted_items = sorted(items, key=lambda item: (item.sales, item.views, item.favorites), reverse=True)
        clusters.append(
            {
                "family": family,
                "listing_count": len(items),
                "total_sales_signal": total_sales,
                "sales_growth_signal": growth if previous_map else None,
                "growth_share_percent": None,
                "new_listing_count": new_listing_count if previous_map else None,
                "sales_share_percent": 0,
                "price_band": {
                    "min": round(min(prices), 2) if prices else None,
                    "average": round(mean(prices), 2) if prices else None,
                    "max": round(max(prices), 2) if prices else None,
                },
                "top_tags": [{"tag": tag, "uses": count} for tag, count in tag_counts.most_common(10)],
                "hero_listings": [
                    {
                        "listing_id": item.listing_id,
                        "title": item.title,
                        "sales_signal": item.sales,
                        "sales_delta": item.sales - previous_map[item.listing_id].sales if item.listing_id in previous_map else None,
                        "price": item.price,
                        "url": item.url,
                    }
                    for item in sorted_items[:5]
                ],
            }
        )
    total = sum(cluster["total_sales_signal"] for cluster in clusters)
    total_growth = sum(cluster["sales_growth_signal"] or 0 for cluster in clusters)
    for cluster in clusters:
        cluster["sales_share_percent"] = round(cluster["total_sales_signal"] / total * 100, 2) if total else 0
        if previous_map:
            cluster["growth_share_percent"] = round((cluster["sales_growth_signal"] or 0) / total_growth * 100, 2) if total_growth else 0
    clusters.sort(key=lambda item: ((item["sales_growth_signal"] or 0) if previous_map else item["total_sales_signal"], item["total_sales_signal"], item["listing_count"]), reverse=True)
    return {
        "cluster_count": len(clusters),
        "clusters": clusters,
        "growth_available": bool(previous_map),
        "limitation": "Listing sales are signals from the input source, not proof of Etsy backend order attribution.",
    }


def change_impact(
    before: Iterable[Listing],
    after: Iterable[Listing],
    before_at: datetime | None = None,
    after_at: datetime | None = None,
) -> dict[str, Any]:
    before_map = {item.listing_id: item for item in before if item.listing_id}
    after_map = {item.listing_id: item for item in after if item.listing_id}
    days = None
    if before_at and after_at:
        days = max((after_at - before_at).total_seconds() / 86400, 0)
    rows: list[dict[str, Any]] = []
    for listing_id in sorted(before_map.keys() & after_map.keys()):
        old, new = before_map[listing_id], after_map[listing_id]
        changes: list[str] = []
        if old.title != new.title:
            changes.append("title")
        if [normalize_phrase(tag) for tag in old.tags] != [normalize_phrase(tag) for tag in new.tags]:
            changes.append("tags")
        if old.price != new.price:
            changes.append("price")
        if old.image_count != new.image_count:
            changes.append("images")
        if old.description != new.description:
            changes.append("description")
        deltas = {
            "views": new.views - old.views,
            "visits": new.visits - old.visits,
            "favorites": new.favorites - old.favorites,
            "sales": new.sales - old.sales,
            "orders": new.orders - old.orders,
            "revenue": round(new.revenue - old.revenue, 2),
        }
        rank_improvement = old.rank - new.rank if old.rank > 0 and new.rank > 0 else None
        confounders: list[str] = []
        if not days:
            confounders.append("snapshot_interval_unknown")
        if len(changes) > 1:
            confounders.append("multiple_simultaneous_changes")
        if old.sales < 5 and new.sales < 5:
            confounders.append("low_sales_baseline")
        rows.append(
            {
                "listing_id": listing_id,
                "changes": changes,
                "deltas": deltas,
                "rank_improvement": rank_improvement,
                "per_day": {key: round(value / days, 3) for key, value in deltas.items()} if days else None,
                "confounders": confounders,
                "evidence_level": "OBSERVATIONAL" if changes and not confounders else "CONFOUNDED" if changes else "CONTROL_NO_CHANGE",
            }
        )
    return {
        "matched_listings": len(rows),
        "snapshot_days": round(days, 2) if days is not None else None,
        "listings": rows,
        "new_listing_ids": sorted(after_map.keys() - before_map.keys()),
        "missing_listing_ids": sorted(before_map.keys() - after_map.keys()),
        "causal_claim_allowed": False,
        "limitation": "Before/after correlation is observational and does not prove that a listing edit caused a metric change.",
    }


def keyword_portfolio(listings: Iterable[Listing], metrics: Iterable[dict[str, Any]] = ()) -> dict[str, Any]:
    items = list(listings)
    metric_map: dict[str, dict[str, Any]] = {}
    for row in metrics:
        keyword = normalize_phrase(str(_pick(row, "keyword", "tag", "phrase") or ""))
        if keyword:
            metric_map[keyword] = dict(row)
    usage: dict[str, set[str]] = defaultdict(set)
    phrase_sources: dict[str, set[str]] = defaultdict(set)
    for item in items:
        for tag in item.tags:
            phrase = normalize_phrase(tag)
            if phrase:
                usage[phrase].add(item.listing_id)
                phrase_sources[phrase].add("tag")
        tokens = tokenize(item.title)
        for size in (2, 3):
            for index in range(max(0, len(tokens) - size + 1)):
                phrase = " ".join(tokens[index:index + size])
                if len(phrase) <= 20:
                    usage[phrase].add(item.listing_id)
                    phrase_sources[phrase].add("title")
    cannibalized = [
        {
            "keyword": phrase,
            "listing_ids": sorted(ids),
            "listing_count": len(ids),
            "intent": _keyword_intent(phrase)[0],
            "search_stage": _keyword_intent(phrase)[1],
        }
        for phrase, ids in usage.items()
        if len(ids) > 1
    ]
    cannibalized.sort(key=lambda row: (-row["listing_count"], row["keyword"]))
    plans: list[dict[str, Any]] = []
    for item in items:
        title_tokens = set(tokenize(item.title))
        candidates = []
        for phrase, ids in usage.items():
            overlap = len(title_tokens.intersection(tokenize(phrase)))
            if item.listing_id not in ids and not overlap:
                continue
            metric = metric_map.get(phrase, {})
            demand = _optional_number(_pick(metric, "search_volume", "demand"))
            competition = _optional_number(_pick(metric, "competition"))
            score = overlap * 10 + (math.log1p(demand) if demand is not None else 0) - (math.log1p(competition) if competition is not None else 0)
            candidates.append((score, phrase, metric))
        candidates.sort(key=lambda entry: (entry[0], entry[1]), reverse=True)
        selected: list[dict[str, Any]] = []
        for score, phrase, metric in candidates:
            if phrase in {row["keyword"] for row in selected}:
                continue
            selected.append(
                {
                    "keyword": phrase,
                    "score": round(score, 2),
                    "current_listing_count": len(usage[phrase]),
                    "intent": _keyword_intent(phrase)[0],
                    "search_stage": _keyword_intent(phrase)[1],
                    "metrics": metric or None,
                }
            )
            if len(selected) == 13:
                break
        plans.append(
            {
                "listing_id": item.listing_id,
                "title": item.title,
                "recommended_slots": selected,
                "slot_count": len(selected),
                "missing_slot_count": 13 - len(selected),
            }
        )
    return {
        "listing_count": len(items),
        "cannibalization": cannibalized,
        "plans": plans,
        "rule": "Recommendations use only phrases present in listing text/tags or supplied metrics; unknown metrics are not converted to zero.",
    }


def analyze_image_file(path: str) -> dict[str, Any]:
    """Extract reproducible technical/CRO signals without claiming semantic vision."""
    with Image.open(path) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
        width, height = image.size
        work = image.copy()
        work.thumbnail((256, 256))
    gray = ImageOps.grayscale(work)
    gray_stat = ImageStat.Stat(gray)
    brightness = gray_stat.mean[0]
    contrast = gray_stat.stddev[0]
    edge_density = ImageStat.Stat(gray.filter(ImageFilter.FIND_EDGES)).mean[0]

    corner_size = max(4, min(work.size) // 10)
    corners = [
        work.crop((0, 0, corner_size, corner_size)),
        work.crop((work.width - corner_size, 0, work.width, corner_size)),
        work.crop((0, work.height - corner_size, corner_size, work.height)),
        work.crop((work.width - corner_size, work.height - corner_size, work.width, work.height)),
    ]
    corner_pixels = [pixel for corner in corners for pixel in corner.getdata()]
    background_rgb = tuple(round(sum(pixel[channel] for pixel in corner_pixels) / len(corner_pixels)) for channel in range(3))
    corner_variance = mean(
        math.sqrt(sum((pixel[channel] - background_rgb[channel]) ** 2 for channel in range(3)))
        for pixel in corner_pixels
    )
    foreground = 0
    pixels = list(work.getdata())
    for pixel in pixels:
        distance = math.sqrt(sum((pixel[channel] - background_rgb[channel]) ** 2 for channel in range(3)))
        if distance >= 45:
            foreground += 1
    product_coverage = foreground / len(pixels) * 100 if pixels else 0
    background_score = _clamp(100 - corner_variance * 2)
    return {
        "path": str(path),
        "width": width,
        "height": height,
        "brightness": round(brightness, 2),
        "contrast": round(contrast, 2),
        "edge_density": round(edge_density, 2),
        "background_rgb": list(background_rgb),
        "background_score": round(background_score, 2),
        "product_coverage": round(product_coverage, 2),
        "technical_method": "Pillow thumbnail, corner-background distance, grayscale contrast, and edge density.",
        "semantic_fields_unverified": ["text_overlay", "size_reference", "personalization_visible", "lifestyle"],
    }


def cro_audit(listing: Listing, images: Iterable[dict[str, Any]] = ()) -> dict[str, Any]:
    image_rows = [dict(row) for row in images]
    first = image_rows[0] if image_rows else {}
    width = _optional_number(_pick(first, "width", "image_width"))
    height = _optional_number(_pick(first, "height", "image_height"))
    coverage = _optional_number(_pick(first, "product_coverage", "coverage_percent"))
    background = _optional_number(_pick(first, "background_score", "background_cleanliness"))
    has_text = str(_pick(first, "has_text", "text_overlay") or "").lower() in {"1", "true", "yes"}
    size_reference = any(str(_pick(row, "size_reference", "scale_reference") or "").lower() in {"1", "true", "yes"} for row in image_rows)
    personalization_visible = any(str(_pick(row, "personalization_visible") or "").lower() in {"1", "true", "yes"} for row in image_rows)
    lifestyle_count = sum(str(_pick(row, "lifestyle") or "").lower() in {"1", "true", "yes"} for row in image_rows)
    video_visible = any(str(_pick(row, "video", "has_video") or "").lower() in {"1", "true", "yes"} for row in image_rows)
    shipping_visible = any(str(_pick(row, "shipping_visible") or "").lower() in {"1", "true", "yes"} for row in image_rows)
    processing_visible = any(str(_pick(row, "processing_time_visible") or "").lower() in {"1", "true", "yes"} for row in image_rows)
    return_policy_visible = any(str(_pick(row, "return_policy_visible") or "").lower() in {"1", "true", "yes"} for row in image_rows)
    review_proof_visible = any(str(_pick(row, "review_proof_visible", "trust_signal_visible") or "").lower() in {"1", "true", "yes"} for row in image_rows)
    listing_tokens = set(tokenize(f"{listing.title} {listing.description}"))
    personalization_expected = bool(listing_tokens.intersection({"custom", "personalized", "personalised", "engraved", "monogram"}))
    digital = bool(set(tokenize(f"{listing.category} {' '.join(listing.materials)}")).intersection({"digital", "pdf", "download", "template"}))
    score = 100
    issues: list[dict[str, str]] = []
    if not image_rows and listing.image_count <= 0:
        issues.append({"severity": "high", "code": "no_image_evidence", "message": "No image manifest or image count was supplied."})
        score -= 35
    if width is None or height is None:
        issues.append({"severity": "medium", "code": "dimensions_unverified", "message": "First-image dimensions are not verified."})
        score -= 10
    elif min(width, height) < 2000:
        issues.append({"severity": "medium", "code": "low_resolution", "message": "First image is below 2000 px on its shortest side."})
        score -= 12
    elif abs(width / height - 1) > 0.25:
        issues.append({"severity": "low", "code": "non_square_crop", "message": "First-image crop is far from square and may lose detail in search thumbnails."})
        score -= 5
    if coverage is None:
        issues.append({"severity": "medium", "code": "coverage_unverified", "message": "Product coverage in the first image is not verified."})
        score -= 8
    elif coverage < 55:
        issues.append({"severity": "medium", "code": "product_too_small", "message": "Product occupies less than 55% of the first image."})
        score -= 12
    if background is not None and background < 60:
        issues.append({"severity": "low", "code": "busy_background", "message": "Background cleanliness score is below 60."})
        score -= 6
    if has_text and len(str(_pick(first, "overlay_text") or "")) > 40:
        issues.append({"severity": "low", "code": "dense_overlay", "message": "First-image text overlay may be hard to read on mobile."})
        score -= 5
    if not size_reference and not digital:
        issues.append({"severity": "low", "code": "missing_scale_proof", "message": "No scale or size-reference image is confirmed."})
        score -= 5
    if personalization_expected and not personalization_visible:
        issues.append({"severity": "low", "code": "personalization_unverified", "message": "Personalization clarity is not confirmed in the image manifest."})
        score -= 4
    if lifestyle_count == 0:
        issues.append({"severity": "low", "code": "no_lifestyle_image", "message": "No lifestyle/use-context image is confirmed."})
        score -= 5
    if not video_visible:
        issues.append({"severity": "low", "code": "video_unverified", "message": "No product video is confirmed."})
        score -= 3
    if not shipping_visible or not processing_visible:
        issues.append({"severity": "low", "code": "fulfillment_clarity_unverified", "message": "Shipping or processing-time clarity is not confirmed in the merchandising evidence."})
        score -= 4
    if not return_policy_visible or not review_proof_visible:
        issues.append({"severity": "low", "code": "trust_signals_unverified", "message": "Return-policy or review/trust proof is not confirmed."})
        score -= 4
    return {
        "listing_id": listing.listing_id,
        "score": max(0, score),
        "issues": issues,
        "checks": {
            "first_image_width": width,
            "first_image_height": height,
            "product_coverage_percent": coverage,
            "background_score": background,
            "text_overlay": has_text,
            "size_reference": size_reference,
            "personalization_visible": personalization_visible,
            "personalization_expected": personalization_expected,
            "lifestyle_image_count": lifestyle_count,
            "video_visible": video_visible,
            "shipping_visible": shipping_visible,
            "processing_time_visible": processing_visible,
            "return_policy_visible": return_policy_visible,
            "review_proof_visible": review_proof_visible,
            "manifest_image_count": len(image_rows),
        },
        "human_review_required": True,
        "limitation": "Manifest checks cannot judge aesthetic quality, factual accuracy, or buyer trust without human visual review.",
    }


def cross_market_validation(rows: Iterable[dict[str, Any]], min_sources: int = 3) -> dict[str, Any]:
    if min_sources < 1:
        raise ValueError("Minimum source count must be at least one.")
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        product = str(_pick(row, "product", "keyword", "name") or "").strip()
        if product:
            grouped[product].append(dict(row))
    results: list[dict[str, Any]] = []
    for product, signals in grouped.items():
        by_source: dict[str, dict[str, Any]] = {}
        for signal in signals:
            source = str(_pick(signal, "source", "marketplace", "channel") or "unknown").strip().lower()
            value = _optional_number(_pick(signal, "signal", "score", "growth", "trend"))
            confidence = _optional_number(_pick(signal, "confidence"))
            by_source[source] = {"source": source, "signal": value, "confidence": confidence, "raw": signal}
        known = [item for item in by_source.values() if item["signal"] is not None]
        weighted = []
        for item in known:
            confidence = item["confidence"] if item["confidence"] is not None else 0.5
            if confidence > 1:
                confidence /= 100
            weighted.append((item["signal"], _clamp(confidence, 0, 1)))
        consensus = sum(value * weight for value, weight in weighted) / sum(weight for _, weight in weighted) if weighted and sum(weight for _, weight in weighted) else None
        positive = sum(item["signal"] >= 55 for item in known)
        source_count = len(by_source)
        validated = source_count >= min_sources and positive >= 2 and consensus is not None and consensus >= 55
        results.append(
            {
                "product": product,
                "source_count": source_count,
                "known_signal_count": len(known),
                "positive_source_count": positive,
                "consensus_score": round(consensus, 1) if consensus is not None else None,
                "decision": "VALIDATED" if validated else "RESEARCH",
                "sources": list(by_source.values()),
            }
        )
    results.sort(key=lambda item: (item["decision"] == "VALIDATED", item["consensus_score"] or -1), reverse=True)
    return {"count": len(results), "minimum_sources": min_sources, "products": results}


def _month_number(value: Any) -> int | None:
    number = _optional_number(value)
    if number is not None and 1 <= int(number) <= 12:
        return int(number)
    parsed = _iso_datetime(value)
    return parsed.month if parsed else None


def seasonal_plan(rows: Iterable[dict[str, Any]], lead_days: int = 45, as_of: date | None = None) -> dict[str, Any]:
    if lead_days < 0:
        raise ValueError("Lead days must be non-negative.")
    grouped: dict[str, list[tuple[int, float, dict[str, Any]]]] = defaultdict(list)
    for row in rows:
        product = str(_pick(row, "product", "keyword", "name") or "").strip()
        month = _month_number(_pick(row, "month", "period", "date"))
        volume = _optional_number(_pick(row, "search_volume", "demand", "signal"))
        if product and month and volume is not None:
            grouped[product].append((month, volume, dict(row)))
    reference = as_of or datetime.now(timezone.utc).date()
    products: list[dict[str, Any]] = []
    for product, signals in grouped.items():
        by_month: dict[int, list[float]] = defaultdict(list)
        for month, volume, _ in signals:
            by_month[month].append(volume)
        monthly = {month: mean(values) for month, values in by_month.items()}
        peak_month = max(monthly, key=monthly.get)
        average = mean(monthly.values())
        uplift = (monthly[peak_month] / average - 1) * 100 if average else 0
        peak_year = reference.year if peak_month >= reference.month else reference.year + 1
        peak_date = date(peak_year, peak_month, 1)
        launch_date = peak_date - timedelta(days=lead_days)
        products.append(
            {
                "product": product,
                "months_observed": len(monthly),
                "peak_month": peak_month,
                "peak_signal": round(monthly[peak_month], 2),
                "average_signal": round(average, 2),
                "peak_uplift_percent": round(uplift, 2),
                "recommended_launch_date": launch_date.isoformat(),
                "prototype_deadline": (launch_date - timedelta(days=14)).isoformat(),
                "backtest_status": "SUFFICIENT" if len(monthly) >= 3 else "INSUFFICIENT_HISTORY",
            }
        )
    products.sort(key=lambda item: item["peak_uplift_percent"], reverse=True)
    return {"count": len(products), "lead_days": lead_days, "products": products}


def fact_gated_draft(facts: dict[str, Any], keywords: Iterable[str]) -> dict[str, Any]:
    product = str(facts.get("product") or facts.get("product_name") or "").strip()
    if not product:
        raise ValueError("Confirmed facts must include product or product_name.")
    candidate_values: list[str] = list(keywords)
    tag_fact_keys = {"material", "style", "color", "size", "occasion", "recipient", "use_case", "personalization", "product_type"}
    for key, value in facts.items():
        if key not in tag_fact_keys:
            continue
        if isinstance(value, list):
            candidate_values.extend(str(item) for item in value)
        elif isinstance(value, (str, int, float)) and str(value).strip():
            candidate_values.append(str(value))
    candidate_values.insert(0, product)
    tags: list[str] = []
    for value in candidate_values:
        phrase = normalize_phrase(value)
        if phrase and len(phrase) <= 20 and phrase not in tags:
            tags.append(phrase)
    if len(tags) < 13:
        return {
            "status": "NEEDS_CONFIRMATION",
            "draft": None,
            "candidate_tags": tags,
            "missing_tag_count": 13 - len(tags),
            "required_action": "Provide additional confirmed buyer phrases; the fact gate will not invent missing tags.",
        }
    tags = tags[:13]
    title_parts = [product]
    for key in ("material", "style", "color", "size", "recipient", "occasion"):
        value = facts.get(key)
        if value and str(value).lower() not in " ".join(title_parts).lower():
            title_parts.append(str(value))
    title = " | ".join(title_parts)[:140]
    description_lines = [f"{key.replace('_', ' ').title()}: {value}" for key, value in facts.items() if value not in (None, "", [])]
    return {
        "status": "DRAFT_READY_REVIEW_ONLY",
        "draft": {
            "title": title,
            "description": "\n".join(description_lines),
            "tags": tags,
            "tags_csv": ", ".join(tags),
        },
        "confirmed_fact_keys": sorted(facts.keys()),
        "publication_authorized": False,
    }


def _shop_extra(row: dict[str, Any]) -> dict[str, float | None]:
    return {
        "reviews": _optional_number(_pick(row, "reviews", "review_count")),
        "listings": _optional_number(_pick(row, "listings", "active_listings", "total_listings")),
    }


def breakout_radar(
    rows: Iterable[dict[str, Any]],
    *,
    as_of: date,
    age_min_months: int,
    age_max_months: int,
    sales_min: int,
    sales_max: int,
    previous_rows: Iterable[dict[str, Any]] = (),
    snapshot_days: float = 7,
) -> dict[str, Any]:
    if min(age_min_months, age_max_months, sales_min, sales_max) < 0:
        raise ValueError("Age and sales ranges must be non-negative.")
    if age_min_months > age_max_months or sales_min > sales_max:
        raise ValueError("Minimum range values cannot exceed maximum values.")
    if snapshot_days <= 0:
        raise ValueError("Snapshot days must be greater than zero.")
    previous_map: dict[str, dict[str, Any]] = {}
    for row in previous_rows:
        normalized = normalize_shop(row, as_of, "all-time")
        if normalized["shop"]:
            previous_map[normalized["shop"].lower()] = {**normalized, **_shop_extra(row)}
    matches: list[dict[str, Any]] = []
    needs_verification: list[dict[str, Any]] = []
    checked = 0
    for row in rows:
        normalized = normalize_shop(row, as_of, "all-time")
        if not normalized["shop"]:
            continue
        checked += 1
        extras = _shop_extra(row)
        sales = normalized["total_sales"]
        sales_ok = sales is not None and normalized["sales_scope"] == "total" and sales_min <= sales <= sales_max
        exact_age = normalized["age_precision"] in {"exact_date", "explicit_months"}
        age_ok = normalized["age_months"] is not None and age_min_months <= normalized["age_months"] <= age_max_months
        if sales_ok and not exact_age:
            needs_verification.append({**normalized, **extras, "verification_reason": "Exact shop age is unavailable."})
            continue
        if not (sales_ok and exact_age and age_ok):
            continue
        previous = previous_map.get(normalized["shop"].lower())
        sales_delta = sales - previous["total_sales"] if previous and previous.get("total_sales") is not None else None
        review_delta = extras["reviews"] - previous["reviews"] if previous and extras["reviews"] is not None and previous.get("reviews") is not None else None
        listing_delta = extras["listings"] - previous["listings"] if previous and extras["listings"] is not None and previous.get("listings") is not None else None
        weekly_sales = sales_delta * 7 / snapshot_days if sales_delta is not None else None
        launch_cadence = max(listing_delta, 0) * 30 / snapshot_days if listing_delta is not None else None
        momentum = 0.0
        if weekly_sales is not None:
            momentum += min(max(weekly_sales, 0), 100) * 0.6
        if review_delta is not None:
            momentum += min(max(review_delta * 7 / snapshot_days, 0), 30) * 0.8
        if launch_cadence is not None:
            momentum += min(launch_cadence, 30) * 0.5
        matches.append(
            {
                **normalized,
                **extras,
                "growth": {
                    "snapshot_days": snapshot_days if previous else None,
                    "sales_delta": sales_delta,
                    "weekly_sales_velocity": round(weekly_sales, 2) if weekly_sales is not None else None,
                    "review_delta": review_delta,
                    "listing_delta": listing_delta,
                    "monthly_listing_launch_cadence": round(launch_cadence, 2) if launch_cadence is not None else None,
                    "momentum_score": round(momentum, 1) if previous else None,
                },
            }
        )
    matches.sort(key=lambda item: (item["growth"]["momentum_score"] if item["growth"]["momentum_score"] is not None else -1, item["total_sales"]), reverse=True)
    return {
        "criteria": {
            "age_min_months": age_min_months,
            "age_max_months": age_max_months,
            "sales_min": sales_min,
            "sales_max": sales_max,
            "sales_scope": "shop lifetime total",
            "as_of": as_of.isoformat(),
        },
        "rows_checked": checked,
        "match_count": len(matches),
        "matches": matches,
        "needs_verification_count": len(needs_verification),
        "needs_verification": needs_verification,
        "growth_available": bool(previous_map),
    }


def detect_anomalies(
    rows: Iterable[dict[str, Any]],
    previous_rows: Iterable[dict[str, Any]] = (),
    spike_multiplier: float = 5,
) -> dict[str, Any]:
    if spike_multiplier <= 1:
        raise ValueError("Spike multiplier must be greater than one.")
    current = [dict(row) for row in rows]
    previous_map = {
        str(_pick(row, "shop", "shop_name", "name", "listing_id", "id") or "").strip().lower(): dict(row)
        for row in previous_rows
    }
    seen: Counter[str] = Counter()
    anomalies: list[dict[str, Any]] = []
    expected_shop_fields = {"shop", "shop_name", "name", "sales", "total_sales", "lifetime_sales", "created_at", "opened_at", "age_months"}
    recognized_any = False
    for index, row in enumerate(current):
        identity = str(_pick(row, "shop", "shop_name", "name", "listing_id", "id") or f"row-{index}").strip()
        seen[identity.lower()] += 1
        recognized_any = recognized_any or bool({str(key).lower() for key in row} & expected_shop_fields)
        for metric in ("sales", "total_sales", "reviews", "review_count", "listings", "active_listings", "age_months"):
            value = _optional_number(_pick(row, metric))
            if value is not None and value < 0:
                anomalies.append({"identity": identity, "code": "negative_metric", "field": metric, "value": value})
        age = _optional_number(_pick(row, "age_months"))
        sales = _optional_number(_pick(row, "total_sales", "lifetime_sales", "sales"))
        if age == 0 and sales is not None and sales > 10000:
            anomalies.append({"identity": identity, "code": "implausible_age_sales_pair", "age_months": age, "sales": sales})
        old = previous_map.get(identity.lower())
        if old:
            old_sales = _optional_number(_pick(old, "total_sales", "lifetime_sales", "sales"))
            if sales is not None and old_sales is not None:
                if sales < old_sales:
                    anomalies.append({"identity": identity, "code": "cumulative_sales_decreased", "before": old_sales, "after": sales})
                elif old_sales > 0 and sales / old_sales >= spike_multiplier:
                    anomalies.append({"identity": identity, "code": "sales_spike", "before": old_sales, "after": sales, "multiplier": round(sales / old_sales, 2)})
    for identity, count in seen.items():
        if count > 1:
            anomalies.append({"identity": identity, "code": "duplicate_identity", "count": count})
    if current and not recognized_any:
        anomalies.append({"identity": "dataset", "code": "schema_contract_drift", "message": "No recognized identity, sales, or age fields were found."})
    return {"rows_checked": len(current), "anomaly_count": len(anomalies), "anomalies": anomalies}


def watchlist_alerts(
    current_rows: Iterable[dict[str, Any]],
    previous_rows: Iterable[dict[str, Any]],
    *,
    seen_alert_ids: Iterable[str] = (),
    prior_unresolved: Iterable[dict[str, Any]] = (),
    min_sales_growth: float = 10,
    min_review_growth: float = 3,
    min_listing_growth: float = 5,
    evidence_ok: bool = True,
) -> dict[str, Any]:
    if min(min_sales_growth, min_review_growth, min_listing_growth) < 0:
        raise ValueError("Alert thresholds must be non-negative.")
    if not evidence_ok:
        return {
            "result_status": "BLOCKED_BY_EVIDENCE",
            "alerts": [],
            "new_alert_count": 0,
            "reason": "Stale, incomplete, or rejected evidence cannot trigger alerts.",
        }
    previous = {
        str(_pick(row, "shop", "shop_name", "name") or "").strip().lower(): dict(row)
        for row in previous_rows
    }
    seen = set(seen_alert_ids)
    alerts: list[dict[str, Any]] = []
    unresolved_by_kind = {
        (str(alert.get("shop") or "").lower(), str(alert.get("kind") or "")): dict(alert)
        for alert in prior_unresolved
        if alert.get("alert_id")
    }
    suppressed = 0
    for row in current_rows:
        shop = str(_pick(row, "shop", "shop_name", "name") or "").strip()
        old = previous.get(shop.lower())
        if not shop or not old:
            continue
        metrics = [
            ("sales_growth", _optional_number(_pick(row, "total_sales", "sales")), _optional_number(_pick(old, "total_sales", "sales")), min_sales_growth),
            ("review_growth", _optional_number(_pick(row, "reviews", "review_count")), _optional_number(_pick(old, "reviews", "review_count")), min_review_growth),
            ("listing_growth", _optional_number(_pick(row, "listings", "active_listings")), _optional_number(_pick(old, "listings", "active_listings")), min_listing_growth),
        ]
        for kind, current, prior, threshold in metrics:
            if current is None or prior is None or current - prior < threshold:
                continue
            alert_id = hashlib.sha1(f"{shop.lower()}|{kind}|{current}".encode("utf-8")).hexdigest()[:16]
            if alert_id in seen:
                suppressed += 1
                continue
            alerts.append({"alert_id": alert_id, "shop": shop, "kind": kind, "before": prior, "after": current, "delta": current - prior})
            seen.add(alert_id)
            unresolved_by_kind[(shop.lower(), kind)] = alerts[-1]
    unresolved = sorted(unresolved_by_kind.values(), key=lambda alert: (str(alert.get("shop")), str(alert.get("kind"))))
    return {
        "result_status": "VERIFIED_ALERTS" if alerts else "NO_NEW_ALERTS",
        "new_alert_count": len(alerts),
        "suppressed_duplicate_count": suppressed,
        "alerts": alerts,
        "unresolved_count": len(unresolved),
        "state": {"seen_alert_ids": sorted(seen), "unresolved": unresolved},
    }
