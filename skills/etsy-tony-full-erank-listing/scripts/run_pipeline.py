#!/usr/bin/env python3
"""Run the Gemini + eRank evidence Etsy listing workflow."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from gemini_client import GeminiClient, GeminiError  # noqa: E402
from select_keyword_portfolio import PortfolioError, rank_evidence  # noqa: E402
from validate_listing import ValidationInputError, validate_package  # noqa: E402


class PipelineError(RuntimeError):
    """Safe pipeline error."""


def load_text(name: str) -> str:
    path = SKILL_DIR / "references" / name
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PipelineError(f"Unable to load reference {name}: {exc}") from exc


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PipelineError(f"Unable to read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PipelineError(f"{path} must contain a JSON object.")
    return value


def write_object(value: dict[str, Any], path: Path | None) -> None:
    rendered = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)


def normalize_request(value: dict[str, Any]) -> dict[str, Any]:
    result = dict(value)
    result.setdefault("market", "US")
    result.setdefault("shop_language", "en-US")
    result.setdefault("product", {})
    result.setdefault("category", "")
    result.setdefault("attributes", {})
    result.setdefault("confirmed_claims", [])
    result.setdefault("images", [])
    result.setdefault("current_listing", {})
    result.setdefault("shop_stats", {})
    result.setdefault("prohibited_terms", [])
    if not isinstance(result["product"], (dict, str)):
        raise PipelineError("product must be an object or string.")
    if not isinstance(result["attributes"], dict):
        raise PipelineError("attributes must be an object.")
    for key in ("confirmed_claims", "images", "prohibited_terms"):
        if not isinstance(result[key], list):
            raise PipelineError(f"{key} must be an array.")
    if str(result["market"]).upper() != "US":
        raise PipelineError("This skill currently requires market=US unless its market rules are extended.")
    return result


def is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value)


def validate_intent_result(value: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if not isinstance(value.get("product_truth"), dict):
        problems.append("product_truth must be an object")
    if not is_string_list(value.get("information_to_confirm")):
        problems.append("information_to_confirm must be an array of non-empty Chinese strings")
    if not is_string_list(value.get("assumptions")):
        problems.append("assumptions must be an array of non-empty Chinese strings")
    candidates = value.get("search_intent_candidates")
    if not isinstance(candidates, list) or not 5 <= len(candidates) <= 40:
        problems.append("search_intent_candidates must contain 5-40 objects")
        return problems
    seen: set[str] = set()
    for index, item in enumerate(candidates):
        if not isinstance(item, dict):
            problems.append(f"search_intent_candidates[{index}] must be an object")
            continue
        phrase = str(item.get("phrase", "")).strip()
        if not phrase:
            problems.append(f"search_intent_candidates[{index}].phrase is required")
        elif phrase.casefold() in seen:
            problems.append(f"duplicate intent phrase: {phrase}")
        seen.add(phrase.casefold())
        if item.get("evidence_status") != "GEMINI_HYPOTHESIS":
            problems.append(f"intent phrase must start as GEMINI_HYPOTHESIS: {phrase}")
        if item.get("product_relevance") not in {"high", "medium", "low"}:
            problems.append(f"invalid product_relevance for {phrase}")
        if not isinstance(item.get("fact_supported"), bool):
            problems.append(f"fact_supported must be boolean for {phrase}")
        for field in ("intent", "search_stage", "rationale"):
            if not isinstance(item.get(field), str) or not str(item.get(field)).strip():
                problems.append(f"{field} is required for {phrase}")
    return problems


def intent_prompt() -> str:
    return f"""
Act as a senior US Etsy customer-search strategist and product-truth analyst.
Use only supplied facts and visible image observations. Keep visible_observations empty when no images are supplied.
Never invent materials, construction,
dimensions, mechanisms, production methods, certifications, market metrics, or private Etsy data.
All reasoning and confirmation questions must be Chinese. All candidate search phrases must be natural English.

Return valid JSON only with exactly these keys:
{{
  "product_truth": {{
    "product_type": "English",
    "confirmed_objective_traits": ["English"],
    "visible_observations": ["English"],
    "supported_use_cases": ["English"],
    "supported_customization": ["English"],
    "unsupported_or_unknown_claims": ["English"]
  }},
  "information_to_confirm": ["Chinese"],
  "assumptions": ["Chinese"],
  "search_intent_candidates": [
    {{
      "phrase": "English",
      "intent": "product|objective_trait|style|room_use|problem_solution|recipient_occasion|personalization|regional_synonym|seasonal",
      "search_stage": "discovery|consideration|high_intent|seasonal",
      "product_relevance": "high|medium|low",
      "fact_supported": true,
      "rationale": "Chinese",
      "evidence_status": "GEMINI_HYPOTHESIS"
    }}
  ]
}}

Generate 5-40 distinct candidates depending on available product truth. These are research hypotheses,
not search-volume claims. Include broad seeds and accurate long-tail buyer language, but reject risky or
materially different product terms. Return an empty information_to_confirm array when nothing material is missing.

SEARCH INTENT RULES:
{load_text('search-intent-taxonomy.md')}

ETSY RULES:
{load_text('etsy-2026-rules.md')}
""".strip()


def run_intent(client: GeminiClient, request_data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = {
        "market": request_data["market"],
        "shop_language": request_data["shop_language"],
        "product": request_data["product"],
        "category": request_data["category"],
        "attributes": request_data["attributes"],
        "confirmed_claims": request_data["confirmed_claims"],
        "current_listing": request_data["current_listing"],
        "task": "Discover customer search language and build an eRank research queue.",
    }
    return client.generate_json(
        stage="intent",
        system_prompt=intent_prompt(),
        payload=payload,
        images=[str(item) for item in request_data["images"]],
        validator=validate_intent_result,
        temperature=0.2,
    )


def compact_keyword(item: dict[str, Any]) -> dict[str, Any]:
    return {
        key: item.get(key)
        for key in ("phrase", "average_searches", "average_clicks", "ctr", "competition", "trend")
    }


def validate_annotation_batch(expected: list[str]):
    expected_keys = {phrase.casefold(): phrase for phrase in expected}

    def validator(value: dict[str, Any]) -> list[str]:
        problems: list[str] = []
        annotations = value.get("keyword_annotations")
        if not isinstance(annotations, list) or len(annotations) != len(expected):
            return [f"keyword_annotations must contain exactly {len(expected)} objects"]
        seen: set[str] = set()
        for index, item in enumerate(annotations):
            if not isinstance(item, dict):
                problems.append(f"keyword_annotations[{index}] must be an object")
                continue
            phrase = str(item.get("phrase", "")).strip()
            key = phrase.casefold()
            if key not in expected_keys:
                problems.append(f"annotation phrase was not supplied: {phrase}")
            if key in seen:
                problems.append(f"duplicate annotation: {phrase}")
            seen.add(key)
            if item.get("product_relevance") not in {"high", "medium", "low"}:
                problems.append(f"invalid product_relevance for {phrase}")
            if not isinstance(item.get("fact_supported"), bool):
                problems.append(f"fact_supported must be boolean for {phrase}")
            for field in ("intent", "search_stage", "rationale", "rejection_reason"):
                if not isinstance(item.get(field), str):
                    problems.append(f"{field} must be a string for {phrase}")
        missing = set(expected_keys) - seen
        if missing:
            problems.append("missing annotations: " + ", ".join(expected_keys[key] for key in sorted(missing)))
        if not is_string_list(value.get("portfolio_reasoning")):
            problems.append("portfolio_reasoning must be an array of non-empty Chinese strings")
        return problems

    return validator


def annotation_prompt() -> str:
    return f"""
Act as a skeptical senior Etsy keyword strategist. Classify every supplied eRank member keyword
against the supplied product truth. Metrics measure market activity; they never override product accuracy.
Do not change, add, remove, translate, or normalize the supplied phrase strings.

Return valid JSON only:
{{
  "keyword_annotations": [
    {{
      "phrase": "exact supplied phrase",
      "intent": "product|objective_trait|style|room_use|problem_solution|recipient_occasion|personalization|regional_synonym|seasonal|unknown",
      "search_stage": "discovery|consideration|high_intent|seasonal|unknown",
      "product_relevance": "high|medium|low",
      "fact_supported": true,
      "rationale": "Chinese",
      "rejection_reason": "Chinese or empty string"
    }}
  ],
  "portfolio_reasoning": ["Chinese"]
}}

Use fact_supported=false whenever the phrase requires an unconfirmed material, mechanism, production
method, personalization, recipient, occasion, brand, or materially different product type.

SEARCH INTENT RULES:
{load_text('search-intent-taxonomy.md')}
""".strip()


def annotate_evidence(
    client: GeminiClient,
    request_data: dict[str, Any],
    intent_result: dict[str, Any],
    evidence: dict[str, Any],
    *,
    batch_size: int = 40,
    max_keywords: int = 200,
) -> tuple[dict[str, Any], list[dict[str, Any]], bool]:
    keywords = evidence.get("keywords")
    if not isinstance(keywords, list) or not keywords:
        raise PipelineError("eRank evidence contains no keywords.")
    usable = [item for item in keywords if isinstance(item, dict) and str(item.get("phrase", "")).strip()]
    truncated = len(usable) > max_keywords
    usable = usable[:max_keywords]
    annotations: dict[str, dict[str, Any]] = {}
    metadata: list[dict[str, Any]] = []
    reasoning: list[str] = []
    for start in range(0, len(usable), batch_size):
        batch = usable[start : start + batch_size]
        phrases = [str(item["phrase"]).strip() for item in batch]
        payload = {
            "market": request_data["market"],
            "product_truth": intent_result["product_truth"],
            "confirmed_claims": request_data["confirmed_claims"],
            "keywords": [compact_keyword(item) for item in batch],
        }
        result, meta = client.generate_json(
            stage=f"evidence_annotation_{(start // batch_size) + 1}",
            system_prompt=annotation_prompt(),
            payload=payload,
            validator=validate_annotation_batch(phrases),
            temperature=0.1,
        )
        metadata.append(meta)
        reasoning.extend(result["portfolio_reasoning"])
        for item in result["keyword_annotations"]:
            annotations[str(item["phrase"]).casefold()] = item
    annotated = deepcopy(evidence)
    annotated_keywords: list[dict[str, Any]] = []
    for item in usable:
        merged = dict(item)
        annotation = annotations.get(str(item["phrase"]).casefold())
        if not annotation:
            raise PipelineError(f"Missing Gemini annotation for eRank keyword: {item['phrase']}")
        merged.update(annotation)
        annotated_keywords.append(merged)
    annotated["keywords"] = annotated_keywords
    annotated["gemini_portfolio_reasoning"] = reasoning
    annotated.setdefault("integrity", {})["input_keyword_count"] = len(keywords)
    annotated["integrity"]["annotated_keyword_count"] = len(annotated_keywords)
    annotated["integrity"]["truncated_for_review"] = truncated
    return annotated, metadata, truncated


def eligible_phrases(portfolio: dict[str, Any]) -> set[str]:
    return {
        str(item.get("phrase", "")).casefold()
        for item in portfolio.get("ranked_keywords", [])
        if isinstance(item, dict) and item.get("eligible") is True
    }


def primary_phrase(portfolio: dict[str, Any]) -> str:
    for item in portfolio.get("ranked_keywords", []):
        if isinstance(item, dict) and item.get("eligible") is True:
            return str(item.get("phrase", "")).strip()
    return ""


def listing_prompt() -> str:
    return f"""
Act as a top-tier US Etsy listing operator and conversion copy chief. Write only from supplied product
truth and keyword evidence. eRank metrics are evidence, not guarantees. Never invent a product fact,
market metric, rank, customer demographic, certification, or private Etsy behavior.

Return valid JSON only with exactly these keys:
{{
  "listing": {{
    "recommended_title": "English",
    "alternate_titles": ["English", "English"],
    "tags": ["13 English tags"],
    "tag_evidence": [
      {{
        "tag": "exact final tag",
        "evidence_status": "ERANK_MEMBER_VERIFIED|ERANK_MEMBER_DERIVED|SHOP_STATS_VERIFIED|SEMANTIC_COVERAGE",
        "matched_keyword": "English",
        "intent": "English",
        "rationale": "Chinese"
      }}
    ],
    "description_opening": ["English", "English", "English"],
    "full_description": "complete ready-to-paste English description with icon-led headings",
    "category_attribute_advice": ["Chinese"],
    "visual_advice": ["Chinese"]
  }},
  "rejected_keywords": [{{"phrase": "English", "reason": "Chinese"}}],
  "information_to_confirm": ["Chinese"],
  "assumptions": ["Chinese"],
  "measurement_plan": ["Chinese"]
}}

Use the highest qualified opportunity, not the highest raw volume. Keep title copy clear and buyer-facing.
Map every tag to honest evidence. Use SEMANTIC_COVERAGE when no exact member metric exists; never attach
an exact metric to a derived phrase. Write a fresh, product-specific full description, not a snippet or reusable
template. Its first three non-empty lines must exactly match description_opening. Prefix every required section
heading with one relevant icon, vary the icons across sections, and include the requested shipping lines.
Never use the prohibited cake-topper boilerplate from the Etsy rules as a default or close paraphrase.
Return empty information_to_confirm and assumptions arrays when none apply.

ETSY RULES:
{load_text('etsy-2026-rules.md')}

OUTPUT RULES:
{load_text('listing-output-schema.md')}
""".strip()


def make_copy_validator(request_data: dict[str, Any], portfolio: dict[str, Any], source: dict[str, Any]):
    eligible = eligible_phrases(portfolio)
    primary = primary_phrase(portfolio)

    def validator(value: dict[str, Any]) -> list[str]:
        package = dict(value)
        package["provenance"] = {"erank": source}
        validation = validate_package(package, request_data)
        problems = list(validation["errors"])
        listing = value.get("listing", {})
        if isinstance(listing, dict):
            for item in listing.get("tag_evidence", []):
                if not isinstance(item, dict):
                    continue
                if item.get("evidence_status") == "ERANK_MEMBER_VERIFIED":
                    matched = str(item.get("matched_keyword", "")).casefold()
                    if matched not in eligible:
                        problems.append(
                            f"Tag {item.get('tag')} claims ERANK_MEMBER_VERIFIED but matched_keyword is not eligible member evidence."
                        )
                if item.get("evidence_status") == "SHOP_STATS_VERIFIED":
                    shop_stats = request_data.get("shop_stats")
                    search_terms = shop_stats.get("search_terms") if isinstance(shop_stats, dict) else None
                    if not isinstance(search_terms, list) or not search_terms:
                        problems.append(
                            f"Tag {item.get('tag')} claims SHOP_STATS_VERIFIED without supplied Shop Stats search_terms."
                        )
        if primary and isinstance(listing.get("recommended_title"), str):
            title_tokens = set(listing["recommended_title"].casefold().split())
            primary_tokens = set(primary.casefold().split())
            if primary_tokens and len(title_tokens & primary_tokens) / len(primary_tokens) < 0.6:
                problems.append("recommended_title does not sufficiently represent the primary qualified keyword")
        for key in ("information_to_confirm", "assumptions", "measurement_plan"):
            if not is_string_list(value.get(key)):
                problems.append(f"{key} must be an array of non-empty Chinese strings")
        if not isinstance(value.get("rejected_keywords"), list):
            problems.append("rejected_keywords must be an array")
        return problems

    return validator


def review_prompt() -> str:
    return f"""
Act as an independent Etsy listing quality reviewer. Review the supplied draft against product truth,
keyword evidence, and the rules. Correct every factual, title, tag, evidence-mapping, readability,
description, or keyword-stuffing issue. Do not add new facts or metrics.

Return valid JSON only:
{{
  "approved": true,
  "issues": ["Chinese"],
  "corrected_listing": {{
    "recommended_title": "English",
    "alternate_titles": ["English", "English"],
    "tags": ["13 English tags"],
    "tag_evidence": [],
    "description_opening": ["English", "English", "English"],
    "full_description": "complete ready-to-paste English description with icon-led headings",
    "category_attribute_advice": ["Chinese"],
    "visual_advice": ["Chinese"]
  }}
}}

Set approved=true only when corrected_listing is safe and ready for deterministic validation. Reject or rewrite
generic repeated openings, incomplete descriptions, missing or repeated section icons, and any description whose
first three non-empty lines do not exactly match description_opening.

ETSY RULES:
{load_text('etsy-2026-rules.md')}
""".strip()


def make_review_validator(
    request_data: dict[str, Any], portfolio: dict[str, Any], source: dict[str, Any]
):
    copy_validator = make_copy_validator(request_data, portfolio, source)

    def validator(value: dict[str, Any]) -> list[str]:
        problems: list[str] = []
        if value.get("approved") is not True:
            problems.append("approved must be true after correcting every issue")
        if not isinstance(value.get("issues"), list) or not all(isinstance(item, str) for item in value["issues"]):
            problems.append("issues must be an array of strings")
        corrected = value.get("corrected_listing")
        if not isinstance(corrected, dict):
            problems.append("corrected_listing must be an object")
        else:
            problems.extend(copy_validator({
                "listing": corrected,
                "rejected_keywords": [],
                "information_to_confirm": ["无"] if not request_data.get("information_to_confirm") else request_data["information_to_confirm"],
                "assumptions": ["无额外假设"],
                "measurement_plan": ["上线前保存基线，上线后根据足够曝光量复核。"],
            }))
        return problems

    return validator


def determine_status(
    request_data: dict[str, Any],
    source: dict[str, Any],
    validation: dict[str, Any],
    information_to_confirm: list[str],
    truncated: bool,
) -> str:
    if not validation["valid"]:
        return "FAILED"
    if source.get("authoritative_member_data") is not True:
        return "UNVERIFIED"
    fetched_at = str(source.get("fetched_at", "")).strip()
    try:
        parsed = datetime.fromisoformat(fetched_at[:-1] + "+00:00" if fetched_at.endswith("Z") else fetched_at)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        evidence_age_days = (datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)).total_seconds() / 86400
    except ValueError:
        return "PARTIAL"
    if evidence_age_days < -1 or evidence_age_days > 45:
        return "PARTIAL"
    audit = request_data.get("member_listing_audit", {})
    audit_complete = isinstance(audit, dict) and audit.get("complete") is True and audit.get("verified") is True
    existing = bool(request_data.get("current_listing"))
    rank_baseline = request_data.get("rank_baseline")
    baseline_complete = not existing or bool(rank_baseline)
    if audit_complete and baseline_complete and not information_to_confirm and not truncated:
        return "VERIFIED_SUCCESS"
    return "PARTIAL"


def run_listing(
    client: GeminiClient,
    request_data: dict[str, Any],
    evidence: dict[str, Any],
    *,
    batch_size: int,
    max_keywords: int,
) -> dict[str, Any]:
    intent_result, intent_meta = run_intent(client, request_data)
    annotated, annotation_meta, truncated = annotate_evidence(
        client,
        request_data,
        intent_result,
        evidence,
        batch_size=batch_size,
        max_keywords=max_keywords,
    )
    portfolio = rank_evidence(annotated)
    if not eligible_phrases(portfolio):
        return {
            "status": "BLOCKED",
            "product_truth": intent_result["product_truth"],
            "information_to_confirm": intent_result["information_to_confirm"],
            "search_intent_map": intent_result["search_intent_candidates"],
            "keyword_portfolio": portfolio,
            "reason": "No fact-supported, relevant keyword rows were found in authoritative eRank member evidence.",
            "provenance": {"gemini": {"intent": intent_meta, "annotations": annotation_meta}, "erank": evidence.get("source", {})},
        }

    prompt_portfolio = deepcopy(portfolio)
    prompt_portfolio["ranked_keywords"] = prompt_portfolio["ranked_keywords"][:80]
    prompt_portfolio["rejected_keywords"] = prompt_portfolio["rejected_keywords"][:40]
    payload = {
        "market": request_data["market"],
        "shop_language": request_data["shop_language"],
        "product_truth": intent_result["product_truth"],
        "information_to_confirm": intent_result["information_to_confirm"],
        "product": request_data["product"],
        "category": request_data["category"],
        "attributes": request_data["attributes"],
        "confirmed_claims": request_data["confirmed_claims"],
        "current_listing": request_data["current_listing"],
        "shop_stats": request_data["shop_stats"],
        "search_intent_map": intent_result["search_intent_candidates"],
        "keyword_portfolio": prompt_portfolio,
    }
    draft, copy_meta = client.generate_json(
        stage="listing_copy",
        system_prompt=listing_prompt(),
        payload=payload,
        validator=make_copy_validator(request_data, portfolio, evidence["source"]),
        temperature=0.15,
    )

    review_payload = {
        "product_truth": intent_result["product_truth"],
        "confirmed_claims": request_data["confirmed_claims"],
        "keyword_portfolio": prompt_portfolio,
        "draft_listing": draft["listing"],
    }
    review, review_meta = client.generate_json(
        stage="quality_review",
        system_prompt=review_prompt(),
        payload=review_payload,
        validator=make_review_validator(request_data, portfolio, evidence["source"]),
        temperature=0.05,
    )
    draft["listing"] = review["corrected_listing"]

    package: dict[str, Any] = {
        "status": "PARTIAL",
        "product_truth": intent_result["product_truth"],
        "information_to_confirm": list(dict.fromkeys(intent_result["information_to_confirm"] + draft["information_to_confirm"])),
        "search_intent_map": intent_result["search_intent_candidates"],
        "keyword_portfolio": portfolio,
        "rejected_keywords": draft["rejected_keywords"],
        "listing": draft["listing"],
        "quality_review": {
            "issues": review["issues"],
            "warnings": [],
            "member_listing_audit_complete": bool(
                isinstance(request_data.get("member_listing_audit"), dict)
                and request_data["member_listing_audit"].get("complete") is True
                and request_data["member_listing_audit"].get("verified") is True
            ),
        },
        "measurement_plan": draft["measurement_plan"],
        "assumptions": list(dict.fromkeys(intent_result["assumptions"] + draft["assumptions"])),
        "provenance": {
            "gemini": {
                "intent": intent_meta,
                "evidence_annotations": annotation_meta,
                "listing_copy": copy_meta,
                "quality_review": review_meta,
            },
            "erank": evidence["source"],
            "evidence_integrity": annotated.get("integrity", {}),
            "selection_method": portfolio["method"],
        },
    }
    validation = validate_package(package, request_data)
    package["quality_review"]["warnings"] = validation["warnings"]
    package["quality_review"]["validator"] = validation
    package["status"] = determine_status(
        request_data,
        evidence["source"],
        validation,
        package["information_to_confirm"],
        truncated,
    )
    if package["status"] == "FAILED":
        raise PipelineError("Final package failed deterministic validation: " + "; ".join(validation["errors"]))
    return package


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("intent", "listing"), required=True)
    parser.add_argument("--input", type=Path, required=True, help="Product request JSON.")
    parser.add_argument("--erank-input", type=Path, help="Canonical normalized eRank member evidence JSON.")
    parser.add_argument("--output", type=Path, help="Write JSON output here; defaults to stdout.")
    parser.add_argument("--model", help="Gemini model name on Clawlist.")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--batch-size", type=int, default=40)
    parser.add_argument("--max-keywords", type=int, default=200)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        request_data = normalize_request(load_object(args.input))
        client = GeminiClient(model=args.model, timeout=args.timeout)
        if args.stage == "intent":
            intent, meta = run_intent(client, request_data)
            result = {
                "status": "UNVERIFIED",
                "product_truth": intent["product_truth"],
                "information_to_confirm": intent["information_to_confirm"],
                "assumptions": intent["assumptions"],
                "search_intent_map": intent["search_intent_candidates"],
                "next_action": "Validate the search hypotheses with the US eRank member Keyword Tool and normalize the export.",
                "provenance": {"gemini": {"intent": meta}},
            }
            write_object(result, args.output)
            return 0
        if not args.erank_input:
            intent, meta = run_intent(client, request_data)
            result = {
                "status": "BLOCKED",
                "product_truth": intent["product_truth"],
                "information_to_confirm": intent["information_to_confirm"],
                "search_intent_map": intent["search_intent_candidates"],
                "reason": "Data-backed listing generation requires normalized eRank member keyword evidence.",
                "next_action": "Research the candidate phrases in the logged-in eRank member account and provide a normalized export.",
                "provenance": {"gemini": {"intent": meta}},
            }
            write_object(result, args.output)
            return 2
        evidence = load_object(args.erank_input)
        if not 1 <= args.batch_size <= 60:
            raise PipelineError("batch-size must be between 1 and 60.")
        if not 1 <= args.max_keywords <= 500:
            raise PipelineError("max-keywords must be between 1 and 500.")
        result = run_listing(
            client,
            request_data,
            evidence,
            batch_size=args.batch_size,
            max_keywords=args.max_keywords,
        )
        write_object(result, args.output)
        return 0 if result["status"] in {"VERIFIED_SUCCESS", "PARTIAL"} else 2
    except (PipelineError, GeminiError, PortfolioError, ValidationInputError, OSError) as exc:
        message = str(exc)
        try:
            if "client" in locals():
                message = client.redact(message)
        except Exception:
            pass
        sys.stderr.write(f"ERROR: {message}\n")
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
