# Material and Global Process Library

Use for PROCESS, FULL-A, and FULL-B when the project needs deeper material/process research. This is a routing library, not proof that a specific substrate or supplier is compatible. Apply P2 and P3 from `../SKILL.md`.

## Material record

Every material candidate needs:

- Material Code (`M##`) and exact commercial/supplier identity;
- generic material family and relevant subtype/grade;
- finish, coating, plating, treatment, weave/structure, transparency, or surface texture;
- thickness/weight/density only from supplier or measured evidence;
- Product component and functional role;
- food/skin/wash/outdoor/heat/chemical/abrasion exposure as applicable;
- dimensional/curvature/rigidity and fixture implications;
- supplier, lot, documentation, sample ID, and status;
- allowed processes, prohibited processes, and Unknown compatibility;
- care, labeling, regulatory, and claim evidence where relevant;
- cost, lead time, MOQ, color/finish consistency, and substitution risk as documented inputs.

Status is Draft / Documented / To Be Tested / Tested / Active / Retired. “Metal,” “wood,” “fabric,” or “acrylic” alone is never an Active material definition.

## Material-family routing questions

| Family | Required distinctions before process selection |
|---|---|
| Metal | alloy/grade, coating/plating/paint/anodizing/polish, corrosion, heat response, curvature, burr, contact/cleaning |
| Wood | species/engineered board, grain, moisture, resin, coating/stain, thickness, warp, char/smoke, edge finish |
| Acrylic / Plastic | polymer type, cast/extruded or supplier identity, color/opacity, film, heat/solvent stress, edge and flame behavior |
| Textile | fiber content, knit/weave, stretch, weight, pile, coating, color migration, wash, stabilizer/hoop response |
| Leather / Leather-like | genuine/synthetic identity, tanning/coating, thickness, finish, heat/pressure response, grain variation |
| Glass / Ceramic | composition/type, tempering/glaze, shape/curvature, heat/impact risk, coating, food/wash claims |
| Paper / Board | fiber/coating, weight/caliper, grain, print/foil/score/fold behavior, moisture, archival and packaging role |
| Composite / Coated Product | every layer, adhesive, finish, hidden substrate, temperature/chemical limits, delamination risk |

If the exact distinction is absent, mark compatibility Unknown and require supplier evidence or a physical sample.

## Global process record

Each process candidate needs:

- Process Code (`PR##`) and precise process name;
- primary structure/decoration/finishing/assembly/packaging role;
- compatible material evidence and prohibited/unknown materials;
- visual vocabulary: line, fill, depth, texture, color, gradient, relief, stitch, edge;
- detail, text, gap, registration, curvature, and filled-area limits from dated evidence only;
- variable-data/personalization method;
- required master, release, machine, mask, toolpath, digitized, or separation files;
- fixture/tooling, setup, manual steps, finishing, curing/cleaning, and inspection;
- small-batch, batch, and scalability direction;
- durability, care, safety, and environmental risks;
- internal equipment profile or supplier profile;
- cost/lead-time inputs and status.

## Open process families

Use these as search routes and compare only 3–5 relevant candidates per Product:

- Laser: marking, engraving, cutting, ablation; exact source/material fit must be documented/tested.
- Printing: UV, screen, pad, sublimation, direct-to-garment/textile, transfer, digital or specialty print.
- Embroidery/Textile: flat embroidery, appliqué, patch, specialty stitch/texture only when capability exists.
- Metal: mechanical engraving, etching, stamping, embossing, forming, machining, casting, plating/coating.
- Wood: laser, CNC routing/carving, print, inlay, stain/paint/finish, hand craft.
- Leather: marking/engraving, deboss/emboss, foil, print, cut/stitch, edge finishing.
- Acrylic/Plastic: laser/CNC cut/engrave, UV print, forming, casting, bonding, edge finishing.
- Glass/Ceramic: etch, print, decal, firing, sandblast, engraving, glaze-related process by specialist.
- Paper/Packaging: digital/offset/screen print, foil, emboss/deboss, die cut, score/fold, lamination.
- CNC/Cutting/Forming: routing, milling, turning, waterjet, knife cutting, bending, forming.
- Additive/Casting: 3D printing, resin/metal/plaster casting, mold-based processes.
- Surface Finishing: polishing, tumbling, coating, plating, staining, painting, sealing, curing.
- Hand/Hybrid: hand finishing, assembly, mixed-process decoration, supplier partnership.

This list is open. A more appropriate process should be added with evidence rather than forced into a listed family.

## Process comparison and selection

Use the comparison fields from `manufacturing-engineering-gate.md`, then add:

- supplier geography and continuity;
- tooling ownership and re-order portability;
- setup amortization and batch breakpoints from real quotes;
- design translation cost and file ownership;
- inspection method and rework/disposition path;
- personalization-data handling and proof handoff;
- regulatory or safety evidence relevant to the Product.

Select Best Overall, Premium, Cost-efficient, Small-batch, Scalable, and Personalization routes. One route may fill several positions. Current equipment is checked only after Ideal Process selection.

## Material–process matrix

Use one row per proposed exact tuple:

| Material Code | Finish Code | Process Code | Product Zone | Evidence | Compatibility 1–5 | Translation | Test ID | Status |
|---|---|---|---|---|---:|---|---|---|

Status: Proposed / To Be Tested / Conditional / Tested Pass / Tested Fail / Retired. A matrix cell without evidence is Unknown, not a pass.
