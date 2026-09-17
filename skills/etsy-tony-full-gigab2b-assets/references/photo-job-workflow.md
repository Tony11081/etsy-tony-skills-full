# 素材与图片工作流

素材准备执行步骤 1–3 和结果回读；只有本轮同时请求生成图片才执行步骤 4。报告实际完成的阶段。

下列命令和非链接相对路径均以本 Skill 的目录为基准。

## Workflow

### 1. Read the GigaB2B page

- Open the provided `https://www.gigab2b.com/index.php?route=product/product&product_id=...` link in the user's logged-in Chrome.
- If the page is already open, use that tab.
- If Chrome shows `route=account/login`, stop and ask the user to log in, then continue.
- Read the visible product title and the main product `Item Code` near the top product summary or the selected product information section.
- Avoid similar-products and recommended-products blocks; they also contain `Item Code` values and must not be used.
- Record the source URL, `product_id`, title, and SKU.

### 2. Run the bundled API downloader

Run the script from this skill folder:

```powershell
node scripts/etsy-tony-full-gigab2b-assets.mjs --sku=<ITEM_CODE> --url='<GIGAB2B_PRODUCT_URL>' --shots=15
```

The script uses the recipient's process environment variables `GIGAB2B_CLIENT_ID` and `GIGAB2B_CLIENT_SECRET`. An explicit `--env-file=<PRIVATE_LOCAL_FILE>` is also supported. Users configure their own credentials locally; never request their values in chat, print them or put the file in this repository. `--help` needs no account. A browser-only extraction path is available through `../etsy-tony-full-gigab2b-photos/SKILL.md`. The default output root is:

```text
./etsy-output/gigab2b-photo-runs
```

The script writes:

```text
<outDir>/
  manifest.json
  mandatory-etsy-prompt.txt
  product-photo-campaign-openrouter-handoff.txt
  product-title.txt
  source-image-urls.txt
  source-file-urls.txt
  api-detail.json
  api-price.json
  api-inventory.json
  reference-images/
    ref-01...
  files/
    file-01...
```

### 3. Verify the output

Before generation, confirm:

- `downloadedReferenceImages` is greater than 0.
- `downloadErrors` is 0, or report the exact failed URLs.
- `mandatory-etsy-prompt.txt` matches the prompt above with only the user-requested count substituted.
- `manifest.json` contains the correct SKU, product title, source URL, and product dimensions.
- Product dimensions distinguish assembled/product dimensions from package dimensions. Dimension images must use assembled/product dimensions when present.

Load at least one or two downloaded reference images with `view_image` to confirm the images belong to the target product, not recommendations.

### 4. Generate the 15-image set

Use `etsy-tony-full-photo-engine` for the final image generation. Load that skill's `SKILL.md` before creating final prompts or calling `image_gen`.

Generation requirements:

- Inspect all verified references, then select only the 2-4 most informative original files for each shot. Prefer one clean full-product view plus the alternate angle or detail view that proves that shot's fragile features. Never exceed the image tool's reference limit.
- Do not build oversized contact sheets merely to force every source image into every generation call. Contact sheets reduce product detail, amplify embedded source text, and increase upload/network failures.
- Include the mandatory Chinese prompt verbatim for the default 15-image set (replace only the count when the user explicitly requests another quantity).
- Generate exactly 15 images unless the user asks for a different count.
- Include product display, lifestyle scenes, detail scenes, size/dimension effect, and human-use or partial-body interaction when category-safe.
- Keep camera distance, scale, angle, room scene, product placement, and prop logic diverse.
- Preserve product structure, proportions, color, material, hardware, labels, and buyer-critical details.
- Do not invent dimensions. Do not create messy or overlapping dimension lines.
- Do not add logos, watermarks, random badges, unrelated text, or visible faces unless explicitly requested.

Reliability gate:

1. Persist the complete plan and individual shot prompts before generation so the run is resumable.
2. Generate `shot-01` alone as a health probe, using the shortest complete prompt and 1-2 best original references.
3. Continue only after a real image file exists and has been opened for visual inspection. Generate later shots one call at a time; do not submit multiple image calls concurrently.
4. Keep campaign strategy and product intelligence in the plan file. In each image prompt include only the shot-specific scene, the concise product lock, fragile invariants, and the mandatory user prompt; do not repeat the full planning schema.
5. On a network error, independently check both the built-in generated-image location and the run output folder before retrying. If no image exists, retry once with fewer references and a shorter prompt.
6. If the same image-service network error occurs again, stop as `BLOCKED`. Preserve completed files, prompts, and the list of missing shots for a later resume. Do not treat request submission, waiting, or a plan file as generation success.

### 5. Report

Report concisely:

- Product title
- SKU / Item Code
- Source URL
- Output folder
- Reference image count
- File/PDF count
- Download errors
- Whether generation is ready or complete

If blocked, say exactly which layer blocked the workflow: login, missing SKU on page, OpenAPI credential/API failure, no reference images, or image-generation validation failure.


## Script Notes

- Use `--help` to show script options.
- Use `--dry-run` only for API metadata tests; it does not download reference images and should not be treated as generation-ready.
- If the user only provides a SKU and no URL, the script can still prepare the job, but the report should say the source URL was not provided.
