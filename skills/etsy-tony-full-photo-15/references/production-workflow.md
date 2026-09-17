# 图片制作流程

仅在制作或重新规划图片时读取；只审图时使用现有 image rules 和 final audit。

下列命令和非链接相对路径均以本 Skill 的目录为基准。

## Fast Execution Mode

Use this mode by default for routine 15-image production when the user has supplied readable references and has not asked to approve each stage. It changes execution order and asset construction only; every product-truth, source, dimension, scene-mix, human-scale, fidelity, and publishing-readiness gate still applies.

- Plan all 15 roles before generation, but keep the saved plan compact. Store shared product locks once in the plan and keep each generation prompt self-contained in its own prompt file. Do not duplicate the full plan schema inside every prompt or pass large JSON through a shell command.
- Make shot-01 a conservative fidelity probe on the first attempt. For exact-detail products, prefer a product-preserving edit or restrained scene whose main change is the environment; do not spend the first probe on an ambitious redesign-prone composition.
- After shot-01 passes, generate the contextual-evidence, use-or-ownership, and first human-containing probes in one parallel batch when they are independent. Each passed probe becomes its planned final shot and must not be regenerated merely because it was a probe.
- Once the probes pass, generate the remaining AI scenes in bounded parallel batches of up to five independent image_gen calls. Keep one call per distinct asset. Do not serialize independent shots, and do not launch another batch until the current batch outputs have been mapped to their shot numbers and inspected for obvious count, structure, and human-scale failures.
- When the supplied reference already provides a clean, truthful base, construct deterministic dimension graphics from that reference or a passed inventory image. Do not call image_gen only to create an empty measurement background.
- For fragile engraving, relief, stitching, hardware, labels, or other exact macro proof, prefer a source crop or another passed reference-preserving image when it answers the buyer question. Generate a macro only when a new viewpoint is necessary. This both improves fidelity and avoids retries caused by invented detail.
- Use generated option or color comparisons only for variations supported by seller facts. A variation without visual evidence remains borderline or BLOCKED even when the generated comparison looks plausible.
- Request the built-in generator's normal highest supported output once. Do not repeat unsupported pixel-size requests in every prompt. Resize selected finals once during deterministic post-processing if the delivery standard requires larger pixels; record that the resize does not add source detail.
- Use ordinary PNG encoding or a moderate compression level during production. Avoid slow maximum PNG optimization because it changes file size rather than image quality. Preserve originals and optimize later only when a destination has a real upload-size constraint.
- Retry only the failed shot and name the single observed defect in the retry prompt. Reuse every passed image. Keep rejected outputs in rejected/ when they document a meaningful fidelity failure.
- Target four generation phases for a normal experience-led set: one strict hero probe, one parallel probe batch, and two bounded batches for the remaining AI scenes. Reference-derived and deterministic assets do not consume image-generation calls.
- Pause for user input only when the user requested approval or when a probe reveals a preference-dependent direction. Otherwise finish the campaign and report the audited result.

The fast path is successful only when the final files still pass the same Etsy-specific audit. Lower model-call count, faster completion, or a complete file count cannot compensate for inaccurate product geometry, invented details, incorrect dimensions, failed human scale, or unsupported publishing claims.


## Workflow

1. Inspect all required references and complete the product-truth and source-classification gates.
2. Load `etsy-tony-full-photo-engine`, `references/category-adaptation.md`, and `references/scene-direction.md`. Create the product intelligence, `category_adapter`, `scene_coverage_plan`, image-set strategy, applicable `scene_direction`, `color_temperature_policy`, coverage matrix, shot briefs, and one prompt per shot.
3. Map the 15 shots to distinct buyer questions and background modes using the buyer-journey template and documented role substitutions. Verify the scene-bearing floor, plain-background budget, early-carousel mix, environment roster, and sequence before generation. Reject a plan that repeats role, question, angle, distance, product state, prop logic, or scene-world combination without a documented reason.
4. Add `publish_readiness`, `source_classification`, `missing_evidence`, `variation_mapping`, `dimension_data_locked`, `non_included_items`, and `mobile_qa_plan` to the campaign plan.
5. Generate `shot-01` as a health and fidelity probe and inspect the actual image. Before the remaining set, `experience_led` and `balanced` campaigns must generate two different scene probes: one `contextual_evidence_probe` that proves a buyer fact inside a real environment, and one `use_or_ownership_probe` that proves action or emotional meaning. For furniture, the second probe must visibly pass the applicable `lived_in_evidence` standard; an empty staged room is a failed probe. When visible human presence is allowed, make the first human-containing scene a `human_presence_probe` before generating any later human shots. If that probe creates miniature/toy scale, foreground-limb dominance, inconsistent perspective, or user discomfort, set `human_probe_result: reject`, reduce `human_presence_budget` to zero, and replace every remaining human shot with `implied_owner_presence` or `no_human_needed`; do not keep retrying people for the same product. A `proof_led` campaign may use one or two context/workflow probes according to safe use. Audit product fidelity, spatial depth, environmental specificity, story, visual hierarchy, contrast, authenticity, white balance, and color cast against the declared baseline. If the user has rejected an earlier direction or explicitly wants approval, pause after the probes; otherwise use them as internal gates. Preserve passed shots and resume only missing or rejected shots.
6. Use deterministic overlays for all exact measurement and option graphics.
7. Independently compare each output with the references and locked facts. Only `pass` images enter the final set by default.
8. Build a contact sheet for final-set review, not as an image-generation reference. Reclassify every actual image by background mode, count scene-bearing versus plain images, and inspect thumbnail-size repetition in palettes, surfaces, prop clusters, camera positions, product states, and consecutive studio/info-board runs.
9. Run the Etsy-specific final audit in `references/campaign-final-audit.md`. A generation tool success or an existing file alone is not evidence that the image is usable.
