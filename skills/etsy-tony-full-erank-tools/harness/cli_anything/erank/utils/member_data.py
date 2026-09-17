from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlencode


SENSITIVE_KEY_PARTS = {
    "authorization",
    "cookie",
    "csrf",
    "localstorage",
    "password",
    "sessionstorage",
    "token",
}


def _normalized_key(value: Any) -> str:
    return "".join(character for character in str(value).lower() if character.isalnum())


def reject_sensitive_fields(value: Any, path: str = "payload") -> None:
    """Reject browser credentials accidentally included in a saved member response."""
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = _normalized_key(key)
            if any(part in normalized for part in SENSITIVE_KEY_PARTS):
                raise ValueError(f"Sensitive credential field is not allowed: {path}.{key}")
            reject_sensitive_fields(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_sensitive_fields(child, f"{path}[{index}]")


def extract_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [dict(row) for row in payload if isinstance(row, dict)]
    if not isinstance(payload, dict):
        raise ValueError("Member input must be a JSON object or array.")
    for key in ("rows", "data", "results", "shops", "listings", "items"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [dict(row) for row in rows if isinstance(row, dict)]
    raise ValueError("Member input contains no rows/data/results/shops/listings/items array.")


def load_member_payload(path: str | Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8-sig"))
    reject_sensitive_fields(payload)
    rows = extract_rows(payload)
    envelope = payload if isinstance(payload, dict) else {"data": payload}
    return envelope, rows


def _page_metadata(payload: dict[str, Any], fallback_page: int) -> dict[str, Any]:
    meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    page = int(meta.get("current_page") or meta.get("page") or payload.get("page") or fallback_page)
    last_page = int(meta.get("last_page") or payload.get("last_page") or 0)
    total = int(meta.get("total") or payload.get("total") or 0)
    per_page = int(meta.get("per_page") or meta.get("perPage") or payload.get("per_page") or 0)
    return {"page": page, "last_page": last_page, "total": total, "per_page": per_page}


def _row_identity(row: dict[str, Any], index: int) -> str:
    for key in ("listing_id", "shop_id", "id"):
        value = row.get(key)
        if value not in (None, "", 0, "0"):
            return f"{key}:{value}"
    shop = row.get("shop_name") or row.get("shop") or row.get("name")
    if shop:
        return f"shop:{str(shop).strip().lower()}"
    return f"row:{index}:{json.dumps(row, sort_keys=True, default=str)}"


def merge_member_pages(paths: Iterable[str | Path], expected_total: int | None = None) -> dict[str, Any]:
    sources = [Path(path) for path in paths]
    if not sources:
        raise ValueError("At least one member JSON page is required.")
    if expected_total is not None and expected_total < 0:
        raise ValueError("Expected total must be non-negative.")

    pages: list[dict[str, Any]] = []
    merged: list[dict[str, Any]] = []
    identities: set[str] = set()
    duplicate_count = 0
    endpoints: set[str] = set()
    timeframes: set[str] = set()
    fetched_values: list[str] = []

    for fallback_page, source in enumerate(sources, 1):
        payload, rows = load_member_payload(source)
        metadata = _page_metadata(payload, fallback_page)
        endpoint = str(payload.get("endpoint") or "").strip()
        timeframe = str(payload.get("timeframe") or payload.get("period") or "").strip()
        fetched_at = str(payload.get("fetched_at") or "").strip()
        if endpoint:
            endpoints.add(endpoint)
        if timeframe:
            timeframes.add(timeframe)
        if fetched_at:
            fetched_values.append(fetched_at)
        pages.append({"path": str(source.resolve()), "row_count": len(rows), **metadata})
        for row in rows:
            identity = _row_identity(row, len(merged))
            if identity in identities:
                duplicate_count += 1
                continue
            identities.add(identity)
            merged.append(row)

    if len(endpoints) > 1:
        raise ValueError("Member pages use different endpoints and cannot be merged.")
    if len(timeframes) > 1:
        raise ValueError("Member pages use different timeframes and cannot be merged.")

    present_pages = sorted({page["page"] for page in pages})
    last_page = max((page["last_page"] for page in pages), default=0)
    reported_total = max((page["total"] for page in pages), default=0)
    target_total = expected_total if expected_total is not None else (reported_total or None)
    missing_pages = [page for page in range(1, last_page + 1) if page not in present_pages] if last_page else []

    if last_page:
        complete = not missing_pages and present_pages and present_pages[0] == 1
    elif target_total is not None:
        complete = len(merged) >= target_total
    else:
        complete = False
    if target_total is not None and len(merged) < target_total:
        complete = False

    coverage = "complete" if complete else "partial" if last_page or target_total is not None else "unknown"
    return {
        "schema_version": 1,
        "source": "erank-member-browser-api",
        "endpoint": next(iter(endpoints), ""),
        "timeframe": next(iter(timeframes), ""),
        "fetched_at": min(fetched_values) if fetched_values else None,
        "coverage": coverage,
        "result_status": "VERIFIED_COMPLETE" if complete else "PARTIAL" if coverage == "partial" else "UNVERIFIED",
        "rows": merged,
        "meta": {
            "row_count": len(merged),
            "duplicate_count": duplicate_count,
            "reported_total": reported_total or None,
            "expected_total": expected_total,
            "pages_present": present_pages,
            "last_page": last_page or None,
            "missing_pages": missing_pages,
            "resume_required": bool(missing_pages),
        },
        "inputs": pages,
        "security_boundary": "Saved response data only; cookies, tokens, browser storage, and passwords are rejected.",
    }


def member_request_plan(
    *,
    timeframe: str = "all-time",
    page_count: int = 1,
    per_page: int = 100,
    missing_pages: Iterable[int] = (),
) -> dict[str, Any]:
    if timeframe not in {"all-time", "yesterday"}:
        raise ValueError("Member timeframe must be all-time or yesterday.")
    if page_count < 1:
        raise ValueError("Page count must be at least one.")
    if per_page < 1 or per_page > 100:
        raise ValueError("Per-page value must be between 1 and 100.")
    requested = sorted({int(page) for page in missing_pages if int(page) > 0}) or list(range(1, page_count + 1))
    paths: list[dict[str, Any]] = []
    for page in requested:
        if timeframe == "yesterday":
            endpoint = "/api/top-sellers/most-sales-yesterday"
            query = {"page": page, "perPage": per_page}
        else:
            endpoint = "/api/top-sellers"
            query = {
                "yearStarted": "all_time",
                "category": "",
                "country": "",
                "page": page,
                "perPage": per_page,
                "sort_by": "sales",
                "sort_order": "desc",
                "onlyActiveShops": "false",
            }
        paths.append({"page": page, "path": f"{endpoint}?{urlencode(query)}"})
    return {
        "origin": "https://members.erank.com",
        "timeframe": timeframe,
        "per_page": per_page,
        "request_count": len(paths),
        "requests": paths,
        "browser_method": "Run read-only same-origin GET requests inside the logged-in member page with credentials: include.",
        "save_only": ["response data", "meta", "endpoint", "timeframe", "fetched_at"],
        "never_save": ["cookies", "tokens", "localStorage", "sessionStorage", "passwords", "CSRF values"],
        "quota_rule": "Stop at the rows and pages returned by the member plan; do not bypass plan limits.",
    }


def _parse_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    try:
        parsed = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _source_kind(source: Any) -> str:
    if isinstance(source, dict):
        source = source.get("kind") or source.get("name") or source.get("source")
    text = str(source or "").lower()
    if "member" in text:
        return "member_session"
    if "erank-live" in text or "undocumented" in text:
        return "undocumented_live"
    if "etsy" in text:
        return "etsy_api"
    if "alura" in text or "public" in text:
        return "third_party_public"
    if "export" in text:
        return "member_export"
    return "local_or_unknown"


def _read_evidence_payload(path: str | Path) -> tuple[Any, int]:
    source = Path(path)
    if source.suffix.lower() == ".json":
        payload = json.loads(source.read_text(encoding="utf-8-sig"))
        reject_sensitive_fields(payload)
        try:
            row_count = len(extract_rows(payload))
        except ValueError:
            row_count = 1 if isinstance(payload, dict) else 0
        return payload, row_count
    if source.suffix.lower() == ".csv":
        with source.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        return {"source": "erank-export", "rows": rows}, len(rows)
    return {"source": "erank-export"}, 0


def evidence_report(path: str | Path, max_age_hours: float = 24, require_complete: bool = False) -> dict[str, Any]:
    if max_age_hours <= 0:
        raise ValueError("Maximum evidence age must be greater than zero.")
    source = Path(path)
    payload, row_count = _read_evidence_payload(source)
    envelope = payload if isinstance(payload, dict) else {"rows": payload}
    source_value = envelope.get("source")
    fetched_at = envelope.get("fetched_at")
    if not fetched_at and isinstance(source_value, dict):
        fetched_at = source_value.get("fetched_at")
    timestamp_basis = "snapshot_metadata"
    captured = _parse_datetime(fetched_at)
    if captured is None:
        captured = datetime.fromtimestamp(source.stat().st_mtime, timezone.utc)
        timestamp_basis = "file_mtime"
    age_hours = round((datetime.now(timezone.utc) - captured).total_seconds() / 3600, 2)
    freshness = "clock_skew" if age_hours < -0.1 else "fresh" if age_hours <= max_age_hours else "stale"

    coverage = str(envelope.get("coverage") or (envelope.get("evidence") or {}).get("coverage") or "unknown")
    meta = envelope.get("meta") if isinstance(envelope.get("meta"), dict) else {}
    total = meta.get("reported_total") or meta.get("total")
    complete = coverage.lower() in {"complete", "full", "member_plan_limit", "requested_rows"}
    if total not in (None, "", 0, "0"):
        complete = row_count >= int(total)
    estimated = _source_kind(source_value) in {"member_session", "member_export", "undocumented_live"}
    issues: list[str] = []
    if freshness != "fresh":
        issues.append("Evidence is not fresh.")
    if timestamp_basis == "file_mtime":
        issues.append("File modification time is not proof of marketplace capture time.")
    if require_complete and not complete:
        issues.append("Complete coverage is required but not proven.")
    if row_count == 0:
        issues.append("No data rows were found.")
    accepted = freshness == "fresh" and row_count > 0 and (complete or not require_complete)
    return {
        "path": str(source.resolve()),
        "source_kind": _source_kind(source_value),
        "row_count": row_count,
        "fetched_at": captured.isoformat(),
        "timestamp_basis": timestamp_basis,
        "age_hours": age_hours,
        "freshness": freshness,
        "coverage": coverage,
        "complete": complete,
        "estimated_metrics": estimated,
        "accepted": accepted,
        "result_status": "VERIFIED_ACCEPTED" if accepted else "REJECTED",
        "issues": issues,
    }
