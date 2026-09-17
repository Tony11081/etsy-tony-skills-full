# Typography and Color Systems

Use this Phase 2 reference for FULL-A design-system expansion and FULL-C launch consistency. It extends the Design Gate without replacing `design-theory-framework.md`. Apply P1 and P3 from `../SKILL.md`.

## Typography library contract

Build a project-specific typography register. A class is a search and decision aid, not a licensed production font.

| Typography class | Useful qualities | Common risks | Typical role candidates |
|---|---|---|---|
| Humanist Sans | readable, warm, flexible | may feel generic without composition discipline | names, instructions, supporting text |
| Geometric Sans | clean, structured, modern | circular forms and tight spacing may close at small scale | modern names, monograms, display text |
| Old-style / Transitional Serif | heritage, readable, editorial | fine serifs and contrast may fail in small marks/stitches | names, archival systems, dates |
| Slab Serif | sturdy visual weight | dense blocks and counters may become heavy | short display words, robust marking |
| Script / Calligraphic | ceremony and personal gesture | joins, flourishes, licensing, long-name crowding, generic wedding similarity | short accent only after process tests |
| Handwritten | informal, personal | poor consistency and glyph coverage | selected casual concepts only |
| Monogram Display | strong initials and identity | ambiguous letter pairs and manual proof load | controlled initial systems |
| Decorative / Historic | distinctive period signal | style soup, readability, cultural misuse, licensing | limited display role only |

Do not select typography from category mood alone. Each candidate must pass:

- semantic and period fit;
- primary/secondary role clarity;
- process expression and minimum-detail testing;
- short, medium, long, dual-name, initials, date, punctuation, case, and required glyph stress tests;
- real commercial-use license evidence;
- editable-master and outlined-release workflow;
- customer-facing label that does not expose confusing technical names.

### Typography register fields

| Field | Required content |
|---|---|
| Font Code | `F##`, unique within the controlled register |
| Buyer-facing Label | natural, non-technical name |
| Internal Font / Version | exact file/family/version used |
| License Evidence | source, scope, date, storage reference; Unknown until documented |
| Role | primary, secondary, accent, fallback, monogram |
| Allowed Families / SKUs | explicit scope |
| Process Scope | tested process/material combinations only |
| Glyph Scope | supported characters/languages actually checked |
| Length Rules | tested states and fallback trigger; no invented character limit |
| Status | Draft / To Be Tested / Tested / Active / Retired |
| Last Review | date and reviewer |

Never release a font because a mockup is readable. Production readability is limited to the tested material, process, scale, and file preparation.

## Color framework

Color is a design and production decision, not a render decoration. Separate:

- Material Color: inherent substrate appearance.
- Finish Color: coating, plating, stain, glaze, thread, film, ink, or other applied finish.
- Graphic Color: process-created mark or printed/decorated color.
- Perceived Color: light-, reflection-, texture-, and camera-dependent appearance.
- Buyer-facing Color Name: the truthful label supported by actual samples.

### Color-system decisions

For every Family define:

- dominant, supporting, accent, and neutral roles;
- value hierarchy and required text/background contrast;
- hue/saturation/temperature logic;
- harmony type only when it helps the design decision;
- material/finish interaction, reflection, transparency, texture, and metamerism risk;
- process gamut, number of colors, registration, gradient/halftone needs, and batch variation;
- photography and screen variation disclosure;
- allowed combinations and prohibited low-contrast pairs.

### Color register fields

| Field | Required content |
|---|---|
| Color Code | `C##`, unique controlled code |
| Buyer-facing Label | truthful natural name |
| Color Role | dominant/supporting/accent/neutral/text/background |
| Physical Source | material, finish, thread, ink, film, supplier reference, or Unknown |
| Digital Reference | design reference only; identify color space and source |
| Production Reference | supplier/process standard or physical swatch evidence |
| Allowed Material / Process | explicit tested scope |
| Contrast Rules | allowed text/background pairs and validation method |
| Sample Evidence | sample ID/photo/measurement reference or Unknown |
| Batch Tolerance | approved evidence or To Be Tested; do not invent numbers |
| Status | Draft / To Be Tested / Tested / Active / Retired |

Do not promise exact screen-to-product color. Do not call an engraving “gold,” “silver,” “black,” or another color unless the actual material/process result supports that buyer-facing claim.

## Typography–color–process compatibility

Before release, test each allowed tuple:

`Font Code × Color/Finish Code × Material Code × Process Code × Size/Artwork State`

This is a validation matrix, not a Cartesian-product SKU generator. Record only combinations the product actually offers. A failed tuple must be prohibited, translated, or separated; it cannot remain available because its individual codes are valid elsewhere.

## Phase 2 output

FULL-A creates only the typography and color registers required by approved Families. FULL-B records sample-backed process scope. FULL-C exposes only Active buyer-facing options and keeps internal fallback logic out of customer menus unless an image and ordering rule explain it safely.
