from __future__ import annotations

import csv
from datetime import date, datetime, timezone
import json
from pathlib import Path
import re
from typing import Any

from cli_anything.erank.utils.live_sources import normalize_key, parse_html_tables


def _values(row: dict[str, Any]) -> dict[str, Any]:
    return {normalize_key(str(key)): value for key, value in row.items()}


def _pick(row: dict[str, Any], *names: str) -> Any:
    values = _values(row)
    for name in names:
        value = values.get(normalize_key(name))
        if value not in (None, ""):
            return value
    return None


def _int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    text = re.sub(r"[^0-9.-]", "", str(value))
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def _datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    text = str(value).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def completed_months(opened: date, as_of: date) -> int:
    months = (as_of.year - opened.year) * 12 + as_of.month - opened.month
    if as_of.day < opened.day:
        months -= 1
    return max(months, 0)


def load_shop_rows(path: str | Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source = Path(path)
    suffix = source.suffix.lower()
    metadata: dict[str, Any] = {}
    if suffix == ".csv":
        with source.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = [dict(row) for row in csv.DictReader(handle)]
    elif suffix in {".html", ".htm"}:
        rows, links = parse_html_tables(source.read_text(encoding="utf-8", errors="ignore"))
        for row in rows:
            shop = str(_pick(row, "shop", "shop name", "seller") or "")
            if shop and not _pick(row, "url", "shop url"):
                row["url"] = links.get(shop, "")
    elif suffix == ".json":
        payload = json.loads(source.read_text(encoding="utf-8-sig"))
        if isinstance(payload, list):
            rows = payload
        elif isinstance(payload, dict):
            rows = payload.get("rows") or payload.get("data") or payload.get("shops") or payload.get("results") or []
            source_info = payload.get("source")
            metadata = {
                "fetched_at": payload.get("fetched_at") or (source_info or {}).get("fetched_at") if isinstance(source_info, dict) else payload.get("fetched_at"),
                "source": source_info.get("kind") if isinstance(source_info, dict) else source_info,
                "period": payload.get("timeframe") or payload.get("period"),
            }
        else:
            raise ValueError("JSON input must be a list or an object containing rows/data/shops/results.")
    else:
        raise ValueError(f"Unsupported shop-search input type: {source.suffix}")
    if not isinstance(rows, list):
        raise ValueError("Shop-search rows must be a list.")
    row_times = [_datetime(_pick(row, "fetched at", "fetched_at", "captured at", "captured_at")) for row in rows if isinstance(row, dict)]
    valid_row_times = [value for value in row_times if value is not None]
    if not metadata.get("fetched_at") and valid_row_times:
        metadata["fetched_at"] = min(valid_row_times).isoformat()
    metadata["path"] = str(source.resolve())
    metadata["file_modified_at"] = datetime.fromtimestamp(source.stat().st_mtime, timezone.utc).isoformat()
    return [row for row in rows if isinstance(row, dict)], metadata


def normalize_shop(row: dict[str, Any], as_of: date, default_period: str | None = None) -> dict[str, Any]:
    shop = str(_pick(row, "shop", "shop name", "shop_name", "seller", "store") or "").strip()
    period = str(_pick(row, "period", "timeframe") or default_period or "").strip().lower()

    total_sales = _int(_pick(row, "total sales", "total_sales", "lifetime sales", "lifetime_sales", "sales total"))
    sales_scope = "total"
    if total_sales is None:
        sales = _int(_pick(row, "sales"))
        if sales is not None and period in {"all-time", "all_time", "lifetime"}:
            total_sales = sales
        else:
            sales_scope = period or "unknown"

    explicit_age = _int(_pick(row, "age months", "age_months", "shop age months"))
    opened_raw = _pick(
        row,
        "opened at",
        "opened_at",
        "created at",
        "created_at",
        "shop created at",
        "shop_created_at",
        "on etsy since",
        "on_etsy_since",
        "opened",
        "year started",
        "year_started",
    )
    opened_at = _datetime(opened_raw)
    age_months: int | None = explicit_age
    age_precision = "explicit_months" if explicit_age is not None else "missing"
    if age_months is None and opened_at is not None:
        age_months = completed_months(opened_at.date(), as_of)
        age_precision = "exact_date"
    elif age_months is None and opened_raw not in (None, ""):
        text = str(opened_raw).strip().lower()
        match = re.search(r"(\d+)\s*(?:months?|mos?|月)", text)
        if match:
            age_months = int(match.group(1))
            age_precision = "explicit_months"
        elif re.fullmatch(r"\d{4}-\d{1,2}", text):
            age_precision = "month_only"
        elif re.fullmatch(r"\d{4}", text):
            age_precision = "year_only"
        else:
            age_precision = "unparsed"

    return {
        "shop": shop,
        "total_sales": total_sales,
        "sales_scope": sales_scope,
        "opened_at": opened_at.isoformat() if opened_at else str(opened_raw or ""),
        "age_months": age_months,
        "age_precision": age_precision,
        "country": str(_pick(row, "country") or "").strip(),
        "category": str(_pick(row, "category", "primary category", "what sold") or "").strip(),
        "url": str(_pick(row, "url", "shop url", "link") or (f"https://www.etsy.com/shop/{shop}" if shop else "")),
        "fetched_at": str(_pick(row, "fetched at", "fetched_at", "captured at", "captured_at") or ""),
    }


def find_shops(
    rows: list[dict[str, Any]],
    *,
    sales_min: int,
    sales_max: int,
    age_months: int,
    age_tolerance: int,
    as_of: date,
    default_period: str | None = None,
) -> dict[str, Any]:
    if sales_min < 0 or sales_max < 0 or sales_min > sales_max:
        raise ValueError("Sales range must be non-negative and --sales-min cannot exceed --sales-max.")
    if age_months < 0 or age_tolerance < 0:
        raise ValueError("Age months and tolerance must be non-negative.")

    normalized = [normalize_shop(row, as_of, default_period) for row in rows]
    normalized = [row for row in normalized if row["shop"]]
    matches: list[dict[str, Any]] = []
    needs_verification: list[dict[str, Any]] = []
    reasons: dict[str, int] = {}
    age_low, age_high = age_months - age_tolerance, age_months + age_tolerance

    for row in normalized:
        sales = row["total_sales"]
        sales_match = sales is not None and sales_min <= sales <= sales_max and row["sales_scope"] == "total"
        age_exact = row["age_precision"] in {"exact_date", "explicit_months"}
        age_match = row["age_months"] is not None and age_low <= row["age_months"] <= age_high
        if sales_match and age_exact and age_match:
            matches.append(row)
            continue
        if sales_match and not age_exact:
            candidate = dict(row)
            candidate["verification_reason"] = "Exact shop age is unavailable; year/month-only data is insufficient."
            needs_verification.append(candidate)
            reasons["age_not_exact"] = reasons.get("age_not_exact", 0) + 1
        elif sales is None or row["sales_scope"] != "total":
            reasons["total_sales_unavailable"] = reasons.get("total_sales_unavailable", 0) + 1
        elif not sales_match:
            reasons["sales_out_of_range"] = reasons.get("sales_out_of_range", 0) + 1
        elif not age_match:
            reasons["age_out_of_range"] = reasons.get("age_out_of_range", 0) + 1

    matches.sort(key=lambda row: (row["total_sales"], row["shop"].lower()))
    needs_verification.sort(key=lambda row: (row["total_sales"], row["shop"].lower()))
    return {
        "criteria": {
            "sales_min": sales_min,
            "sales_max": sales_max,
            "sales_scope": "shop lifetime total",
            "age_months": age_months,
            "age_tolerance": age_tolerance,
            "as_of": as_of.isoformat(),
        },
        "rows_checked": len(normalized),
        "match_count": len(matches),
        "matches": matches,
        "needs_verification_count": len(needs_verification),
        "needs_verification": needs_verification,
        "excluded_summary": reasons,
    }


def add_freshness(result: dict[str, Any], metadata: dict[str, Any], max_age_hours: float) -> None:
    fetched_at = _datetime(metadata.get("fetched_at"))
    basis = "snapshot_metadata"
    if fetched_at is None:
        fetched_at = _datetime(metadata.get("file_modified_at"))
        basis = "file_mtime"
    now = datetime.now(timezone.utc)
    age_hours = round((now - fetched_at).total_seconds() / 3600, 2) if fetched_at else None
    freshness = "unknown"
    if age_hours is not None:
        freshness = "clock_skew" if age_hours < -0.1 else ("fresh" if age_hours <= max_age_hours else "stale")
    result["evidence"] = {
        "input_path": metadata.get("path"),
        "source": metadata.get("source") or "erank-export",
        "fetched_at": fetched_at.isoformat() if fetched_at else None,
        "timestamp_basis": basis,
        "age_hours": age_hours,
        "max_age_hours": max_age_hours,
        "freshness": freshness,
        "coverage": metadata.get("coverage") or "input_rows_only",
    }
    result["result_status"] = (
        "STALE_MATCHES" if result["match_count"] and freshness != "fresh"
        else "VERIFIED_MATCHES" if result["match_count"]
        else "NEEDS_VERIFICATION" if result["needs_verification_count"]
        else "NO_MATCHES"
    )
    result["limitations"] = [
        "Matches are strict only when lifetime sales and exact-date/explicit-month shop age are both present.",
        "File modification time is not proof of when the marketplace snapshot was captured." if basis == "file_mtime" else "Snapshot time comes from input metadata.",
    ]
