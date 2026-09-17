from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import date, datetime, timezone
import math
import re
from statistics import mean
from typing import Any, Iterable

from cli_anything.erank.core.models import Listing, Order, parse_number


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
    "your",
}

CATEGORY_HINTS = {
    "wall": "Art & Collectibles > Prints",
    "print": "Art & Collectibles > Prints",
    "poster": "Art & Collectibles > Prints",
    "mug": "Home & Living > Kitchen & Dining > Drinkware",
    "shirt": "Clothing > Unisex Adult Clothing > T-shirts",
    "tshirt": "Clothing > Unisex Adult Clothing > T-shirts",
    "jewelry": "Jewelry & Accessories",
    "necklace": "Jewelry & Accessories > Necklaces",
    "ring": "Jewelry & Accessories > Rings",
    "earrings": "Jewelry & Accessories > Earrings",
    "sticker": "Paper & Party Supplies > Stickers",
    "digital": "Paper & Party Supplies > Digital Prints",
    "pattern": "Craft Supplies & Tools > Patterns & How To",
    "candle": "Home & Living > Home Decor > Candles",
    "wedding": "Weddings",
}


def tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9]+", (text or "").lower()) if token not in STOPWORDS]


def normalize_phrase(text: str) -> str:
    return " ".join(tokenize(text))


def listing_text(listing: Listing) -> str:
    return " ".join([listing.title, listing.description, " ".join(listing.tags), listing.category]).lower()


def listing_match_score(keyword: str, listing: Listing) -> float:
    phrase = keyword.lower().strip()
    tokens = tokenize(keyword)
    if not tokens:
        return 0.0
    title = listing.title.lower()
    tags = [tag.lower() for tag in listing.tags]
    body = listing_text(listing)
    score = 0.0
    if phrase and phrase in title:
        score += 12
    if any(phrase == tag for tag in tags):
        score += 10
    if phrase and phrase in body:
        score += 4
    score += sum(3 for token in tokens if token in tokenize(listing.title))
    score += sum(2 for token in tokens for tag in tags if token in tokenize(tag))
    score += sum(1 for token in tokens if token in tokenize(listing.description))
    score += math.log1p(max(listing.sales, 0)) * 0.7
    score += math.log1p(max(listing.views, 0)) * 0.2
    return round(score, 4)


def filter_keyword_matches(keyword: str, listings: Iterable[Listing]) -> list[tuple[float, Listing]]:
    matches = []
    tokens = set(tokenize(keyword))
    for listing in listings:
        text_tokens = set(tokenize(listing_text(listing)))
        score = listing_match_score(keyword, listing)
        if score > 0 and (not tokens or tokens.intersection(text_tokens)):
            matches.append((score, listing))
    return sorted(matches, key=lambda item: item[0], reverse=True)


def keyword_analysis(
    keyword: str,
    listings: Iterable[Listing],
    limit: int = 20,
    external_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    matches = filter_keyword_matches(keyword, listings)
    top_matches = matches[:limit]
    matched_listings = [listing for _, listing in matches]
    external_metrics = external_metrics or {}
    views = sum(item.views for item in matched_listings)
    favorites = sum(item.favorites for item in matched_listings)
    sales = sum(item.sales for item in matched_listings)
    competition = len(matched_listings)
    proxy_volume = int(round((views * 0.15) + (favorites * 1.5) + (sales * 8) + (competition * 12)))
    avg_price = round(mean([item.price for item in matched_listings if item.price > 0]), 2) if matched_listings else 0
    engagement_rate = round(((favorites + sales) / views) * 100, 2) if views else 0
    click_proxy = int(round((favorites * 2) + (sales * 4) + (views * 0.04)))
    ctr_proxy = round((click_proxy / proxy_volume) * 100, 2) if proxy_volume else 0
    demand = parse_number(external_metrics.get("search_volume") or external_metrics.get("avg_searches"), proxy_volume)
    difficulty = round(min(100, (competition / max(demand / 100, 1)) * 8), 1) if demand else 0

    tag_counter: Counter[str] = Counter()
    for listing in matched_listings:
        for tag in listing.tags:
            normalized = normalize_phrase(tag)
            if normalized and normalized != normalize_phrase(keyword):
                tag_counter[normalized] += 1

    return {
        "keyword": keyword,
        "data_source": "local_proxy" if not external_metrics else "imported_metrics",
        "metrics": {
            "search_volume_proxy": int(demand),
            "competition": competition,
            "clicks_proxy": click_proxy,
            "ctr_proxy_percent": ctr_proxy,
            "engagement_rate_percent": engagement_rate,
            "keyword_difficulty_proxy": difficulty,
            "average_price": avg_price,
            "matched_views": views,
            "matched_favorites": favorites,
            "matched_sales": sales,
        },
        "related_keywords": [
            {"keyword": tag, "count": count} for tag, count in tag_counter.most_common(20)
        ],
        "top_listings": [
            {
                "rank": index + 1,
                "score": score,
                "listing_id": listing.listing_id,
                "shop": listing.shop,
                "title": listing.title,
                "price": listing.price,
                "views": listing.views,
                "favorites": listing.favorites,
                "sales": listing.sales,
                "tags": listing.tags,
                "url": listing.url,
            }
            for index, (score, listing) in enumerate(top_matches)
        ],
        "limitations": [
            "Metrics are transparent local proxies unless you import authoritative keyword data.",
            "This does not use private eRank member-only search volume/click data.",
        ],
    }


def compare_keywords(keywords: Iterable[str], listings: Iterable[Listing]) -> dict[str, Any]:
    analyses = [keyword_analysis(keyword, listings, limit=5) for keyword in keywords]
    rows = []
    for item in analyses:
        metrics = item["metrics"]
        rows.append(
            {
                "keyword": item["keyword"],
                "volume": metrics["search_volume_proxy"],
                "competition": metrics["competition"],
                "difficulty": metrics["keyword_difficulty_proxy"],
                "ctr": metrics["ctr_proxy_percent"],
                "avg_price": metrics["average_price"],
            }
        )
    rows.sort(key=lambda row: (row["volume"], -row["difficulty"]), reverse=True)
    return {"keywords": rows, "winner": rows[0] if rows else None}


def rank_check(keyword: str, listings: Iterable[Listing], shop: str | None = None, limit: int = 100) -> dict[str, Any]:
    ranked = keyword_analysis(keyword, listings, limit=limit)["top_listings"]
    shop_lower = (shop or "").lower()
    hits = [
        row for row in ranked if not shop_lower or str(row.get("shop", "")).lower() == shop_lower
    ]
    return {
        "keyword": keyword,
        "shop": shop,
        "found": bool(hits),
        "best_rank": hits[0]["rank"] if hits else None,
        "matches": hits,
        "checked_results": len(ranked),
    }


def tag_report(listings: Iterable[Listing], shop: str | None = None) -> dict[str, Any]:
    selected = [item for item in listings if not shop or item.shop.lower() == shop.lower()]
    counter: Counter[str] = Counter()
    metrics: dict[str, dict[str, float]] = defaultdict(lambda: {"views": 0, "sales": 0, "favorites": 0})
    for listing in selected:
        for tag in listing.tags:
            normalized = normalize_phrase(tag)
            if not normalized:
                continue
            counter[normalized] += 1
            metrics[normalized]["views"] += listing.views
            metrics[normalized]["sales"] += listing.sales
            metrics[normalized]["favorites"] += listing.favorites
    rows = []
    for tag, count in counter.most_common():
        row_metrics = metrics[tag]
        rows.append(
            {
                "tag": tag,
                "uses": count,
                "views": int(row_metrics["views"]),
                "favorites": int(row_metrics["favorites"]),
                "sales": int(row_metrics["sales"]),
            }
        )
    return {"shop": shop, "listing_count": len(selected), "tags": rows}


def shop_info(shop: str, listings: Iterable[Listing]) -> dict[str, Any]:
    selected = [item for item in listings if item.shop.lower() == shop.lower()]
    return {
        "shop": shop,
        "listing_count": len(selected),
        "active_listing_count": sum(1 for item in selected if item.status.lower() == "active"),
        "total_views": sum(item.views for item in selected),
        "total_favorites": sum(item.favorites for item in selected),
        "total_sales": sum(item.sales for item in selected),
        "average_price": round(mean([item.price for item in selected if item.price > 0]), 2) if selected else 0,
        "top_tags": tag_report(selected)["tags"][:15],
        "top_listings": sorted(
            [item.to_dict() for item in selected],
            key=lambda row: (row.get("sales", 0), row.get("views", 0)),
            reverse=True,
        )[:20],
    }


def competitor_sales(shop: str, listings: Iterable[Listing]) -> dict[str, Any]:
    selected = [item for item in listings if item.shop.lower() == shop.lower()]
    total_sales = sum(item.sales for item in selected)
    age_days = mean([item.age_days() for item in selected]) if selected else 30
    daily = total_sales / max(age_days, 1)
    return {
        "shop": shop,
        "listing_count": len(selected),
        "estimated_total_sales": total_sales,
        "estimated_daily_sales": round(daily, 2),
        "estimated_weekly_sales": round(daily * 7, 2),
        "estimated_monthly_sales": round(daily * 30, 2),
        "method": "Local estimate from listing sales and listing age. Not eRank proprietary competitor sales data.",
    }


def top_sellers(listings: Iterable[Listing], limit: int = 100) -> dict[str, Any]:
    shops: dict[str, dict[str, Any]] = defaultdict(lambda: {"shop": "", "listings": 0, "sales": 0, "views": 0, "favorites": 0})
    for listing in listings:
        key = listing.shop or "(unknown)"
        shops[key]["shop"] = key
        shops[key]["listings"] += 1
        shops[key]["sales"] += listing.sales
        shops[key]["views"] += listing.views
        shops[key]["favorites"] += listing.favorites
    rows = sorted(shops.values(), key=lambda row: (row["sales"], row["views"]), reverse=True)[:limit]
    for index, row in enumerate(rows, 1):
        row["rank"] = index
    return {"sellers": rows}


def audit_listing(listing: Listing) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    recommendations: list[str] = []
    score = 100

    title_len = len(listing.title)
    if not listing.title:
        issues.append({"severity": "high", "code": "missing_title", "message": "Missing listing title."})
        score -= 25
    elif title_len < 40:
        issues.append({"severity": "medium", "code": "short_title", "message": "Title is short; add descriptive buyer search terms."})
        score -= 8
    elif title_len > 140:
        issues.append({"severity": "high", "code": "long_title", "message": "Title is longer than Etsy's 140 character limit."})
        score -= 18

    normalized_tags = [normalize_phrase(tag) for tag in listing.tags if normalize_phrase(tag)]
    duplicate_tags = [tag for tag, count in Counter(normalized_tags).items() if count > 1]
    one_word_tags = [tag for tag in normalized_tags if len(tag.split()) == 1]
    long_tags = [tag for tag in listing.tags if len(tag) > 20]
    if len(normalized_tags) < 13:
        issues.append({"severity": "medium", "code": "unused_tags", "message": f"Uses {len(normalized_tags)} of 13 Etsy tag slots."})
        score -= max(0, 13 - len(normalized_tags)) * 2
    if duplicate_tags:
        issues.append({"severity": "medium", "code": "duplicate_tags", "message": f"Duplicate tags: {', '.join(duplicate_tags[:5])}."})
        score -= min(10, len(duplicate_tags) * 3)
    if long_tags:
        issues.append({"severity": "high", "code": "long_tags", "message": f"Tags over 20 characters: {', '.join(long_tags[:5])}."})
        score -= min(15, len(long_tags) * 4)
    if len(one_word_tags) > 5:
        issues.append({"severity": "low", "code": "many_one_word_tags", "message": "Many tags are one word; consider more specific long-tail phrases."})
        score -= 4

    description_len = len(listing.description)
    if description_len < 250:
        issues.append({"severity": "medium", "code": "thin_description", "message": "Description is thin; add materials, sizing, use cases, care, and shipping details."})
        score -= 10

    title_tokens = set(tokenize(listing.title))
    tag_tokens = set(token for tag in normalized_tags for token in tokenize(tag))
    if title_tokens and tag_tokens:
        alignment = len(title_tokens.intersection(tag_tokens)) / max(len(tag_tokens), 1)
        if alignment < 0.25:
            issues.append({"severity": "medium", "code": "low_title_tag_alignment", "message": "Few tag terms appear in the title."})
            score -= 7
    else:
        alignment = 0.0

    if listing.price <= 0:
        issues.append({"severity": "high", "code": "missing_price", "message": "Price is missing or zero."})
        score -= 15
    if listing.image_count and listing.image_count < 5:
        issues.append({"severity": "low", "code": "few_images", "message": "Fewer than five images detected."})
        score -= 5
    if not listing.materials:
        issues.append({"severity": "low", "code": "missing_materials", "message": "Materials are missing."})
        score -= 3

    if not issues:
        recommendations.append("Listing covers the main SEO hygiene checks.")
    else:
        recommendations.extend(
            [
                "Fill all 13 tag slots with specific buyer phrases.",
                "Mirror the strongest tag phrases naturally in the title and opening description.",
                "Keep each Etsy tag at 20 characters or fewer.",
            ]
        )

    final_score = max(0, min(100, score))
    grade = "A" if final_score >= 90 else "B" if final_score >= 80 else "C" if final_score >= 70 else "D" if final_score >= 60 else "F"
    return {
        "listing_id": listing.listing_id,
        "shop": listing.shop,
        "title": listing.title,
        "score": final_score,
        "grade": grade,
        "issues": issues,
        "recommendations": recommendations,
        "checks": {
            "title_length": title_len,
            "tag_count": len(normalized_tags),
            "duplicate_tags": duplicate_tags,
            "long_tags": long_tags,
            "one_word_tag_count": len(one_word_tags),
            "description_length": description_len,
            "title_tag_alignment": round(alignment, 2),
            "image_count": listing.image_count,
        },
    }


def health_check(listings: Iterable[Listing], shop: str | None = None) -> dict[str, Any]:
    selected = [item for item in listings if not shop or item.shop.lower() == shop.lower()]
    audits = [audit_listing(item) for item in selected]
    buckets = Counter(audit["grade"] for audit in audits)
    issue_counts = Counter(issue["code"] for audit in audits for issue in audit["issues"])
    return {
        "shop": shop,
        "listing_count": len(selected),
        "grade_counts": dict(sorted(buckets.items())),
        "issue_counts": issue_counts.most_common(),
        "listings": audits,
    }


def compare_listing_audits(listings: Iterable[Listing]) -> dict[str, Any]:
    audits = [audit_listing(listing) for listing in listings]
    return {
        "count": len(audits),
        "best": max(audits, key=lambda audit: audit["score"], default=None),
        "listings": audits,
    }


def generate_listing_helper(seed: str, keywords: Iterable[str], listings: Iterable[Listing] | None = None) -> dict[str, Any]:
    seed_tokens = tokenize(seed)
    keyword_phrases = [normalize_phrase(keyword) for keyword in keywords if normalize_phrase(keyword)]
    if listings:
        for related in keyword_analysis(seed, listings, limit=5)["related_keywords"][:10]:
            keyword_phrases.append(related["keyword"])
    deduped: list[str] = []
    for phrase in keyword_phrases + [" ".join(seed_tokens[:3])]:
        phrase = phrase.strip()
        if phrase and phrase not in deduped and len(phrase) <= 20:
            deduped.append(phrase)
    tags = deduped[:13]
    title_parts = [seed.strip().title()]
    for phrase in tags[:4]:
        titled = phrase.title()
        if titled.lower() not in title_parts[0].lower():
            title_parts.append(titled)
    title = " | ".join(title_parts)[:140]
    description = (
        f"{seed.strip().title()} made for shoppers looking for {', '.join(tags[:5])}. "
        "Use the first paragraph to describe the product, size, material, occasion, and what is included. "
        "Close with processing time, personalization notes, and care instructions."
    )
    return {"title": title, "tags": tags, "description": description}


def profit_calculator(
    price: float,
    shipping_charged: float = 0,
    item_cost: float = 0,
    shipping_cost: float = 0,
    ad_cost: float = 0,
    listing_fee: float = 0.20,
    transaction_fee_rate: float = 0.065,
    payment_fee_rate: float = 0.03,
    payment_fixed_fee: float = 0.25,
    offsite_ad_rate: float = 0.0,
) -> dict[str, Any]:
    revenue = price + shipping_charged
    transaction_fee = revenue * transaction_fee_rate
    payment_fee = revenue * payment_fee_rate + payment_fixed_fee
    offsite_fee = revenue * offsite_ad_rate
    total_cost = item_cost + shipping_cost + ad_cost + listing_fee + transaction_fee + payment_fee + offsite_fee
    profit = revenue - total_cost
    margin = (profit / revenue) * 100 if revenue else 0
    return {
        "revenue": round(revenue, 2),
        "fees": {
            "listing_fee": round(listing_fee, 2),
            "transaction_fee": round(transaction_fee, 2),
            "payment_fee": round(payment_fee, 2),
            "offsite_ad_fee": round(offsite_fee, 2),
        },
        "costs": {
            "item_cost": round(item_cost, 2),
            "shipping_cost": round(shipping_cost, 2),
            "ad_cost": round(ad_cost, 2),
        },
        "total_cost": round(total_cost, 2),
        "profit": round(profit, 2),
        "margin_percent": round(margin, 2),
    }


def roi_calculator(ad_spend: float, clicks: int, orders: int, revenue: float, cost_of_goods: float = 0) -> dict[str, Any]:
    cpc = ad_spend / clicks if clicks else 0
    conversion_rate = (orders / clicks) * 100 if clicks else 0
    profit_before_ads = revenue - cost_of_goods
    roas = revenue / ad_spend if ad_spend else 0
    roi = ((profit_before_ads - ad_spend) / ad_spend) * 100 if ad_spend else 0
    cost_per_order = ad_spend / orders if orders else 0
    return {
        "ad_spend": round(ad_spend, 2),
        "clicks": clicks,
        "orders": orders,
        "revenue": round(revenue, 2),
        "cost_per_click": round(cpc, 2),
        "cost_per_order": round(cost_per_order, 2),
        "conversion_rate_percent": round(conversion_rate, 2),
        "roas": round(roas, 2),
        "roi_percent": round(roi, 2),
    }


def category_suggestions(title: str, tags: Iterable[str] = ()) -> dict[str, Any]:
    words = tokenize(" ".join([title, " ".join(tags)]))
    counter: Counter[str] = Counter()
    for word in words:
        if word in CATEGORY_HINTS:
            counter[CATEGORY_HINTS[word]] += 1
    suggestions = [{"category": category, "score": count} for category, count in counter.most_common(10)]
    return {"title": title, "suggestions": suggestions or [{"category": "Review Etsy taxonomy manually", "score": 0}]}


def sales_map(orders: Iterable[Order]) -> dict[str, Any]:
    countries: dict[str, dict[str, Any]] = defaultdict(lambda: {"country": "", "orders": 0, "revenue": 0.0})
    for order in orders:
        country = order.country or "(unknown)"
        countries[country]["country"] = country
        countries[country]["orders"] += 1
        countries[country]["revenue"] += order.total
    rows = sorted(countries.values(), key=lambda row: (row["orders"], row["revenue"]), reverse=True)
    for row in rows:
        row["revenue"] = round(row["revenue"], 2)
    return {"countries": rows}


def delivery_status(orders: Iterable[Order]) -> dict[str, Any]:
    statuses: dict[str, dict[str, Any]] = defaultdict(lambda: {"status": "", "orders": 0, "tracking_missing": 0})
    for order in orders:
        status = order.status or "(unknown)"
        statuses[status]["status"] = status
        statuses[status]["orders"] += 1
        if not order.tracking_number:
            statuses[status]["tracking_missing"] += 1
    return {"statuses": sorted(statuses.values(), key=lambda row: row["orders"], reverse=True)}


def spell_check(listings: Iterable[Listing], shop: str | None = None) -> dict[str, Any]:
    selected = [item for item in listings if not shop or item.shop.lower() == shop.lower()]
    suspicious = []
    for listing in selected:
        bad_tags = [tag for tag in listing.tags if re.search(r"[^a-zA-Z0-9 '&,-]", tag)]
        repeated_words = re.findall(r"\b([a-zA-Z]+)\s+\1\b", listing.title.lower())
        if bad_tags or repeated_words:
            suspicious.append(
                {
                    "listing_id": listing.listing_id,
                    "title": listing.title,
                    "bad_tags": bad_tags,
                    "repeated_words": sorted(set(repeated_words)),
                }
            )
    return {"shop": shop, "listing_count": len(selected), "potential_issues": suspicious}


def traffic_stats(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    sources: dict[str, dict[str, Any]] = defaultdict(lambda: {"source": "", "visits": 0, "orders": 0, "revenue": 0.0})
    for row in rows:
        source = str(row.get("source") or row.get("channel") or row.get("medium") or "(unknown)")
        sources[source]["source"] = source
        sources[source]["visits"] += int(parse_number(row.get("visits") or row.get("sessions") or row.get("views"), 0))
        sources[source]["orders"] += int(parse_number(row.get("orders") or row.get("sales"), 0))
        sources[source]["revenue"] += parse_number(row.get("revenue") or row.get("total"), 0)
    result = sorted(sources.values(), key=lambda row: (row["revenue"], row["visits"]), reverse=True)
    for row in result:
        row["conversion_rate_percent"] = round((row["orders"] / row["visits"]) * 100, 2) if row["visits"] else 0
        row["revenue"] = round(row["revenue"], 2)
    return {"sources": result}


def trend_buzz(rows: Iterable[dict[str, Any]], marketplace: str | None = None, limit: int = 100) -> dict[str, Any]:
    selected = []
    for row in rows:
        market = str(row.get("marketplace") or row.get("platform") or "etsy").lower()
        if marketplace and market != marketplace.lower():
            continue
        keyword = str(row.get("keyword") or row.get("term") or row.get("query") or "").strip()
        if not keyword:
            continue
        selected.append(
            {
                "keyword": keyword,
                "marketplace": market,
                "search_volume": int(parse_number(row.get("search_volume") or row.get("volume") or row.get("avg_searches"), 0)),
                "competition": int(parse_number(row.get("competition") or row.get("results"), 0)),
                "trend": parse_number(row.get("trend") or row.get("growth") or row.get("change"), 0),
                "category": row.get("category", ""),
            }
        )
    selected.sort(key=lambda row: (row["trend"], row["search_volume"]), reverse=True)
    return {"marketplace": marketplace, "trends": selected[:limit]}


def monthly_calendar(country: str = "US", month: int | None = None) -> dict[str, Any]:
    month = month or date.today().month
    reminders = {
        1: ["Valentine listing refresh", "Spring wedding keyword planning"],
        2: ["Mother's Day research", "Spring decor inventory"],
        3: ["Graduation gifts", "Easter and spring tags"],
        4: ["Mother's Day final push", "Summer party products"],
        5: ["Father's Day", "Wedding season"],
        6: ["Back-to-school research", "Summer travel gifts"],
        7: ["Fall decor planning", "Halloween keyword drafts"],
        8: ["Halloween launch", "Q4 holiday inventory"],
        9: ["Christmas SEO refresh", "Thanksgiving and fall gifting"],
        10: ["Black Friday readiness", "Holiday shipping cutoffs"],
        11: ["Cyber week", "Last-order-by date messaging"],
        12: ["New year trends", "Valentine product planning"],
    }
    return {"country": country, "month": month, "reminders": reminders.get(month, [])}


def api_surface_report() -> dict[str, Any]:
    return {
        "erank_public_api": {
            "found": False,
            "summary": "No official public eRank developer API documentation was found in eRank public docs during this build.",
        },
        "known_integrations": [
            "eRank states that it uses Etsy API.",
            "eRank's public GitHub organization exposes a fork of an Etsy API v3 PHP SDK.",
            "The eRank Chrome extension surfaces eRank data in the browser, but that is not documented as a public API.",
        ],
        "undocumented_read_only_routes": {
            "stability": "not guaranteed; probe at runtime",
            "routes": [
                "/api/top-sellers/most-sales-yesterday",
                "/api/top-sellers",
                "/api/shop-info/{shop_name}",
                "/api/shop-info/{shop_name}/badge",
                "/api/shop-info/{shop_name}/listings",
            ],
            "boundary": "Public responses may be sample-limited. Complete paid/member data stays in the logged-in same-origin browser or member exports.",
        },
        "member_workflow": [
            "live member-plan",
            "live member-ingest",
            "live evidence-check --require-complete",
        ],
        "recommended_backend": {
            "name": "Etsy Open API v3",
            "requires": ["x-api-key", "OAuth token for private seller data"],
            "covers": ["shops", "listings", "inventory", "orders/receipts", "taxonomy"],
        },
        "harness_policy": "Do not bypass eRank login, plan limits, or browser security. Use same-origin member reads, Etsy API, or imported exports.",
    }


def listings_summary(listings: Iterable[Listing]) -> dict[str, Any]:
    rows = list(listings)
    return {
        "listing_count": len(rows),
        "shops": len({row.shop for row in rows if row.shop}),
        "total_views": sum(row.views for row in rows),
        "total_favorites": sum(row.favorites for row in rows),
        "total_sales": sum(row.sales for row in rows),
        "average_price": round(mean([row.price for row in rows if row.price > 0]), 2) if rows else 0,
        "status_counts": dict(Counter(row.status for row in rows)),
    }
