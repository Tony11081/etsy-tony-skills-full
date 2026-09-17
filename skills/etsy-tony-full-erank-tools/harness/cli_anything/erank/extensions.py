from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timezone
import json
import math
from pathlib import Path
from typing import Any

import click

from cli_anything.erank.core.analyzers import shop_info as shop_info_analysis
from cli_anything.erank.core.intelligence import (
    analyze_image_file,
    breakout_radar,
    change_impact,
    cluster_listings,
    cro_audit,
    cross_market_validation,
    detect_anomalies,
    fact_gated_draft,
    keyword_portfolio,
    opportunity_engine,
    seasonal_plan,
    true_profit,
    watchlist_alerts,
)
from cli_anything.erank.core.models import Listing
from cli_anything.erank.core.shop_search import load_shop_rows
from cli_anything.erank.utils.data_io import load_listings, load_rows, write_csv, write_json
from cli_anything.erank.utils.etsy_backend import EtsyBackend
from cli_anything.erank.utils.live_sources import (
    derive_shop_tags,
    fetch_erank_shop_info,
    fetch_erank_shop_listings,
    fetch_erank_top_sellers,
    parse_erank_or_export,
)
from cli_anything.erank.utils.member_data import evidence_report, member_request_plan, merge_member_pages


def _emit(ctx: click.Context, payload: Any) -> None:
    click.echo(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def _require_listings(path: str | None) -> list[Listing]:
    listings = load_listings(path)
    if not listings:
        raise click.ClickException("No listings were loaded from the supplied file.")
    return listings


def _backend(ctx: click.Context) -> EtsyBackend:
    return EtsyBackend(ctx.obj["session"].config())


def _read_json(path: str | Path, default: Any = None) -> Any:
    source = Path(path)
    if not source.exists():
        return default
    return json.loads(source.read_text(encoding="utf-8-sig"))


def _number(value: Any) -> float | None:
    if value in (None, "") or str(value).strip().lower() in {"unknown", "n/a", "< 20", "<20"}:
        return None
    try:
        return float(str(value).replace(",", "").replace("%", "").strip())
    except ValueError:
        return None


def _merge_opportunity_inputs(paths: tuple[str, ...]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    merged: dict[str, dict[str, Any]] = {}
    conflicts: list[dict[str, Any]] = []
    for path in paths:
        for index, row in enumerate(load_rows(path)):
            key_value = row.get("product") or row.get("sku") or row.get("keyword") or row.get("name")
            key = str(key_value or f"{Path(path).name}:{index}").strip().lower()
            target = merged.setdefault(key, {"_source_files": []})
            target["_source_files"].append(str(Path(path).resolve()))
            for field, value in row.items():
                if value in (None, ""):
                    continue
                if field not in target or target[field] in (None, ""):
                    target[field] = value
                elif str(target[field]) != str(value):
                    conflicts.append({"key": key, "field": field, "kept": target[field], "conflicting": value, "source": str(Path(path).resolve())})
    return list(merged.values()), conflicts


def _etsy_shop_id(live: EtsyBackend, shop: str, shop_id: str) -> str:
    if shop_id:
        return shop_id
    matches = live.find_shops(shop, limit=10)
    exact = [row for row in matches if str(row.get("shop_name") or "").lower() == shop.lower()]
    selected = exact[0] if exact else (matches[0] if matches else None)
    if not selected or not selected.get("shop_id"):
        raise click.ClickException(f"Etsy shop was not found: {shop}")
    return str(selected["shop_id"])


def _listing_report(
    ctx: click.Context,
    *,
    shop: str,
    source: str,
    input_path: str | None,
    shop_id: str,
    limit: int,
    timeout: int,
) -> dict[str, Any]:
    if source == "erank-live":
        return fetch_erank_shop_listings(shop, limit=limit, timeout=timeout)
    if source == "export":
        if not input_path:
            raise click.ClickException("Missing --input for exported shop listings.")
        listings = load_listings(input_path)
        selected = [item for item in listings if not item.shop or item.shop.lower() == shop.lower()][:limit]
        return {
            "shop": shop,
            "source": "local-export",
            "fetched_at": datetime.fromtimestamp(Path(input_path).stat().st_mtime, timezone.utc).isoformat(),
            "requested_limit": limit,
            "count": len(selected),
            "category": "",
            "is_handmade": None,
            "top_categories": [],
            "top_tags": [],
            "listings": [item.to_dict() for item in selected],
            "coverage": "input_rows_only",
            "limitations": ["Coverage is limited to rows in the supplied export."],
        }
    live = _backend(ctx)
    numeric_shop_id = _etsy_shop_id(live, shop, shop_id)
    listings: list[Listing] = []
    for offset in range(0, limit, 100):
        batch = live.shop_listings(numeric_shop_id, limit=min(100, limit - offset), offset=offset)
        listings.extend(batch)
        if len(batch) < min(100, limit - offset):
            break
    return {
        "shop": shop,
        "shop_id": numeric_shop_id,
        "source": "etsy-open-api-v3",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "requested_limit": limit,
        "count": len(listings),
        "listings": [item.to_dict() for item in listings],
        "top_categories": [],
        "top_tags": [],
        "coverage": "requested_active_listing_pages",
        "limitations": ["Etsy Open API fields depend on the configured application and scopes."],
    }


def register_extensions(
    *,
    cli: click.Group,
    live_group: click.Group,
    competitor_group: click.Group,
    listing_group: click.Group,
    keyword_group: click.Group,
    shop_group: click.Group,
    tools_group: click.Group,
    trends_group: click.Group,
) -> None:
    @live_group.command("member-ingest")
    @click.option("--input", "inputs", multiple=True, required=True, type=click.Path(exists=True, dir_okay=False))
    @click.option("--expected-total", type=click.IntRange(0), help="Optional expected member-plan row count.")
    @click.option("--output", type=click.Path(dir_okay=False), help="Optional merged JSON output.")
    @click.pass_context
    def live_member_ingest(ctx: click.Context, inputs: tuple[str, ...], expected_total: int | None, output: str | None) -> None:
        """Merge saved same-origin member JSON pages and report missing pages."""
        try:
            result = merge_member_pages(inputs, expected_total=expected_total)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            raise click.ClickException(str(exc)) from exc
        if output:
            result["output"] = write_json(output, result)
        _emit(ctx, result)

    @live_group.command("member-plan")
    @click.option("--timeframe", type=click.Choice(["all-time", "yesterday"]), default="all-time", show_default=True)
    @click.option("--pages", "page_count", default=1, type=click.IntRange(1, 1000), show_default=True)
    @click.option("--per-page", default=100, type=click.IntRange(1, 100), show_default=True)
    @click.option("--resume-from", type=click.Path(exists=True, dir_okay=False), help="Merged member JSON whose missing_pages should be requested.")
    @click.option("--output", type=click.Path(dir_okay=False))
    @click.pass_context
    def live_member_plan(ctx: click.Context, timeframe: str, page_count: int, per_page: int, resume_from: str | None, output: str | None) -> None:
        """Build safe same-origin member GET paths, including resume pages."""
        missing_pages: list[int] = []
        if resume_from:
            payload = _read_json(resume_from)
            if not isinstance(payload, dict):
                raise click.ClickException("Resume file must be a merged member JSON object.")
            missing_pages = list((payload.get("meta") or {}).get("missing_pages") or [])
        try:
            result = member_request_plan(timeframe=timeframe, page_count=page_count, per_page=per_page, missing_pages=missing_pages)
        except ValueError as exc:
            raise click.ClickException(str(exc)) from exc
        if resume_from:
            result["resume_from"] = str(Path(resume_from).resolve())
            result["resume_complete"] = not missing_pages
            if not missing_pages:
                result["requests"] = []
                result["request_count"] = 0
        if output:
            result["output"] = write_json(output, result)
        _emit(ctx, result)

    @live_group.command("evidence-check")
    @click.option("--input", "input_path", required=True, type=click.Path(exists=True, dir_okay=False))
    @click.option("--max-age-hours", default=24.0, show_default=True, type=float)
    @click.option("--require-complete", is_flag=True)
    @click.pass_context
    def live_evidence_check(ctx: click.Context, input_path: str, max_age_hours: float, require_complete: bool) -> None:
        """Validate source, freshness, coverage, and credential safety."""
        try:
            _emit(ctx, evidence_report(input_path, max_age_hours=max_age_hours, require_complete=require_complete))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            raise click.ClickException(str(exc)) from exc

    @live_group.command("shop-info")
    @click.argument("shop")
    @click.option("--source", type=click.Choice(["erank-live", "etsy", "export"]), default="erank-live", show_default=True)
    @click.option("--input", "input_path", type=click.Path(exists=True, dir_okay=False))
    @click.option("--shop-id", default="")
    @click.option("--timeout", default=30, type=click.IntRange(1, 60), show_default=True)
    @click.pass_context
    def live_shop_info(ctx: click.Context, shop: str, source: str, input_path: str | None, shop_id: str, timeout: int) -> None:
        """Read a shop overview from eRank, Etsy API, or an export."""
        try:
            if source == "erank-live":
                result = fetch_erank_shop_info(shop, timeout=timeout)
            elif source == "etsy":
                live = _backend(ctx)
                numeric_shop_id = _etsy_shop_id(live, shop, shop_id)
                result = {"shop": shop, "source": "etsy-open-api-v3", "overview": live.shop_by_id(numeric_shop_id)}
            else:
                if not input_path:
                    raise click.ClickException("Missing --input for exported shop data.")
                result = shop_info_analysis(shop, _require_listings(input_path))
                result.update({"source": "local-export", "coverage": "input_rows_only"})
        except click.ClickException:
            raise
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc
        _emit(ctx, result)

    @live_group.command("shop-listings")
    @click.argument("shop")
    @click.option("--source", type=click.Choice(["erank-live", "etsy", "export"]), default="erank-live", show_default=True)
    @click.option("--input", "input_path", type=click.Path(exists=True, dir_okay=False))
    @click.option("--shop-id", default="")
    @click.option("--limit", default=100, type=click.IntRange(1, 500), show_default=True)
    @click.option("--timeout", default=30, type=click.IntRange(1, 60), show_default=True)
    @click.option("--output", type=click.Path(dir_okay=False))
    @click.pass_context
    def live_shop_listings(ctx: click.Context, shop: str, source: str, input_path: str | None, shop_id: str, limit: int, timeout: int, output: str | None) -> None:
        """Read bounded competitor listings without copying browser credentials."""
        try:
            result = _listing_report(ctx, shop=shop, source=source, input_path=input_path, shop_id=shop_id, limit=limit, timeout=timeout)
        except click.ClickException:
            raise
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc
        if output:
            result["output"] = {"path": str(Path(output).resolve()), "rows": write_csv(output, result["listings"])}
        _emit(ctx, result)

    @live_group.command("shop-tags")
    @click.argument("shop")
    @click.option("--source", type=click.Choice(["erank-live", "etsy", "export"]), default="erank-live", show_default=True)
    @click.option("--input", "input_path", type=click.Path(exists=True, dir_okay=False))
    @click.option("--shop-id", default="")
    @click.option("--listing-limit", default=100, type=click.IntRange(1, 500), show_default=True)
    @click.option("--limit", default=100, type=click.IntRange(1, 500), show_default=True)
    @click.option("--timeout", default=30, type=click.IntRange(1, 60), show_default=True)
    @click.pass_context
    def live_shop_tags(ctx: click.Context, shop: str, source: str, input_path: str | None, shop_id: str, listing_limit: int, limit: int, timeout: int) -> None:
        """Derive competitor tag frequency from the bounded listing sample."""
        try:
            report = _listing_report(ctx, shop=shop, source=source, input_path=input_path, shop_id=shop_id, limit=listing_limit, timeout=timeout)
            _emit(ctx, derive_shop_tags(report, limit=limit))
        except click.ClickException:
            raise
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc

    @competitor_group.command("clusters")
    @click.option("--listings", required=True, type=click.Path(exists=True, dir_okay=False))
    @click.option("--previous", type=click.Path(exists=True, dir_okay=False), help="Optional prior listing snapshot for growth drivers.")
    @click.option("--shop", default="")
    @click.pass_context
    def competitor_clusters(ctx: click.Context, listings: str, previous: str | None, shop: str) -> None:
        """Cluster competitor listings into product families and price bands."""
        items = _require_listings(listings)
        if shop:
            items = [item for item in items if item.shop.lower() == shop.lower()]
        previous_items = load_listings(previous) if previous else []
        if shop:
            previous_items = [item for item in previous_items if item.shop.lower() == shop.lower()]
        result = cluster_listings(items, previous_items)
        result["inputs"] = {"current": str(Path(listings).resolve()), "previous": str(Path(previous).resolve()) if previous else None}
        _emit(ctx, result)

    @listing_group.command("impact")
    @click.option("--before", required=True, type=click.Path(exists=True, dir_okay=False))
    @click.option("--after", required=True, type=click.Path(exists=True, dir_okay=False))
    @click.option("--before-at", type=click.DateTime())
    @click.option("--after-at", type=click.DateTime())
    @click.pass_context
    def listing_impact(ctx: click.Context, before: str, after: str, before_at: datetime | None, after_at: datetime | None) -> None:
        """Correlate listing edits with later metric deltas without causal claims."""
        result = change_impact(_require_listings(before), _require_listings(after), before_at, after_at)
        result["inputs"] = {"before": str(Path(before).resolve()), "after": str(Path(after).resolve())}
        _emit(ctx, result)

    @listing_group.command("cro-audit")
    @click.option("--listing-file", required=True, type=click.Path(exists=True, dir_okay=False))
    @click.option("--image-manifest", type=click.Path(exists=True, dir_okay=False))
    @click.option("--image", "image_paths", multiple=True, type=click.Path(exists=True, dir_okay=False))
    @click.pass_context
    def listing_cro_audit(ctx: click.Context, listing_file: str, image_manifest: str | None, image_paths: tuple[str, ...]) -> None:
        """Audit image resolution plus supplied merchandising/CRO evidence."""
        listing = _require_listings(listing_file)[0]
        images = load_rows(image_manifest) if image_manifest else []
        technical = []
        for path in image_paths:
            technical.append(analyze_image_file(str(Path(path).resolve())))
        if technical:
            images = technical + images
        _emit(ctx, cro_audit(listing, images))

    @listing_group.command("fact-draft")
    @click.option("--facts", required=True, type=click.Path(exists=True, dir_okay=False))
    @click.option("--keyword", "keywords", multiple=True)
    @click.option("--keywords-file", type=click.Path(exists=True, dir_okay=False))
    @click.pass_context
    def listing_fact_draft(ctx: click.Context, facts: str, keywords: tuple[str, ...], keywords_file: str | None) -> None:
        """Generate a review-only draft from confirmed facts with exactly 13 tags."""
        payload = _read_json(facts)
        if not isinstance(payload, dict):
            raise click.ClickException("Facts file must be a JSON object.")
        terms = list(keywords)
        if keywords_file:
            terms.extend(line.strip() for line in Path(keywords_file).read_text(encoding="utf-8").splitlines() if line.strip())
        try:
            _emit(ctx, fact_gated_draft(payload, terms))
        except ValueError as exc:
            raise click.ClickException(str(exc)) from exc

    @keyword_group.command("portfolio")
    @click.option("--listings", required=True, type=click.Path(exists=True, dir_okay=False))
    @click.option("--metrics", type=click.Path(exists=True, dir_okay=False))
    @click.pass_context
    def keyword_portfolio_command(ctx: click.Context, listings: str, metrics: str | None) -> None:
        """Map keyword intent, tag slots, and listing cannibalization."""
        result = keyword_portfolio(_require_listings(listings), load_rows(metrics) if metrics else [])
        result["inputs"] = {"listings": str(Path(listings).resolve()), "metrics": str(Path(metrics).resolve()) if metrics else None}
        _emit(ctx, result)

    @tools_group.command("true-profit")
    @click.option("--price", required=True, type=float)
    @click.option("--shipping-charged", default=0.0, show_default=True)
    @click.option("--supplier-cost", default=0.0, show_default=True)
    @click.option("--shipping-cost", default=0.0, show_default=True)
    @click.option("--packaging-cost", default=0.0, show_default=True)
    @click.option("--ad-cost", default=0.0, show_default=True)
    @click.option("--production-minutes", default=0.0, show_default=True)
    @click.option("--labor-rate-hourly", default=0.0, show_default=True)
    @click.option("--return-rate", default=0.0, show_default=True)
    @click.option("--breakage-rate", default=0.0, show_default=True)
    @click.option("--weekly-orders", default=0.0, show_default=True)
    @click.option("--weekly-capacity-minutes", default=0.0, show_default=True)
    @click.option("--target-margin", default=30.0, show_default=True)
    @click.option("--formula-multiplier", type=float)
    @click.option("--offsite-ad-rate", default=0.0, show_default=True)
    @click.pass_context
    def tools_true_profit(ctx: click.Context, **kwargs: Any) -> None:
        """Calculate expected profit, returns, breakage, labor, capacity, and formula gates."""
        try:
            _emit(ctx, true_profit(**kwargs))
        except ValueError as exc:
            raise click.ClickException(str(exc)) from exc

    @trends_group.command("seasonal-plan")
    @click.option("--input", "input_path", required=True, type=click.Path(exists=True, dir_okay=False))
    @click.option("--lead-days", default=45, type=click.IntRange(0), show_default=True)
    @click.option("--as-of", type=click.DateTime(formats=["%Y-%m-%d"]))
    @click.pass_context
    def trends_seasonal_plan(ctx: click.Context, input_path: str, lead_days: int, as_of: datetime | None) -> None:
        """Backtest monthly signals and calculate lead-time-aware launch dates."""
        result = seasonal_plan(load_rows(input_path), lead_days=lead_days, as_of=(as_of.date() if as_of else None))
        result["input"] = str(Path(input_path).resolve())
        _emit(ctx, result)

    @shop_group.command("anomalies")
    @click.option("--current", required=True, type=click.Path(exists=True, dir_okay=False))
    @click.option("--previous", type=click.Path(exists=True, dir_okay=False))
    @click.option("--spike-multiplier", default=5.0, type=float, show_default=True)
    @click.option("--max-age-hours", default=168.0, type=float, show_default=True)
    @click.pass_context
    def shop_anomalies(ctx: click.Context, current: str, previous: str | None, spike_multiplier: float, max_age_hours: float) -> None:
        """Detect duplicate, impossible, decreasing, spike, and schema-drift data."""
        current_rows, _ = load_shop_rows(current)
        previous_rows, _ = load_shop_rows(previous) if previous else ([], {})
        try:
            result = detect_anomalies(current_rows, previous_rows, spike_multiplier=spike_multiplier)
            evidence = evidence_report(current, max_age_hours=max_age_hours, require_complete=True)
            result["evidence"] = evidence
            if evidence["freshness"] != "fresh":
                result["anomalies"].append({"identity": "dataset", "code": "stale_evidence", "age_hours": evidence["age_hours"]})
            if not evidence["complete"]:
                result["anomalies"].append({"identity": "dataset", "code": "incomplete_coverage", "coverage": evidence["coverage"]})
            result["anomaly_count"] = len(result["anomalies"])
            _emit(ctx, result)
        except ValueError as exc:
            raise click.ClickException(str(exc)) from exc

    @shop_group.command("watchlist-alerts")
    @click.option("--current", required=True, type=click.Path(exists=True, dir_okay=False))
    @click.option("--previous", required=True, type=click.Path(exists=True, dir_okay=False))
    @click.option("--state", "state_path", type=click.Path(dir_okay=False))
    @click.option("--resolve-alert", "resolved_alert_ids", multiple=True, help="Mark an unresolved alert id as reviewed.")
    @click.option("--output", type=click.Path(dir_okay=False), help="Optional JSON alert report.")
    @click.option("--max-age-hours", default=168.0, type=float, show_default=True)
    @click.option("--min-sales-growth", default=10.0, type=float, show_default=True)
    @click.option("--min-review-growth", default=3.0, type=float, show_default=True)
    @click.option("--min-listing-growth", default=5.0, type=float, show_default=True)
    @click.pass_context
    def shop_watchlist_alerts(
        ctx: click.Context,
        current: str,
        previous: str,
        state_path: str | None,
        resolved_alert_ids: tuple[str, ...],
        output: str | None,
        max_age_hours: float,
        min_sales_growth: float,
        min_review_growth: float,
        min_listing_growth: float,
    ) -> None:
        """Generate deduplicated alerts only from fresh and complete evidence."""
        current_rows, _ = load_shop_rows(current)
        previous_rows, _ = load_shop_rows(previous)
        current_evidence = evidence_report(current, max_age_hours=max_age_hours, require_complete=True)
        previous_evidence = evidence_report(previous, max_age_hours=max_age_hours, require_complete=True)
        state = _read_json(state_path, {}) if state_path else {}
        seen = state.get("seen_alert_ids", []) if isinstance(state, dict) else []
        prior_unresolved = state.get("unresolved", []) if isinstance(state, dict) else []
        resolved = set(resolved_alert_ids)
        prior_unresolved = [alert for alert in prior_unresolved if alert.get("alert_id") not in resolved]
        result = watchlist_alerts(
            current_rows,
            previous_rows,
            seen_alert_ids=seen,
            prior_unresolved=prior_unresolved,
            min_sales_growth=min_sales_growth,
            min_review_growth=min_review_growth,
            min_listing_growth=min_listing_growth,
            evidence_ok=current_evidence["accepted"] and previous_evidence["accepted"],
        )
        result["evidence"] = {"current": current_evidence, "previous": previous_evidence}
        result["resolved_alert_ids"] = sorted(resolved)
        if state_path and "state" in result:
            result["state_output"] = write_json(state_path, result["state"])
        if output:
            result["output"] = write_json(output, result)
        _emit(ctx, result)

    @click.group("selection")
    def selection_group() -> None:
        """Private-data product selection and breakout-shop intelligence."""

    @selection_group.command("breakout-shops")
    @click.option("--input", "input_path", required=True, type=click.Path(exists=True, dir_okay=False))
    @click.option("--previous", type=click.Path(exists=True, dir_okay=False))
    @click.option("--snapshot-dir", type=click.Path(file_okay=False), help="Save current rows and reuse the latest prior snapshot.")
    @click.option("--age-min-months", default=3, type=click.IntRange(0), show_default=True)
    @click.option("--age-max-months", default=5, type=click.IntRange(0), show_default=True)
    @click.option("--sales-min", default=660, type=click.IntRange(0), show_default=True)
    @click.option("--sales-max", default=680, type=click.IntRange(0), show_default=True)
    @click.option("--snapshot-days", default=7.0, type=float, show_default=True)
    @click.option("--as-of", type=click.DateTime(formats=["%Y-%m-%d"]))
    @click.option("--max-age-hours", default=168.0, type=float, show_default=True)
    @click.option("--output", type=click.Path(dir_okay=False))
    @click.pass_context
    def selection_breakout_shops(
        ctx: click.Context,
        input_path: str,
        previous: str | None,
        snapshot_dir: str | None,
        age_min_months: int,
        age_max_months: int,
        sales_min: int,
        sales_max: int,
        snapshot_days: float,
        as_of: datetime | None,
        max_age_hours: float,
        output: str | None,
    ) -> None:
        """Find young high-velocity shops with strict lifetime-sales semantics."""
        rows, metadata = load_shop_rows(input_path)
        previous_from_snapshot = False
        if snapshot_dir and not previous:
            snapshot_root = Path(snapshot_dir)
            existing = sorted(snapshot_root.glob("shop-snapshot-*.json"), key=lambda path: path.stat().st_mtime)
            if existing:
                previous = str(existing[-1])
                previous_from_snapshot = True
        previous_rows, _ = load_shop_rows(previous) if previous else ([], {})
        try:
            result = breakout_radar(
                rows,
                as_of=(as_of.date() if as_of else datetime.now(timezone.utc).date()),
                age_min_months=age_min_months,
                age_max_months=age_max_months,
                sales_min=sales_min,
                sales_max=sales_max,
                previous_rows=previous_rows,
                snapshot_days=snapshot_days,
            )
            result["evidence"] = evidence_report(input_path, max_age_hours=max_age_hours)
            result["source_metadata"] = metadata
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            raise click.ClickException(str(exc)) from exc
        result["result_status"] = "VERIFIED_MATCHES" if result["match_count"] and result["evidence"]["accepted"] else "UNVERIFIED_MATCHES" if result["match_count"] else "NO_MATCHES"
        if previous:
            result["previous_snapshot"] = {"path": str(Path(previous).resolve()), "auto_selected": previous_from_snapshot}
        if snapshot_dir:
            captured = datetime.now(timezone.utc)
            snapshot_path = Path(snapshot_dir) / f"shop-snapshot-{captured.strftime('%Y%m%dT%H%M%SZ')}.json"
            snapshot_payload = {
                "source": metadata.get("source") or "local-export",
                "coverage": metadata.get("coverage") or "input_rows_only",
                "fetched_at": metadata.get("fetched_at") or captured.isoformat(),
                "rows": rows,
            }
            result["snapshot_output"] = write_json(snapshot_path, snapshot_payload)
        if output:
            result["output"] = write_json(output, result)
        _emit(ctx, result)

    @selection_group.command("opportunity")
    @click.option("--input", "input_paths", multiple=True, required=True, type=click.Path(exists=True, dir_okay=False), help="Repeat for market, cost, capability, and risk exports.")
    @click.option("--target-margin", default=30.0, type=float, show_default=True)
    @click.option("--output", type=click.Path(dir_okay=False))
    @click.pass_context
    def selection_opportunity(ctx: click.Context, input_paths: tuple[str, ...], target_margin: float, output: str | None) -> None:
        """Score products using market evidence, margin, capacity fit, and risk."""
        rows, conflicts = _merge_opportunity_inputs(input_paths)
        result = opportunity_engine(rows, target_margin=target_margin)
        result["input_sources"] = [str(Path(path).resolve()) for path in input_paths]
        result["merge_conflicts"] = conflicts
        if output:
            result["output"] = write_json(output, result)
        _emit(ctx, result)

    @selection_group.command("cross-market")
    @click.option("--input", "input_path", required=True, type=click.Path(exists=True, dir_okay=False))
    @click.option("--min-sources", default=3, type=click.IntRange(1), show_default=True)
    @click.pass_context
    def selection_cross_market(ctx: click.Context, input_path: str, min_sources: int) -> None:
        """Require agreement across multiple market channels before promotion."""
        result = cross_market_validation(load_rows(input_path), min_sources=min_sources)
        result["input"] = str(Path(input_path).resolve())
        _emit(ctx, result)

    @selection_group.command("daily")
    @click.option("--source", type=click.Choice(["mixed-live", "exports"]), default="mixed-live", show_default=True)
    @click.option("--yesterday-input", type=click.Path(exists=True, dir_okay=False))
    @click.option("--member-all-time-input", type=click.Path(exists=True, dir_okay=False))
    @click.option("--trend-input", type=click.Path(exists=True, dir_okay=False))
    @click.option("--tracked-input", type=click.Path(exists=True, dir_okay=False))
    @click.option("--yesterday-limit", default=300, type=click.IntRange(1, 1000), show_default=True)
    @click.option("--all-time-limit", default=300, type=click.IntRange(1, 10000), show_default=True)
    @click.option("--top-n", default=3, type=click.IntRange(1, 100), show_default=True)
    @click.option("--output-dir", type=click.Path(file_okay=False))
    @click.pass_context
    def selection_daily(
        ctx: click.Context,
        source: str,
        yesterday_input: str | None,
        member_all_time_input: str | None,
        trend_input: str | None,
        tracked_input: str | None,
        yesterday_limit: int,
        all_time_limit: int,
        top_n: int,
        output_dir: str | None,
    ) -> None:
        """Combine yesterday, all-time, trend, and tracked-shop signals."""
        limitations: list[str] = []
        if yesterday_input:
            yesterday = parse_erank_or_export(yesterday_input)[:yesterday_limit]
            yesterday_complete = evidence_report(yesterday_input, max_age_hours=168, require_complete=True)["accepted"]
        elif source == "mixed-live":
            yesterday = fetch_erank_top_sellers("yesterday", yesterday_limit)
            yesterday_complete = len(yesterday) >= yesterday_limit
            if not yesterday_complete:
                limitations.append("The no-cookie yesterday endpoint returned fewer rows than requested; member-session coverage is not proven.")
        else:
            yesterday = []
            yesterday_complete = False
            limitations.append("No yesterday export was supplied.")
        all_time = parse_erank_or_export(member_all_time_input)[:all_time_limit] if member_all_time_input else []
        all_time_complete = evidence_report(member_all_time_input, max_age_hours=168, require_complete=True)["accepted"] if member_all_time_input else False
        if not member_all_time_input:
            limitations.append("Complete member all-time data was not supplied; all-time confirmation is unavailable.")
        all_time_map = {str(row.get("shop") or "").lower(): row for row in all_time}
        tracked = load_rows(tracked_input) if tracked_input else []
        trend_rows = load_rows(trend_input) if trend_input else []
        tracked_names = {str(row.get("shop") or row.get("shop_name") or "").lower() for row in tracked}
        candidates = []
        for row in yesterday:
            shop = str(row.get("shop") or "")
            lifetime = all_time_map.get(shop.lower())
            score = float(row.get("sales") or row.get("total_sales") or row.get("monthly_sales") or 0)
            haystack = " ".join(str(row.get(key) or "") for key in ("category", "what_sold", "shop")).lower()
            trend_matches = []
            for trend in trend_rows:
                keyword = str(trend.get("keyword") or trend.get("product") or "").strip().lower()
                if keyword and keyword in haystack:
                    volume = _number(trend.get("search_volume") or trend.get("demand"))
                    growth = _number(trend.get("growth") or trend.get("trend"))
                    if volume is None and growth is None:
                        continue
                    boost = min(math.log1p(max(volume or 0, 0)) * 2 + max(growth or 0, 0), 50)
                    score += boost
                    trend_matches.append({"keyword": keyword, "boost": round(boost, 2)})
            if lifetime:
                score += 50
            if shop.lower() in tracked_names:
                score += 25
            candidates.append({"shop": shop, "score": round(score, 2), "yesterday": row, "all_time": lifetime, "tracked": shop.lower() in tracked_names, "trend_matches": trend_matches})
        candidates.sort(key=lambda row: row["score"], reverse=True)
        result = {
            "source": source,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "yesterday_count": len(yesterday),
            "all_time_count": len(all_time),
            "trend_rows": len(trend_rows),
            "tracked_rows": len(tracked),
            "recommendations": candidates[:top_n],
            "limitations": limitations,
            "result_status": "VERIFIED_COMPLETE" if yesterday and all_time and yesterday_complete and all_time_complete else "PARTIAL",
        }
        if output_dir:
            target = Path(output_dir) / f"erank-daily-selection-{date.today().isoformat()}.json"
            result["output"] = write_json(target, result)
        _emit(ctx, result)

    @selection_group.command("sales-report")
    @click.option("--source", type=click.Choice(["erank-live", "erank-export"]), default="erank-live", show_default=True)
    @click.option("--timeframe", type=click.Choice(["yesterday", "all-time"]), default="yesterday", show_default=True)
    @click.option("--input", "input_path", type=click.Path(exists=True, dir_okay=False))
    @click.option("--limit", default=300, type=click.IntRange(1, 10000), show_default=True)
    @click.option("--output-dir", type=click.Path(file_okay=False))
    @click.pass_context
    def selection_sales_report(ctx: click.Context, source: str, timeframe: str, input_path: str | None, limit: int, output_dir: str | None) -> None:
        """Build a reproducible shop-sales summary from live or exported rows."""
        if source == "erank-export":
            if not input_path:
                raise click.ClickException("Missing --input for eRank export.")
            rows = parse_erank_or_export(input_path)[:limit]
        else:
            rows = fetch_erank_top_sellers(timeframe, limit)
        categories = Counter(str(row.get("category") or row.get("what_sold") or "Unknown") for row in rows)
        complete = False
        if source == "erank-export" and input_path:
            complete = evidence_report(input_path, max_age_hours=168, require_complete=True)["accepted"]
        elif source == "erank-live":
            complete = len(rows) >= limit
        result = {
            "source": source,
            "timeframe": timeframe,
            "count": len(rows),
            "top_categories": categories.most_common(20),
            "rows": rows,
            "result_status": "VERIFIED_COMPLETE" if complete else "PARTIAL",
            "limitations": [] if complete else ["Requested coverage is not proven complete."],
        }
        if output_dir:
            result["output"] = write_json(Path(output_dir) / f"erank-sales-report-{date.today().isoformat()}.json", result)
        _emit(ctx, result)

    @selection_group.command("furniture-report")
    @click.option("--input", "input_path", required=True, type=click.Path(exists=True, dir_okay=False))
    @click.option("--tracked-input", type=click.Path(exists=True, dir_okay=False))
    @click.option("--output-dir", type=click.Path(file_okay=False))
    @click.pass_context
    def selection_furniture_report(ctx: click.Context, input_path: str, tracked_input: str | None, output_dir: str | None) -> None:
        """Filter high-sales furniture shops and attach tracked-shop evidence."""
        rows = parse_erank_or_export(input_path)
        terms = {"furniture", "table", "desk", "nightstand", "cabinet", "shelf", "chair", "bed", "storage", "stand"}
        furniture = [row for row in rows if any(term in " ".join(str(value).lower() for value in row.values()) for term in terms)]
        tracked = load_rows(tracked_input) if tracked_input else []
        tracked_names = {str(row.get("shop") or row.get("shop_name") or "").lower() for row in tracked}
        for row in furniture:
            row["tracked"] = str(row.get("shop") or "").lower() in tracked_names
        result = {"source": "erank-export", "input_count": len(rows), "furniture_count": len(furniture), "rows": furniture, "tracked_count": sum(row["tracked"] for row in furniture)}
        if output_dir:
            result["output"] = write_json(Path(output_dir) / f"erank-furniture-report-{date.today().isoformat()}.json", result)
        _emit(ctx, result)

    cli.add_command(selection_group)
