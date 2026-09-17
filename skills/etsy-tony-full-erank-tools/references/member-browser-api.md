# eRank Member Browser API

Use this workflow when the public eRank API is quota-limited or returns `401`/`403`, especially for the complete all-time Top Sellers ranking, Trend Buzz, Keyword Tool metrics, Rank Checker, and Competitor Sales.

## Security Boundary

- Read and follow the `browser:control-in-app-browser` skill before browser actions.
- Use an existing logged-in `members.erank.com` browser tab or navigate a claimed tab to the required member page.
- Make only read-only, same-origin requests from the page context.
- Never inspect, copy, print, persist, or transfer cookies, local storage, passwords, OAuth tokens, CSRF values, or browser profile files.
- Do not call write endpoints, change tracked shops, or bypass plan quotas.

## Full All-Time Top Sellers

1. Generate the initial or resume request list:

   ```powershell
   python -m cli_anything.erank --json live member-plan --timeframe all-time --pages 4
   python -m cli_anything.erank --json live member-plan --resume-from merged.json
   ```

2. Navigate the logged-in tab to `https://members.erank.com/top-sellers`.
3. Use the tab's CDP capability and `Runtime.evaluate` to perform each planned same-origin `GET`. The first path is:

   `/api/top-sellers?yearStarted=all_time&category=&country=&page=1&perPage=100&sort_by=sales&sort_order=desc&onlyActiveShops=false`

4. Include `credentials: "include"`, `Accept: application/json`, and `X-Requested-With: XMLHttpRequest`. Do not read the credential values themselves.
5. Verify HTTP `200`, `data.length`, `meta.total`, current/last page, first rank, and last rank. Respect the account's returned limit.
6. Save only the response data and non-sensitive provenance to one JSON file per page:

   `./etsy-output\erank-member-top-sellers-all-time-YYYY-MM-DD.json`

   Recommended shape:

   ```json
   {
     "source": "erank-member-browser-api",
     "timeframe": "all-time",
     "fetched_at": "ISO-8601 timestamp",
     "endpoint": "/api/top-sellers",
     "data": [],
     "meta": {}
   }
   ```

7. Merge, validate, and resume if required:

   ```powershell
   python -m cli_anything.erank --json live member-ingest --input page-1.json --input page-2.json --output merged.json
   python -m cli_anything.erank --json live evidence-check --input merged.json --require-complete
   python -m cli_anything.erank --json live member-plan --resume-from merged.json
   ```

   `member-ingest` rejects payloads containing cookie, token, password, localStorage, sessionStorage, authorization, or CSRF fields.

8. Ingest the verified merged file with either:

   ```powershell
   python -m cli_anything.erank --json live top-sellers --source erank-export --input ./etsy-output\erank-member-top-sellers-all-time-YYYY-MM-DD.json --limit 100
   python -m cli_anything.erank --json selection daily --source mixed-live --member-all-time-input ./etsy-output\erank-member-top-sellers-all-time-YYYY-MM-DD.json --output-dir ./etsy-output
   ```

## Fallback

If the same-origin request is blocked or the browser is not logged in, use the visible eRank export control and parse CSV/HTML/JSON. Keep the five-row no-cookie response clearly labeled as a public sample, not the member ranking.
