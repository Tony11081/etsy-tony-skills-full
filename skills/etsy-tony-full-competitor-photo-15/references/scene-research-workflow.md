# 研究到原创图片的流程

执行本 Skill 时读取；研究未达到证据门槛时，不进入声称受竞品证据支持的生成阶段。

下列命令和非链接相对路径均以本 Skill 的目录为基准。

## Workflow

### 1. Establish Product Truth

Inspect every readable product reference before competitor research. Record:

- source and rights classification;
- stable visual invariants;
- confirmed dimensions and variants;
- visible but unconfirmed attributes;
- unknowns that generation must not invent;
- seller claims that require confirmation.

Block generation when there is no readable permitted product reference, the only available reference is a competitor image, or the product is prohibited or unlicensed under the photo-campaign rules.

### 2. Find True Competitors

Use the competitor fingerprint and scoring system from `etsy-tony-full-listing`:

1. Write the target product fingerprint before searching.
2. Run 2–4 focused Etsy searches that describe the product class and primary buyer need.
3. Open candidates individually and apply both hard gates: `same_core_product` and `same_primary_buyer_need`.
4. Retain 3–5 independently opened core competitors scoring 80–100; deduplicate same-shop near copies and include at least two shops where available.
5. Record exact public URL, visible title, shop, access time, score, hard-gate result, matches, mismatches, and visible facts.

One bounded search expansion is allowed if fewer than three core competitors remain. If there are still fewer than three, mark `competitor_research_status=PARTIAL` and `scene_plan_status=BLOCKED`; do not silently replace core competitors with adjacent products or start the competitor-informed generation path. The standalone parent photo skill may still be used as a separate, clearly labeled non-competitor-informed workflow.

### 3. Audit Competitor Scenes

Inspect enough public images from each retained listing to understand its buyer journey, normally the first 5–10 readable images. For every useful image, record:

- listing ID and image index;
- scene class and buyer question answered;
- environment anchor and product-environment contact;
- foreground, midground, and background structure;
- product scale, occupancy, angle, distance, and state;
- lighting direction, color balance, reflection, and shadow behavior;
- human-presence mode and the proof it supplies;
- prop family and each prop's job;
- text or graphic-overlay function;
- strength, product-fidelity risk, and unsupported-claim risk.

Record observations in words. Do not save competitor image paths into a generation plan.

### 4. Extract Category Patterns

Separate repeatable category grammar from a single shop's distinctive execution:

- `recurrent_patterns`: seen across at least two independent shops;
- `single_listing_ideas`: informative but weak evidence, never a template;
- `buyer_questions_covered`: scale, use, installation, texture, styling, gifting, storage, or category-specific concerns;
- `market_gaps`: important buyer questions competitors leave weak or unanswered;
- `risk_patterns`: misleading scale, invented mounting, impossible reflections, generic rooms, copied-looking layouts, unreadable overlays, or color cast.

Do not call a visual convention a market pattern when it appears in only one listing.

### 5. Translate Learning Into Original Direction

Create a `scene_learning_translation` record for every scene-bearing shot. Each record must include:

- competitor evidence sources by listing ID and image index;
- the abstract principle learned;
- the current product's buyer question;
- the product-truth source that supports the depiction;
- at least three `creative_delta_axes` changed from the evidence;
- competitor-specific elements that must be avoided.

Allowed creative-delta axes are environment, prop family, camera, lighting, palette, product placement, supported product state, and human action. Preserve product truth while changing the execution. Never reproduce the same combination of environment, props, camera, lighting, and product placement as a competitor.

Prefer improving a weakly served buyer question over cloning a high-performing competitor image.

### 6. Build the 15-Image Campaign

Hand the verified product facts and original scene translations to `etsy-tony-full-photo-15`. Follow that skill completely, including:

- its exact mandatory Chinese campaign prompt;
- exactly 15 distinct buyer-value roles, not 15 background swaps;
- category-specific scene-capacity floors and first-five sequencing;
- at least one dimension-proof image with locked values and deterministic overlays;
- scene probes before full production;
- neutral white balance and material-color fidelity;
- human-use proof only when relevant and supported;
- one image-generation call per shot;
- contact-sheet, individual-image, set-level, fidelity, and listing-readiness audits.

For each generation call, pass only explicit permitted product-reference paths. Prompts may contain abstract scene principles but must not contain competitor shop names, listing titles, URLs, artist names, or instructions to imitate a competitor.

### 7. Validate Before Generation

Create a combined JSON campaign plan using the schema in `references/competitor-scene-learning.md`, then run:

```powershell
$env:PYTHONUTF8='1'
python scripts/validate_scene_plan.py <path-to-plan.json>
```

Fix all validation errors before the shot-01 health probe. This validator supplements, and does not replace, the required `etsy-tony-full-photo-15` audits.

### 8. Audit Originality and Final State

Before delivery, compare the contact sheet against the recorded competitor observations without feeding competitor images into the generator. Reject and regenerate any shot that:

- looks like a close reconstruction of a competitor composition;
- contains competitor branding or distinctive artwork;
- invents a product fact;
- fails the intended buyer question;
- violates the photo-campaign scene, dimension, or fidelity gates.

Report these statuses separately:

- `competitor_research_status`;
- `scene_plan_status`;
- `generation_status`;
- `product_fidelity_status`;
- `originality_status`;
- `publish_readiness`.

Local draft success is not Etsy publication success. Use `VERIFIED_SUCCESS` only when all local campaign gates are independently reread and passed; otherwise use `PARTIAL`, `BLOCKED`, `FAILED`, or `UNVERIFIED` accurately.


## Required Deliverables

Save or return:

- `product-truth.json`;
- `competitor-evidence.json`;
- `competitor-scene-patterns.json`;
- `scene-learning-translation.json`;
- combined validated `plan.codex-direct.json`;
- 15 prompt briefs and 15 final image files;
- `alt-text.json`;
- `originality-audit.json`;
- all fidelity and listing-readiness artifacts required by `etsy-tony-full-photo-15`.

For user-facing reporting, lead with the final status, show which competitor scene principles were learned, explain how each was transformed, and list any facts the seller still needs to confirm.
