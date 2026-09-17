# 竞品与 eRank 研究

仅当本轮要求竞品研究、基于竞品合成标题或完整 SEO 审查时读取；普通写作不触发。

下列命令和非链接相对路径均以本 Skill 的目录为基准。

## Competitor Fingerprint and Relevance Gate

When competitor research is requested, apply this gate to the current product category; never reuse category-specific keywords or matching assumptions from a different product.

1. Build a product fingerprint from the images, working title, and confirmed seller facts. Record the core product identity, primary buyer need, structure or mounting, material or production process, personalization or variant structure, use case, target buyer, style, and visible differentiators. Mark each field as `visible`, `seller_confirmed`, or `unknown`; never score an assumption as a match.
2. Generate 2-4 focused Etsy searches from applicable fingerprint dimensions: core product plus structure, material or process, personalization or variant, and buyer need or use case. Do not rely on one broad title query.
3. Require both hard-gate fields for every retained candidate: `same_core_product: true` and `same_primary_buyer_need: true`. Reject digital files, supplies, different product types, or different buyer jobs when the target is a finished physical product, regardless of popularity or total score.
4. Score every retained candidate out of 100 and preserve the component scores:
   - `core_product`: 0-30.
   - `buyer_need`: 0-20.
   - `structure_or_mounting`: 0-15.
   - `personalization_or_variant`: 0-15; compare the equivalent option or configuration structure when personalization is not applicable.
   - `material_or_process`: 0-10.
   - `style_or_use_case`: 0-10.
5. Classify `80-100` as `core`, `60-79` as `adjacent`, and reject anything below 60. A hard-gate failure is always rejected even if the arithmetic score would be 60 or higher. Keep 3-5 independently opened `core` listings before using competitor evidence for title synthesis or direct eRank tag collection.
6. If fewer than 3 core competitors remain, expand one secondary dimension at a time, such as color, style, finish, or material. Never relax core product identity and primary buyer need together, never silently promote an adjacent listing, and report the competitor/title basis as `PARTIAL` if bounded expansion still produces fewer than 3 core listings.
7. Deduplicate near-identical listings from the same shop. Advertising position, bestseller badges, sales, reviews, or popularity may be recorded but never substitute for relevance.
8. Open every retained listing and record its public Etsy URL, exact visible title, access time, score breakdown, tier, hard-gate result, concise match reasons, explicit mismatches, and visible description facts. Search snippets alone are not competitor proof.

Use `core` competitors for title language and direct competitor-tag evidence. Keep `adjacent` competitors visibly separated and use them only for positioning or keyword ideas that are independently validated; never present their language or tags as exact-competitor evidence.


## Image + Title Competitor Workflow

Use this ordered, review-only workflow when the user requests competitor/eRank research using product images and a working title. Images and a title alone do not trigger it. Do not edit or publish an Etsy listing unless the user separately authorizes that external write.

1. Inspect every supplied image and the working title, then build the preliminary product fingerprint. Separate visible facts from assumptions; do not infer hidden materials, measurements, weight, package contents, production method, or performance claims from an image.
2. Build the search matrix and use the Codex in-app browser to run 2-4 focused Etsy queries under the `Competitor Fingerprint and Relevance Gate`. Search the US market when a locale choice is available. Use an already rendered Etsy page instead of direct HTTP when Etsy returns a challenge or 403.
3. Open, score, classify, and deduplicate candidates until 3-5 core competitors pass the gate or bounded one-dimension-at-a-time expansion is exhausted. Record the required evidence for each retained listing. Do not copy long competitor prose into the new listing.
4. Summarize the competitor evidence. Reuse confirmed seller facts and ask one compact question only for missing facts that change product identity, safety, or the core requested result. Relevant fields may include:
   - Quantity and exact package contents.
   - Product dimensions with units, including component dimensions when needed.
   - Net item weight and packaged/shipping weight when known.
   - Confirmed materials, color, finish, and production method.
   - Personalization options, care, assembly, compatibility, or capacity claims relevant to the product.
   - Price, processing time, and shipping method when applicable facts have not been confirmed.
   Treat explicit seller answers as authoritative product facts. Once the seller confirms a material, finish, production method, food-contact claim, mounting method, or use case, allow that fact in accurate tags and copy even when it was not visually provable from the image.
5. Block only the statements that depend on a missing essential fact; continue independent drafting. Omit nonessential unknown fields without asking permission to omit them, and keep them in `information_to_confirm`. Update the fingerprint and rescore affected candidates only when new facts change their relevance. Generate the requested description from confirmed facts, applicable captured evidence, and explicitly confirmed risky claims; never use placeholders to bypass an essential fact gap.
6. Collect eRank tags without requiring seller interaction. Use this automated source order:
   - First inspect and run the local `etsy-tony-full-erank-tools` harness from `../etsy-tony-full-erank-tools/harness`. Confirm its current command surface with `python -m cli_anything.erank --help` before relying on it. Use its read-only live listing or shop-tag commands when they provide source-attributed data. Submit core competitor listings first.
   - If the harness is missing, broken, or cannot return exact listing tags, continue in the same run with the user's already logged-in Chrome. Open the normal HTTPS eRank member dashboard, submit each Etsy listing URL or ID through `Look Up Any Listing`, then read the 13 rows from `https://members.erank.com/listing-audit/{listing_id}`. Preserve exact tag spelling, source listing ID/URL, marketplace, and visible values such as `Unknown`, `-`, or `< 20` without estimating them.
   - Treat the eRank Chrome extension side panel as an optional visual cross-check only. Do not make a seller click `Copy Tags`, open an extension panel, or paste clipboard text when the CLI or normal member webpage can supply the same evidence automatically.
   - Never inspect or expose cookies, tokens, localStorage, sessionStorage, extension internals, or other credentials. Do not bypass login, paid limits, browser security policy, or member quotas. If automated login is unavailable, report the exact blocker instead of requesting credentials.
7. When tags are part of the requested deliverable, deduplicate the retrieved tags, remove competitor brands, trademarks, irrelevant phrases, unconfirmed materials or production methods, and any tag longer than 20 characters. Reintroduce seller-confirmed attributes such as `acrylic`, `laser cut`, or `mirror acrylic` through specific buyer-intent phrases. Keep adjacent-competitor tags separate; use them only as ideas and validate an accurate phrase automatically in the logged-in eRank Keyword Tool before selection. When a confirmed phrase is absent from the audited core competitor tags, validate it through the same Keyword Tool and preserve visible values such as `Unknown`, `-`, or `< 20`. Select exactly 13 accurate tags and return them on one line separated by English commas. If fewer than 13 accurate eRank tags remain, make at most one additional focused collection from core listings, then report the remaining evidence gap; if every safe automated eRank path is unavailable, report the tag step as `BLOCKED` or the overall package as `PARTIAL` instead of inventing or relabeling tags. When the user skips tags, leave the Etsy tag fields unchanged or empty as requested and report that state explicitly.
8. Independently reread the final competitor URLs, scores, tiers, hard-gate results, confirmed facts, generated title and description, and any requested 13-tag line. Verify that each generated title combines accurate language from at least two core competitor titles without copying one title in full. Reject and directly revise a description that uses a boilerplate opening, lacks icon-led sections, contains placeholders or omitted-fact commentary, or introduces unconfirmed occasions, options, effects, mounting performance, or care claims. Report core and adjacent evidence separately; generated content is not proof of eRank access or Etsy publication.


## Competitor Title Synthesis Gate

- Use only the exact visible titles from 3-5 rescored `core` competitors as the title language pool. Adjacent listings and search-result snippets must not contribute title language.
- Split the titles into reusable segments: core product noun, confirmed material or finish, personalization type, placement or mounting language, style, and seller-confirmed occasion.
- Build each English title by combining accurate segments represented across at least two competitor titles with the seller's confirmed facts. Prefer repeated buyer language; do not add a material, use, option, or effect merely because a competitor uses it.
- Put the strongest repeated product phrase plus a confirmed differentiator in the first 40 characters. Remove duplicated wording and keep the result natural rather than concatenating every keyword.
- Never copy or lightly punctuate an entire competitor title. Preserve the source URLs, match scores, and tiers, and identify which core competitor titles contributed language during final verification.
