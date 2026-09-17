## Scene Coverage Gate

For every 15-image campaign, create a `scene_coverage_plan` before the coverage matrix. Use [category-adaptation.md](category-adaptation.md) to select the tier and [scene-direction.md](scene-direction.md) to design the actual environments.

Classify each shot as one of:

- `studio_evidence`: seamless, solid, gradient, paper, fabric, plinth, or isolated macro whose main purpose is clean factual proof;
- `contextual_evidence`: factual proof embedded in a recognizable, category-native place or spatial relationship;
- `functional_use`: the product being worn, handled, installed, operated, filled, opened, selected, or otherwise used truthfully;
- `ownership_story`: a believable before/during/after ownership moment that creates product-specific desire or meaning;
- `deterministic_graphic`: a comparison, option, instruction, or dimension composition whose exact text or lines are added after generation.

The plan must include:

- `scene_capacity` and the evidence for that classification;
- `target_mode_counts` across the five modes;
- `scene_bearing_shots`: every planned `contextual_evidence`, `functional_use`, and `ownership_story` shot;
- `pure_background_budget`: the maximum combined `studio_evidence` and visually plain `deterministic_graphic` shots;
- `environment_roster`: the distinct real environments, buyer moments, and spatial anchors used across the set;
- `dual_duty_roles`: factual roles that will also carry scale, use, setting, identity, or ownership context;
- `plain_background_exceptions`: each shot that genuinely needs visual isolation and why;
- `sequence_check`: how the carousel avoids long runs of studio or information-board images.

Use these 15-image defaults as a planning target and audit floor:

| Scene capacity | Typical products | Scene-bearing target | Minimum | Direction |
| --- | --- | ---: | ---: | --- |
| `experience_led` | residential furniture, decor, apparel, jewelry, gifts, personalized goods, food, beauty, leisure | 9–11 | 8 | combine desire, real use, scale, material, gifting or ownership without repeating one environment |
| `balanced` | construction-, condition-, or compatibility-led furniture; craft supplies; many tools; kits; vintage goods; digital products with a real workflow | 6–8 | 5 | balance environmental proof with clean component, condition, compatibility, or content proof |
| `proof_led` | replacement parts, industrial components, raw materials, compatibility-critical goods, highly technical downloads | 3–5 | 3 when truthful context exists | favor real installation, workspace, compatibility, or workflow context; do not fabricate emotional lifestyle scenes |

A scene-bearing image must show a recognizable place, use relationship, or ownership moment. A new solid color, seamless sweep, fabric sheet, paper texture, isolated plinth, shadow pattern, foliage corner, or bokeh-only background does not count as a scene by itself.

Apply these gates:

- For `experience_led` sets, at least two of the first five images must be scene-bearing, and no more than two plain/studio or information-board images may appear consecutively anywhere in the carousel.
- For `balanced` sets, at least one of the first five images must be scene-bearing. Place contextual proof between factual studio images when it improves comprehension.
- Design evidence images as dual-duty scenes when accuracy remains clear: show size in a real spatial relationship, material in situ, personalization during selection or display, contents in a believable workspace, or variations in a controlled category-native context.
- Do not convert every evidence image into lifestyle. Exact color comparison, fragile detail, condition, compatibility, and deterministic text may require isolation; record those exceptions and keep the rest of the set spatially rich.
- Every scene-bearing shot must name an `environment_anchor`, `foreground_midground_background_plan`, `product_environment_contact`, and `scene_presence_evidence` in the coverage matrix and prompt.
- Every furniture scene must also name `lived_in_evidence`: the exact daily moment, supported interaction or owner trace, visible physical relationship, and reason the moment depends on this furniture. A styled but inactive room does not pass this field.
- Count the actual final images, not their planned labels. If an intended room, use, or ownership scene renders as an isolated product on a colored field, audit it as `studio_evidence` and replace or rebalance it.

## Lifestyle Scene Creative-Direction Gate

When the set contains generated lifestyle, aspirational, human-use, gifting, or ownership scenes, read [scene-direction.md](scene-direction.md) before writing the coverage matrix or prompts.

Add a `scene_direction` object to the campaign plan with:

- `product_specific_story`: the product-specific ownership, use, memory, identity, or transformation the scenes should make visible;
- `emotional_payoff`: the feeling the target buyer should anticipate, tied to a real product use or ownership moment;
- `price_positioning`: the visual signals that support the product's intended market position without inventing luxury claims;
- `scene_worlds`: two to four related but visibly distinct environments, each with its own palette, surfaces, lighting, and moment;
- `visual_contrast_plan`: how the product separates from the background in value, hue, texture, scale, or focus;
- `scene_progression`: how the lifestyle images move from attraction to real use to emotional ownership rather than repeating one setup;
- `authenticity_cues`: natural interaction, believable wear or motion, physical contact, shadows, and small imperfections appropriate to the category;
- `forbidden_template_cluster`: the repeated palette, prop, background, camera, and product-state combination that would make the set look like generic stock imagery;
- `product_prominence_plan`: the intended visual hierarchy for each scene, including justified exceptions such as room-scale or fit proof.

Also add a `color_temperature_policy` object with:

- `set_white_balance_baseline`: normally `neutral_daylight`, visually equivalent to roughly 5000–5500 K, with whites and neutral grays rendered neutral rather than cream, yellow, amber, or orange;
- `reference_color_anchors`: reference-verified whites, grays, skin tones, metals, woods, fabrics, and product colors used to judge color drift;
- `shot_exceptions`: any shot that genuinely needs a warmer motivated source, why it supports the buyer moment, and how the warm light will be kept local;
- `forbidden_global_casts`: yellow, amber, orange, sepia, or vintage filters that tint the whole frame or change product/material perception.

Apply these gates:

- Write the product story before choosing props. A scene that can be reused unchanged for an unrelated product is too generic.
- Every lifestyle shot must show a distinct moment, not merely a new background. For a 15-image set, include a truthful functional interaction and an emotional ownership or outcome scene when the category and evidence support them.
- Count a scene as materially different only when at least three of these change for a reason: environment, palette/value structure, camera height or angle, visual distance, product state/action, human presence, lighting direction/time, or anchor prop family.
- Use props only when they establish context, scale, action, buyer identity, season, or story. Decorative filler is not a scene concept.
- Keep a small product unambiguously primary in ordinary lifestyle shots; normally plan it to occupy roughly 30%–60% of the frame unless the shot's stated purpose requires a wider scale context. Do not apply this range blindly to furniture, wall art, apparel fit, or room-scale products.
- Build contrast around the verified product. Do not default an entire campaign to pale neutral surfaces, flat high-key light, or one repeated color family merely because it looks clean.
- Human presence must create a believable action or relationship. Reject stiff display hands, impossible grips, pristine staged food, floating contact, or gestures that do not match actual use.
- Clean inventory, dimension, variation, and comparison images may intentionally use controlled backgrounds, but each one counts against the declared plain-background budget. Do not let this exception dominate a scene-capable set.

## Color Temperature and White Balance Gate

Use a neutral, color-accurate daylight rendering as the default for the entire campaign. This is a visual target, not a claim that generated-image metadata contains a measured Kelvin value.

- In every shot brief, coverage-matrix entry, and generation prompt, state `white_balance`, `color_temperature_intent`, and `forbidden_color_cast`. The ordinary default is: `neutral daylight white balance; clean whites and neutral grays; accurate product color and natural skin; no global yellow, amber, orange, sepia, or vintage cast`.
- Treat surface palette and illumination separately. Beige, cream, walnut, brass, autumnal props, or an emotionally intimate scene do not justify a warm color cast over the product or the whole frame.
- Do not use `warm`, `cozy lighting`, `golden glow`, `golden hour`, `sun-kissed`, `amber`, `candlelit`, or similar shorthand unless that exact lighting condition is necessary to the product-specific story. Replace mood adjectives with observable environment, action, direction, softness, contrast, and shadow decisions.
- When a warmer source is justified, keep it visibly motivated and local—for example, a practical lamp in the background or a narrow late-day edge light. Preserve neutral whites, accurate product color, natural skin, and neutral fill; do not wash highlights, midtones, and shadows in orange.
- Color/material comparison, hero, inventory, detail, and dimension-base images do not receive a warm-light exception. Keep their white balance neutral and mutually consistent unless the user explicitly requests another calibrated treatment.
- If an output is too warm, revise by removing warm-light vocabulary and restating neutral color anchors. Do not merely add `cooler`, which can replace the failure with a blue/cyan cast.
- Audit the actual image, not the prompt. Reject a shot when nominally white or neutral areas are visibly yellow/orange, skin is unnaturally orange, silver/clear materials look gold, the product shifts from the reference color, or the shot is materially warmer than the approved set baseline without a documented exception.
- Record `color_cast_status` as `pass`, `borderline`, or `reject`, plus the visual evidence and any approved exception. A `borderline` color cast cannot enter the final set without explicit user approval.
