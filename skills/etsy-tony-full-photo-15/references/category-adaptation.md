# Etsy Product-Photo Category Adaptation

Use this reference for every campaign before assigning shot roles. Its purpose is to adapt the evidence and creative direction to the actual product, not to promise that every product needs the same amount of lifestyle imagery.

## 1. Identify How the Buyer Decides

Classify the product by form and select the few decision modes that actually control purchase:

- `appearance`: shape, color, finish, pattern, visual presence;
- `fit`: worn size, drape, comfort, closure, movement;
- `scale_or_space`: physical size, capacity, viewing distance, room or wall relationship;
- `function`: grip, loading, operation, movement, result, access;
- `compatibility`: connector, model, opening, mount, software, file type, device, or system fit;
- `installation`: mounting, assembly, placement, orientation, or clearance;
- `condition`: age, wear, flaws, labels, repairs, patina, completeness;
- `personalization`: editable area, placement, finished example, option mapping;
- `contents`: included parts, pages, files, formats, variants, or kit relationships.

Turn the dominant modes into three to six plain buyer questions. Build the set around answering them. Category names are only routing hints; buyer questions are the actual design input.

## 2. Choose the Right Proof

Select proof types that answer those questions:

- clean hero and full inventory;
- category-native scale, worn fit, room view, or locked numeric dimensions;
- component, connection, closure, base, edge, underside, back, or inside only when visible in a source;
- material, texture, finish, construction, print, engraving, or condition macro;
- real use, operation, installation, movement, capacity, or result only when the product and action are supported;
- variation and personalization mapping using exact supplied options;
- packaging, making process, care, wash result, provenance, or delivery condition only when verified;
- file/page/format/compatibility proof for digital products instead of fictional shipping or physical packaging.

If a template role lacks evidence, replace it before prompts are written. A wider view of verified surfaces is safer than inventing an unseen back or mechanism.

## 3. Decide Whether People Help

Human presence is a proof method, not a quota.

Record `human_scale_risk` and `human_presence_budget` before assigning human-containing shots. A high-risk product may have a budget of zero even when the generic 15-shot template mentions human use.

- Use a hand for grip, operation, scale, opening, fastening, placement, or tactile interaction.
- Use a worn or partial-body view for fit, drape, movement, body scale, or access.
- Use POV for assembly, use sequence, selection, or workspace context.
- Use implied ownership when a human body would distract but a believable in-progress state adds life.
- Use no person when identity, components, condition, exact detail, compatibility, or digital contents need cleaner evidence.

The action must be physically possible, the contact believable, and buyer-critical details unobstructed. Do not add a face or full person merely to make an image feel lifestyle-oriented.

## 4. Classify Scene Capacity

Choose a tier before assigning shot roles:

- `experience_led`: context, use, display, fit, ritual, gifting, identity, or ownership is a major part of why the product is bought. The set should feel lived-in and visually transporting while keeping the product accurate.
- `balanced`: buyers need both environmental understanding and clean factual proof. Use context to explain scale, workflow, placement, use, or condition rather than adding generic decoration.
- `proof_led`: compatibility, components, condition, file contents, or technical facts dominate. Use truthful installation, workspace, device, or workflow scenes where useful, but never manufacture emotional lifestyle content to reach a quota.

Classify the current product, not its broad Etsy category. A decorative hand tool may be `experience_led`; an industrial-looking jewelry component may be `proof_led`. Record the buyer behavior that supports the choice.

## 5. Adapt by Product Family

Use the table as a question-and-proof guide, never as a fixed aesthetic template.

| Product family | Usual starting tier | Dominant questions | Useful proof | Common scene risk |
| --- | --- | --- | --- | --- |
| Wearable and soft goods | experience-led | fit, scale, drape, texture, closure, movement | worn view, front/back when sourced, fabric macro, natural motion | invented body fit, hidden closure, unsupported care claims |
| Jewelry and small accessories | experience-led or balanced | worn scale, clasp/back, material, engraving, gifting | macro, worn crop, closure view, scale cue, verified package | oversized product, fake stones/metal, generic ring-box luxury |
| Home decor and wall products | experience-led | room scale, viewing distance, installation, finish | room view, wall/surface relationship, close texture, verified mount | impossible mounting, invented dimensions, generic empty-room mockup |
| Furniture and large objects | experience-led for residential use; balanced when construction, condition, or compatibility dominates | footprint, capacity, construction, clearance, comfort, daily use | room context, lived-in use, multiple distances, joints, doors/drawers when sourced | empty showroom staging, wrong scale, floating object, architecture overpowering product |
| Tools, kitchenware, and functional goods | balanced | grip, operation, parts, result, cleaning, storage | action sequence, component inventory, contact points, verified result | unsafe use, physically impossible grip, staged gifting replacing function |
| Personalized, event, and gift products | experience-led | finished personalization, option mapping, occasion use, included items | completed sample, legible detail, real interaction, verified packaging | invented names/options, unrelated occasion styling, filler props |
| Craft, art, vintage, and one-of-a-kind goods | balanced | authenticity, surface, condition, flaws, provenance, uniqueness | front/side/detail, labels or underside when sourced, condition map | AI restoration, removed flaws, fabricated history, repeated generic studio scenes |
| Digital and print-on-demand products | balanced or proof-led | file contents, format, compatibility, print placement, actual base item | page/screen previews, exact file list, accurate device or base-product mockup | implying physical delivery, invented files, inaccurate print size or base product |
| Kits and multi-piece sets | balanced | what is included, part relationship, sequence, storage | full inventory, individual parts, assembled/use state, scale | missing or extra parts, showing accessories as included, repetitive full-set poses |

### Furniture lived-in scene adapter

For furniture and furniture-scale products, add `furniture_scene_adapter` to the campaign plan with:

- `furniture_function_class`: seating, dining/work/coffee table, storage, bedside/console, shelving/display, or another evidence-based class;
- `primary_room_and_daily_routine`: the natural room and specific routine supported by the product's apparent function;
- `supported_interactions`: sitting, reaching, working, dining, setting down, retrieving, opening, closing, displaying, passing, or another action justified by the references and product identity;
- `unsupported_mechanisms`: drawers, doors, extensions, hinges, shelves, load claims, or hidden features that must not be shown because the references do not verify them;
- `lived_in_shot_plan`: the shot numbers and distinct daily moments intended to pass the lived-in standard;
- `human_presence_strategy`: direct partial-body use, anonymous hand/POV, implied owner, or a deliberate mix;
- `owner_trace_strategy`: in-progress evidence that implies a person without turning props into decorative filler;
- `circulation_and_scale_plan`: how room clearance, approach, reach, seating position, or movement proves believable scale;
- `empty_showroom_failure_pattern`: the room, prop, camera, and static-product treatment the set must reject.

Also add `compact_furniture_scale_policy` for freestanding residential furniture:

- `trigger`: use `locked_dimensions` when confirmed width is at most 20 in / 50.8 cm or confirmed height is at most 25 in / 63.5 cm. If dimensions are unavailable but the verified product class is clearly a nightstand, side table, stool, or similarly compact cabinet, use `conservative_visual_classification`; otherwise use `not_applicable`.
- `human_presence_default`: `human_presence_unsafe` when the trigger applies.
- `human_shot_budget`: zero by default. Allow at most one human-containing final image only when that exact interaction answers a decision-critical buyer question and the user explicitly requests or approves it.
- `scale_anchor_plan`: prioritize locked dimensions plus stable room/furniture anchors such as a bed or mattress edge, chair, doorway, baseboard, floorboards, or verified room clearance. Do not use hands, phones, or small books as the primary scale anchor for triggered products.
- `human_probe_required`: true only when the one-shot exception is approved. The probe must precede every other human-containing image.
- `probe_fallback`: `implied_owner_presence` or `no_human_needed` for all affected roles.
- `perceptual_scale_rejectors`: miniature/toy-like first impression, a hand or limb that visually dominates the product, a person closer to the camera than the product, inconsistent body/product perspective, or any user-reported scale discomfort.

When the trigger applies, show no visible human anatomy in the hero, dimension graphic, room-fit/circulation proof, or premium closing image. The default set may contain zero people and still satisfy the mandatory human-use intent through verified drawer/door state changes, a specific just-before/just-after routine, objects being stored or retrieved without a visible body, and other implied-owner evidence. If the approved exception is used, show fingertips only—no palm, wrist, forearm, full person, or foreground limb. Keep the product dominant, prefer a 70–85 mm-equivalent normal-to-short-telephoto view, keep product and fingertips in the same middle-distance plane, and treat roughly 25% of product width as a maximum planning warning for visible hand span rather than a substitute for visual judgment.

If the human probe hits any rejector or the user says the scale feels wrong, set `human_probe_result: reject`, reduce the budget to zero, and replace all planned human shots. Do not generate another human route for the same product merely to satisfy a template.

Classify ordinary residential furniture as `experience_led` when room fit, comfort, daily ritual, display, or ownership is a major purchase driver. Use `balanced` when construction, condition, collectible value, component proof, installation, or compatibility genuinely dominates; do not choose it merely because the product is large.

For a 15-image residential-furniture set:

- `experience_led` furniture needs at least four actual lived-in images, including at least one function proof or verified product-state change, one in-progress routine or transition, and one scale/circulation relationship; at least one must appear among the first five;
- `balanced` furniture needs at least three actual lived-in images when normal residential use can be shown truthfully, including at least one function proof, verified state change, or in-progress routine;
- count the rendered result, not the planned label. If the image shows only an untouched product in a decorated room, reclassify it as contextual evidence without lived-in proof and replace it when the floor is missed.

The lived-in floor never requires visible people. For a triggered compact product, meet it entirely through supported state changes and specific owner traces when needed.

Adapt moments to the verified furniture function:

- seating: a believable sit, reach, read, converse, stand-up transition, or recently occupied state with correct body scale, contact, weight, and cushion/fabric response where applicable;
- dining, coffee, and work tables: a specific activity underway, such as working, serving, gathering, sorting, or setting something down, with hands/objects placed in a functional relationship rather than a centered décor arrangement;
- storage furniture: putting away, choosing, or retrieving an item only when the relevant door, drawer, shelf, or opening is visible in the references; otherwise show truthful closed-state placement and circulation;
- bedside tables and consoles: a credible arrival, departure, bedtime, morning, or everyday-carry transition in which the furniture organizes the moment;
- shelving and display furniture: selecting, placing, or viewing an object with believable reach and spacing rather than a symmetrical prop wall;
- large or specialty furniture: emphasize approach, clearance, body scale, movement path, installation relationship, or supported use appropriate to the verified form.

A lived-in image needs a clear moment plus observable evidence such as body contact, hand action, weight, a verified drawer/door displacement, an object mid-use, a pulled seating position, reachable spacing, or a just-before/just-after transition. Flowers, books, cups, throws, plants, rugs, lamps, or a person merely standing and looking at the camera do not create lived-in evidence by themselves.

Do not manufacture life through clutter, fake wear, unverified children/pets, exaggerated mess, full-face stock models, or yellow/orange grading. Lived-in direction changes the action and spatial relationship, not the product truth or neutral white-balance baseline.

## 6. Build Style From the Current Product

Derive art direction from:

1. verified product color, material, shape, pattern, age, and finish;
2. the primary buyer and natural context of use;
3. the intended market position supported by observable quality;
4. the buyer journey and the specific moment each scene must show.

Do not default to `luxury`, `cozy`, `minimal`, `rustic`, pale neutral, dark green, walnut, marble, wedding, holiday, or gift-ready styling. These directions are valid only when the current product and buyer context support them.

Before generation, compare the current plan with the most recent unrelated campaign if one is available. If three or more signature elements—palette, surface, prop family, action, lighting pattern, camera pattern, or narrative—have carried over without current-product evidence, rewrite the plan.

## 7. Role-Substitution Examples

- No verified packaging: replace `packaging_and_gifting` with a second decision-critical proof such as closure, capacity, finish, condition, compatibility, or a component relationship.
- No process evidence: replace `process_or_provenance` with a supported material, construction, variation, or use-state view.
- No back or inside reference: replace `back_inside_or_structure` with a sourced edge, connection, side profile, or wider inventory view.
- No exact dimensions: use a truthful category-native scale cue and label the plan `scale_effect`; do not generate numbers.
- Digital download: replace physical lifestyle, shipping, and packaging roles with contents, page previews, formats, software compatibility, editability, and intended-use previews.
- Product has no meaningful human use: replace the person shot with condition, parts, compatibility, installation clearance, or another factual proof.

## 8. Final Generalization Check

Reject or rewrite the plan when any answer is `no`:

- Do the first five images answer this product's main purchase questions rather than a generic Etsy checklist?
- Does every role have source evidence or a clearly documented safe substitution?
- Is the human-presence choice tied to proof or believable ownership?
- Does visible human anatomy stay within the declared budget, and does every human-containing image pass perceptual scale without a miniature/toy impression?
- Are scenes native to how this product is bought, used, worn, displayed, installed, downloaded, or collected?
- Is the style derived from this product rather than an earlier campaign?
- Does the declared scene-capacity tier match how this product is actually bought, and does the planned mode count meet that tier without fabricating facts?
- Would removing the product make each lifestyle image's story noticeably incomplete?
- Does every additional image add new buyer understanding?
- For furniture, does the final set meet the declared lived-in floor with supported daily moments rather than empty showroom styling?
- For compact freestanding furniture, was `compact_furniture_scale_policy` resolved before prompts, and was any failed or user-rejected human route removed rather than retried?
