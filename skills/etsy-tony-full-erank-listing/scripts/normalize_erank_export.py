#!/usr/bin/env python3
"""Normalize eRank member CSV, JSON, or HTML keyword exports."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable


MEMBER_SOURCES = {
    "erank-member",
    "erank-member-export",
    "erank-member-browser",
    "erank-member-browser-api",
}


class EvidenceError(RuntimeError):
    """Raised when an export cannot be represented safely."""


def normalized_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).strip().casefold()).strip()


ALIASES = {
    "phrase": {"keyword", "term", "phrase", "tag", "query", "keyword phrase"},
    "average_searches": {
        "average searches",
        "avg searches",
        "avg search",
        "avg_searches",
        "search volume",
        "search_volume",
        "average monthly searches",
        "searches",
    },
    "average_clicks": {
        "average clicks",
        "avg clicks",
        "avg click",
        "avg_clicks",
        "average monthly clicks",
        "clicks",
    },
    "ctr": {
        "average ctr",
        "avg ctr",
        "avg_ctr",
        "ctr",
        "click through rate",
        "click-through rate",
    },
    "competition": {
        "etsy competition",
        "competition",
        "competing listings",
        "competing_listings",
        "results",
    },
    "trend": {"trend", "trend score", "trend_score", "growth", "change"},
    "intent": {"intent", "buyer intent", "intent class"},
    "search_stage": {"search stage", "search_stage", "stage"},
    "product_relevance": {"product relevance", "product_relevance", "relevance"},
    "fact_supported": {"fact supported", "fact_supported", "supported"},
}


def pick(row: dict[str, Any], field: str) -> Any:
    index = {normalized_key(key): value for key, value in row.items()}
    for alias in ALIASES[field]:
        key = normalized_key(alias)
        if key in index and index[key] not in (None, ""):
            return index[key]
    return None


def parse_number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        return number if math.isfinite(number) else None
    text = str(value).strip().casefold()
    if not text or text in {"n/a", "na", "none", "null", "-", "--"}:
        return None
    multiplier = 1.0
    if text.endswith("k"):
        multiplier, text = 1_000.0, text[:-1]
    elif text.endswith("m"):
        multiplier, text = 1_000_000.0, text[:-1]
    text = text.replace(",", "").replace("%", "").strip()
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return None
    number = float(match.group(0)) * multiplier
    return number if math.isfinite(number) else None


def parse_boolean(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None or value == "":
        return None
    text = str(value).strip().casefold()
    if text in {"true", "yes", "y", "1", "supported"}:
        return True
    if text in {"false", "no", "n", "0", "unsupported"}:
        return False
    return None


class FirstTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_table = False
        self.finished = False
        self.in_cell = False
        self.cell_parts: list[str] = []
        self.current_row: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table" and not self.in_table and not self.finished:
            self.in_table = True
        elif self.in_table and tag == "tr":
            self.current_row = []
        elif self.in_table and tag in {"th", "td"}:
            self.in_cell = True
            self.cell_parts = []

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self.in_table and tag in {"th", "td"} and self.in_cell:
            self.current_row.append(" ".join("".join(self.cell_parts).split()))
            self.in_cell = False
        elif self.in_table and tag == "tr" and self.current_row:
            self.rows.append(self.current_row)
        elif self.in_table and tag == "table":
            self.in_table = False
            self.finished = True


def rows_from_html(text: str) -> list[dict[str, Any]]:
    parser = FirstTableParser()
    parser.feed(text)
    if len(parser.rows) < 2:
        raise EvidenceError("No usable HTML table was found in the eRank export.")
    headers = parser.rows[0]
    return [dict(zip(headers, row)) for row in parser.rows[1:] if any(cell.strip() for cell in row)]


def find_json_rows(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list) and all(isinstance(item, dict) for item in value):
        return list(value)
    if isinstance(value, dict):
        for key in ("keywords", "keyword_ideas", "keywordIdeas", "data", "results", "rows", "items"):
            if key in value:
                found = find_json_rows(value[key])
                if found:
                    return found
        if any(normalized_key(key) in ALIASES["phrase"] for key in value):
            return [value]
    return []


def load_rows(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.casefold()
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    if suffix == ".json":
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise EvidenceError(f"Invalid JSON export: {exc}") from exc
        rows = find_json_rows(parsed)
    elif suffix in {".html", ".htm"}:
        rows = rows_from_html(text)
    else:
        rows = list(csv.DictReader(text.splitlines()))
    if not rows:
        raise EvidenceError("The export contained no keyword rows.")
    return rows


def validate_timestamp(value: str) -> str:
    clean = value.strip()
    if clean.endswith("Z"):
        candidate = clean[:-1] + "+00:00"
    else:
        candidate = clean
    try:
        datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise EvidenceError("fetched_at must be an ISO-8601 timestamp.") from exc
    return clean


def normalize_rows(
    rows: Iterable[dict[str, Any]],
    *,
    source: str,
    market: str,
    fetched_at: str,
    input_file: str = "",
) -> dict[str, Any]:
    fetched_at = validate_timestamp(fetched_at)
    source = source.strip()
    authoritative = source in MEMBER_SOURCES
    normalized: list[dict[str, Any]] = []
    skipped = 0
    seen: set[str] = set()
    for row in rows:
        phrase_value = pick(row, "phrase")
        phrase = " ".join(str(phrase_value or "").split()).strip()
        key = phrase.casefold()
        if not phrase or key in seen:
            skipped += 1
            continue
        seen.add(key)
        relevance = str(pick(row, "product_relevance") or "unknown").strip().casefold()
        if relevance not in {"high", "medium", "low", "unknown"}:
            relevance = "unknown"
        normalized.append(
            {
                "phrase": phrase,
                "average_searches": parse_number(pick(row, "average_searches")),
                "average_clicks": parse_number(pick(row, "average_clicks")),
                "ctr": parse_number(pick(row, "ctr")),
                "competition": parse_number(pick(row, "competition")),
                "trend": parse_number(pick(row, "trend")),
                "intent": str(pick(row, "intent") or "unknown").strip(),
                "search_stage": str(pick(row, "search_stage") or "unknown").strip(),
                "product_relevance": relevance,
                "fact_supported": parse_boolean(pick(row, "fact_supported")),
                "evidence_status": "ERANK_MEMBER_VERIFIED" if authoritative else "UNVERIFIED",
                "raw": dict(row),
            }
        )
    if not normalized:
        raise EvidenceError("No rows contained a recognizable keyword phrase.")
    metrics = ("average_searches", "average_clicks", "ctr", "competition")
    coverage = {
        field: round(sum(item[field] is not None for item in normalized) / len(normalized), 4)
        for field in metrics
    }
    return {
        "source": {
            "kind": source,
            "market": market,
            "fetched_at": fetched_at,
            "authoritative_member_data": authoritative,
            "input_file": input_file,
        },
        "keywords": normalized,
        "integrity": {
            "row_count": len(normalized),
            "skipped_rows": skipped,
            "metric_coverage": coverage,
            "limitations": []
            if authoritative
            else ["This source is not authenticated eRank member keyword evidence."],
        },
    }


def write_json(data: dict[str, Any], output: Path | None) -> None:
    rendered = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="eRank member CSV, JSON, or HTML export.")
    parser.add_argument("--source", required=True, help="Provenance label, normally erank-member-export.")
    parser.add_argument("--market", default="US", help="Target market/country, default US.")
    parser.add_argument("--fetched-at", required=True, help="ISO-8601 collection timestamp.")
    parser.add_argument("--output", type=Path, help="Write normalized JSON here; defaults to stdout.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        rows = load_rows(args.input)
        package = normalize_rows(
            rows,
            source=args.source,
            market=args.market,
            fetched_at=args.fetched_at,
            input_file=args.input.name,
        )
        write_json(package, args.output)
        return 0
    except (EvidenceError, OSError) as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
