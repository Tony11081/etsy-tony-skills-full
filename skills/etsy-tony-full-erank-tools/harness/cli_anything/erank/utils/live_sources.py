from __future__ import annotations

import csv
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import re
import time
from typing import Any
from urllib.parse import quote

import requests

from cli_anything.erank.core.models import Listing
from cli_anything.erank.utils.member_data import load_member_payload


ALURA_TOP_SELLERS_URL = "https://www.alura.io/best-selling-etsy-shops"
ERANK_TOP_SELLERS_URL = "https://members.erank.com/top-sellers"
ERANK_TREND_BUZZ_URL = "https://members.erank.com/trend-buzz"
ERANK_API_BASE_URL = "https://members.erank.com/api"


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def parse_int(value: Any) -> int:
    if value is None:
        return 0
    text = re.sub(r"[^0-9.-]", "", str(value))
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def parse_money(value: Any) -> float:
    if value is None:
        return 0.0
    text = re.sub(r"[^0-9.-]", "", str(value))
    if not text:
        return 0.0
    try:
        return round(float(text), 2)
    except ValueError:
        return 0.0


def pick(row: dict[str, Any], *names: str) -> str:
    lowered = {normalize_key(key): value for key, value in row.items()}
    for name in names:
        key = normalize_key(name)
        value = lowered.get(key)
        if value not in (None, ""):
            return str(value).strip()
    return ""


def normalize_top_seller_row(row: dict[str, Any], source: str) -> dict[str, Any]:
    return {
        "rank": parse_int(pick(row, "rank", "#", "position")),
        "shop": pick(row, "shop", "shop name", "shop_name", "seller", "store", "name"),
        "total_sales": parse_int(pick(row, "sales", "total sales", "total_sales", "lifetime sales", "lifetime_sales")),
        "monthly_sales": parse_int(pick(row, "monthly sales", "30 day sales", "past month sales")),
        "revenue": parse_money(pick(row, "revenue", "estimated revenue", "lifetime revenue")),
        "currency": pick(row, "currency") or infer_currency(row),
        "listings": parse_int(pick(row, "listings", "active listings")),
        "category": pick(row, "category", "primary category"),
        "on_etsy_since": pick(row, "on etsy since", "opened", "year opened", "year_started", "created_at"),
        "url": pick(row, "url", "shop url", "link"),
        "source": source,
    }


def normalize_erank_api_top_seller_row(row: dict[str, Any], source: str, period: str) -> dict[str, Any]:
    sales = parse_int(row.get("sales"))
    return {
        "rank": parse_int(row.get("rank")),
        "shop": str(row.get("shop_name") or row.get("shop") or "").strip(),
        "shop_id": parse_int(row.get("shop_id")),
        "sales": sales,
        "period": period,
        "what_sold": str(row.get("category") or "").strip(),
        "category": str(row.get("category") or "").strip(),
        "country": str(row.get("country") or "").strip(),
        "global_rank": parse_int(row.get("global_rank")),
        "national_rank": parse_int(row.get("national_rank")),
        "year_started": str(row.get("year_started") or "").split("-")[0],
        "url": f"https://www.etsy.com/shop/{row.get('shop_name')}" if row.get("shop_name") else "",
        "source": source,
    }


def infer_currency(row: dict[str, Any]) -> str:
    text = " ".join(str(value) for value in row.values())
    for currency in ("USD", "GBP", "EUR", "CAD", "AUD"):
        if currency in text:
            return currency
    return ""


def read_csv_rows(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


class TableHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self._table: list[list[str]] | None = None
        self._row: list[str] | None = None
        self._cell: list[str] | None = None
        self._capture = False
        self.links: dict[str, str] = {}
        self._href: str | None = None
        self._link_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "table":
            self._table = []
        elif tag == "tr" and self._table is not None:
            self._row = []
        elif tag in {"td", "th"} and self._row is not None:
            self._cell = []
            self._capture = True
        elif tag == "a":
            self._href = attrs_dict.get("href")
            self._link_text = []

    def handle_data(self, data: str) -> None:
        if self._capture and self._cell is not None:
            self._cell.append(data)
        if self._href:
            self._link_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self._cell is not None and self._row is not None:
            value = re.sub(r"\s+", " ", " ".join(self._cell)).strip()
            self._row.append(value)
            self._cell = None
            self._capture = False
        elif tag == "tr" and self._row is not None and self._table is not None:
            if any(cell for cell in self._row):
                self._table.append(self._row)
            self._row = None
        elif tag == "table" and self._table is not None:
            if self._table:
                self.tables.append(self._table)
            self._table = None
        elif tag == "a" and self._href:
            text = re.sub(r"\s+", " ", " ".join(self._link_text)).strip()
            if text:
                self.links[text] = self._href
            self._href = None
            self._link_text = []


def parse_html_tables(html: str) -> tuple[list[dict[str, str]], dict[str, str]]:
    parser = TableHTMLParser()
    parser.feed(html)
    rows: list[dict[str, str]] = []
    for table in parser.tables:
        if not table:
            continue
        headers = [normalize_key(cell) for cell in table[0]]
        if not headers or not any(headers):
            continue
        for raw_row in table[1:]:
            row = {}
            for index, header in enumerate(headers):
                if header:
                    row[header] = raw_row[index] if index < len(raw_row) else ""
            if row:
                rows.append(row)
    return rows, parser.links


def parse_erank_or_export(path: str | Path, source: str = "erank-export") -> list[dict[str, Any]]:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        rows = read_csv_rows(file_path)
    elif suffix in {".html", ".htm"}:
        rows, links = parse_html_tables(file_path.read_text(encoding="utf-8", errors="ignore"))
        for row in rows:
            shop = pick(row, "shop", "shop name", "seller")
            if shop and not pick(row, "url"):
                row["url"] = links.get(shop, "")
    elif suffix == ".json":
        _, rows = load_member_payload(file_path)
    else:
        raise ValueError(f"Unsupported export type: {file_path.suffix}")
    normalized = [normalize_top_seller_row(row, source) for row in rows]
    return [row for row in normalized if row["shop"]]


def _erank_json_get(url: str, *, params: dict[str, Any] | None = None, timeout: int = 30, http: Any = requests) -> dict[str, Any]:
    headers = {
        "User-Agent": "Mozilla/5.0 cli-anything-erank/0.3",
        "Accept": "application/json, text/plain, */*",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://members.erank.com/shop-info",
    }
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            response = http.get(url, params=params, headers=headers, timeout=timeout)
            if response.status_code in {429, 500, 502, 503, 504} and attempt == 0:
                last_error = requests.HTTPError(f"HTTP {response.status_code}")
                time.sleep(0.5)
                continue
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise RuntimeError("eRank endpoint returned a non-object JSON payload.")
            return payload
        except requests.RequestException as exc:
            last_error = exc
            if attempt == 0 and not getattr(exc, "response", None):
                time.sleep(0.5)
                continue
            break
        except ValueError as exc:
            raise RuntimeError(f"eRank endpoint returned invalid JSON: {exc}") from exc
    raise RuntimeError(f"Failed to fetch eRank shop data: {last_error}")


def fetch_erank_shop_info(shop: str, timeout: int = 30, http: Any = requests) -> dict[str, Any]:
    name = shop.strip()
    if not name:
        raise ValueError("Shop name is required.")
    encoded = quote(name, safe="")
    base = f"{ERANK_API_BASE_URL}/shop-info/{encoded}"
    overview = _erank_json_get(base, timeout=timeout, http=http)
    profile = _erank_json_get(f"{base}/badge", timeout=timeout, http=http)
    return {
        "schema_version": 1,
        "shop": name,
        "source": "erank-undocumented-read-only-api",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "overview": overview,
        "profile": profile,
        "coverage": "shop_overview_and_badge",
        "estimated_metrics": True,
        "limitations": [
            "This is an undocumented read-only web endpoint and its schema may change.",
            "eRank sales and ranking values are research signals, not Etsy backend order records.",
        ],
    }


def _normalize_erank_listing(row: dict[str, Any], shop: str) -> dict[str, Any]:
    listing = Listing.from_mapping({**row, "shop": shop})
    normalized = listing.to_dict()
    normalized.update(
        {
            "listing_image": pick(row, "listing_image", "image", "image_url", "thumbnail"),
            "estimated_sales": parse_int(pick(row, "estimated sales", "estimated_sales", "sales")),
            "estimated_revenue": parse_money(pick(row, "estimated revenue", "estimated_revenue", "revenue")),
            "source": "erank-undocumented-read-only-api",
        }
    )
    return normalized


def fetch_erank_shop_listings(shop: str, limit: int = 100, timeout: int = 30, http: Any = requests) -> dict[str, Any]:
    if limit < 1 or limit > 500:
        raise ValueError("Listing limit must be between 1 and 500.")
    name = shop.strip()
    if not name:
        raise ValueError("Shop name is required.")
    encoded = quote(name, safe="")
    payload = _erank_json_get(
        f"{ERANK_API_BASE_URL}/shop-info/{encoded}/listings",
        params={"offset": 0},
        timeout=timeout,
        http=http,
    )
    raw_rows = payload.get("recent_listings") if isinstance(payload.get("recent_listings"), list) else []
    rows = [_normalize_erank_listing(row, name) for row in raw_rows if isinstance(row, dict)][:limit]
    return {
        "schema_version": 1,
        "shop": name,
        "source": "erank-undocumented-read-only-api",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "requested_limit": limit,
        "count": len(rows),
        "category": payload.get("category") or "",
        "is_handmade": payload.get("is_handmade"),
        "top_categories": payload.get("top_categories") or [],
        "top_tags": payload.get("top_tags") or [],
        "listings": rows,
        "coverage": "first_endpoint_page_only",
        "limitations": [
            "Only the endpoint page returned without member-session pagination is included.",
            "An empty response means no usable public sample was returned, not that the shop has no listings.",
            "Listing sales and revenue fields are eRank estimates, not Etsy order records.",
        ],
    }


def derive_shop_tags(listing_report: dict[str, Any], limit: int = 100) -> dict[str, Any]:
    if limit < 1:
        raise ValueError("Tag limit must be at least one.")
    counts: dict[str, int] = {}
    for row in listing_report.get("listings") or []:
        for tag in row.get("tags") or []:
            normalized = str(tag).strip().lower()
            if normalized:
                counts[normalized] = counts.get(normalized, 0) + 1
    tags = [
        {"tag": tag, "occurrences": count}
        for tag, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]
    return {
        "schema_version": 1,
        "shop": listing_report.get("shop"),
        "source": f"{listing_report.get('source', 'unknown')}-derived",
        "fetched_at": listing_report.get("fetched_at"),
        "listing_count": listing_report.get("count", 0),
        "unique_tags": len(counts),
        "tags": tags,
        "erank_top_tags": listing_report.get("top_tags") or [],
        "coverage": listing_report.get("coverage"),
        "limitations": [
            "Occurrences are computed only from listings present in the input sample.",
            "Search volume, clicks, CTR, competition, and difficulty are not inferred.",
        ],
    }


def extract_alura_text_rows(html: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    pattern = re.compile(
        r"(?P<rank>\d+)\s+(?P<shop>[A-Za-z0-9][A-Za-z0-9_.-]{1,80})\s+"
        r"(?P<sales>\d{3,})\s+(?P<monthly>\d+)\s+"
        r"(?P<currency>USD|GBP|EUR|CAD|AUD)\s+(?P<revenue>\d+)\s+"
        r"(?P<listings>\d+)\s+(?P<tail>.+?)(?=\s+\d+\s+[A-Za-z0-9][A-Za-z0-9_.-]{1,80}\s+\d{3,}\s+\d+\s+(?:USD|GBP|EUR|CAD|AUD)|$)",
        re.S,
    )
    text = re.sub(r"\s+", " ", html)
    for match in pattern.finditer(text):
        tail = match.group("tail").strip()
        year_match = re.search(r"(19|20)\d{2}", tail)
        category = tail[: year_match.start()].strip() if year_match else tail
        opened = year_match.group(0) if year_match else ""
        rows.append(
            {
                "rank": parse_int(match.group("rank")),
                "shop": match.group("shop"),
                "total_sales": parse_int(match.group("sales")),
                "monthly_sales": parse_int(match.group("monthly")),
                "currency": match.group("currency"),
                "revenue": parse_money(match.group("revenue")),
                "listings": parse_int(match.group("listings")),
                "category": category,
                "on_etsy_since": opened,
                "url": "",
                "source": "alura-public-live",
            }
        )
    return rows


def extract_alura_card_rows(html: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    row_pattern = re.compile(r'<a[^>]+id="bestShopRow"[^>]+href="(?P<href>[^"]+)"[^>]*>(?P<body>.*?)</a>', re.S)
    for match in row_pattern.finditer(html):
        body = match.group("body")
        values = [
            re.sub(r"\s+", " ", value).strip()
            for value in re.findall(r'class="bs-table-text(?:-date)?">([^<]+)</div>', body)
        ]
        if len(values) < 8:
            continue
        href = match.group("href")
        if href.startswith("/"):
            href = f"https://www.alura.io{href}"
        rows.append(
            {
                "rank": parse_int(values[0]),
                "shop": unescape(values[1]),
                "total_sales": parse_int(values[2]),
                "monthly_sales": parse_int(values[3]),
                "currency": values[4],
                "revenue": parse_money(values[5]),
                "listings": parse_int(values[6]),
                "category": unescape(values[7]),
                "on_etsy_since": values[8] if len(values) > 8 else "",
                "url": href,
                "source": "alura-public-live",
            }
        )
    return rows


def fetch_alura_top_sellers(limit: int = 100, timeout: int = 30) -> list[dict[str, Any]]:
    response = requests.get(
        ALURA_TOP_SELLERS_URL,
        timeout=timeout,
        headers={"User-Agent": "Mozilla/5.0 cli-anything-erank/0.1"},
    )
    response.raise_for_status()
    table_rows, links = parse_html_tables(response.text)
    rows = [normalize_top_seller_row(row, "alura-public-live") for row in table_rows]
    if not any(row["shop"] for row in rows):
        rows = extract_alura_card_rows(response.text)
    if not any(row["shop"] for row in rows):
        rows = extract_alura_text_rows(response.text)
    for row in rows:
        if row["shop"] and not row.get("url"):
            row["url"] = links.get(row["shop"], "")
    cleaned = [row for row in rows if row["shop"]]
    cleaned.sort(key=lambda row: row["rank"] or 999999)
    return cleaned[:limit]


def fetch_erank_top_sellers(timeframe: str = "yesterday", limit: int = 100, timeout: int = 30) -> list[dict[str, Any]]:
    headers = {
        "User-Agent": "Mozilla/5.0 cli-anything-erank/0.1",
        "Accept": "application/json, text/plain, */*",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": ERANK_TOP_SELLERS_URL,
    }
    session = requests.Session()

    def get_json(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(1, 3):
            try:
                response = session.get(url, params=params, headers=headers, timeout=timeout)
            except requests.RequestException as exc:
                last_error = exc
                if attempt == 2:
                    break
                time.sleep(0.75 * attempt)
                continue
            if response.status_code in {429, 500, 502, 503, 504} and attempt == 1:
                last_error = requests.HTTPError(f"HTTP {response.status_code}")
                time.sleep(0.75)
                continue
            try:
                response.raise_for_status()
                return response.json()
            except (requests.RequestException, ValueError) as exc:
                raise RuntimeError(f"Failed to fetch eRank live data: {exc}") from exc
        raise RuntimeError(f"Failed to fetch eRank live data after retries: {last_error}")

    rows: list[dict[str, Any]] = []
    if timeframe == "yesterday":
        endpoint = f"{ERANK_API_BASE_URL}/top-sellers/most-sales-yesterday"
        page = 1
        while len(rows) < limit:
            payload = get_json(endpoint, params={"page": page, "perPage": 100})
            data = payload.get("data") or []
            if not data:
                break
            rows.extend(
                normalize_erank_api_top_seller_row(row, "erank-live", "yesterday")
                for row in data
                if row.get("shop_name")
            )
            meta = payload.get("meta") or {}
            if page >= int(meta.get("last_page") or page):
                break
            page += 1
    elif timeframe == "all-time":
        endpoint = f"{ERANK_API_BASE_URL}/top-sellers"
        payload = get_json(
            endpoint,
            params={
                "yearStarted": "all_time",
                "category": "",
                "country": "",
                "page": 1,
                "perPage": limit,
                "sort_by": "sales",
                "sort_order": "desc",
                "onlyActiveShops": "false",
            },
        )
        rows.extend(
            normalize_erank_api_top_seller_row(row, "erank-live", "all-time")
            for row in payload.get("data", [])
            if row.get("shop_name")
        )
    else:
        raise ValueError(f"Unsupported eRank timeframe: {timeframe}")
    rows.sort(key=lambda row: row["rank"] or 999999)
    return rows[:limit]


def probe_erank_live_api(timeout: int = 10, http: Any = requests) -> dict[str, Any]:
    """Check public/sample/member boundaries without using browser credentials."""
    checked_at = datetime.now(timezone.utc).isoformat()
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Referer": ERANK_TOP_SELLERS_URL,
        "User-Agent": "Mozilla/5.0 cli-anything-erank/0.2",
        "X-Requested-With": "XMLHttpRequest",
    }
    targets = {
        "yesterday": (
            f"{ERANK_API_BASE_URL}/top-sellers/most-sales-yesterday",
            {"page": 1, "perPage": 1},
        ),
        "all_time_sample": (
            f"{ERANK_API_BASE_URL}/top-sellers",
            {"yearStarted": "all_time", "page": 1, "perPage": 100, "sort_by": "sales", "sort_order": "desc"},
        ),
        "current_year_filter": (
            f"{ERANK_API_BASE_URL}/top-sellers",
            {"yearStarted": str(datetime.now(timezone.utc).year), "page": 1, "perPage": 100, "sort_by": "sales", "sort_order": "desc"},
        ),
    }
    checks: dict[str, Any] = {}
    for name, (url, params) in targets.items():
        try:
            response = http.get(url, params=params, headers=headers, timeout=timeout)
            count = None
            if response.ok:
                try:
                    count = len(response.json().get("data") or [])
                except (ValueError, AttributeError):
                    pass
            checks[name] = {
                "status_code": response.status_code,
                "available_without_member_session": response.ok,
                "auth_required": response.status_code in {401, 403},
                "sample_count": count,
                "requested_rows": params.get("perPage"),
            }
        except requests.RequestException as exc:
            checks[name] = {
                "status_code": None,
                "available_without_member_session": False,
                "auth_required": None,
                "sample_count": None,
                "error": str(exc),
            }
    accessible = [value["available_without_member_session"] for value in checks.values()]
    sample_limited = any(
        value.get("sample_count") is not None
        and value.get("requested_rows")
        and value["sample_count"] < value["requested_rows"]
        for name, value in checks.items()
        if name in {"all_time_sample", "current_year_filter"}
    )
    access = "blocked" if not any(accessible) else "partial" if not all(accessible) or sample_limited else "full"
    return {
        "checked_at": checked_at,
        "access": access,
        "checks": checks,
        "conclusion": "Member browser or export is required for complete filtered Top Sellers coverage." if access != "full" else "All probed read-only routes were accessible.",
    }


def source_status(etsy_configured: bool, etsy_oauth_configured: bool) -> dict[str, Any]:
    return {
        "etsy_api": {
            "available": etsy_configured,
            "oauth_available": etsy_oauth_configured,
            "use_for": ["live keyword listing search", "shop lookup", "shop active listings"],
            "missing_action": None if etsy_configured else "Run config set etsy_api_key <key>.",
        },
        "erank_member_browser": {
            "available": True,
            "use_for": ["complete member Top Sellers", "Trend Buzz yesterday", "Keyword Tool metrics", "Competitor Sales"],
            "url_examples": [ERANK_TOP_SELLERS_URL, ERANK_TREND_BUZZ_URL],
            "workflow_commands": [
                "live member-plan --timeframe all-time --pages <plan-pages>",
                "live member-ingest --input page-1.json --input page-2.json --output merged.json",
                "live evidence-check --input merged.json --require-complete",
            ],
            "security_boundary": "Use the user's logged-in browser session. Do not copy cookies or bypass Chrome's remote-debugging confirmation.",
        },
        "erank_live_api": {
            "available": None,
            "access": "Undocumented endpoint; current access must be probed and may require a member session.",
            "probe_command": "live source-probe",
            "use_for": ["Top Sellers public samples", "Shop Info overview/profile", "bounded recent competitor-listing sample", "derived tag frequency"],
            "commands": [
                "live top-sellers --source erank-live --timeframe yesterday --limit 100",
                "live top-sellers --source erank-live --timeframe all-time --limit 100",
                "live shop-info ShopName",
                "live shop-listings ShopName --limit 100",
                "live shop-tags ShopName --listing-limit 100",
            ],
        },
        "erank_export": {
            "available": True,
            "use_for": ["CSV/HTML exports downloaded from eRank member tools"],
            "commands": [
                "live top-sellers --source erank-export --input path.csv",
                "live top-sellers --source erank-export --input saved-page.html",
            ],
        },
        "public_live_fallback": {
            "available": True,
            "use_for": ["current public Etsy top-seller snapshot when eRank member browser/export is unavailable"],
            "command": "live top-sellers --source alura-public",
            "limitation": "Not eRank data and not a yesterday-only sales ranking.",
        },
    }
