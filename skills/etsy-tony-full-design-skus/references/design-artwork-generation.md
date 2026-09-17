# Design Artwork Generation Rules

Use this reference in FULL-B and, only after production approval, FULL-C. The artwork pack turns the approved product concept into an editable visual specification. It is separate from concept mockups and separate from machine-ready production files.

## Required FULL-B pack

After the selected Base SKU, customization architecture, and originality review are locked, create:

1. One editable concept vector for the selected design.
2. One editable personalization-state vector showing the approved short, medium, and long input states.
3. One deterministic rendered preview for each vector.
4. One completed `templates/design-artwork-manifest.md`.

Use native vector geometry such as SVG. Image-generation output, a flattened PNG, a text prompt, or a mockup does not satisfy the editable artwork requirement.

## Concept-vector contract

Until the exact production scope is verified, every vector and manifest must say:

`CONCEPT VECTOR / NOT FOR PRODUCTION`

The concept vector must:

- use a `viewBox` and avoid invented physical width, height, thickness, tolerance, kerf, power, speed, tool, or machine values;
- separate structural geometry, editable personalization, non-production guides, and metadata into named groups or layers;
- preserve the approved silhouette, hierarchy, motif system, and personalization logic;
- keep customer text editable and identify font names as concept references only;
- record Unknown facts instead of silently filling them;
- avoid competitor-specific artwork, layout, lettering, and recognizable element combinations.

The personalization-state vector must show the approved short, medium, and long states. It must expose overflow, counter, legibility, and structural-risk questions instead of hiding them.

## Validation contract

Delivery requires all of the following:

- each vector parses as valid XML/SVG;
- required status label and named groups are present;
- each vector renders to a preview from the saved source file;
- the rendered preview is visually reopened and checked for missing geometry, clipping, unreadable text, accidental overlap, and concept drift;
- file names, hashes, unknowns, font state, and validation result are recorded in the manifest.

If a required vector cannot be parsed, rendered, or visually verified, return `PARTIAL`. A successful file write or tool exit code alone is not proof.

## Production-release gate

Do not create or label a file `RELEASE`, machine-ready, cut-ready, print-ready, or production-ready until the exact material, finish, physical size, process, equipment or supplier, file format/version, minimum bridges/gaps/counters, and approved personalization states have physical-sample evidence and Production Status is `Sample Passed` or `Approved` for that scope.

Before `RELEASE`:

- confirm the exact licensed font and convert the approved glyph set to vector paths;
- close or intentionally preserve paths according to the verified production process;
- remove non-production guides and unresolved placeholders;
- apply only verified physical dimensions and process constraints;
- test short, medium, long, and edge-case approved inputs;
- record the release file version, scope, checks, approver, and rollback source.

FULL-C may keep a launch draft blocked while concept artwork exists. Concept artwork never changes production status by itself.
