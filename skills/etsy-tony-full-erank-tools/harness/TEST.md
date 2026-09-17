# Test Plan

## Unit Tests

- Verify tag normalization, listing loading, keyword analysis, listing audit scoring, ROI/profit calculators, session undo/redo, exact-month shop age, lifetime-sales scope, member pagination/security, evidence gates, opportunity scoring, clustering, impact, keyword portfolio, CRO, cross-market, seasonality, fact-gated drafts, anomalies, and alert deduplication.

## Full E2E Tests

- Invoke the installed module command with `python -m cli_anything.erank`.
- Validate JSON output and help discovery for every extended command group, including member ingest/plans, restored live export modes, breakout shops, opportunity/cross-market reports, true profit, seasonal plans, alert state, and compatibility reports.
- Keep E2E tests offline by using fixtures.

## Live Validation

Optional live calls require:

```powershell
python -m cli_anything.erank config set etsy_api_key <key>
python -m cli_anything.erank config set etsy_oauth_token <token>
```

Then run:

```powershell
python -m cli_anything.erank --json competitor shop-info YourShopName
python -m cli_anything.erank --json keyword tool "wall art" --source etsy --limit 25
```
