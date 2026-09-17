# 原创新品开发流程

开发时按阶段读取：未选款执行 1–6；已有明确选款与场景请求时复用上游证据，执行 7–8。

下列命令和非链接相对路径均以本 Skill 的目录为基准。

## Workflow

### 1. Capture the Source

Open the public Etsy URL, preferring the Codex in-app browser and using an already authorized browser only when necessary. Save the source URL, access time, and the visible product gallery or user-supplied images.

Record each product fact as one of:

- `visible_fact`: directly visible in images or page fields
- `seller_claim`: stated by the Etsy seller but not independently proven
- `inference`: plausible from visual evidence but unconfirmed
- `unknown`: not safely determinable

Capture only facts relevant to product identity, components, function, material or finish, dimensions, variants, personalization, construction, manufacturing, installation, use, and photography. Preserve `Unknown`; never turn it into a guess.

### 2. Separate Inspiration From Expression

Create `source-audit.md` with:

- `product_identity`
- `buyer_job_and_function`
- `functional_mechanism`
- `component_map`
- `materials_and_finish`
- `likely_processes_with_confidence`
- `category_conventions`
- `distinctive_expression`
- `must_not_copy`
- `scene_language`
- `unknowns_and_required_confirmation`

The scene analysis may describe lighting softness and direction, camera distance and angle, depth of field, environment type, product scale cues, prop purpose, color relationship, and buyer question answered. Do not save competitor images as final deliverables or remove their watermarks.

### 3. Build the Manufacturing Brief

Create `manufacturing-brief.md` before concept generation. For each plausible construction path, state:

- material and part categories
- process sequence
- machinery, tooling, or supplier type
- assembly and finishing steps
- fragile tolerances or quality checks
- packaging and shipping risks
- safety, labeling, or regulatory questions
- what can be sourced commonly versus what needs custom development
- complexity: `low`, `medium`, or `high`, with reasons
- prototype tests required before production

Prefer products that preserve the buyer job while using locally accessible materials and common processes. If feasibility depends on an unverified process, mark the concept `CONDITIONAL`, not easy.

### 4. Create the Originality Brief

Write:

- `may_inspire`: generic function, buyer need, common construction principle, category-standard feature, broad photography principle
- `must_change`: the design axes that will create a different overall impression
- `must_not_copy`: protected, branded, artistic, or distinctive source expression
- `manufacturing_constraints`
- `similarity_failure_conditions`

Each concept must materially change at least four applicable axes: overall silhouette or geometry, component layout, interaction or function execution, motif or surface language, material or finish, color system, proportions or dimensions, assembly method, personalization system, or included-piece relationship.

### 5. Produce Three Concept Directions

Default to:

1. `easy-to-make`: lowest process risk using common materials and tools
2. `balanced-commercial`: strongest balance of differentiation, cost, shipping, and buyer appeal
3. `premium-differentiated`: higher perceived value with a clearly different design language

For each concept provide:

- concept ID and original working name
- buyer job and main benefit
- short design description
- explicit differences from the source
- materials, parts, and finish
- process and supplier requirements
- manufacturability rating and unknowns
- packaging and shipping considerations
- IP or similarity risk
- facts the user or manufacturer must confirm

Generate one separate square concept render per concept. Build each prompt from the new concept brief. Use source images only to understand product category and function; do not ask image generation to reproduce the source design or source scene. Do not add logos, copied text, copied patterns, trademarks, watermarks, or characters.

Compare each render against all source images. Reject and regenerate if it copies a distinctive motif, ornamental placement, silhouette, component arrangement, pattern, or overall impression. Save the accepted concept sheets and renders under `concepts/`.

### 6. Approval Gate

Present the three concepts side by side with their manufacturing tradeoffs. Ask the user to select one, merge specified elements, or request revisions.

Stop here until the user explicitly approves a concept. Record the approval in `approval.json` with:

- `approved_concept_id`
- `approved_render`
- `locked_function`
- `locked_components`
- `locked_materials`
- `locked_finish_and_colors`
- `locked_dimensions` or `dimensions_unknown`
- `locked_process`
- `approved_variants`
- `remaining_unknowns`

User approval of a concept does not prove physical manufacturability. Keep prototype and supplier-validation items open until evidence is supplied.

### 7. Open the Photo Gate

After approval, classify the next phase:

- `prototype-locked`: readable prototype or production images exist; eligible for listing-ready campaign planning
- `spec-locked`: no prototype, but the user confirms a complete manufacturer-ready specification; generate carefully and mark physical fidelity unverified
- `concept-only`: generate only pre-production scene mockups with the disclosure above

The approved concept, prototype, and locked specification become the only product-truth references. The competitor Etsy images become scene-analysis references only.

Create a new scene strategy that may learn abstract photographic principles but not duplicate the source. Across every source-like shot, change at least three applicable elements: location, background architecture, prop family, camera height or azimuth, crop, product placement, color palette, lighting direction or temperature, model styling, human action, or narrative purpose. A similar camera angle alone is acceptable only when the total composition is clearly different.

Broad styling colors may inspire a new palette, but do not reproduce a distinctive outfit, textile pattern, accessory combination, pose, or model identity. Product colors and dimensions must come from the approved new-product specification, not the competitor listing.

Then follow `etsy-tony-full-photo-engine`:

- plan the complete set before generation
- generate `shot-01` as a health probe
- inspect it before continuing
- use one image-generation call per distinct shot
- preserve only accepted images
- use environmental scale cues when dimensions are unknown
- render exact numeric dimensions only from locked data using deterministic overlays
- audit product fidelity, scene originality, and campaign variety

### 8. Final Audit and Delivery

Create `similarity-audit.md` and `manifest.json`. Verify:

- no copied branding, artwork, pattern, text, character, motif, silhouette, or overall composition
- approved product function and components are present
- unconfirmed facts remain labeled unknown
- every visible dimension and color matches locked data
- scene composition differs materially from the competitor references
- every final image answers a different buyer question or adds new value
- rejected and regenerated images are recorded
- prototype status and manufacturing verification state are explicit

Save outputs as:

```text
<run-dir>/
  source-audit.md
  manufacturing-brief.md
  originality-brief.md
  reference-images/
  concepts/
    concept-a.md
    concept-a.png
    concept-b.md
    concept-b.png
    concept-c.md
    concept-c.png
  approval.json
  photo-plan.json
  prompts/
  photos/
  similarity-audit.md
  fidelity-audit.json
  manifest.json
```

Report one final status:

- `VERIFIED_SUCCESS`: required source evidence, approved design, manufacturing facts, final assets, and independent audits all pass
- `PARTIAL`: useful stages are complete but later approval, prototype, or images remain
- `BLOCKED`: source access, user approval, reference quality, or required facts prevent safe continuation
- `UNVERIFIED`: outputs exist but physical manufacturing or final fidelity lacks evidence

Never call a generated concept, submitted image request, local folder, or tool completion business success without reopening and validating the final artifacts.
