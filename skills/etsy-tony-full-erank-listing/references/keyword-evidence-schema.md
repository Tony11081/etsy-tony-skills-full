# Keyword Evidence Schema

## Canonical package

```json
{
  "source": {
    "kind": "erank-member-export",
    "market": "US",
    "fetched_at": "2026-07-28T00:00:00Z",
    "authoritative_member_data": true,
    "input_file": "member-keywords.csv"
  },
  "keywords": [
    {
      "phrase": "wood frame rocker",
      "average_searches": 0.0,
      "average_clicks": 0.0,
      "ctr": 0.0,
      "competition": 0.0,
      "trend": null,
      "intent": "product",
      "search_stage": "consideration",
      "product_relevance": "high",
      "fact_supported": true,
      "evidence_status": "ERANK_MEMBER_VERIFIED",
      "raw": {}
    }
  ]
}
```

## Authoritative sources

Accept keyword metrics as member evidence only when the source is explicitly one of:

- `erank-member`
- `erank-member-export`
- `erank-member-browser`
- `erank-member-browser-api`

Reject `local_proxy`, `sample`, `synthetic`, `alura-public`, public Top Sellers samples, competitor frequency, and unlabeled rows as authoritative keyword metrics.

## Required provenance

- Preserve `market`; default to `US` only when the user requested the US market.
- Preserve a parseable `fetched_at` timestamp.
- Preserve the input filename, member export label, and non-sensitive endpoint or page label when available.
- Never store browser cookies, storage, passwords, OAuth tokens, CSRF data, or authentication headers.

## Metric aliases

The normalizer may map common export headers:

- phrase: `keyword`, `term`, `phrase`, `tag`, `query`
- searches: `average searches`, `avg searches`, `avg_searches`, `search volume`, `search_volume`
- clicks: `average clicks`, `avg clicks`, `avg_clicks`, `clicks`
- CTR: `average ctr`, `avg ctr`, `ctr`, `click through rate`
- competition: `etsy competition`, `competition`, `competing listings`, `results`
- trend: `trend`, `trend score`, `growth`

Do not silently turn missing metrics into claimed zero demand. Preserve missing metrics as `null` and report coverage.

## Evidence states

- `ERANK_MEMBER_VERIFIED`: exact member keyword row.
- `ERANK_MEMBER_DERIVED`: phrase assembled from verified component terms; never report an exact search metric for the assembled phrase.
- `SHOP_STATS_VERIFIED`: first-party Etsy search-query evidence.
- `COMPETITOR_OBSERVED`: observed in competitor listings or tags; not demand proof.
- `GEMINI_HYPOTHESIS`: semantic suggestion awaiting research.
- `SEMANTIC_COVERAGE`: accurate final phrase used to diversify query coverage without a direct metric.
- `REJECTED`: inaccurate, risky, redundant, or otherwise unsuitable.

## Freshness

Report data age. Treat freshness as configurable rather than as a universal Etsy rule. Default guidance:

- Keyword Tool averages: refresh within 45 days for active optimization.
- Trend Buzz: refresh within 7 days for time-sensitive decisions.
- Rank Checker and Shop Stats baseline: capture on the day of a planned change.

Mark stale evidence `PARTIAL`; do not silently present it as current.
