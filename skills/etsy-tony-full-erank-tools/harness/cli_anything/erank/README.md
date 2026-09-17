# CLI-Anything eRank Harness

This is a local, read-only eRank-like CLI for Etsy SEO research, listing audits, competitor analysis, shop health checks, trend imports, and calculators.

It uses read-only local exports, Etsy Open API v3 when configured, and selected undocumented eRank web endpoints. The latter are probed at runtime, may be server-limited or require the logged-in member browser, and are never treated as an official public API.

## Install

```powershell
cd erank\agent-harness
python -m pip install -e .
```

## Quick Start

Create sample data:

```powershell
python -m cli_anything.erank --json data sample exports\sample-listings.csv
```

Run an eRank-style keyword report:

```powershell
python -m cli_anything.erank --json keyword tool "crochet pattern" --listings exports\sample-listings.csv
```

Audit a listing:

```powershell
python -m cli_anything.erank --json listing audit --title "Custom Wall Art Print" --tags "wall art;custom print;gift for mom" --price 18 --image-count 6
```

Check API surface:

```powershell
python -m cli_anything.erank --json api-check
```

## Command Map

- `api-check`: report eRank API findings and Etsy API fallback.
- `config set|get|show`: save local API keys or profile settings.
- `keyword tool|compare|bulk|lists`: keyword research and saved keyword lists.
- `rank check|bulk`: rank-check imported search/listing rows.
- `competitor shop-info|tags|listings|sales|top-sellers|clusters`: competitor research and product-family clustering.
- `listing audit|compare|draft-audit|changes|impact|cro-audit|fact-draft|ai-helper`: listing optimization and evidence-based experiments.
- `shop health-check|tag-report|sales-map|delivery-status|spotted|spell-check|traffic-stats|anomalies|watchlist-alerts`: shop insight and monitoring tools.
- `tools profit|true-profit|roi|category|calendar|shortcut`: calculators, private cost/capacity gates, and planning helpers.
- `trends buzz|monthly|seasonal-plan`: imported trend reporting and launch planning.
- `live sources|source-probe|open|member-plan|member-ingest|evidence-check|top-sellers|shop-info|shop-listings|shop-tags|shop-search`: source checks, safe member ingestion, live shop connectors, and strict discovery.
- `selection breakout-shops|opportunity|cross-market|daily|sales-report|furniture-report`: seller-specific decision intelligence.
- `data summarize|remember|sample`: data import helpers.
- `undo|redo|status`: state management.

## Data Shapes

Listings CSV/JSON can include:

```text
listing_id,shop,title,description,tags,price,views,favorites,sales,image_count,materials,created,status
```

Orders CSV/JSON can include:

```text
order_id,country,total,status,carrier,tracking_number,created
```

Trend CSV/JSON can include:

```text
keyword,marketplace,search_volume,competition,trend,category
```

Traffic CSV/JSON can include:

```text
source,visits,orders,revenue
```

## Etsy API

Optional live mode:

```powershell
python -m cli_anything.erank config set etsy_api_key YOUR_KEY
python -m cli_anything.erank config set etsy_oauth_token YOUR_TOKEN
python -m cli_anything.erank --json keyword tool "wall art" --source etsy
```

Private seller data needs OAuth scopes approved by Etsy. The harness will not bypass eRank login or paid limits.

## Realtime eRank Member Data

Use the `live` command group for realtime workflows:

```powershell
python -m cli_anything.erank --json live sources
python -m cli_anything.erank --json live source-probe
python -m cli_anything.erank --json live member-plan --timeframe all-time --pages 4
python -m cli_anything.erank --json live member-ingest --input downloads\page-1.json --input downloads\page-2.json --output exports\member-all-time.json
python -m cli_anything.erank --json live evidence-check --input exports\member-all-time.json --require-complete
python -m cli_anything.erank --json live open top-sellers
python -m cli_anything.erank --json live top-sellers --source erank-live --timeframe yesterday --limit 100 --output exports\top-sellers-yesterday.csv
python -m cli_anything.erank --json live top-sellers --source erank-export --input downloads\top-sellers.csv --limit 100 --output exports\top-sellers-live.csv
python -m cli_anything.erank --json live shop-search --input downloads\top-sellers.csv --sales-min 660 --sales-max 680 --age-months 4 --as-of 2026-08-03 --output exports\matching-shops.csv
python -m cli_anything.erank --json selection breakout-shops --input exports\current-shops.json --previous exports\previous-shops.json --age-min-months 3 --age-max-months 5 --sales-min 660 --sales-max 680
python -m cli_anything.erank --json selection opportunity --input exports\opportunities.csv --target-margin 30
python -m cli_anything.erank --json tools true-profit --price 80 --supplier-cost 20 --shipping-cost 10 --production-minutes 30 --target-margin 30
```

`shop-search` only returns a strict match when the row contains lifetime shop sales and either an exact opening date or an explicit age in months. Year-only and month-only opening values are retained under `needs_verification`. Every result also reports snapshot time, timestamp basis, freshness, and coverage; a five-row public sample is never reported as an exhaustive search.

The browser-backed path uses your logged-in Chrome session. Do not copy cookies into another browser. If Chrome asks to allow remote debugging, approve it only when you intend Codex to use that browser session.

When eRank live/export is not available, a public current snapshot can be pulled as a fallback:

```powershell
python -m cli_anything.erank --json live top-sellers --source alura-public --limit 100
```

That fallback is not eRank member data and is not a yesterday-only sales ranking.
