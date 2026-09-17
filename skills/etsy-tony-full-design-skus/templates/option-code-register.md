# Option and Production Code Register

Use one row per controlled code. Never reuse retired codes or place customer-entered text in a code.

## Register metadata

- Project / Product:
- Register Version:
- Effective Date:
- Owner / Reviewer:
- Base SKU Scope:

## Base and Production SKUs

| Base SKU | Production SKU | M | FN | S | PR | Exact Production Identity | Status | Evidence / Sample | Replacement |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |

## Customer option codes

| Code | Type (P/F/C/L/PK/AD) | Buyer-facing Label | Internal Definition | Allowed SKU Scope | Dependencies / Prohibitions | Evidence / Test | Price / Lead Reference | Status | Replacement |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |

## Material, finish, size, and process registers

| Code | Type (M/FN/S/PR) | Exact Definition | Supplier / Equipment | Allowed Scope | File / Sample / QC Reference | Cost / Lead Reference | Status | Last Review |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

## Personalization fields

| Field ID | Buyer Label | Required | Allowed Input | Tested Length / Glyph Scope | Over-limit Rule | Layout / Font Dependency | Proof Rule | Status |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

## Dependency matrix

| If | Then allow | Then prohibit | Automatic Restriction | Manual Review / Proof | Separate SKU / Listing |
|---|---|---|---|---|---|
| | | | | | |

## Audit

- [ ] Base SKU core format and lineage are preserved.
- [ ] Production SKUs exist only for separately controlled identities.
- [ ] Options do not create a Cartesian-product SKU list.
- [ ] Every Active code has evidence, scope, owner, status, and dependencies.
- [ ] Retired codes have not been reassigned.
- [ ] Listing, images, files, cards, QC, price, and order export use the same codes.
- [ ] Invalid combinations are blocked or reviewed before order acceptance.
