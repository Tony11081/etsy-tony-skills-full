## Etsy 15-Image Buyer-Journey Template

Use this as a flexible role map, not a rigid one-size-fits-all composition list. Substitute category-native proof when a role is not applicable, but preserve the buyer journey and avoid duplicates.

1. `hero`: completed product, immediately recognizable, truthful, and sized for the search thumbnail.
2. `what_you_receive`: full product or set inventory, with included-item accuracy.
3. `size_and_scale`: locked numeric dimensions when supplied and/or a truthful real-world scale view.
4. `variations`: visible color, material, finish, shape, font, or style choices when applicable.
5. `material_and_craft`: texture, finish, edge, stitch, hardware, print, engraving, or construction proof.
6. `personalization_or_unique_value`: finished personalization or the strongest category-specific differentiator.
7. `use_or_lifestyle`: natural use context that proves use, fit, atmosphere, or buyer outcome.
8. `back_inside_or_structure`: the important area the hero cannot show.
9. `packaging_and_gifting`: actual packaging and gift readiness only when verified.
10. `process_or_provenance`: real making, finishing, personalization, or vintage evidence only when supported.
11. `installation_care_or_use`: how to install, handle, wear, clean, or use the item.
12. `limits_and_exclusions`: non-included props, color/size caveats, compatibility, or other decision-critical limits.
13. `alternate_angle_or_state`: a genuinely new angle, configuration, opening, movement, or component relationship.
14. `category_specific_trust`: fit, capacity, clasp, base, label, flaw, thickness, wash result, delivery condition, or other category-native proof.
15. `premium_closing_context`: an aspirational but truthful closing image that reinforces ownership, gifting, or use without changing the product.

Put the most important purchase answers early. The first five images should normally establish product identity, what is included, size/scale, visible choices, and quality. Do not hide exclusions or major limitations at the end.

## Category Adaptation Gate

Before assigning the 15 roles, read [category-adaptation.md](category-adaptation.md) and add a `category_adapter` object to the campaign plan with:

- `product_form`: how the item physically or digitally exists, such as wearable, handheld, freestanding, wall-mounted, furniture-scale, consumable, kit, digital, or one-of-a-kind;
- `primary_decision_modes`: the buyer decisions that matter most, such as appearance, fit, scale, compatibility, function, installation, condition, personalization, or file contents;
- `proof_priorities`: three to six product-specific questions the image set must answer;
- `category_native_states`: the truthful positions, configurations, actions, or use states worth showing;
- `safe_contexts` and `forbidden_contexts`: settings that support or misrepresent natural use, buyer intent, or price positioning;
- `scale_proof_method`: locked dimensions, a category-native scale cue, a worn/room view, or `not_applicable`;
- `human_presence_mode`: none, hand, POV, worn, partial body, or another justified mode tied to a buyer question;
- `human_scale_risk`: `low`, `medium`, or `high`, with the specific perceptual-scale failure to avoid;
- `human_presence_budget`: the maximum number of final images allowed to contain visible human anatomy, including zero;
- `scene_capacity`: `experience_led`, `balanced`, or `proof_led`, based on how much real context helps the buyer understand or desire this product;
- `role_substitutions`: every template role that lacks evidence or does not apply, paired with a supported replacement role;
- `style_source`: verified product design, target buyer, natural use, and price positioning—not the palette or props of a previous campaign.

For furniture-scale products, also create the `furniture_scene_adapter` defined in [category-adaptation.md](category-adaptation.md). Use it to distinguish genuine daily use from an empty showroom with decorative props. For freestanding residential furniture, always resolve its `compact_furniture_scale_policy` before assigning any person, hand, POV, or partial-body shot.

Apply these gates:

- Do not inherit a previous product's palette, surfaces, props, actions, or narrative unless the current product independently supports them.
- Do not force lifestyle, gifting, people, packaging, process, care, back/inside, or installation images into a category that does not need them or lacks source evidence.
- Replace unsupported roles before writing prompts. Never generate an unseen back, inside, mechanism, label, flaw, package, process, result, or care claim as if it were factual proof.
- Let factual proof dominate when that is how the category is bought. Replacement parts, tools, raw materials, collectibles, vintage goods, and digital products may need fewer or no lifestyle scenes.
- Use category families as decision aids, not visual templates. A category label alone does not justify a luxury, cozy, minimalist, rustic, wedding, seasonal, or gift-ready art direction.
- If a planned image cannot answer a real buyer question or create truthful desire for this product, remove or replace it.
