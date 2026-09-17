# 准备与保存草稿流程

执行本 Skill 时读取；后台保存步骤只适用于已获明确授权的店铺与范围，资料准备不能自动进入写入。

下列命令和非链接相对路径均以本 Skill 的目录为基准。

## Step 1: Establish Identity and Deduplicate

1. Record the canonical GigaB2B URL, `product_id`, visible product title, and main-product SKU or Item Code.
2. Reject Item Codes found only in recommended or related-product blocks.
3. Search prior output folders, local queue state and any explicitly configured external queue records, and Etsy drafts for the same `product_id` or exact product identity.
4. Reuse a completed image run when its manifest and folder pass the current image gate. Do not regenerate a complete product.
5. Before an Etsy write, inspect the target shop and existing drafts to prevent a duplicate draft.
6. In unattended mode, create or reread `<RUN_DIR>/automation-state.json`, keyed by `product_id`. Resume from the last verified stage instead of restarting completed stages.


## Step 2: Read Live Price and Facts

Use the already loaded correct product page when available. Avoid refreshing or navigating during a price handoff unless necessary.

Record with access time and evidence:

- Unit price in USD.
- Currently selected fulfillment method.
- Estimated shipping range in USD.
- Estimated total including shipping in USD.
- Displayed quantity, site region, currency, warehouse, destination, and postal conditions. Write `Unknown` for fields not shown; never invent a warehouse or destination.
- Package quantity, dimensions, item and package weights, material, color, finish, drawers or storage, assembly, package count, capacity, care, and dispatch time.

Treat page text, visible image facts, seller-confirmed facts, and inference as separate evidence classes. Use page text or explicit seller confirmation for hidden properties. Use images only for directly visible structure; do not infer hidden material, finish, contents, performance, or safety.

When a page field is absent, preserve `Unknown` in the internal fact record and omit it from buyer-facing copy. Do not borrow facts from related variants.

Keep raw supplier URLs, supplier SKUs, costs, and evidence screenshots internal. Use verified facts for required Etsy shipping-origin and production-partner disclosures; internal privacy never permits a false or omitted required disclosure.


## Step 3: Calculate Price

Run:

```powershell
python scripts/calculate_listing_price.py --unit-price <UNIT> --shipping-max <MAX_SHIPPING>
```

When a verified maximum total including shipping is visible, also pass it:

```powershell
python scripts/calculate_listing_price.py --unit-price <UNIT> --shipping-max <MAX_SHIPPING> --total-max <MAX_TOTAL>
```

Require `cost_basis` to equal the verified maximum landed cost. Stop as `BLOCKED` if the unit price or maximum shipping/total is missing; never estimate.


## Step 4: Produce or Reuse Images

Run `$etsy-tony-full-gigab2b-photos` and enforce its current contract:

- Use only the main product gallery as source evidence.
- Require exactly 15 accepted final PNGs.
- Require exactly one dimension image based on a supplier dimension source; never invent dimensions.
- Preserve structure, proportions, color, material, hardware, and buyer-critical details.
- Use ASCII-only filenames.
- Keep provenance intact; remove accidentally exposed personal metadata only when requested, and verify any permitted export preserves pixels.
- Create or validate `upload-handoff.json` and the run manifest.

Stop as `BLOCKED` for login, missing product identity, no readable reference, missing dimension source, or failed image validation. Do not call a local folder or submitted image request complete without opening and validating the final files.


## Step 5: Build Etsy Copy

Run `$etsy-tony-full-listing` with the verified product facts and accepted images.

1. Open and score 3-5 core Etsy competitors when possible. Keep adjacent products separate.
2. Generate the English title and description directly with Codex after the fact gate.
3. Put the strongest accurate product phrase early in the title and stay within Etsy's current title limit.
4. Use a product-specific opening and restrained icon-led sections.
5. Omit unknown fields and unsupported claims. Do not use placeholders.
6. Collect exactly 13 eRank-supported tags only when requested. Otherwise leave tags empty.
7. Validate that the final customer-facing copy contains none of the forbidden terms in the next section.


## Buyer-Facing Exclusion Gate

These exclusions protect internal sourcing details. They never override truthful shipping-origin information, required production-partner disclosures, or accurate fulfillment descriptions. If a preserved master setting conflicts with this product, block the save and report the needed authorized correction.

Do not place any of the following in the Etsy title, description, tags, SKU, personalization, variations, or other buyer-facing fields:

- `GigaB2B`, its URL, product ID, or supplier SKU.
- Supplier, sourcing, purchase cost, margin formula, or evidence time.
- Dropshipping, forwarding, transshipment, intermediary warehouse, cloud warehouse, `一件代发`, `云送仓`, or `中转`.
- Invented warehouse, origin, destination, delivery promise, production method, handmade claim, or brand association.


## Step 6: Create the Etsy Draft

Read [references/etsy-editor.md](../references/etsy-editor.md), then use the available authorized browser/computer-use tool.

1. Open Listings and reread the current shop state.
2. Select the dedicated same-category master only if it has zero photos, zero tags, no variations or custom fields, and blank product-specific attributes. Choose `Copy`. If Etsy cannot retain a zero-photo master, use a new blank listing and set the same verified category and approved delivery profile instead.
3. Upload the 15 new images into the empty photo set. When the validated folder contains exactly those 15 files, navigate the Windows picker to the folder and use `Ctrl+A` for one-shot upload; avoid long absolute-path lists because the picker can truncate them. Read the actual image count and the current editor limit; do not assume a fixed remaining-slot label and retry only the specifically missing files once. Do not use deletion as part of the unattended path.
4. Replace the title and description.
5. Verify tags are already empty when tags are skipped. Write only confirmed dimensions, color, and other accurate attributes. In unattended mode, treat copied variations, custom fields, or conflicting claims as a template-integrity failure instead of trying to clean them up.
6. Set the calculated USD price and quantity. Leave SKU empty unless the user explicitly supplies an Etsy-facing SKU.
7. Preserve `How It's Made` and `Settings` unchanged.
8. Click `Save as draft`. Never click `Publish copy with changes` or `Publish`.

After every verified stage, atomically update `automation-state.json`. If Computer Use is stopped or fails, stop all Computer Use calls immediately, record whether Etsy had unsaved or saved changes, and leave the item recoverable.


## Interrupted-Run Recovery

1. Read `automation-state.json` and reacquire the lease only when it is absent, owned by the current worker, or expired.
2. Before retrying any Etsy write, reopen Listings and search for the exact product identity or stored draft ID.
3. If the draft exists, reopen it and continue from the first unmet verification gate. Do not create another copy.
4. If the prior action outcome is unknown, reread the target before one idempotent retry. Never issue an alternate write in the same recovery cycle.
5. Record `WAITING_LOGIN`, `WAITING_CAPTCHA`, or `WAITING_RUNTIME` and send one deduplicated alert only for those blocker classes. Keep normal progress silent.


## Step 7: Independent Final Readback

Do not treat a save click or success toast as completion.

1. Return to Listings and refresh.
2. Confirm the Draft count increased or the target draft is present.
3. Open the draft and verify the `Draft` badge, exact title, price, quantity, image count, tag state, and relevant copied attributes.
4. Confirm `You have no unsaved changes`.
5. Confirm the listing was not published and the Active count did not increase because of this item.

Return `VERIFIED_SUCCESS` only when all checks pass. Use `PARTIAL`, `BLOCKED`, `FAILED`, or `UNVERIFIED` honestly otherwise.


## Completion Report

Report in Chinese:

- Status and Etsy draft ID or editor URL when visible.
- Product title, image count, price, quantity, and tag state.
- Cost calculation using internal numbers, while confirming those numbers were excluded from buyer-facing fields.
- Queue/Feishu/Dashi result when queue mode was used.
- Verification evidence and any blockers.

Never expose credentials, cookies, tokens, localStorage, sessionStorage, or app secrets.
