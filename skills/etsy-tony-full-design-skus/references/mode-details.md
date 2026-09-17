# 按交付选择深度

先按请求选择：初判 QUICK；工艺 PROCESS；设计研究 DESIGN；先看方案 VISUAL；系列与 SKUs 用 STANDARD；完整深度开发才用 FULL。进入所选模式前读取对应段落，不默认跑完整流程。

下列命令和非链接相对路径均以本 Skill 的目录为基准。

## Runtime modes

Use the smallest matching mode before considering STANDARD: QUICK for an initial judgment, PROCESS for manufacturing, DESIGN for design study, and VISUAL for requested concept-image choices. Use STANDARD when the user requests a developed set of Design Families and SKUs; if scope remains vague, start with QUICK. FULL still requires its explicit scope below.

### VISUAL

Use for “先出图”, “生成一些产品图片”, “给我几个/各种方案”, “多做几个效果图”, “让我自己挑”, “先看视觉方向”, or an equivalent image-first request.

Round 1 defaults to six separate concept images, `V01–V06`, organized as three clearly different Visual Families with two concepts each. Generate one concept per image rather than one small six-panel image. Preserve the same Product identity, camera logic, and comparable presentation while changing meaningful design axes. Use a compact pre-visual screen for Product identity, functional zones, obvious process impossibility, and competitor-specific/IP exclusions; do not run or display full STANDARD analysis, score matrices, Design Family Cards, SKUs, Manufacturing Cards, QC, or Listing copy before the images.

Deliver the six actual images, saved paths, evidence label, and a one-line selection note for each. Stop after Round 1 and ask the user to choose `V01–V06` or request a mix of specified features. Do not choose a winner for the user.

After the user selects one or two directions, remain in VISUAL only if they ask for visual refinement; then generate up to three higher-quality refinements per selected direction. Switch to STANDARD only when the user asks to develop the selected direction into Design Families, SKUs, manufacturing, or ranking. An unselected concept receives no detailed downstream analysis.

### QUICK

Use for “值不值得做”, “快速看一下”, “先判断”, or “要不要开发”. Return GO, MAYBE, or NO-GO plus Product, buyer, motivation, competitor hook, main Design DNA, 1–3 relevant Ideal Process candidates, opportunity, risk, originality risk, production difficulty, recommendation, at most one Design Direction, and at most three Concept Directions. Do not create Manufacturing Cards, full options, a Listing, six/twenty SKUs, or a full score matrix.

### STANDARD

Default daily mode. Create exactly two Design Families and up to three qualified SKUs per Family, targeting six SKUs total, then rank a Top 3 from Hard-Gate-qualified candidates. Generate one clearly labeled Top 3 concept board only after ranking and visually inspect it. Include evidence, product/buyer, architecture/zones, process exploration, capability check, competitor DNA, design theory, customization/dependencies, all Gates, basic production assessment, ranking, concept-image evidence, and employee actions. Do not expand into full QC, complete sample plans for every SKU, complete Etsy descriptions, or Phase 2 libraries.

### PROCESS

Study materials, surface zones, 3–5 relevant Ideal Processes, process comparison, current internal capability, outsourcing, supplier partnership, alternatives, investment candidates, and required tests. Do not generate SKUs.

### DESIGN

Study competitor DNA, elements, Element Styles, typography, color, composition, design theory, and Design Families. Apply known material/process constraints, but do not produce a full production plan or Listing. Do not generate complete SKUs unless the user changes mode.

### FULL

Use only when the user explicitly requests FULL, or explicitly confirms that an approved STANDARD project should enter deep development. FULL may be staged:

- FULL-A: research, process exploration, four Design Families, and up to twenty qualified SKUs.
- FULL-B: selected-SKU Manufacturing Cards, production codes, customization, sample plans, QC, supplier/cost decisions, equipment evaluation when relevant, three visually inspected pre-production mockups—clean front concept, use-scene concept, and personalization-state concept—and an editable design-artwork pack containing a concept vector, personalization-state vector, previews, and manifest.
- FULL-C: advanced IP review, Listing Launch Pack, image plan, commercial readiness, final ranking, and production-release artwork only for the exact sample-backed and approved scope.

FULL-B requires approved STANDARD/FULL-A candidates. FULL-C may create a blocked draft before samples, but `Listing-Ready` requires the exact sample-backed production scope. Do not sacrifice quality to finish all stages in one response. Installing Phase 2 does not automatically run FULL.
