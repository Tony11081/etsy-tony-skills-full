#!/usr/bin/env python3
"""Run Etsy listing optimization through the required Clawlist Gemini API."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any
from urllib import error, request


BASE_URL = "https://clawlist.best/v1"
CHAT_URL = f"{BASE_URL}/chat/completions"
DEFAULT_MODEL = "gemini-3.1-pro-preview"
API_KEY_ENV = "CLAWLIST_API_KEY"
MODEL_ENV = "ETSY_LISTING_GEMINI_MODEL"
TRANSIENT_HTTP_CODES = {429, 500, 502, 503, 504}
MAX_IMAGES = 6
MAX_IMAGE_BYTES = 12 * 1024 * 1024
HANDBOOK_KB_PATH = (
    Path(__file__).resolve().parent.parent
    / "references"
    / "etsy-seller-handbook-kb"
    / "etsy_seller_handbook_kb.sqlite"
)
HANDBOOK_KB_SNAPSHOT = "2026-07-29"
HANDBOOK_KB_EXPECTED_DOCUMENTS = 945
MAX_HANDBOOK_HITS = 8
GENERIC_OPENING_PATTERNS = (
    r"^\s*add\b.*\btouch\b",
    r"^\s*add\s+(?:instant\s+|modern\s+|timeless\s+)?elegance\b",
    r"^\s*elevate\b",
    r"^\s*make\s+your\b",
    r"^\s*perfect\s+for\b",
)
DESCRIPTION_SECTION_ICONS = (
    "✨",
    "💍",
    "📐",
    "📏",
    "🎂",
    "🍰",
    "📦",
    "🚚",
    "⚠️",
    "📝",
    "🎁",
    "✅",
    "📌",
)
DESCRIPTION_PLACEHOLDER_TERMS = (
    "unknown",
    "to be confirmed",
    "not specified",
    "not provided",
)
CARE_COPY_TERMS = (
    "care instructions",
    "clean with",
    "wipe with",
    "wash with",
    "damp cloth",
    "soft cloth",
    "dishwasher",
    "handle with care",
)
QUALITY_COPY_TERMS = (
    "premium",
    "high quality",
    "high-quality",
    "durable",
    "long lasting",
    "long-lasting",
    "reusable",
    "keepsake",
)
MOUNTING_PERFORMANCE_TERMS = (
    "secure mounting",
    "securely",
    "stable",
    "sturdy",
    "invisible",
    "seamless",
    "floating",
    "effortlessly",
    "attached to each",
    "pre-attached",
    "ready to insert",
    "arrive ready",
)
OCCASION_AND_USE_TERMS = (
    "wedding",
    "bridal shower",
    "reception",
    "anniversary",
    "engagement",
    "birthday",
    "baby shower",
    "graduation",
    "christmas",
    "halloween",
    "valentine",
    "mother's day",
    "father's day",
    "dessert",
    "centerpiece",
)
TITLE_TOKEN_STOPWORDS = {
    "and",
    "for",
    "from",
    "the",
    "this",
    "with",
    "your",
}
COMPETITOR_SCORE_MAX = {
    "core_product": 30,
    "buyer_need": 20,
    "structure_or_mounting": 15,
    "personalization_or_variant": 15,
    "material_or_process": 10,
    "style_or_use_case": 10,
}
QUERY_STOPWORDS = {
    "and",
    "are",
    "description",
    "etsy",
    "for",
    "from",
    "listing",
    "product",
    "tags",
    "that",
    "the",
    "this",
    "title",
    "with",
    "your",
}
CHINESE_QUERY_TERMS = (
    "摄影",
    "图片",
    "搜索",
    "关键词",
    "标签",
    "排名",
    "流量",
    "物流",
    "运费",
    "发货",
    "品牌",
    "营销",
    "广告",
    "法律",
    "合规",
    "政策",
    "知识产权",
    "产品安全",
    "定价",
    "税务",
    "财务",
    "利润",
    "成本",
    "效率",
    "增长",
    "社区",
    "季节",
    "节日",
    "趋势",
    "更新",
)
INITIALIZATION_MESSAGE = (
    "我是你的 Etsy 运营专家。请发送你的产品信息（标题、图片描述、标签、价格等），"
    "我准备好为你诊断了。"
)


class OptimizerError(RuntimeError):
    """A safe user-facing optimizer failure."""


def resolve_setting(name: str) -> tuple[str | None, str]:
    value = os.environ.get(name)
    if value:
        return value.strip(), "process_environment"
    if os.name != "nt":
        return None, "missing"
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, name)
        resolved = str(value).strip() or None
        return resolved, "windows_user_environment" if resolved else "missing"
    except (FileNotFoundError, OSError):
        return None, "missing"


def read_user_environment(name: str) -> str | None:
    return resolve_setting(name)[0]


def validate_competitor_evidence(request_data: dict[str, Any]) -> list[str]:
    product = request_data.get("product")
    if not isinstance(product, dict) or "competitor_evidence" not in product:
        return []
    evidence = product.get("competitor_evidence")
    if not isinstance(evidence, list):
        raise OptimizerError("product.competitor_evidence must be an array.")
    if not evidence:
        return []

    core_titles: list[str] = []
    seen_urls: set[str] = set()
    for index, item in enumerate(evidence, 1):
        prefix = f"product.competitor_evidence[{index}]"
        if not isinstance(item, dict):
            raise OptimizerError(f"{prefix} must be an object.")

        for key in ("url", "title", "accessed_at"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise OptimizerError(f"{prefix}.{key} must be a non-empty string.")
        url = item["url"].strip()
        if not re.match(r"^https://(?:www\.)?etsy\.com/(?:[a-z-]+/)?listing/\d+", url, re.I):
            raise OptimizerError(f"{prefix}.url must be a public Etsy listing URL.")
        normalized_url = url.casefold().rstrip("/")
        if normalized_url in seen_urls:
            raise OptimizerError("competitor_evidence must not contain duplicate listing URLs.")
        seen_urls.add(normalized_url)

        hard_gate = item.get("hard_gate")
        if not isinstance(hard_gate, dict) or set(hard_gate) != {
            "same_core_product",
            "same_primary_buyer_need",
        }:
            raise OptimizerError(
                f"{prefix}.hard_gate must contain same_core_product and "
                "same_primary_buyer_need."
            )
        if hard_gate["same_core_product"] is not True or hard_gate["same_primary_buyer_need"] is not True:
            raise OptimizerError(f"{prefix} failed the mandatory competitor hard gate.")

        breakdown = item.get("score_breakdown")
        if not isinstance(breakdown, dict) or set(breakdown) != set(COMPETITOR_SCORE_MAX):
            raise OptimizerError(f"{prefix}.score_breakdown must contain the six required dimensions.")
        for key, maximum in COMPETITOR_SCORE_MAX.items():
            value = breakdown[key]
            if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= maximum:
                raise OptimizerError(f"{prefix}.score_breakdown.{key} must be from 0 to {maximum}.")
        score = item.get("match_score")
        if not isinstance(score, int) or isinstance(score, bool) or score != sum(breakdown.values()):
            raise OptimizerError(f"{prefix}.match_score must equal its score_breakdown total.")

        tier = item.get("tier")
        if tier == "core" and 80 <= score <= 100:
            core_titles.append(item["title"].strip())
        elif tier == "adjacent" and 60 <= score <= 79:
            pass
        else:
            raise OptimizerError(
                f"{prefix}.tier must be core for scores 80-100 or adjacent for scores 60-79."
            )

        match_reasons = item.get("match_reasons")
        mismatches = item.get("mismatches")
        if not isinstance(match_reasons, list) or not match_reasons or not all(
            isinstance(value, str) and value.strip() for value in match_reasons
        ):
            raise OptimizerError(f"{prefix}.match_reasons must be a non-empty string array.")
        if not isinstance(mismatches, list) or not all(
            isinstance(value, str) and value.strip() for value in mismatches
        ):
            raise OptimizerError(f"{prefix}.mismatches must be a string array.")

    if not 3 <= len(core_titles) <= 5:
        raise OptimizerError("competitor_evidence must contain 3-5 core competitors.")
    return core_titles


def load_request(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    if not raw:
        return {"task": "initialize", "product": {}, "confirmed_claims": [], "images": []}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "task": "standard_diagnosis",
            "product": raw,
            "confirmed_claims": [],
            "images": [],
        }
    if isinstance(parsed, str):
        return {
            "task": "standard_diagnosis",
            "product": parsed,
            "confirmed_claims": [],
            "images": [],
        }
    if not isinstance(parsed, dict):
        raise OptimizerError("Input must be a JSON object, JSON string, or plain text.")
    result = dict(parsed)
    result.setdefault("task", "standard_diagnosis")
    result.setdefault("product", {})
    result.setdefault("confirmed_claims", [])
    result.setdefault("images", [])
    if result["task"] not in {"initialize", "standard_diagnosis", "full_description"}:
        raise OptimizerError("task must be initialize, standard_diagnosis, or full_description.")
    if not isinstance(result["confirmed_claims"], list):
        raise OptimizerError("confirmed_claims must be an array.")
    if not isinstance(result["images"], list):
        raise OptimizerError("images must be an array.")
    return result


def image_url(value: str) -> dict[str, Any]:
    if value.startswith(("https://", "http://", "data:image/")):
        url = value
    else:
        path = Path(value).expanduser().resolve()
        if not path.is_file():
            raise OptimizerError(f"Image not found: {path}")
        size = path.stat().st_size
        if size > MAX_IMAGE_BYTES:
            raise OptimizerError(f"Image exceeds {MAX_IMAGE_BYTES // (1024 * 1024)} MB: {path.name}")
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if not mime.startswith("image/"):
            raise OptimizerError(f"Unsupported image type: {path.name}")
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        url = f"data:{mime};base64,{encoded}"
    return {"type": "image_url", "image_url": {"url": url}}


def load_rules() -> str:
    path = Path(__file__).resolve().parent.parent / "references" / "etsy-listing-rules.md"
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise OptimizerError(f"Unable to load Etsy rules: {exc}") from exc


def iter_query_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_query_strings(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from iter_query_strings(item)


def handbook_query_tokens(request_data: dict[str, Any]) -> list[str]:
    text = " ".join(
        iter_query_strings(
            [request_data.get("product", {}), request_data.get("confirmed_claims", [])]
        )
    ).casefold()
    candidates = re.findall(r"[a-z0-9][a-z0-9'-]{1,}", text)
    candidates.extend(term for term in CHINESE_QUERY_TERMS if term in text)
    tokens: list[str] = []
    for token in candidates:
        if token in QUERY_STOPWORDS or token in tokens:
            continue
        tokens.append(token)
        if len(tokens) == 24:
            break
    return tokens


def search_handbook(
    conn: sqlite3.Connection, tokens: list[str], limit: int
) -> list[sqlite3.Row]:
    if not tokens:
        return []
    query = " OR ".join(f'"{token.replace(chr(34), chr(34) * 2)}"' for token in tokens)
    return conn.execute(
        """
        SELECT a.id, a.title, a.url, a.summary, a.author, a.published_date,
               a.categories_json, a.metadata_status, bm25(articles_fts) AS score
        FROM articles_fts
        JOIN articles a ON a.id = articles_fts.id
        WHERE articles_fts MATCH ?
        ORDER BY score
        LIMIT ?
        """,
        (query, limit),
    ).fetchall()


def load_handbook_context(
    request_data: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    if request_data["task"] == "initialize":
        return "", {
            "loaded": False,
            "snapshot": HANDBOOK_KB_SNAPSHOT,
            "documents": 0,
            "hits": [],
        }
    if not HANDBOOK_KB_PATH.is_file():
        raise OptimizerError(f"Etsy Seller Handbook knowledge base not found: {HANDBOOK_KB_PATH}")

    try:
        uri = HANDBOOK_KB_PATH.resolve().as_uri() + "?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
        document_count = conn.execute("SELECT count(*) FROM articles").fetchone()[0]
        if document_count != HANDBOOK_KB_EXPECTED_DOCUMENTS:
            raise OptimizerError(
                "Etsy Seller Handbook knowledge base count mismatch: "
                f"expected {HANDBOOK_KB_EXPECTED_DOCUMENTS}, got {document_count}."
            )
        contextual = search_handbook(conn, handbook_query_tokens(request_data), 6)
        baseline = search_handbook(
            conn, ["etsy", "search", "listing", "title", "tags", "description"], 5
        )
        conn.close()
    except sqlite3.Error as exc:
        raise OptimizerError(f"Unable to query Etsy Seller Handbook knowledge base: {exc}") from exc

    hits: list[sqlite3.Row] = []
    seen: set[str] = set()
    for row in [*contextual, *baseline]:
        if row["id"] in seen:
            continue
        seen.add(row["id"])
        hits.append(row)
        if len(hits) == MAX_HANDBOOK_HITS:
            break
    if not hits:
        raise OptimizerError("Etsy Seller Handbook knowledge base returned no reference hits.")

    lines = [
        f"Snapshot: {HANDBOOK_KB_SNAPSHOT}; documents: {document_count}.",
        "These are official index summaries and URLs, not complete article bodies.",
    ]
    hit_metadata = []
    for index, row in enumerate(hits, 1):
        categories = json.loads(row["categories_json"])
        lines.extend(
            [
                f"{index}. {row['title']}",
                f"Summary: {row['summary'] or 'Not shown in the source index.'}",
                f"Categories: {'; '.join(categories) or 'Not categorized'}",
                f"Author/date: {row['author'] or 'Not shown'} / "
                f"{row['published_date'] or 'Not shown'}",
                f"Official URL: {row['url']}",
                f"Evidence: {row['metadata_status']}",
            ]
        )
        hit_metadata.append(
            {
                "id": row["id"],
                "title": row["title"],
                "url": row["url"],
                "categories": categories,
                "metadata_status": row["metadata_status"],
            }
        )
    return "\n".join(lines), {
        "loaded": True,
        "snapshot": HANDBOOK_KB_SNAPSHOT,
        "documents": document_count,
        "hits": hit_metadata,
    }


def system_prompt(task: str, handbook_context: str = "") -> str:
    if task == "initialize":
        return (
            "Return valid compact JSON only with one key, initialization_message. "
            f"Its value must be exactly: {INITIALIZATION_MESSAGE}"
        )

    full_description_rule = (
        "full_description must contain a complete Etsy-ready English description with 4-7 "
        "distinct relevant icon-led section headers. Omit unknown fields entirely."
        if task == "full_description"
        else "full_description must be null."
    )
    return f"""
Act as a senior Etsy operator and SEO/CRO strategist. Follow the rules below.
All diagnosis and strategy prose must be Chinese. All Etsy-facing assets must be English.
Use only supplied facts. Never invent measurements, materials, mechanisms, certifications,
production methods, shipping facts, or market data. Treat confirmed_claims as the only explicit
authorization for risky claims. Do not claim access to Etsy private ranking internals.

Return valid compact JSON only, without Markdown fences, using exactly this shape:
{{
  "title_seo_diagnosis": {{"score": 1, "findings": ["Chinese"]}},
  "optimized_titles": ["English", "English", "English"],
  "tags": ["English tag"],
  "visual_advice": ["Chinese"],
  "description_cro_diagnosis": {{"score": 1, "findings": ["Chinese"]}},
  "description_opening": ["English", "English", "English"],
  "full_description": null,
  "competitive_strategy": ["Chinese"],
  "information_to_confirm": ["Chinese"],
  "assumptions": ["Chinese"]
}}

Requirements:
- Return exactly 3 distinct optimized_titles, each no more than 140 characters.
- Use only product.competitor_evidence records marked tier `core`, scored 80-100, and passing both
  hard-gate fields as title sources. Adjacent records may inform positioning but must not supply
  title language or be presented as exact-competitor evidence. Build every optimized title by
  recombining accurate language represented in at least 2 core competitor titles plus seller_facts.
  Never copy, reorder, or lightly repunctuate a complete competitor title. Put a repeated core
  product phrase and a confirmed differentiator early, and keep the result natural.
- Return exactly 13 distinct tags, each no more than 20 characters.
- Return exactly 3 description_opening lines.
- Make the first description_opening line product-specific. Never start with a generic
  `Add ... touch`, `Add elegance`, `Elevate`, `Make your`, or `Perfect for` formula.
- Scores must be integers from 1 to 10.
- visual_advice, competitive_strategy, information_to_confirm, and assumptions must be arrays.
- {full_description_rule}
- For a full description, use the 3 opening lines at the start, use icons on section headers
  rather than every bullet, and never include square-bracket placeholders, `Unknown`,
  `To be confirmed`, `Not specified`, or `Not provided` in customer-facing copy.
- Mention occasions, options, materials, effects, care, safety, and mounting performance only
  when seller_facts or confirmed_claims explicitly support them. Competitor evidence supplies
  market language, not product authorization.
- Treat absent seller_facts as absent product claims: never fill missing care instructions,
  packaged weight, assembly state, stake attachment, durability, quality, or product readiness.
  Avoid unsupported words such as premium, durable, secure, invisible, seamless, floating,
  pre-attached, ready to insert, and will arrive ready.
- If images are not supplied, clearly base visual advice on the written product facts.

ETSY RULES:
{load_rules()}

ETSY SELLER HANDBOOK KNOWLEDGE BASE HITS:
{handbook_context}

Use relevant handbook guidance as reference evidence, but do not turn general guidance into
unsupported product facts, keyword metrics, ranking guarantees, or market-demand claims.
The knowledge base contains index summaries, not full article bodies. For policy-sensitive,
legal, tax, fee, product-safety, or current-platform claims, state when the official URL
must be checked live before the seller acts.
""".strip()


def user_content(request_data: dict[str, Any]) -> str | list[dict[str, Any]]:
    safe_data = dict(request_data)
    images = safe_data.get("images", [])
    safe_data["images"] = [f"image_{index + 1}" for index, _ in enumerate(images)]
    text = "Optimize this Etsy request:\n" + json.dumps(safe_data, ensure_ascii=False, indent=2)
    if not images:
        return text
    if len(images) > MAX_IMAGES:
        raise OptimizerError(f"At most {MAX_IMAGES} images are supported per request.")
    content: list[dict[str, Any]] = [{"type": "text", "text": text}]
    content.extend(image_url(str(item)) for item in images)
    return content


def call_api(
    api_key: str,
    model: str,
    messages: list[dict[str, Any]],
    timeout: int,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.15,
        "max_tokens": 8000,
        "response_format": {"type": "json_object"},
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    last_error = "unknown API failure"
    for attempt in range(1, 3):
        req = request.Request(
            CHAT_URL,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "etsy-tony-full-listing/1.0",
            },
        )
        try:
            with request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read(1200).decode("utf-8", errors="replace")
            detail = detail.replace(api_key, "[REDACTED]")
            last_error = f"Clawlist HTTP {exc.code}: {detail}"
            if exc.code not in TRANSIENT_HTTP_CODES or attempt == 2:
                break
        except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = f"Clawlist request failed: {exc}"
            if attempt == 2:
                break
        time.sleep(2 ** (attempt - 1))
    raise OptimizerError(last_error)


def extract_content(response_data: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    try:
        choice = response_data["choices"][0]
        content = choice["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise OptimizerError("Clawlist returned an unexpected response shape.") from exc
    if not isinstance(content, str) or not content.strip():
        raise OptimizerError("Clawlist returned empty model content.")
    metadata = {
        "returned_model": response_data.get("model"),
        "finish_reason": choice.get("finish_reason"),
        "usage": response_data.get("usage"),
    }
    return content, metadata


def parse_json_content(content: str) -> dict[str, Any]:
    clean = content.strip()
    clean = re.sub(r"^```(?:json)?\s*", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\s*```$", "", clean)
    try:
        parsed = json.loads(clean)
    except json.JSONDecodeError as exc:
        raise OptimizerError(f"Gemini returned invalid or truncated JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise OptimizerError("Gemini JSON must be an object.")
    return parsed


def require_string_list(data: dict[str, Any], key: str, count: int | None = None) -> list[str]:
    value = data.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise OptimizerError(f"{key} must be an array of non-empty strings.")
    if count is not None and len(value) != count:
        raise OptimizerError(f"{key} must contain exactly {count} items; got {len(value)}.")
    return [item.strip() for item in value]


def validate_diagnosis(data: dict[str, Any], key: str) -> None:
    value = data.get(key)
    if not isinstance(value, dict):
        raise OptimizerError(f"{key} must be an object.")
    score = value.get("score")
    if not isinstance(score, int) or isinstance(score, bool) or not 1 <= score <= 10:
        raise OptimizerError(f"{key}.score must be an integer from 1 to 10.")
    findings = value.get("findings")
    if not isinstance(findings, list) or not all(isinstance(item, str) and item.strip() for item in findings):
        raise OptimizerError(f"{key}.findings must be an array of non-empty strings.")


def validate_listing(data: dict[str, Any], request_data: dict[str, Any]) -> None:
    validate_diagnosis(data, "title_seo_diagnosis")
    validate_diagnosis(data, "description_cro_diagnosis")
    titles = require_string_list(data, "optimized_titles", 3)
    tags = require_string_list(data, "tags", 13)
    opening = require_string_list(data, "description_opening", 3)
    for key in ("visual_advice", "competitive_strategy", "information_to_confirm", "assumptions"):
        require_string_list(data, key)

    product = request_data.get("product")
    product = product if isinstance(product, dict) else {}
    competitor_titles = validate_competitor_evidence(request_data)

    if len({item.casefold() for item in titles}) != 3:
        raise OptimizerError("optimized_titles must be distinct.")
    if any(len(item) > 140 for item in titles):
        raise OptimizerError("Every optimized title must be 140 characters or fewer.")
    if len(competitor_titles) >= 2:
        normalized_sources = {
            re.sub(r"[^a-z0-9]+", " ", item.casefold()).strip() for item in competitor_titles
        }
        source_tokens = [
            {
                token
                for token in re.findall(r"[a-z0-9]+", item.casefold())
                if len(token) >= 3 and token not in TITLE_TOKEN_STOPWORDS
            }
            for item in competitor_titles
        ]
        for title in titles:
            normalized_title = re.sub(r"[^a-z0-9]+", " ", title.casefold()).strip()
            if normalized_title in normalized_sources:
                raise OptimizerError("optimized_titles must not copy a complete competitor title.")
            generated_tokens = {
                token
                for token in re.findall(r"[a-z0-9]+", title.casefold())
                if len(token) >= 3 and token not in TITLE_TOKEN_STOPWORDS
            }
            matched_sources = sum(
                1 for tokens in source_tokens if len(generated_tokens & tokens) >= 2
            )
            source_union = set().union(*source_tokens)
            if matched_sources < 2 or len(generated_tokens & source_union) < 3:
                raise OptimizerError(
                    "Each optimized title must synthesize language from at least two competitor titles."
                )
    if len({item.casefold() for item in tags}) != 13:
        raise OptimizerError("tags must be distinct.")
    if any(len(item) > 20 for item in tags):
        raise OptimizerError("Every tag must be 20 characters or fewer.")
    if any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 '\-]*", item) for item in tags):
        raise OptimizerError("Tags may only use English letters, numbers, spaces, apostrophes, and hyphens.")

    task = request_data["task"]
    description = data.get("full_description")
    opening_first = opening[0].strip()
    if any(re.search(pattern, opening_first, flags=re.IGNORECASE) for pattern in GENERIC_OPENING_PATTERNS):
        raise OptimizerError("description_opening uses a prohibited boilerplate opening.")
    if task == "full_description":
        if not isinstance(description, str) or not description.strip():
            raise OptimizerError("full_description is required for task full_description.")
        clean_description = description.strip()
        if not clean_description.startswith(opening_first):
            raise OptimizerError("full_description must start with description_opening line 1.")
        if "[" in clean_description or "]" in clean_description:
            raise OptimizerError("full_description must not contain square-bracket placeholders.")
        lowered_description = clean_description.casefold()
        if any(term in lowered_description for term in DESCRIPTION_PLACEHOLDER_TERMS):
            raise OptimizerError("full_description must omit unknown fields instead of describing them.")
        distinct_icons = {icon for icon in DESCRIPTION_SECTION_ICONS if icon in clean_description}
        if len(distinct_icons) < 4:
            raise OptimizerError("full_description must contain at least 4 distinct relevant section icons.")

        seller_facts = product.get("seller_facts")
        seller_facts = seller_facts if isinstance(seller_facts, dict) else {}
        supplied_title = str(product.get("supplied_title", ""))
        authorized_text = " ".join(
            [
                supplied_title,
                json.dumps(seller_facts, ensure_ascii=False),
                " ".join(str(item) for item in request_data["confirmed_claims"]),
            ]
        ).casefold()

        def has_supplied_fact(*keys: str) -> bool:
            for key in keys:
                value = seller_facts.get(key)
                if value is None:
                    continue
                text = str(value).strip().casefold()
                if text and not any(term in text for term in DESCRIPTION_PLACEHOLDER_TERMS):
                    return True
            return False

        semantic_errors: list[str] = []
        if not has_supplied_fact("care", "care_instructions") and any(
            term in lowered_description for term in CARE_COPY_TERMS
        ):
            semantic_errors.append("care instructions not supplied by the seller")
        if not has_supplied_fact("packaged_weight", "packaged_shipping_weight") and (
            "packaged weight" in lowered_description or "shipping weight" in lowered_description
        ):
            semantic_errors.append("packaged weight not supplied by the seller")

        for term in QUALITY_COPY_TERMS:
            if term in lowered_description and term not in authorized_text:
                semantic_errors.append(f"unconfirmed quality claim: {term}")
        for term in MOUNTING_PERFORMANCE_TERMS:
            if term in lowered_description and term not in authorized_text:
                semantic_errors.append(f"unconfirmed mounting or readiness claim: {term}")
        for term in OCCASION_AND_USE_TERMS:
            if term in lowered_description and term not in authorized_text:
                semantic_errors.append(f"unconfirmed occasion or use: {term}")
        if semantic_errors:
            raise OptimizerError(
                "full_description semantic validation failed: " + "; ".join(semantic_errors) + "."
            )
    elif description not in (None, ""):
        raise OptimizerError("full_description must be null for a standard diagnosis.")

    confirmed = " ".join(str(item).casefold() for item in request_data["confirmed_claims"])
    listing_text = " ".join(titles + tags + opening + ([description] if isinstance(description, str) else []))
    risky_claims = {
        "glider": ("glider", "gliding mechanism"),
        "solid wood": ("solid wood",),
        "handmade": ("handmade", "handcrafted", "hand crafted"),
        "orthopedic": ("orthopedic", "orthopaedic"),
        "waterproof": ("waterproof",),
        "leather": ("leather",),
        "stainless steel": ("stainless steel", "stainless"),
        "sterling silver": ("sterling silver", "pure silver"),
    }
    lowered = listing_text.casefold()
    for claim, terms in risky_claims.items():
        if claim not in confirmed and any(re.search(rf"\b{re.escape(term)}\b", lowered) for term in terms):
            raise OptimizerError(f"Unconfirmed risky claim appeared in listing copy: {claim}.")


def validate_result(data: dict[str, Any], request_data: dict[str, Any]) -> None:
    if request_data["task"] == "initialize":
        if data.get("initialization_message") != INITIALIZATION_MESSAGE:
            raise OptimizerError("Initialization message did not match the required text.")
        return
    validate_listing(data, request_data)


def run_optimizer(request_data: dict[str, Any], api_key: str, model: str, timeout: int) -> dict[str, Any]:
    if request_data["task"] != "initialize":
        validate_competitor_evidence(request_data)
    handbook_context, handbook_metadata = load_handbook_context(request_data)
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": system_prompt(request_data["task"], handbook_context),
        },
        {"role": "user", "content": user_content(request_data)},
    ]
    last_error = "validation failed"
    last_metadata: dict[str, Any] = {}
    for generation_attempt in range(1, 4):
        response_data = call_api(api_key, model, messages, timeout)
        content, last_metadata = extract_content(response_data)
        try:
            result = parse_json_content(content)
            validate_result(result, request_data)
            result["_meta"] = {
                "provider": "Clawlist",
                "endpoint": CHAT_URL,
                "requested_model": model,
                "validated": True,
                "generation_attempts": generation_attempt,
                "seller_handbook_knowledge_base": handbook_metadata,
                **last_metadata,
            }
            return result
        except OptimizerError as exc:
            last_error = str(exc)
            if generation_attempt == 3:
                break
            messages.extend(
                [
                    {"role": "assistant", "content": content},
                    {
                        "role": "user",
                        "content": (
                            f"Validation failed: {last_error} Return a complete corrected JSON object only. "
                            "Preserve accurate content while fixing every stated validation error."
                        ),
                    },
                ]
            )
    finish = last_metadata.get("finish_reason")
    raise OptimizerError(f"Gemini output failed validation after 3 attempts: {last_error}; finish_reason={finish}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Optimize Etsy listings through the mandatory Clawlist Gemini API."
    )
    parser.add_argument("--input", type=Path, help="UTF-8 JSON or plain-text request file; defaults to stdin.")
    parser.add_argument("--output", type=Path, help="Write validated UTF-8 JSON here instead of stdout.")
    parser.add_argument("--model", help=f"Gemini model on Clawlist; default: {DEFAULT_MODEL}.")
    parser.add_argument("--timeout", type=int, default=120, help="Per-request timeout in seconds.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.input:
            raw = args.input.read_text(encoding="utf-8-sig")
        else:
            raw = sys.stdin.read()
        request_data = load_request(raw)
        api_key, credential_source = resolve_setting(API_KEY_ENV)
        if not api_key:
            raise OptimizerError(
                f"{API_KEY_ENV} is not configured. The skill cannot fall back to another provider."
            )
        configured_model, _ = resolve_setting(MODEL_ENV)
        model = args.model or configured_model or DEFAULT_MODEL
        if "gemini" not in model.casefold():
            raise OptimizerError("Only Gemini models on the configured Clawlist endpoint are allowed.")
        if args.timeout < 10 or args.timeout > 600:
            raise OptimizerError("timeout must be between 10 and 600 seconds.")
        result = run_optimizer(request_data, api_key, model, args.timeout)
        result["_meta"]["credential_source"] = credential_source
        result["_meta"]["knowledge_base_loaded"] = request_data["task"] != "initialize"
        result["_meta"]["knowledge_base"] = (
            "references/etsy-listing-rules.md" if request_data["task"] != "initialize" else None
        )
        result["_meta"]["reference_knowledge_base"] = (
            "references/etsy-seller-handbook-kb/etsy_seller_handbook_kb.sqlite"
            if request_data["task"] != "initialize"
            else None
        )
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 0
    except (OptimizerError, OSError) as exc:
        message = str(exc)
        key = read_user_environment(API_KEY_ENV)
        if key:
            message = message.replace(key, "[REDACTED]")
        sys.stderr.write(f"ERROR: {message}\n")
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
