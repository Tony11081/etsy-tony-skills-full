# eRank Harness Command Map

Run from `本 Skill 的 `harness/` 目录`.

## API and State

- `api-check`: Report the supported eRank read-only web API, member-session boundary, and Etsy/local fallbacks.
- `live sources`: Check realtime source readiness: Etsy API, eRank member browser/export, and public live fallback.
- `live open top-sellers`: Return the eRank member Top Sellers URL and next export/browser step.
- `live member-plan --timeframe all-time --pages 4`: Generate safe same-origin GET paths; use `--resume-from merged.json` to request only missing pages.
- `live member-ingest --input page-1.json --input page-2.json --output merged.json`: Merge pages, deduplicate rows, reject credential fields, and report missing pages/coverage.
- `live evidence-check --input merged.json --require-complete`: Gate downstream work on source, freshness, rows, and complete coverage.
- `live top-sellers --source erank-live --timeframe yesterday --limit 100`: Fetch eRank live Top Sellers by yesterday sales.
- `live top-sellers --source erank-live --timeframe all-time --limit 100`: Fetch the no-cookie all-time sample; eRank currently caps it at five shops, so use the member browser/export for the full ranking.
- `live top-sellers --source erank-export --input ./etsy-output\erank-member-top-sellers-all-time-YYYY-MM-DD.json --limit 100`: Parse the complete ranking fetched through the logged-in browser's same-origin API.
- `live top-sellers --source erank-export --input file.csv --limit 100`: Parse eRank member Top Sellers CSV/HTML exports.
- `live top-sellers --source alura-public --limit 100`: Pull a public current Etsy top-seller fallback; not eRank and not yesterday-only.
- `live shop-info ShopName`: Fetch eRank Shop Info overview and profile.
- `live shop-listings ShopName --limit 100 [--output file.csv]`: Fetch the bounded no-cookie eRank listing sample; use `--source etsy` or `--source export` for up to 500 authorized/input rows.
- `live shop-tags ShopName --listing-limit 100 --limit 100`: Derive tag frequency without inventing member keyword metrics.
- `selection daily --source mixed-live --member-all-time-input ./etsy-output\erank-member-top-sellers-all-time-YYYY-MM-DD.json --yesterday-limit 300 --all-time-limit 300 --top-n 3 --output-dir ./etsy-output`: Build the daily product-selection report with the authenticated member all-time ranking.
- `selection sales-report --source erank-live --timeframe yesterday --limit 300 --output-dir ./etsy-output`: Build the daily high-sales trend report for category/shop movement.
- `selection furniture-report --input ./etsy-output\erank-high-sales-trend-YYYY-MM-DD.csv --tracked-input ./etsy-output\erank-tracked-shops-after-reset-YYYY-MM-DD.json --output-dir ./etsy-output`: Build a furniture/Home & Living report from exported rows plus tracked shops.
- `selection breakout-shops --input current.json --previous previous.json --age-min-months 3 --age-max-months 5 --sales-min 660 --sales-max 680`: Strict young-shop filtering plus growth velocity.
- `selection opportunity --input opportunities.csv --target-margin 30`: Combine market, private cost, capability, and risk evidence.
- `selection cross-market --input signals.csv --min-sources 3`: Require multi-channel signal agreement.
- For user requests involving realtime eRank member data, first try logged-in Chrome/browser automation; use CSV/HTML export parsing when browser access is blocked.
- `status`: Show local session path, remembered imports, keyword lists, snapshots, undo/redo counts.
- `undo`, `redo`: Revert or reapply local state mutations.
- `config set|get|show`: Store Etsy API key/token or inspect masked config.

## Keyword Research

- `keyword tool "<term>" --listings file.csv`: Keyword metrics, related keywords, top listings from local data.
- `keyword tool "<term>" --source etsy --limit 25`: Live Etsy active-listing keyword lookup when API key is configured.
- `keyword compare term1 term2 --listings file.csv`: Compare proxy volume, competition, difficulty, CTR, and price.
- `keyword bulk --file keywords.txt --listings file.csv`: Batch keyword reports.
- `keyword lists add|show|remove`: Local saved keyword list state.

## Rank Research

- `rank check "<term>" --shop ShopName --listings file.csv`: Find best local rank for a shop.
- `rank bulk --file keywords.txt --shop ShopName --listings file.csv`: Batch rank checks.

## Competitors

- `live shop-info ShopName`: Read the current eRank overview/profile route.
- `competitor shop-info ShopName --listings file.csv`: Summarize locally imported listings.
- `competitor shop-info ShopName --source etsy`: Search shops through Etsy API.
- `competitor tags ShopName --listings file.csv`: Local competitor tag frequency.
- `competitor listings ShopName --listings file.csv --limit 100`: Local competitor listings.
- `competitor sales ShopName --listings file.csv`: Transparent local sales estimate.
- `competitor top-sellers --listings file.csv --limit 100`: Local shop aggregation.
- `competitor clusters --listings file.csv [--shop ShopName]`: Product-family, price-band, tag, and hero-listing clusters.

## Listing Optimization

- `listing audit --listing-file listing.csv`: Audit first row from a listing file.
- `listing audit --title ... --tags ... --price ...`: Audit a typed listing draft.
- `listing compare file1.csv file2.csv`: Compare listing audit scores.
- `listing draft-audit --listings file.csv`: Audit draft/inactive listings.
- `listing changes track LISTING_ID --listings file.csv --note "before edit"`: Snapshot a listing and audit.
- `listing changes show [LISTING_ID]`: Show snapshots.
- `listing ai-helper "seed product" keyword1 keyword2`: Generate local title/tag/description suggestions.
- `listing impact --before before.csv --after after.csv --before-at ... --after-at ...`: Observational edit/metric deltas with confounder flags.
- `listing cro-audit --listing-file listing.csv --image-manifest images.csv [--image first.png]`: Technical image and merchandising evidence checks; always requires human review.
- `listing fact-draft --facts facts.json --keyword ...`: Review-only factual draft; returns `NEEDS_CONFIRMATION` instead of inventing missing tags and emits exactly 13 when ready.
- `keyword portfolio --listings listings.csv --metrics keyword-metrics.csv`: Intent mapping, 13-slot planning, and cannibalization detection.

## Shop Tools

- `shop health-check --listings file.csv [--shop ShopName]`: Listing audit rollup.
- `shop tag-report --listings file.csv [--shop ShopName]`: Tag usage/performance.
- `shop sales-map --orders orders.csv`: Orders by country.
- `shop delivery-status --orders orders.csv`: Shipping status and missing tracking.
- `shop spotted term1 term2 --shop ShopName --listings file.csv`: Spot shop in local ranked results.
- `shop spell-check --listings file.csv`: Suspicious characters/repeated words.
- `shop traffic-stats --traffic-csv traffic.csv`: Traffic source conversion summary.
- `shop anomalies --current current.json [--previous previous.json]`: Duplicate, negative, decreasing, spike, implausible-pair, and schema-drift checks.
- `shop watchlist-alerts --current current.json --previous previous.json --state alerts.json`: Fresh/complete-evidence-only alerts with deduplication.

## Tools and Trends

- `tools profit --price 30 --item-cost 9 --shipping-cost 5`: Etsy-style profit estimate.
- `tools true-profit --price 80 --supplier-cost 20 --shipping-cost 10 --production-minutes 30 --target-margin 30`: Landed cost, labor, return/breakage, capacity, margin, and optional formula gates.
- `tools roi --ad-spend 100 --clicks 400 --orders 20 --revenue 500`: Ads ROI/ROAS.
- `tools category --title "Printable Wedding Welcome Sign" --tags "wedding sign;printable wedding"`: Category suggestions.
- `tools calendar --month 11 --country US`: Monthly Etsy planning reminders.
- `tools shortcut --keyword "wall art" --shop ShopName`: eRank page shortcut URLs.
- `trends buzz --trends-csv trends.csv [--marketplace etsy]`: Imported trend ranking.
- `trends monthly --trends-csv trends.csv [--category home]`: Monthly/category trend view.
- `trends seasonal-plan --input monthly-signals.csv --lead-days 45`: Historical peak/uplift backtest and launch/prototype dates.
- `selection daily --trend-input trends.csv`: Add imported Trend Buzz or keyword exports to the daily selection score.
- `selection daily --tracked-input tracked-shops.json`: Add exported eRank tracked shops to the daily selection score.
- `selection furniture-report --input <csv-html-or-json>`: Filter furniture/Home & Living rows; this compatibility report never treats a public sample as complete.

## Data Helpers

- `data sample exports\sample-listings.csv`: Generate sample listing CSV.
- `data summarize --listings file.csv`: Listing export summary.
- `data remember listings file.csv`: Save local import paths in session.
