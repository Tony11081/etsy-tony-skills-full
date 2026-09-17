# Manufacturing Engineering Gate

Apply P2 and P3 from `../SKILL.md`. This gate occurs before Design Families are recommended.

## 1. Product, material, and zones

Record the Product form, components, material candidates, geometry, rigidity/flexibility, coatings or finishes, assembly, main viewing side, functional zones, decoration zones, grip/contact/edge areas, washing/cleaning, abrasion, food/skin contact, and expected environment.

For each real surface zone decide:

- main motif, secondary motif, text, and personalization suitability;
- functional, ergonomic, cleaning, or safety interference;
- wear and scratch exposure;
- fixture, positioning, and registration difficulty;
- labor/setup impact;
- compatible process candidates.

Missing physical facts remain `Unknown — Physical Sample Required`.

## 2. Ideal Process Exploration

Before reading the current production profile, identify only 3–5 processes genuinely relevant to the Product. The open search space may include laser, printing, embroidery/textile, metal, wood, leather, acrylic/plastic, glass/ceramic, paper/packaging, casting, CNC, additive, finishing, hand craft, hybrid, or a better product-specific process.

For every candidate compare:

| Criterion | Required judgment |
|---|---|
| Visual Quality | line/fill/texture/depth/contrast character on the real material |
| Material Compatibility | substrate, coating, heat, chemistry, deformation, adhesion, corrosion |
| Detail Capability | text, stroke, gap, counter, gradient/halftone where relevant |
| Durability | cleaning, wash, scratch, UV, handling, food/skin contact as applicable |
| Personalization | unit-level variable data and proof/file implications |
| Small Batch / Scale | setup, batch economics, repeatability, throughput direction |
| Complexity / Labor | tooling, fixture, registration, color/tool changes, finishing, inspection |
| Cost / Lead Time | Low/Medium/High direction only unless real inputs exist |
| Premium Potential | perceived and actual finish quality, not mockup effect |
| Failure Risk | likely physical or visual failure and detectability |
| Supplier Availability | in-house, common supplier, specialist supplier, Unknown |
| Production Files | vector, raster, embroidery digitization, mask, toolpath, separations, or Unknown |

Then name Best Overall, Premium, Cost-efficient, Small-batch, Scalable, and Personalization processes. One process may fill multiple roles when justified.

## 3. Material–process and process–style compatibility

Do not treat a generic material label as proof. Metal type, coating, plating, paint, polish, anodizing, and curvature can change process behavior. The same applies to wood species/finish, acrylic type, textile structure, leather coating, ceramic glaze, and other real substrates.

Check whether the intended visual language survives the process:

- line art may require minimum line/gap validation;
- filled areas may reveal banding, heat, stitch, or surface inconsistency;
- tiny counters or script joins may close, break, or become unreadable;
- watercolor/gradient may require print, halftone, separations, or a different visual translation;
- embroidery requires digitized stitch logic, underlay, density, pull compensation, and fabric tests;
- engraving/marking may produce only material-dependent contrast, not a chosen mockup color.

When translation is required, state:

- Required Design Translation
- Required File Type
- What visual property is preserved
- What visual property is lost or changed
- Sample Test
- Main Failure Risk

Examples of translation categories include Line Art, closed vector, outlined type, reduced detail, halftone, color separation, digitized embroidery, toolpath, mask, and short/long personalization states. Do not invent numeric thresholds.

## 4. Current Capability Check

Only after Ideal Process selection, read `production-profile.md` and classify each route as exactly one of:

- In-house Verified
- In-house Available but Untested
- In-house with Modification
- Outsource Recommended
- Supplier Partnership Candidate
- Equipment Investment Candidate
- Experimental
- Not Recommended

If the Ideal Process is not verified in-house, keep it and report:

- Ideal Process
- Current In-house Capability
- In-house Alternative
- Visual / Quality Trade-off
- Outsource Route
- Future Capability Candidate
- Required Validation

No model, machine name, or general knowledge may fill a parameter absent from the profile. Use `Unknown`, `To Be Tested`, or `Awaiting Capability Data`.

## 5. Process Compatibility Score

Score 1–5:

| Score | Meaning |
|---:|---|
| 5 | Material, motif, typography, position, and process are highly compatible; route is clear. |
| 4 | Compatible; only routine sampling remains. |
| 3 | Conditionally compatible; explicit translation or focused testing is required. |
| 2 | Clear conflicts require major redesign. |
| 1 | No reasonable implementation path. |

Passing line: `≥3`.

Every score of 3 must include Required Design Translation, Sample Test, and Main Failure Risk. A score below 3 is a Hard Gate veto and cannot enter Top 3. A valuable blocked concept becomes `Requires Manufacturing Redesign` with a concrete translation path; do not silently delete it.

## 6. Manufacturing Gate checklist

- Ideal Process was explored before current equipment.
- Current equipment did not become the design boundary.
- Material and finish compatibility are evidenced or explicitly unverified.
- Motif, typography, and Placement can be expressed by the process.
- Functional, grip, cleaning, edge, and safety zones remain protected.
- Required translation and production file are identified.
- Unknown parameters and required tests are explicit.
- In-house, outsource, supplier, alternative, or investment route is identified.

Gate result:

- `PASS`: credible route with no unresolved critical conflict.
- `CONDITIONAL PASS — Sample Required`: concept may proceed to design and sampling inside stated limits.
- `FAIL — Requires Manufacturing Redesign`: no recommendation until the conflict changes.

## 7. Production Readiness Gate

Production Status must be exactly one of:

- Concept
- Awaiting Capability Data
- Sample Required
- Sample Passed
- Approved
- Rejected

Without a real sample record, never use `Sample Passed` or `Approved`. A STANDARD recommendation may be `Sample Required` only if it states Test Material, Test Design Feature, Pass Criteria, and Main Risk.

## 8. Production Feasibility Score

| Score | Meaning |
|---:|---|
| 5 | A proven internal or mature supplier route exists with low risk. |
| 4 | Route is clear; routine sampling remains. |
| 3 | Principally feasible; material, machine, supplier, or critical detail still needs validation. |
| 2 | Major redesign or complex supply chain is needed. |
| 1 | No reasonable current route. |

Top 3 requires `≥3`. Feasibility does not override another failed Hard Gate.

## 9. Validation record

For every recommended sample record: material and supplier/lot, finish, Product/zone, artwork and version, process/equipment/supplier, fixture, actual settings from the operator, result images, measured observations, defects, pass criteria, pass/fail, approved scope, date, operator, and reviewer. A pass applies only to the tested scope.
