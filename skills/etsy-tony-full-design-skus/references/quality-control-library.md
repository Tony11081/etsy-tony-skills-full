# Quality Control Library

Use for FULL-B after the exact Product, production route, and sample scope are defined. A QC checklist is process- and SKU-specific; this library does not turn an untested concept into an approved product.

## QC layers

### Incoming inspection

- supplier/product code, material/finish/size/lot, quantity, documents;
- component count, visible damage, contamination, coating/color/texture consistency;
- dimensional or functional checks required by the Product;
- approved-sample comparison;
- hold/quarantine rule for unknown or mismatched inputs.

### Setup and first-article inspection

- correct SKU/configuration, file/version, equipment/supplier, fixture/tool, orientation and zone;
- correct personalization input and proof approval;
- first completed unit checked before the remaining run;
- line/fill/text/color/stitch/depth/edge/registration checks appropriate to process;
- critical functional and protected-zone checks.

### In-process inspection

- frequency based on risk, batch, drift history, and approved plan;
- process drift, fixture movement, thread/ink/tool/material changes, operator handoff;
- defect/rework count, reason, and containment action.

### Final inspection

- exact Product/SKU/options/personalization and spelling/date;
- visual hierarchy and actual mark/decor quality against approved sample;
- surface scratches, residue, heat/pressure damage, puckering, deformation, burrs, loose parts, edge/finish defects as applicable;
- function, care/safety, included pieces, labels/instructions;
- packaging protection, presentation, barcode/order identity where applicable.

### Release and traceability

- inspector, date, quantity, pass/hold/reject, sample/lot reference;
- file/process/material/supplier versions;
- rework and second-inspection result;
- retained evidence and manager release where required.

## Defect severity

| Severity | Definition | Default disposition |
|---|---|---|
| Critical | safety, legal, wrong identity/personalization, missing essential function, prohibited material/process, or high-impact claim mismatch | stop, contain, do not ship |
| Major | visible/function/durability/option failure likely to cause rejection, return, or material mismatch | hold/rework/reject under approved rule |
| Minor | limited cosmetic deviation outside critical areas that still meets approved acceptance | record and accept only within documented tolerance |

Numeric tolerances and sampling rates must come from product requirements, process capability, supplier agreement, or approved testing. Do not invent AQL, dimensions, color difference, stitch limits, or inspection frequency.

## Process QC routing

| Process | Typical critical checks to tailor |
|---|---|
| Laser / engraving / etch | material/finish, file/orientation, contrast/depth character, line/text completeness, edge/heat/coating damage, residue, fixture position |
| Print / transfer | substrate, color/white layer, registration, adhesion/cure, banding/pinholes, edge lifting, migration, wash/care result |
| Embroidery | fabric/stabilizer/hoop, thread/sequence, text/stitch completeness, puckering, trims/jumps, backing, wash/abrasion result |
| CNC / cutting / forming | material/thickness, tool/path/origin, dimension, edge/burr/chip/burn, depth, fit/assembly, deformation |
| Finish / coating / foil | surface preparation, coverage, adhesion, color/texture, cure, edge, scratch, batch consistency |
| Assembly / packaging | component/version, orientation, fastening/adhesive cure, function, included parts, protection, movement and presentation |

## Nonconformance and rework

Every nonconformance records defect, severity, affected scope, containment, suspected cause, evidence, disposition, rework instruction, second inspection, and preventive action. Do not rework personalized spelling/date errors into saleable stock unless the exact new order matches and identity control remains reliable.

Repeated failure triggers a hold and root-cause review of material, supplier, file, process, fixture, training, option dependency, proof flow, or packaging. Scores and commercial pressure cannot waive a Critical defect.

## QC release gate

An Approved production scope requires:

- Sample Passed evidence for the exact tuple;
- released production file and approved sample reference;
- complete incoming/first-article/in-process/final/packaging checks;
- clear defect severity and disposition rules;
- trained owner and traceable record;
- option dependencies and personalization proof aligned with the Listing.

If any item is missing, remain Sample Passed or Sample Required as appropriate; do not mark Approved.
