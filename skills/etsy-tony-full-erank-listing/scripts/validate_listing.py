#!/usr/bin/env python3
"""Deterministically validate an Etsy listing package and its evidence mapping."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


TAG_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9 '\-]*")
REQUIRED_SECTIONS = (
    "Why You'll Love It",
    "Product Details",
    "Perfect For",
    "Care Instructions",
    "Shipping & Processing",
    "Important Notes",
)
MIN_DESCRIPTION_CHARACTERS = 400
DESCRIPTION_BOILERPLATE_PATTERNS = (
    re.compile(
        r"add an elegant finishing touch to your celebratory cake with a custom laser[- ]cut acrylic cake topper",
        re.IGNORECASE,
    ),
    re.compile(
        r"perfect for birthdays, weddings, bridal showers, baby showers, graduations, and other special occasions",
        re.IGNORECASE,
    ),
)
EVIDENCE_STATES = {
    "ERANK_MEMBER_VERIFIED",
    "ERANK_MEMBER_DERIVED",
    "SHOP_STATS_VERIFIED",
    "COMPETITOR_OBSERVED",
    "GEMINI_HYPOTHESIS",
    "SEMANTIC_COVERAGE",
    "REJECTED",
}
FINAL_TAG_EVIDENCE_STATES = {
    "ERANK_MEMBER_VERIFIED",
    "ERANK_MEMBER_DERIVED",
    "SHOP_STATS_VERIFIED",
    "SEMANTIC_COVERAGE",
}
TITLE_BANNED = {
    "best",
    "perfect",
    "beautiful",
    "amazing",
    "sale",
    "free shipping",
    "discount",
}
RISKY_CLAIMS = {
    "glider": ("glider", "gliding mechanism"),
    "solid wood": ("solid wood",),
    "handmade": ("handmade", "handcrafted", "hand crafted"),
    "orthopedic": ("orthopedic", "orthopaedic"),
    "waterproof": ("waterproof",),
    "leather": ("leather",),
    "stainless steel": ("stainless steel", "stainless"),
    "sterling silver": ("sterling silver", "pure silver"),
    "vintage": ("vintage",),
    "custom-made": ("custom-made", "custom made"),
}


class ValidationInputError(RuntimeError):
    """Raised when validation inputs cannot be read."""


def normalized_phrase(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))


def words(value: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)?", value)


def string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value)


def listing_from_package(package: dict[str, Any]) -> dict[str, Any]:
    value = package.get("listing", package)
    if not isinstance(value, dict):
        raise ValidationInputError("listing must be an object.")
    return value


def request_claims(request: dict[str, Any]) -> str:
    claims = request.get("confirmed_claims", [])
    if not isinstance(claims, list):
        return ""
    return " ".join(str(item).casefold() for item in claims)


def request_structured_phrases(request: dict[str, Any]) -> set[str]:
    values: list[str] = []
    category = request.get("category")
    if category:
        values.append(str(category))
    attributes = request.get("attributes", {})
    if isinstance(attributes, dict):
        for key, value in attributes.items():
            values.append(str(key))
            if isinstance(value, list):
                values.extend(str(item) for item in value)
            elif value not in (None, ""):
                values.append(str(value))
    return {normalized_phrase(value) for value in values if normalized_phrase(value)}


def section_heading_icon(description: str, section: str) -> str:
    for raw_line in description.splitlines():
        line = raw_line.strip()
        position = line.casefold().find(section.casefold())
        if position < 0:
            continue
        prefix = line[:position].strip().strip("#*_`>-:|[]()")
        if prefix and any(ord(character) > 127 for character in prefix):
            return prefix
    return ""


def validate_package(package: dict[str, Any], request: dict[str, Any] | None = None) -> dict[str, Any]:
    request = request or {}
    listing = listing_from_package(package)
    errors: list[str] = []
    warnings: list[str] = []

    recommended = listing.get("recommended_title")
    alternatives = listing.get("alternate_titles")
    if not isinstance(recommended, str) or not recommended.strip():
        errors.append("listing.recommended_title must be a non-empty string.")
        recommended = ""
    if not string_list(alternatives) or len(alternatives) != 2:
        errors.append("listing.alternate_titles must contain exactly 2 non-empty strings.")
        alternatives = alternatives if string_list(alternatives) else []
    titles = [recommended.strip()] + [str(item).strip() for item in alternatives]
    nonempty_titles = [title for title in titles if title]
    if len({title.casefold() for title in nonempty_titles}) != len(nonempty_titles):
        errors.append("All 3 titles must be distinct.")
    for index, title in enumerate(nonempty_titles, 1):
        if len(title) > 140:
            errors.append(f"Title {index} exceeds 140 characters.")
        if len(words(title)) > 15:
            warnings.append(f"Title {index} exceeds the approximately 15-word clarity target.")
        allowed = {str(item).casefold() for item in request.get("title_allowed_terms", []) if str(item).strip()}
        for banned in TITLE_BANNED:
            if banned not in allowed and re.search(rf"\b{re.escape(banned)}\b", title.casefold()):
                errors.append(f"Title {index} contains disallowed term: {banned}.")
        if "gift" not in allowed and re.search(r"\bgift(?:s|ing)?\b", title.casefold()):
            errors.append(f"Title {index} contains gifting language without explicit title authorization.")

    tags = listing.get("tags")
    if not string_list(tags) or len(tags) != 13:
        actual = len(tags) if isinstance(tags, list) else 0
        errors.append(f"listing.tags must contain exactly 13 non-empty strings; got {actual}.")
        tags = tags if string_list(tags) else []
    clean_tags = [tag.strip() for tag in tags]
    if len({tag.casefold() for tag in clean_tags}) != len(clean_tags):
        errors.append("All tags must be distinct.")
    normalized_tags = [normalized_phrase(tag) for tag in clean_tags]
    if len(set(normalized_tags)) != len(normalized_tags):
        errors.append("Tags contain normalized duplicates or trivial punctuation variants.")
    for tag in clean_tags:
        if len(tag) > 20:
            errors.append(f"Tag exceeds 20 characters: {tag}.")
        if not TAG_PATTERN.fullmatch(tag):
            errors.append(f"Tag contains unsupported characters: {tag}.")
    one_word_count = sum(len(words(tag)) == 1 for tag in clean_tags)
    if one_word_count > 4:
        warnings.append(f"{one_word_count} one-word tags reduce long-tail coverage.")

    structured = request_structured_phrases(request)
    for tag in clean_tags:
        if normalized_phrase(tag) in structured:
            warnings.append(f"Tag exactly duplicates a category or attribute value: {tag}.")

    tag_evidence = listing.get("tag_evidence")
    if not isinstance(tag_evidence, list) or len(tag_evidence) != 13:
        actual = len(tag_evidence) if isinstance(tag_evidence, list) else 0
        errors.append(f"listing.tag_evidence must contain exactly 13 objects; got {actual}.")
        tag_evidence = tag_evidence if isinstance(tag_evidence, list) else []
    evidence_by_tag: dict[str, dict[str, Any]] = {}
    for item in tag_evidence:
        if not isinstance(item, dict):
            errors.append("Every tag_evidence item must be an object.")
            continue
        tag = str(item.get("tag", "")).strip()
        state = str(item.get("evidence_status", "")).strip()
        if not tag:
            errors.append("Every tag_evidence item must name its tag.")
        if state not in FINAL_TAG_EVIDENCE_STATES:
            errors.append(f"Invalid evidence status for tag {tag or '(missing)'}: {state or '(missing)'}.")
        for field in ("matched_keyword", "intent", "rationale"):
            if not isinstance(item.get(field), str) or not str(item.get(field)).strip():
                errors.append(f"tag_evidence for {tag or '(missing)'} requires non-empty {field}.")
        if tag:
            evidence_by_tag[tag.casefold()] = item
    for tag in clean_tags:
        if tag.casefold() not in evidence_by_tag:
            errors.append(f"Missing evidence mapping for tag: {tag}.")

    opening = listing.get("description_opening")
    if not string_list(opening) or len(opening) != 3:
        errors.append("listing.description_opening must contain exactly 3 non-empty strings.")
        opening = opening if string_list(opening) else []
    description = listing.get("full_description")
    if not isinstance(description, str) or not description.strip():
        errors.append("listing.full_description must be a non-empty string.")
        description = ""
    if description and len(description.strip()) < MIN_DESCRIPTION_CHARACTERS:
        errors.append(
            f"listing.full_description must be a complete description of at least {MIN_DESCRIPTION_CHARACTERS} characters."
        )
    description_lines = [line.strip() for line in description.splitlines() if line.strip()]
    if opening and description_lines[:3] != [line.strip() for line in opening]:
        errors.append("The first 3 non-empty full_description lines must exactly match description_opening.")
    section_icons: list[str] = []
    for section in REQUIRED_SECTIONS:
        if section.casefold() not in description.casefold():
            errors.append(f"Description is missing required section: {section}.")
            continue
        icon = section_heading_icon(description, section)
        if not icon:
            errors.append(f"Description section heading requires a leading icon: {section}.")
        else:
            section_icons.append(icon)
    if len(section_icons) == len(REQUIRED_SECTIONS) and len(set(section_icons)) < 3:
        errors.append("Description section icons must be varied; use at least 3 distinct icons.")
    for pattern in DESCRIPTION_BOILERPLATE_PATTERNS:
        if pattern.search(description):
            errors.append("Description contains prohibited generic cake-topper boilerplate.")

    shipping = request.get("shipping", {})
    use_default_shipping = not isinstance(shipping, dict) or not shipping
    if use_default_shipping:
        for line in ("Processing time: 1-3 days", "Shipping method: 3-7 days"):
            if line.casefold() not in description.casefold():
                errors.append(f"Description is missing default shipping line: {line}.")
    joined_tags = ", ".join(clean_tags)
    if joined_tags and joined_tags.casefold() in description.casefold():
        errors.append("Description contains the complete comma-separated tag list.")

    listing_text = " ".join(nonempty_titles + clean_tags + list(opening) + [description]).casefold()
    confirmed = request_claims(request)
    for claim, terms in RISKY_CLAIMS.items():
        if claim not in confirmed and any(re.search(rf"\b{re.escape(term)}\b", listing_text) for term in terms):
            errors.append(f"Unconfirmed risky claim appears in listing copy: {claim}.")
    prohibited = request.get("prohibited_terms", [])
    if isinstance(prohibited, list):
        for term in prohibited:
            clean = str(term).strip().casefold()
            if clean and re.search(rf"\b{re.escape(clean)}\b", listing_text):
                errors.append(f"Prohibited term appears in listing copy: {term}.")

    title_tokens = Counter(token.casefold() for token in words(recommended))
    repeated = sorted(token for token, count in title_tokens.items() if count > 2 and len(token) > 2)
    if repeated:
        warnings.append("Recommended title repeats words heavily: " + ", ".join(repeated) + ".")

    source = package.get("provenance", {}).get("erank", {}) if isinstance(package.get("provenance"), dict) else {}
    authoritative = source.get("authoritative_member_data") is True
    evidence_counts = Counter(
        str(item.get("evidence_status")) for item in tag_evidence if isinstance(item, dict)
    )
    checks = {
        "title_count": len(nonempty_titles),
        "recommended_title_characters": len(recommended),
        "recommended_title_words": len(words(recommended)),
        "tag_count": len(clean_tags),
        "one_word_tag_count": one_word_count,
        "tag_evidence_count": len(tag_evidence),
        "tag_evidence_states": dict(evidence_counts),
        "description_characters": len(description),
        "description_section_icon_count": len(section_icons),
        "authoritative_member_data": authoritative,
    }
    return {"valid": not errors, "errors": errors, "warnings": warnings, "checks": checks}


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationInputError(f"Unable to read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationInputError(f"{path} must contain a JSON object.")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Listing package JSON.")
    parser.add_argument("--request", type=Path, help="Original product request JSON.")
    parser.add_argument("--output", type=Path, help="Write validation JSON here; defaults to stdout.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        package = load_object(args.input)
        request = load_object(args.request) if args.request else {}
        result = validate_package(package, request)
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 0 if result["valid"] else 1
    except ValidationInputError as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        return 2


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
