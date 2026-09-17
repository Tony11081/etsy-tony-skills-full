# Option Dependency Rules

The dependency matrix is an executable production contract. Employees must not resolve invalid combinations from memory.

## Required rules

- Material → Allowed Processes
- Process → Allowed Graphic Styles
- Process → Allowed Fonts
- Process → Allowed Colors
- Product Size → Maximum Detail Level
- Placement → Maximum Artwork Area
- Name Length → Font Rules
- Name Length → Layout Rules
- Pattern → Compatible Layouts
- Pattern → Compatible Fonts
- Background Color → Text Color
- Process → Required File Format
- Process → Required Finishing
- Process → Required Test
- Transparent/Subsurface Product → Print Side
- Print Side → Mirror / White Ink / Layer Order / Surface Protection / QC
- Acrylic Type and Thickness → UV / Laser / Cutting / Slot Fit
- Stand/Base Color → Availability / Contrast / Assembly / Photography
- Product Size → Stand Fit / Artwork File / Fixture / Packaging

## Rule format

Each rule has Rule ID, IF condition, THEN allowed/required action, ELSE invalid/fallback, customer message, employee action, evidence source, and test state.

Example:

| Rule ID | IF | THEN | ELSE |
|---|---|---|---|
| R-NAME-01 | name length within tested medium state | use F01 and standard layout | switch to F02 long-name layout; if still over limit, proof required |
| R-EMB-01 | process is Embroidery | use digitized file and stitch-safe fonts/colors | reject gradients and non-digitized artwork |
| R-ACR-01 | clear acrylic + reverse UV | include white ink plan and mirrored layer order | do not release file |
| R-ZONE-01 | placement is handle | use only tested narrow motif/text | reject complex/full design |

Front print, reverse print, and back print are production configurations. Keep one fixed within a Base SKU or split the production identity; do not expose them as a casual buyer Placement choice. A stand/base change must pass supply, contrast, mechanical fit, photography, packaging, and SKU-boundary checks.

## Split rules

Use a Separate SKU or Listing when the process, material, size-specific artwork, fixture, cost, lead time, safety/QC, or buyer intent changes materially. Do not present different production processes as a simple visual option.

## Verification

Test every allowed combination or test a documented equivalence class. The matrix must list invalid combinations explicitly and match the images, SKU database, order form, production card, and Listing options.
