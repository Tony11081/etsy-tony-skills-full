# eRank Keyword Tool and Listing Tags via Logged-in Browser

Optional read-only path for eRank keyword metrics, related keywords, and the current tags of any Etsy listing. It needs only a browser that is logged in to `members.erank.com`; it does not depend on the local CLI harness.

## Pick the browser

- Use the browser the current user has already logged in to `members.erank.com`; do not assume a specific browser or existing login.
- Check by opening `https://members.erank.com/keyword-tool`. A logged-in page shows the search allowance (e.g. `Searches: 0/200`) and the user's search history.
- If no browser is logged in, stop this path and report it. Do not ask for the password, do not log in for the user, do not copy cookies from another browser.

## Keyword metrics

1. Open `https://members.erank.com/keyword-tool?keyword=<URL-encoded phrase>&source=etsy&country=USA`.
   - Use `keyword=` (singular). `keywords=` opens the tool without running the search.
   - Alternatively type the phrase into the `Enter a keyword` box and press `Search`.
2. Wait about 5 seconds for the results to load.
3. Read the `Keyword Statistics` panel: `Avg. Searches`, `Avg. Clicks`, `CTR`, `Competition`.
4. Read the `Keyword Ideas` table by its header names (`Keywords`, `Avg. Searches`, `Avg. Clicks`, `Avg. CTR`, `Etsy Competition`, ...). Some columns can be empty or hidden depending on the `Columns` setting; record only what is shown.
5. One search returns many related phrases. Run one search for the core product phrase and a few for distinct buyer intents (gift, occasion, material) instead of one search per candidate tag.

Each search uses the current account's allowance. Read the actual remaining quota and only run searches that can change the keyword choice; do not assume a fixed plan limit.

## Current tags of a listing

Submit the Etsy listing URL or ID through `Look Up Any Listing`, then read the 13 tag rows on `https://members.erank.com/listing-audit/{listing_id}`. Use this for the user's own listing (to evaluate the existing tags) and for competitor listings.

## What to record

For every row used: phrase, `Avg. Searches`, `Avg. Clicks`, `CTR`, `Competition` (if shown), market `USA`, read date, source `erank-member-browser`. Keep `< 20`, `Unknown`, `-` and blanks exactly as shown; never convert them to 0 or an estimate.

A phrase longer than 20 characters cannot be a tag even if it has volume; note it for the title or description instead.

## Boundaries

- Read-only. Do not star keywords, add to Keyword Lists, change tracked shops, or use any write action.
- Never read, copy, print or save cookies, tokens, passwords, localStorage, sessionStorage or CSRF values.
- Do not bypass login, plan limits or the daily search quota.
