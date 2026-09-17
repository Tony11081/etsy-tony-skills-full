# eRank CLI-Anything Harness

Target: `erank.com`

This harness implements an eRank-like command surface for Etsy SEO and shop research workflows. eRank does not publish a documented public developer API. The harness uses local exports, Etsy Open API v3 when configured, and bounded read-only probes of selected eRank web endpoints; complete member-only coverage still requires the logged-in browser or a member export.

## Backend Strategy

- Local CSV/JSON is the default backend for repeatable analysis.
- `live source-probe` records the current public/sample/member boundary without reading browser credentials.
- `live shop-search` validates lifetime-sales scope, exact shop age, evidence freshness, and coverage before declaring a match.
- `live member-plan|member-ingest|evidence-check` provides resumable member-page ingestion, rejects credential fields, and proves freshness and coverage before downstream alerts.
- `live shop-info|shop-listings|shop-tags` restores the current read-only Shop Info route contract while clearly labeling empty public listing samples.
- Etsy Open API v3 is optional for live shop/listing lookups.
- eRank private estimates such as search volume, clicks, CTR, and keyword difficulty are represented as transparent local proxies unless imported from an external data file.
- Mutating Etsy/eRank data is not implemented. This harness is read-only except for local state such as keyword lists, snapshots, and config.

## Main Command Groups

- `keyword`: keyword tool, compare keywords, bulk keyword analysis, keyword lists.
- `rank`: rank checker and bulk rank checks.
- `competitor`: competitor tags, listings, sales estimates, top sellers, shop info, product-family clusters.
- `listing`: listing audit, compare listings, draft audit, change tracking/impact, CRO checks, fact-gated drafts.
- `shop`: health check, tag report, sales map, delivery status, spotted checks, spell check, traffic stats, anomalies, watchlist alerts.
- `tools`: shortcut URLs, calendar reminders, ROI/profit calculators, true-profit/capacity gates, category suggestions.
- `trends`: trend buzz, monthly imports, and seasonal launch planning.
- `selection`: breakout shops, opportunity scoring, cross-market validation, and daily/sales/furniture reports.
- `data`: local CSV/JSON summaries and sample export.
- `config`: local Etsy API/profile configuration.

## Private Decision Layer

The harness adds seller-specific intelligence that eRank cannot derive without private operating data:

- breakout-shop growth snapshots and deduplicated watchlist alerts;
- product-family clustering, listing-change impact, keyword cannibalization, and image/CRO evidence checks;
- landed cost, labor, returns, breakage, capacity, margin, and pricing-formula gates;
- opportunity scoring, cross-market consensus, seasonal planning, and fact-gated review-only drafts with exactly 13 tags;
- anomaly detection for duplicates, decreases, implausible values, spikes, and schema drift.

## API Findings

Current public evidence indicates:

- eRank pages say the application uses Etsy API.
- eRank GitHub only exposes a forked Etsy API v3 PHP SDK.
- eRank feature pages and help pages expose product functionality, not public API documentation.
- Etsy Open API v3 is the official supported API for shop, listing, order, and inventory workflows.
