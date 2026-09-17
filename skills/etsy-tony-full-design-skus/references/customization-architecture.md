# Customization Architecture

Apply P4 from `../SKILL.md`. The goal is the smallest clear option system that preserves the design, can be photographed, can be produced reliably, and has commercial value.

## SKU, option, Variation, and personalization boundaries

- Base SKU: fixed production identity for Product form, core design, main material, and process.
- Customer Selectable Option: a controlled buyer choice such as an approved pattern, font, color, size, Placement, or finish.
- Etsy Variation: a storefront field used to present some Customer Selectable Options; it is not automatically a Base SKU definition.
- Personalization Input: buyer-entered content such as names, date, initials, family name, or short quote.
- Add-on: extra charged material, process, labor, time, packaging, or proof service.
- Separate SKU: a material, size, structure, process, supplier, cost, lead-time, file, fixture, or quality plan change requiring separate production control.
- Separate Listing: a different buyer, use scene, main style, price band, search intent, or ordering logic.

Names, dates, and ordinary allowed text do not create new SKUs. A process or major material change is not a casual buyer option when it changes the production identity.

## Required option groups

For every SKU classify each group as exactly one of:

- Fixed
- Customer Selectable
- Conditional
- Add-on
- Separate SKU
- Separate Listing
- Not Offered

Groups:

- Pattern
- Font
- Color
- Placement
- Size
- Material
- Finish
- Personalization
- Packaging
- Add-ons

## Option admission test

Offer a choice only when all are true:

1. The customer understands it without professional vocabulary.
2. An image can show the difference accurately.
3. Production can identify and enforce it.
4. Dependencies and invalid pairs are controlled.
5. It preserves aesthetics, function, and process compatibility.
6. It has clear commercial value.
7. It does not create disproportionate proof, error, lead-time, or return risk.

If a choice fails, fix it, make it Conditional, charge it as an Add-on, split it into a Separate SKU/Listing, or do not offer it.

## Personalization fields

For each input record: label, required/optional, allowed content, recommended and maximum **tested** length, over-limit handling, date format, case, punctuation, character support, spelling responsibility, preview, and proof policy.

When no test establishes a limit, use `Unknown — To Be Tested`; do not invent character counts. Test short, long, dual-name, initials, surname, date, multiline, punctuation, capitalization, and required language glyphs as applicable.

## Option dependency rules

At minimum define:

- Material → Process
- Process → Graphic Style
- Process → Font
- Process → Color
- Size → Detail Level
- Name Length → Font
- Name Length → Composition
- Pattern → Layout
- Pattern → Font
- Placement → Artwork Area
- Background → Text Contrast
- Process → Required File Type
- Process → Required Validation

An option is not valid merely because it can be displayed in a menu. Prohibit or route invalid combinations before production; do not rely on staff memory.

Use dependencies to define automatic restriction, controlled fallback, manual review, proof approval, or listing separation. Phase 1 does not create Pattern/Font/Color/Placement code libraries; those remain Phase 2.

## Option Error Risk Gate

Use only:

| Risk | Meaning | Gate result |
|---|---|---|
| Low | Few clear choices; customer and staff can execute reliably. | Pass |
| Medium-Low | Small number of explicit conditions controlled by images/rules. | Pass |
| Medium | Significant dependency; needs control and re-evaluation. | Not rank-eligible yet |
| High | Likely invalid combinations, wrong production, or support issues. | Hard veto |
| Critical | Option system cannot be executed reliably. | Hard veto |

A Medium candidate must add at least one of Dependency Rule, Automatic Restriction, Manual Review, Proof Approval, or Separate Listing, then be rescored. High or Critical cannot enter Top 3.

## Complexity control

- Keep Placement and process fixed unless a choice creates real buyer value and is fully testable.
- Prefer two or three tested type choices over an open font library.
- Use length-responsive layouts internally rather than asking buyers to understand production constraints.
- Split choices when the image, price, lead time, care, or production workflow becomes materially different.
- Count manual review and proof steps in ranking tie-breaks.
