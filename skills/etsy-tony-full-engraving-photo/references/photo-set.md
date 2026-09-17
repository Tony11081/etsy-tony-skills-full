# 完成场景图组

母版通过后读取；如同时请求创作雕刻稿，先执行其中的 Optional design creation，再制作母版。

下列命令和非链接相对路径均以本 Skill 的目录为基准。

## Stage 2: create the final listing set

Follow [references/shot-plan.md](../references/shot-plan.md) in order.

For every final image:

1. Use the approved product master as the primary product reference.
2. Also use the original engraving source for shots where text or line art is readable.
3. Generate from the product master, never from a previous scene image.
4. Change only the environment, camera distance, camera angle, crop, props and safe human interaction required by that shot.
5. Preserve the exact engraving and physical product fingerprint. Do not re-typeset or reinterpret the engraving.
6. Make exactly one built-in `image_gen` call for that shot and output one standalone image. Repeat one shot at a time without commentary between generations.

Use this prompt structure with the shot brief appended:

```text
Use case: product-mockup for product-first shots; photorealistic-natural for lifestyle and interaction shots.
Asset type: one standalone Etsy listing photo
Input images: the approved product master is product identity truth; the original engraving design is text/layout truth when included.

Create one photorealistic Etsy listing photo. Use the approved product master as the identity truth and the original black-and-white design as the engraving truth. Preserve exactly the same two-piece stainless-steel cake knife/server set, blade contours, serrations, ornate floral handles, collars, proportions, material, and every engraved word, date, skyline and ornament. The engraving must remain subtle gray laser etching and must not be rewritten or replaced.

[Insert one shot brief from the shot plan.]

Make the product the visual priority and keep the full required part in frame. Do not add, remove, duplicate, merge or redesign utensils. Do not invent text, dimensions, logos, badges or watermarks. Do not make a collage, split screen, contact sheet, illustration or CGI-looking render. Output one image only.
```


## Dimension safety

- If verified product dimensions are supplied, reproduce only those exact values with clean, non-overlapping lines.
- If dimensions are absent, use a hand-scale or cake-scale context with no numeric labels.
- Never estimate measurements from the photo.


## Final quality gate

Review the 15 images as one set and individually:

- exactly 15 standalone images exist;
- all required shot categories are represented;
- personalization is identical to the approved master wherever visible;
- product count, shapes, handles, serrations and material stay consistent;
- camera distance, angle, setting and prop logic are genuinely varied;
- no two shots are near-duplicates;
- no invented measurements, random text, logos, watermarks, malformed hands or extra utensils appear;
- the product remains large enough to judge in listing thumbnails.

Regenerate only failed shots from the approved product master. Do not restart passed shots and do not silently accept engraving drift.


## Optional design creation

If the user asks to create the engraving layout as well, design it before Stage 0:

- Use monochrome, vector-friendly line art with no gradients or shadows.
- Put the main emotional content on the wide cake server and a short companion line on the knife.
- Keep generous safe margins and avoid hairline ornaments that will disappear on reflective metal.
- Preserve any provided outline, handle, serration, spacing, canvas and background exactly; edit only interior engraving content.
- Obtain approval for the engraving layout before creating the product master when the requested text or design direction is ambiguous.
