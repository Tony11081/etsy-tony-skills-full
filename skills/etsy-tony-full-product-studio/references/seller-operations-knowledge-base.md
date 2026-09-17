# Etsy Seller Operations Knowledge Base

Last normalized through: 2026-08-31  
Current official policy last verified: 2026-09-01  
Maintenance model: daily append, normalize, deduplicate, supersede, and quarantine  
Privacy rule: retain reusable knowledge only; do not store names, account identifiers, credentials, referral links, or verbatim chat transcripts.

This reference supports read-only decisions about shop ownership, onboarding country, KYC, payments, network/device claims, fulfillment disclosure, carrier routing, category transitions, dated market observations, and product-media operations. It is not an account-opening, review-evasion, or location-masking playbook.

## 1. Evidence classes and precedence

| Evidence Class | Meaning | Employee Use |
|---|---|---|
| Current Official Policy | Current Etsy legal or Help content verified at execution time | Governs the decision; save URL and date |
| Official Support Confirmation | Case-specific written Etsy Support answer or current UI behavior | Use only within its documented scope |
| Internal Business Rule | Approved operating preference such as a carrier candidate or category-transition cadence | Apply only after policy and case prerequisites pass |
| Empirical Observation | Dated operational experience without platform guarantee | Use as a hypothesis or risk signal; revalidate |
| Historical Snapshot | Dated market or platform observation | Never present as current without refresh |
| Unverified / High Risk | Claim lacks reliable evidence or conflicts with identity, disclosure, or customer-truthfulness duties | Quarantine; do not operationalize |

Precedence is Current Official Policy, then current official UI or Support, then Internal Business Rule, Empirical Observation, Historical Snapshot, and Unverified / High Risk. A newer official rule supersedes an older workaround even if the workaround once appeared to work.

## 2. Current official baseline

The following baseline was verified on 2026-09-01 and must be rechecked when used because it can change.

| Area | Current Baseline | Decision Consequence | Official Source |
|---|---|---|---|
| Accurate shop and listing information | Sellers must provide accurate information and accurately represent how, by whom, and where an item is made and where it ships from | False owner, maker, production, or ships-from claims are not acceptable | https://www.etsy.com/legal/sellers/ |
| Account ownership | Etsy accounts are not transferable; if ownership changes, the new owner must open a new account and shop | Buying, transferring, or taking over an Etsy account is not an approved operating path | https://help.etsy.com/hc/en-gb/articles/360040985353-Can-I-Transfer-My-Etsy-Account-to-Someone-Else |
| Identity accuracy | Users must provide accurate information and may not impersonate another person or entity | Identity substitution, borrowed credentials, and false entity data are prohibited decisions | https://www.etsy.com/legal/terms-of-use |
| Etsy Payments country availability | Eligibility is determined by the current Etsy Payments country list, not by IP location | Verify the real subject's country at runtime before shop-opening advice | https://help.etsy.com/hc/en-us/articles/115015710408-Countries-Eligible-for-Etsy-Payments |
| China and Tanzania snapshot | On the 2026-09-01 official page, Tanzania is absent; China is marked for existing shops and the page states new shops cannot open in China | Preserve as a dated policy snapshot, not a timeless statement | Same current eligibility source above |
| Bank country | Etsy states the bank country selected when opening becomes the shop bank country and the bank account generally must be from that country, with only stated exceptions | Do not treat third-party payout products as a cure for ownership or country mismatch | Same current eligibility source above and https://help.etsy.com/hc/en-us/articles/115014503608-How-to-Get-Paid-on-Etsy |
| Production partners | A seller using a production partner must disclose the partner as required and maintain accurate delivery locations | Do not hide third-party production or use a fictitious domestic dispatch point | https://help.etsy.com/hc/en-in/articles/360000336547-Working-with-Production-Partners-on-Etsy |
| US import duties | Current Seller Policy states that US-bound orders must use Delivery Duty Paid shipping | Validate the carrier route and duty responsibility before promising US delivery | https://www.etsy.com/legal/sellers/ |

Official-policy verification is mandatory for live operational advice. If an official page is unavailable, output Official Policy Verification Required and do not convert historical guidance into current policy.

## 3. Account integrity and shop onboarding

### 3.1 Reusable decision rules

- The safest and policy-aligned owner is the real person or entity that controls the shop, identity documents, bank account, payment method, tax information, recovery methods, and long-term operation.
- Registration success is not stability proof. First order, a short survival period, or initial payout compatibility does not prove that later review or KYC will pass.
- Country selection follows the real eligible subject and current Etsy Payments rules. IP, email region, phone location, or device location does not create eligibility.
- Phone versus computer is a workflow choice, not a compliance guarantee. Current eligibility, truthful identity, account ownership, and accurate data matter more than device brand.
- A current official rejection or unavailable country cannot be bypassed by old developer-tools tricks, legacy parameters, or stale code.
- One stable device and environment may reduce accidental login friction, but it is not evidence that Etsy approves the underlying identity, payout, or country setup.

### 3.2 Dated source-note disposition

| First Seen | Normalized Knowledge | Class | Current Disposition |
|---|---|---|---|
| 2026-08-19 | Evaluate a shop plan across ownership, KYC, payout, payment, recovery, post-order history, and long-term cooperation rather than registration success alone | Empirical Observation | Keep as risk-screening questions; account purchase or proxy registration is superseded by the non-transfer rule |
| 2026-08-19 | Identity, entity, bank, payment, and tax records should describe the same real subject | Internal Business Rule supported by official accuracy duties | Keep; do not invent a platform guarantee |
| 2026-08-20 | Shop country should follow the real subject and the current eligible-country list, not the IP country | Current Official Policy synthesis | Keep with runtime verification |
| 2026-08-20 | A single real owner may use a phone browser for onboarding and email verification; an Etsy shopping app is not proof of seller-onboarding capability | Empirical Observation | Optional workflow note only; verify current UI |
| 2026-08-20 | Email region is secondary to truthful identity, owner, bank-country, and shop-country requirements | Empirical Observation | Keep as a limited observation, not a rule |
| 2026-08-24 | Having the real owner perform first registration and identity steps on their own device may reduce handoff errors | Empirical Observation | Keep only as owner-integrity guidance; do not prescribe remote identity handling |
| 2026-08-24 | Waiting about two days before changing device environment was suggested | Unverified / High Risk | Do not treat as policy, safety proof, or required timing |
| 2026-08-24 | After early milestones, product and operations affect business performance | General Business Observation | Keep; it does not erase compliance risk |
| 2026-08-27 | Country-level stable access was preferred over frequent network changes | Empirical Observation | Use only as login-hygiene advice; no proxy or fingerprint mimicry instructions |
| 2026-08-29 | Waiting three days after a first order before considering a payout change was suggested | Unverified / High Risk | It is not a safe-harbor period; current official requirements and real ownership still govern |

### 3.3 Account decision checklist

1. Who is the real owner and continuing operator?
2. Is the owner personally or organizationally eligible under the current official country list?
3. Do identity, bank, tax, payment, and recovery records belong to or lawfully represent that owner?
4. Does the proposal assume purchase, transfer, takeover, borrowed identity, or continuing cooperation from a prior owner?
5. Has current Etsy onboarding and payout guidance been rechecked?
6. Is the requested action read-only, draft, or a live external change requiring explicit authorization?

If questions 1 to 4 are unresolved, use Account Ownership Verification Required and stop before operational instructions.

## 4. KYC, payouts, and payment methods

- KYC is an identity and entity verification process, not a technical obstacle to route around.
- A payment card, bank account, Payoneer account, PayPal account, or other provider does not repair a mismatched shop owner or unsupported country.
- Country-specific payout and payment behavior cannot be copied to another country without current official verification and a lawful, matching owner.
- Changing payout information after orders is a sensitive live account mutation. It requires the real owner, current official guidance, case-specific risk review, and explicit authorization.
- Advice such as a particular domestic identity-card, card, payout provider, and residential-IP combination is retained only as a historical example of subject consistency. It is not a guaranteed or current onboarding recipe.
- Advice about using PayPal for a specific country or using a third party's payout account remains Unverified / High Risk unless current official policy and the real owner's lawful control are documented.

Never claim that a provider is safe merely because registration completed, the first order survived, or two providers offer similar functionality.

## 5. Network, device, and location claims

### Permitted knowledge

- Avoid unnecessary device and network changes that can create operational confusion or trigger security checks.
- Consult the current official documentation for the browser or network tool being used when solving ordinary connectivity issues.
- Record actual login problems as evidence; do not infer shop safety from a clean login.

### Quarantined knowledge

- A fingerprint-browser brand is not a substitute for truthful identity and account ownership.
- Static residential IP suggestions and named proxy vendors are not retained as approved Etsy-operating instructions.
- City-level IP matching, waiting periods, or device sequences are not compliance guarantees.
- Proxy/fingerprint setup intended to appear in another country is prohibited.
- Referral URLs from source notes are intentionally excluded from this knowledge base.

## 6. Fulfillment, ships-from, production partners, and postal codes

### 6.1 Truthful fulfillment rules

- The shop country, production location, and actual ships-from location can be different only when each field is truthful, permitted, and accurately disclosed.
- Treat accurate ships-from information as a launch gate, not an optional SEO or routing field.
- If a product is made or dispatched from China, do not state that it ships from the United States merely because the shop, buyer market, operating IP, warehouse label, or last-mile carrier is in the United States.
- Do not select a US postal code based on operating IP. A postal code must represent the real and permitted dispatch or return context for that field.
- If a production partner participates, verify whether current Etsy rules require disclosure and keep delivery locations accurate.
- A last-mile tracking number may be used when it truthfully represents the shipment and meets platform/carrier rules. It must not be selected to hide the real origin or route.
- Delivery estimates should reflect the full real route and include reasonable operational buffer. Padding time does not cure an inaccurate origin claim.
- For US orders, verify current Delivery Duty Paid, customs, restricted-item, and carrier requirements before launch.

### 6.2 Dated source-note disposition

| First Seen | Source Note | Class | Current Disposition |
|---|---|---|---|
| 2026-08-25 | Shop registration country and actual ships-from can differ | Conditionally correct | Keep only with truthful actual origin and current field rules |
| 2026-08-25 | A route can physically originate in China while a backend setting says United States | Unverified / High Risk | Reject when the field would misrepresent actual fulfillment |
| 2026-08-28 | Match a US shipping postal code to the operating IP region | Unverified / High Risk | Reject; IP is not fulfillment evidence |
| 2026-08-31 | An Indonesian shop may list a US postal code for US dispatch | Unverified / High Risk | Only valid if the item really dispatches from that represented US location and current policy permits it |
| 2026-08-31 | A last-mile line may reduce front-leg visibility | Unverified / High Risk framing | Use tracking for truthful buyer visibility, never for concealment |
| 2026-08-31 | Disclose production partners and verify ships-from policy | Current Official Policy synthesis | Keep and verify at runtime |

Any unresolved mismatch creates Fulfillment Disclosure Required and blocks Listing-Ready status.

## 7. Internal carrier-routing candidates

These are internal routing candidates first recorded from operations. They are not Etsy policy, real-time quotations, or proof of service availability.

| Destination | Candidate | First Seen | Required Validation Before Use |
|---|---|---|---|
| United States | 出口易 SUR virtual-warehouse route | 2026-08-22 | Current service availability, real origin, DDP/customs, restricted goods, price, weight/dimensions, end-to-end tracking, delivery performance, claims, and accurate Etsy disclosure |
| United Kingdom | 燕文 UK Royal Mail or tracked route | 2026-08-31 | Current service availability, real origin, VAT/customs, valid tracking, delivery performance, price, claims, and accurate disclosure |
| Other non-US destinations | 燕文 candidate selected by destination | 2026-08-22 | Destination coverage, customs/tax, tracking, service level, price, claims, and accurate disclosure |

Reusable routing sequence:

1. Confirm the actual dispatch point and destination country.
2. Confirm product restrictions, dimensions, weight, order value, and duty/tax responsibility.
3. Compare current candidate services.
4. Confirm the entire route, not only the last-mile label.
5. Confirm end-to-end tracking and realistic delivery estimate.
6. Confirm that Etsy ships-from, production-partner, and delivery information remains accurate.
7. Obtain explicit authorization before changing a live shipping profile.

If any input is unknown, return Requires Carrier Quote or Official Policy Verification Required rather than selecting a route as approved.

## 8. Category transition and shop positioning

- New shops should generally start with a coherent vertical category rather than an unrelated general store, because buyer expectation, imagery, keywords, and operations are easier to align.
- For an existing shop changing to a materially different category, use a gradual transition as an Internal Business Rule: a starting cadence may be 3 to 5 new listings and about 3 old listings retired per day.
- The cadence is not an Etsy limit or risk guarantee. Adjust it using current traffic, conversion, favorites, orders, ad effects, inventory, support load, and policy status.
- Update shop icon, banner, About content, photography language, category navigation, listing copy, and customer expectations as the product direction changes.
- Do not mass-delete active listings solely to imitate a schedule. Preserve records, review dependencies, and use reversible changes with explicit authorization.

## 9. Product photography and image workflow

- A phone can be sufficient for upstream capture when lighting, focus, scale, color, surface, personalization, and defects are shown truthfully.
- Codex and product-photo Skills may standardize cropping, naming, option charts, mockups, and Listing image sequencing after capture.
- A generated mockup or edited concept is not proof of a physical sample, material, engraving color, embroidery quality, size, production approval, or shipping readiness.
- Preserve real-product evidence and label pre-production visuals. Verify current Etsy AI-image and listing-image disclosure requirements at execution time.

## 10. Dated eRank market snapshot

The following is a Historical Snapshot dated 2026-08-29. It must not be described as today's market without a fresh source pull.

| Metric | 2026-08-29 Snapshot | Interpretation Boundary |
|---|---:|---|
| Top 100 reported daily sales total | 41,937 | Reported eRank snapshot, not Etsy backend order verification |
| Change versus prior valid summary | -0.3 percent | Overall scale roughly flat for that comparison only |
| Median sales | 263 | Up 14.8 percent versus the prior valid summary; observe more days before action |
| Craft Supplies & Tools shops | 36 | Category concentration signal, not a product recommendation by itself |
| Home & Living shops | 18 | Category concentration signal, not a product recommendation by itself |
| United States shops | 59 | Geographic concentration for that dated Top 100 |
| United Kingdom shops | 15 | Geographic concentration for that dated Top 100 |
| Top 5 category pattern | Distributed across apparel, party supplies, bags, and accessories | Do not infer one-category dominance from one day |

Decision rule: obtain at least 2 to 3 fresh valid data days, preserve the source definition, compare total and median movement, and combine market signals with product margin, production capability, originality, fulfillment, and customer need. Do not convert a dated eRank snapshot into fabricated Etsy sales or a guaranteed selection decision.

## 11. Quarantined actions and claims

Do not automate or recommend any of the following:

- buying, transferring, or taking over an Etsy account
- using a prior owner, borrowed identity, third-party entity, payment card, bank account, or payout account to obscure the real operator
- identity substitution, impersonation, KYC circumvention, or false documents
- proxy/fingerprint setup intended to appear in another country
- developer-tools or legacy-parameter manipulation intended to bypass current eligibility or verification
- US postal codes chosen from IP location
- false US ships-from information when the product actually dispatches elsewhere
- tracking chosen to hide the real origin or route
- omitting a required production partner or misrepresenting who made the item
- treating registration, first order, three-day survival, one payout, or an unchanged login as proof of long-term safety

When such a request appears, output Do Not Implement, explain the policy or evidence conflict, propose a truthful owner/fulfillment path, and identify the minimum official verification needed.

## 12. Daily update protocol

1. Remove names, account identifiers, credentials, recovery information, referral links, order numbers, and verbatim chat text.
2. Convert the source into one reusable decision statement with scope and prerequisites.
3. Assign one evidence class, knowledge date, confidence, time sensitivity, and authorization state.
4. Deduplicate against existing statements and merge only when meaning and scope match.
5. For shop-country, KYC, payments, ownership, shipping origin, production partner, marketplace fields, and platform limits, verify the current official Etsy source.
6. If a new official source conflicts with an old note, mark the old note Superseded; if the note enables deception or circumvention, move it to Quarantined actions.
7. Preserve eRank and other market numbers only as dated Historical Snapshots with source scope and comparison basis.
8. End each update with permitted employee action, prohibited action, next verification date or trigger, and whether any external write requires explicit authorization.

Use templates/seller-knowledge-update.md for every daily merge. Run scripts/audit_skill.py after editing, then validate the source and installed copies and compare hashes.
