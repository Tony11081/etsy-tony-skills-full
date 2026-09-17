# Option Codes and Advanced SKU Coding

Use in FULL-A/B when an approved project needs production identities and buyer-option registers. Apply P4 from `../SKILL.md`.

## Preserve the Phase 1 core

The immutable core remains:

`[PRODUCT]-[FAMILY]-[DESIGN]-[VERSION]`

Example: `CS-MCC-HZN-01`.

Do not rename issued core codes merely because Phase 2 adds option or production detail. Customer names, dates, messages, order numbers, and other variable text never enter a SKU code.

## Three identities

### Base SKU

The Phase 1 core concept and production family identity.

### Production SKU

Use only when a fixed material, finish, size, process, supplier/tooling route, cost, lead time, file, or QC scope requires separate inventory/production control:

`[BASE-SKU]-[MATERIAL]-[FINISH]-[SIZE]-[PROCESS]`

Example structure: `CS-MCC-HZN-01-M01-FN01-S01-PR01`.

Omit no identity-changing dimension from the internal production record. If an ERP/channel has a length limit, create a controlled alias register; do not silently truncate or reinterpret codes.

### Order Configuration

Customer choices attach to the order line, not to an unrestricted production-SKU Cartesian product:

`[PRODUCTION-SKU]|P##|F##|C##|L##|PK##|AD##`

Include only offered choices. Personalization values remain structured order data linked to the configuration; do not place the buyer's text in the code.

## Code prefixes

| Register | Prefix | Meaning |
|---|---|---|
| Pattern | P## | approved graphic/pattern option within allowed SKU scope |
| Font | F## | licensed, tested typography option or internal fallback |
| Color | C## | buyer-facing tested color/graphic option |
| Placement | L## | measured, tested artwork zone |
| Size | S## | physical size or production-artwork state when separately controlled |
| Material | M## | exact controlled material/supplier definition |
| Finish | FN## | exact surface/finish definition |
| Process | PR## | exact controlled production process route |
| Packaging | PK## | packaging system or approved Add-on |
| Add-on | AD## | separately priced operational addition |

Two digits are the initial convention, not a permanent capacity limit. Expand the register deliberately without reusing retired codes.

## Register contract

Every code records:

- code and buyer-facing label where applicable;
- internal definition and evidence source;
- allowed Base/Production SKUs and prohibited combinations;
- material/process/file/sample/QC scope;
- pricing and lead-time reference if applicable;
- dependency rules and fallback behavior;
- status Draft / To Be Tested / Tested / Active / Retired;
- version, effective date, owner, last review, and replacement code.

Retired codes are never reassigned to a different meaning.

## Version rules

- Increment VERSION when a controlled design revision changes production artwork but preserves the Family/Design identity and requires traceability.
- Create a new DESIGN token when the concept structure, hierarchy, personalization system, or production identity becomes a distinct design direction.
- Create a Production SKU suffix when material/finish/size/process needs separate operational control but should retain the approved Base SKU lineage.
- Use option codes only for valid customer choices; do not use them to hide a Separate SKU or Separate Listing.

## Dependency and uniqueness audit

Before activation check:

- Base and Production SKU uniqueness;
- no customer text in codes;
- no duplicate meanings or reused retired codes;
- every code has an owner, status, and allowed scope;
- every exposed tuple passes Material → Process, Process → Style/Font/Color/File/Validation, Size → Detail, Name Length → Layout/Font, Pattern → Layout/Font, Placement → Artwork Area, and Background → Contrast rules;
- Listing, images, proof, production file, Manufacturing Card, QC, price, and order export use the same codes;
- invalid combinations are blocked automatically or routed to manual review/Separate Listing.

If the system cannot prevent an invalid tuple, Option Error Risk cannot be Low or Medium-Low.
