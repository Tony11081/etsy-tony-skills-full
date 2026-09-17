#!/usr/bin/env python3
"""Rank fact-supported eRank keyword evidence without claiming Etsy rank."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


INTENT_ORDER = (
    "product",
    "objective_trait",
    "style",
    "room_use",
    "problem_solution",
    "personalization",
    "recipient_occasion",
    "regional_synonym",
    "seasonal",
    "unknown",
)
TAG_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9 '\-]*")
MEMBER_SOURCES = {
    "erank-member",
    "erank-member-export",
    "erank-member-browser",
    "erank-member-browser-api",
}


class PortfolioError(RuntimeError):
    """Raised for unusable keyword evidence."""


def phrase_key(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))


def token_set(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.casefold()))


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PortfolioError(f"Unable to read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PortfolioError("Input JSON must be an object.")
    return value


def extract_intent_map(value: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not value:
        return {}
    candidates = value.get("search_intent_map") or value.get("search_intent_candidates") or []
    if isinstance(value.get("intent_result"), dict):
        nested = value["intent_result"]
        candidates = nested.get("search_intent_map") or nested.get("search_intent_candidates") or candidates
    if not isinstance(candidates, list):
        return {}
    return {
        phrase_key(str(item.get("phrase", ""))): item
        for item in candidates
        if isinstance(item, dict) and phrase_key(str(item.get("phrase", "")))
    }


def metric_value(item: dict[str, Any], field: str) -> float:
    value = item.get(field)
    if isinstance(value, bool) or value is None:
        return 0.0
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, number) if math.isfinite(number) else 0.0


def minmax(values: list[float], value: float, *, logarithmic: bool = False) -> float:
    prepared = [math.log1p(v) if logarithmic else v for v in values]
    current = math.log1p(value) if logarithmic else value
    low, high = min(prepared, default=0.0), max(prepared, default=0.0)
    if high <= low:
        return 0.5 if high > 0 else 0.0
    return (current - low) / (high - low)


def similarity(left: str, right: str) -> float:
    a, b = token_set(left), token_set(right)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def rank_evidence(evidence: dict[str, Any], intent_result: dict[str, Any] | None = None) -> dict[str, Any]:
    source = evidence.get("source")
    keywords = evidence.get("keywords")
    if not isinstance(source, dict) or not isinstance(keywords, list) or not keywords:
        raise PortfolioError("Evidence must contain source and non-empty keywords.")
    authoritative = (
        source.get("authoritative_member_data") is True
        and str(source.get("kind", "")) in MEMBER_SOURCES
        and bool(str(source.get("fetched_at", "")).strip())
    )
    intent_map = extract_intent_map(intent_result)
    searches = [metric_value(item, "average_searches") for item in keywords if isinstance(item, dict)]
    clicks = [metric_value(item, "average_clicks") for item in keywords if isinstance(item, dict)]
    ctrs = [metric_value(item, "ctr") for item in keywords if isinstance(item, dict)]
    competitions = [metric_value(item, "competition") for item in keywords if isinstance(item, dict)]
    trends = [metric_value(item, "trend") for item in keywords if isinstance(item, dict)]

    ranked: list[dict[str, Any]] = []
    for raw in keywords:
        if not isinstance(raw, dict):
            continue
        item = dict(raw)
        phrase = " ".join(str(item.get("phrase", "")).split())
        if not phrase:
            continue
        intent = intent_map.get(phrase_key(phrase), {})
        for field in ("intent", "search_stage", "product_relevance", "fact_supported"):
            if field in intent:
                item[field] = intent[field]
        relevance = str(item.get("product_relevance", "unknown")).casefold()
        fact_supported = item.get("fact_supported") is True
        metric_evidence = any(
            item.get(field) is not None
            for field in ("average_searches", "average_clicks", "ctr", "competition")
        )
        eligible = authoritative and metric_evidence and fact_supported and relevance in {"high", "medium"}
        search_score = minmax(searches, metric_value(item, "average_searches"), logarithmic=True)
        click_score = minmax(clicks, metric_value(item, "average_clicks"), logarithmic=True)
        ctr_score = minmax(ctrs, metric_value(item, "ctr"))
        competition_score = 1.0 - minmax(competitions, metric_value(item, "competition"), logarithmic=True)
        trend_score = minmax(trends, metric_value(item, "trend")) if any(trends) else 0.5
        relevance_factor = 1.0 if relevance == "high" else 0.78 if relevance == "medium" else 0.0
        opportunity = (
            (0.32 * search_score)
            + (0.24 * click_score)
            + (0.18 * ctr_score)
            + (0.16 * competition_score)
            + (0.10 * trend_score)
        ) * relevance_factor
        item.update(
            {
                "phrase": phrase,
                "eligible": eligible,
                "has_member_metrics": metric_evidence,
                "opportunity_score": round(opportunity * 100, 2),
                "score_components": {
                    "searches": round(search_score, 4),
                    "clicks": round(click_score, 4),
                    "ctr": round(ctr_score, 4),
                    "competition_opportunity": round(competition_score, 4),
                    "trend": round(trend_score, 4),
                    "relevance_factor": relevance_factor,
                },
            }
        )
        ranked.append(item)
    ranked.sort(key=lambda item: (item["eligible"], item["opportunity_score"]), reverse=True)

    eligible = [item for item in ranked if item["eligible"]]
    tag_pool = [
        item
        for item in eligible
        if len(item["phrase"]) <= 20 and TAG_PATTERN.fullmatch(item["phrase"])
    ]
    selected: list[dict[str, Any]] = []
    for intent_name in INTENT_ORDER:
        match = next(
            (
                item
                for item in tag_pool
                if str(item.get("intent", "unknown")) == intent_name
                and all(similarity(item["phrase"], other["phrase"]) < 0.8 for other in selected)
            ),
            None,
        )
        if match and match not in selected:
            selected.append(match)
    for item in tag_pool:
        if len(selected) >= 13:
            break
        if item in selected:
            continue
        if all(similarity(item["phrase"], other["phrase"]) < 0.8 for other in selected):
            selected.append(item)

    rejected = [
        {
            "phrase": item["phrase"],
            "reason": (
                "non_member_source"
                if not authoritative
                else "missing_member_metrics"
                if authoritative and not item.get("has_member_metrics")
                else "fact_or_relevance_not_confirmed"
                if not item["eligible"]
                else "not_tag_eligible_or_redundant"
            ),
        }
        for item in ranked
        if item not in selected
    ]
    return {
        "source": source,
        "method": {
            "name": "transparent_opportunity_score_v1",
            "weights": {"searches": 0.32, "clicks": 0.24, "ctr": 0.18, "competition": 0.16, "trend": 0.10},
            "disclaimer": "Selection aid only; not an Etsy rank, traffic, or sales prediction.",
        },
        "ranked_keywords": ranked,
        "selected_tag_candidates": selected[:13],
        "coverage": {
            "authoritative_member_data": authoritative,
            "eligible_keyword_count": len(eligible),
            "tag_candidate_count": len(tag_pool),
            "selected_tag_count": min(13, len(selected)),
            "needs_semantic_coverage": max(0, 13 - len(selected)),
        },
        "rejected_keywords": rejected,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Canonical keyword evidence JSON.")
    parser.add_argument("--intent-input", type=Path, help="Gemini intent JSON used to confirm relevance and facts.")
    parser.add_argument("--output", type=Path, help="Write portfolio JSON here; defaults to stdout.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        evidence = load_json(args.input)
        intent = load_json(args.intent_input) if args.intent_input else None
        result = rank_evidence(evidence, intent)
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 0
    except PortfolioError as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
