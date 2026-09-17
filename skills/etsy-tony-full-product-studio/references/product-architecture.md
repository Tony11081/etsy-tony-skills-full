# Product Architecture

Analyze the Product before surface decoration.

## Buyer and product record

Capture Product Name, Category, Function, Functional/Decorative/Memorial/Gift role, Usage Scene, Occasion, Target Buyer, Final User, Gift Recipient, Emotional Value, Functional Value, personalization state, indoor/outdoor use, viewing distance, lifespan, use frequency, price position, urgency, seasonality, main purchase risk, and main concern.

Answer:

1. Is the buyer paying mainly for the object, ritual, memory, identity, gift value, or customization experience?
2. What failure is the buyer trying to avoid?
3. Which confirmed features justify a premium?
4. Which design details are decoration versus purchase reasons?

## Architecture dimensions

Map Product Form, Components, Size, Material, Surface Type, Functional Zones, Decoration Zones, Main/Secondary Viewing Sides, Color, Finish, Pattern, Typography, Personalization, Assembly, Packaging, and each process layer.

Each row receives one state:

- Fixed
- Variable
- Customer Selectable
- Conditional
- Add-on
- Separate SKU
- Separate Listing
- Not Recommended
- Unknown

## Component record

For every component record:

| Component | Function | Material | Geometry | Contact/Exposure | Orientation | Join | Decoration Access | Evidence |
|---|---|---|---|---|---|---|---|---|

Do not infer a hidden substrate from a plated or painted surface. If construction affects safety, cleaning, food contact, skin contact, outdoor use, or assembly, use Unknown — Physical Sample Required.

## Change classification

A change belongs in:

- option when it is bounded, compatible, easy to show, and does not create inventory/process confusion;
- Add-on when it adds paid labor/material without changing the core product identity;
- Separate SKU when material, finish, size, tooling, process, cost, or QA changes materially;
- Separate Listing when buyer intent, style family, scene, search intent, price band, or ordering logic changes materially.
