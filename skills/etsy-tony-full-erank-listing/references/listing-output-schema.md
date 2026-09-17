# Listing Package Output Schema

Return valid JSON with this top-level shape:

```json
{
  "status": "PARTIAL",
  "product_truth": {},
  "information_to_confirm": [],
  "search_intent_map": [],
  "keyword_portfolio": {},
  "rejected_keywords": [],
  "listing": {
    "recommended_title": "",
    "alternate_titles": ["", ""],
    "tags": [""],
    "tag_evidence": [],
    "description_opening": ["", "", ""],
    "full_description": "",
    "category_attribute_advice": [],
    "visual_advice": []
  },
  "quality_review": {
    "issues": [],
    "warnings": [],
    "member_listing_audit_complete": false
  },
  "measurement_plan": [],
  "assumptions": [],
  "provenance": {}
}
```

## Listing requirements

- Return one recommended title and exactly two alternatives.
- Keep all titles distinct and at or below 140 characters.
- Return exactly 13 distinct English tags, each at or below 20 characters.
- Return one `tag_evidence` object per tag with `tag`, `evidence_status`, `matched_keyword`, `intent`, and `rationale`.
- Return exactly three non-empty, product-specific description opening lines and place those same lines at the start of `full_description`.
- Return a complete, ready-to-paste English description rather than an excerpt or template fragment.
- Prefix every required description section heading with a relevant icon and vary the icons across sections.
- Do not reuse generic stock introductions or the prohibited cake-topper boilerplate in the Etsy rules.
- Keep analysis, reasoning, warnings, assumptions, and confirmation questions in Chinese unless the user requests another language.
- Keep Etsy-facing title, tags, description, personalization fields, and bullets in English unless the user requests another shop language.

## Provenance requirements

Include:

- Gemini provider, requested model, returned model, and generation attempts for each stage;
- eRank source kind, market, fetched timestamp, and evidence coverage;
- validator errors and warnings;
- member Listing Audit and Rank Checker state when requested.

Do not expose secrets or browser authentication data.

## Status decision

- Use `VERIFIED_SUCCESS` only after authoritative member evidence, deterministic validation, and all requested independent audits/readbacks are complete.
- Use `PARTIAL` when the copy passes validation but a member audit, rank baseline, freshness target, evidence mapping, or requested readback remains incomplete.
- Use `BLOCKED` when data-backed SEO cannot proceed without member evidence or a material product fact.
- Use `UNVERIFIED` for hypothesis/proxy/sample-only work.
- Use `FAILED` for an execution, schema, or validation failure.
