# SKU Coding System

Use:

[Product]-[Family]-[Design]-[Material/Finish]-[Size or Version]

Example: CS-VB-OLV-SLV-01.

## Code registers

- Pattern: P01, P02, P03
- Font: F01, F02, F03
- Color: C01, C02, C03
- Placement: L01, L02
- Size: S01, S02
- Material: M01, M02
- Finish: FN01, FN02

For unknown product facts, use an explicit provisional token such as MX0 or FNX0 and mark the record Awaiting Machine Parameters/Physical Sample. Replace it only through a controlled mapping; do not silently reinterpret an issued code.

## Rules

- Codes are unique, stable, and uppercase ASCII.
- Customer names, dates, messages, or order numbers never enter the Base SKU.
- Family and design codes refer to approved registers.
- Finish and material may share a compact token only when the register remains unambiguous.
- A size that requires a different artwork, digitization, fixture, process, cost, or QA path is a Separate SKU.
- Option codes are attached to the order line, not baked into every possible SKU combination.

## Required registers

Maintain Product, Family, Design, Material, Finish, Size, Pattern, Font, Color, Placement, Process, and Packaging registers with code, customer-visible label where applicable, internal definition, version, allowed scope, status, and last update.

Before release, check uniqueness, orphan codes, duplicate meanings, option dependencies, and consistency across manufacturing card, files, Listing images, variations, and order exports.
