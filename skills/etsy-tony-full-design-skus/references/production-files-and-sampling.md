# Production Files and Advanced Sample Testing

Use for FULL-B after approved SKUs and a credible process route exist. This reference does not set machine parameters or approve production without recorded samples.

## Production file package

Separate these artifacts:

- Editable Master: source artwork/type/layout with licensed resources and version history.
- Proof File: buyer/manager review image; not a machine file.
- Release File: outlined, flattened, separated, digitized, masked, or otherwise prepared for one process scope.
- Machine/Supplier File: process-specific output accepted by the named equipment/supplier.
- Setup Reference: orientation, zone, scale, fixture/alignment, layer/color/tool legend, and safe-zone reference.
- Inspection Reference: approved sample images and critical visual/functional checks.

Every release package records Base SKU, Production SKU/configuration scope, artwork version, material/finish/size/process codes, equipment/supplier, Product orientation, physical scale, units, date, preparer, reviewer, and status.

## File naming and change control

Use stable ASCII names:

`[ProductionSKU]_[ARTWORK]_[PROCESS]_[VERSION]_[STATUS].[ext]`

Example structure only: `CS-MCC-HZN-01-M01-FN01-PR01_ART01_PR01_V03_RELEASE.svg`.

Status: DRAFT / PROOF / TEST / RELEASED / RETIRED. Never overwrite a released file silently. A change to geometry, typography, process translation, scale state, or personalization logic creates a new artwork/file version and may require re-testing.

## Process-specific file questions

| Process family | Required questions before release |
|---|---|
| Laser / engraving / etch | vector/raster support, scale/units, line/fill behavior, text outlines, mask/toolpath needs, orientation, material-specific translation |
| Print / transfer | color space/profile, spot/process colors, white/underbase, separations, bleed, resolution at output size, substrate and curing/transfer notes |
| Embroidery | digitized file ownership, thread chart, sequence, underlay, density/pull compensation evidence, hoop/orientation, stabilizer, trim/jump plan |
| CNC / cutting / forming | closed paths, toolpath/kerf/bit/tool ownership, depth/layer, tabs/hold-down, origin, units, material thickness evidence |
| Foil / stamp / emboss / deboss | die/tool file, relief/depth evidence, pressure/heat scope, registration, material/finish compatibility |
| Assembly / packaging | part revision, hardware/adhesive, orientation, sequence, inspection points, packaging fit/protection |

Do not invent supported formats; obtain them from the actual equipment profile or supplier.

## Advanced sample stages

Use only the stages needed by risk:

1. Material Coupon: basic compatibility, contrast/color, line/gap/text/fill ladder, adhesion/heat/chemical response.
2. Geometry/Fixture Sample: actual Product curvature, orientation, zone, registration, edge/grip clearance, repeatability.
3. Personalization Stress Sample: short/medium/long, dual names, initials/monogram, date, punctuation, case, required glyphs, invalid inputs.
4. Design Sample: full Family/SKU hierarchy, motif, negative space, actual finish and viewed distance.
5. Durability/Care Sample: relevant wash, cleaning, scratch, abrasion, UV, outdoor, food/skin contact, flex or impact method backed by Product requirements.
6. Packaging/Transit Sample: abrasion, movement, bend/crush/moisture risks, presentation, correct components and instructions.
7. Pilot Run: repeated units across realistic operators/batch conditions, defect/rework/time/cost capture.

A low-risk project may combine stages when the record still proves each acceptance criterion. Do not skip a critical stage merely to reduce documentation.

## Test plan contract

Each plan records:

- Test ID, objective, risk/hypothesis, Product/SKU/version;
- exact material/finish/supplier/lot and Product zone;
- equipment/supplier/process/fixture and operator;
- file and artwork version;
- input states and control/reference sample;
- actual settings entered by the operator, not generated from model knowledge;
- inspection method, acceptance criteria, failure definitions, and evidence required;
- result, defects, measurements/observations, images, rework, conclusion, approved scope;
- date, operator, reviewer, and next action.

Acceptance criteria may be qualitative when numeric thresholds do not exist, but they must be observable and binary enough to support pass/fail. Mark missing thresholds `To Be Established by Test`.

## Status transitions

- Concept → Awaiting Capability Data: route selected but critical inputs absent.
- Awaiting Capability Data → Sample Required: enough evidence exists to run a controlled test.
- Sample Required → Sample Passed: recorded test passes all criteria for the exact scope.
- Sample Passed → Approved: manager releases the exact scope with files, QC, options, supplier/equipment, and evidence complete.
- Any status → Rejected: failed Hard Gate or unrecoverable test result.

Approval never transfers automatically to another material, finish, size, supplier, process, file version, or option tuple.
