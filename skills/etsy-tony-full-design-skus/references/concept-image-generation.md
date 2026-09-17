# Concept Image Generation Rules

Use this reference in VISUAL, STANDARD, and FULL-B. VISUAL assets help the user choose a direction before heavy analysis; STANDARD/FULL-B assets validate decisions already made. They are not Etsy listing photography and cannot close manufacturing or release Gates.

## When to generate

- VISUAL Round 1: after a compact pre-visual screen, generate six separate concepts (`V01–V06`) before full analysis. Stop and wait for user selection.
- VISUAL refinement: only after selection, generate up to three refinements per selected direction when requested.
- STANDARD: lock the qualified Top 3 first, then generate one comparison board containing exactly those three ranked SKUs.
- FULL-B: lock the selected Base SKU, customization architecture, and production unknowns first, then generate three separate assets: clean front concept, use-scene concept, and short/medium/long personalization-state concept.
- QUICK, PROCESS, and DESIGN: generate no image unless the user explicitly requests one.
- FULL-C: follow the separate listing-image evidence ladder in `listing-and-image-launch-rules.md`.

For VISUAL, do not run the full Originality Gate before Round 1, but remove competitor-specific/protected expressions from the brief and generate independently from Product/buyer needs. STANDARD and FULL-B still require the applicable Originality Gate first. Do not use an attractive render to rescue a failed candidate.

## VISUAL pre-visual screen

Keep this internal or report it in at most twelve short bullets:

- Product identity and what must not change;
- owned/authorized base image versus competitor evidence;
- main functional, grip, edge, opening, cleaning, safety, or wear zones;
- confirmed material/finish facts and Unknowns;
- target buyer, occasion, emotional direction, and price position if known;
- required and forbidden elements;
- obvious process/material conflicts to avoid in the render;
- competitor-specific artwork, composition, branding, characters, and text to exclude;
- typography treatment: directional placeholder versus exact text;
- output count, view, background, and scene preference.

Do not produce Product Architecture tables, full process comparisons, Gate scores, or SKU rankings in VISUAL Round 1.

## Required generation behavior

Use the available image-generation tool rather than returning text-only prompts. Generate one VISUAL concept per image so each direction has enough detail and resolution; do not substitute a six-panel sheet for the six source images. Save every delivered image in the case output—default to `./etsy-output` when no project output is specified—and complete `templates/concept-image-manifest.md`. Deliver the actual images in chat when the interface supports it.

Visually inspect every saved file for Product geometry, subject count, composition, hierarchy, legibility, missing/extra elements, surface continuity, unrealistic attachments/reflections, and conflicts with the concept. Regenerate a rejected asset once with a targeted correction when feasible; otherwise keep it rejected, do not count it toward the six accepted choices, and return `PARTIAL` if the set cannot be completed.

Prompts must state the Product identity lock, must-preserve geometry, concept narrative, motif treatment, intended hierarchy, composition, Placement, general material appearance, view/camera, background, scene, lighting, and explicit avoid-list. Preserve confirmed facts and leave Unknown facts unspecified.

Image models are not production typography tools. When exact lettering is not essential to the selection, use a blank personalization zone or one short clearly identified placeholder and label typography as directional. When exact text is essential, inspect it and reject material misspelling. After selection, rebuild approved lettering as editable vector artwork; never treat generated text pixels as a production file.

## Originality distance

Concept images may learn the category and buyer need, but must not reproduce competitor-specific artwork, recognizable element combinations, composition, lettering, scene styling, or customization structure. Record meaningful distance on at least four axes such as silhouette, motif system, typography, composition, personalization architecture, material/finish direction, or use-scene styling.

Do not feed a competitor image into an edit or ask for a near-copy. Generate from the approved original design record.

For VISUAL, an owned/authorized blank Product image may be used as the geometry anchor. A competitor image may be analyzed for generic category language but must not be the edit target or visual base.

## Evidence label and prohibited implications

Until the exact production scope has physical-sample evidence, every file entry and delivery caption must say:

`PRE-PRODUCTION MOCKUP / UNVERIFIED AGAINST PHYSICAL SAMPLE`

Before sample verification:

- use environmental scale only; do not invent exact dimensions or thickness;
- do not imply confirmed material, finish, color match, food-contact suitability, durability, process quality, packaging, or included accessories;
- do not label the asset as real product photography, sample, approved, listing-ready, or published;
- keep props visually secondary and do not imply that they are included.

## Asset contracts

### VISUAL Round 1 selection set

- Six separate accepted images labeled `V01–V06`.
- Three clearly different Visual Families with two concepts each unless the user specifies another breadth.
- One stable Product identity and comparable view/background/lighting logic across the set.
- Each concept differs from its siblings on at least three meaningful axes, including at least one of narrative, motif role/treatment, composition/hierarchy, personalization architecture, or Placement strategy.
- Color-only, font-only, flower-species-only, and scene-only changes do not count as separate concepts.
- Keep filenames, prompt records, and manifest IDs aligned.
- Provide a one-line note per concept: Visual Family, main visual hook, and one visible risk/unknown.
- Stop after delivery and wait for the user's `V01–V06` selection; do not assign Base SKU codes or choose a winner.

### VISUAL refinement set

- Refine only selected directions.
- Generate up to three images per selected direction by default: polished clean hero, close-up design/detail view, and optional use-scene or alternate composition requested by the user.
- Preserve the chosen concept's identity; do not silently drift to another Family.
- If the user combines features, state the new combined brief before generation and give it a new visual ID.

### STANDARD comparison board

- One coherent board with exactly three labeled panels in rank order.
- Each panel must retain the approved SKU's distinctive silhouette, hierarchy, and personalization logic.
- The board must make the concepts comparable without collapsing them into one visual Family.

### FULL-B selected-SKU set

1. Clean front concept: isolated view for silhouette, hierarchy, typography, and structural reading.
2. Use-scene concept: realistic occasion context showing general environmental scale without exact size claims.
3. Personalization-state concept: short, medium, and long approved input states, exposing overflow or legibility risk rather than hiding it.

## Failure and status

An image-generation call completing is not delivery proof. Delivery requires the requested number of accepted saved files, completed manifest, visual reread, truthful evidence label, and actual image delivery—not merely prompts or filenames. If any required asset is missing, corrupt, materially inconsistent, duplicated, or not visually inspected, report `PARTIAL`. Concept images never change `Awaiting Capability Data`, `Sample Required`, or other production status by themselves.
