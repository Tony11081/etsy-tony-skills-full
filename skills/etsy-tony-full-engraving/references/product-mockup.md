# 固定产品效果图

制作或修改产品效果图时读取；单纯构思雕刻布局不需要加载贴合摄影底图的流程。

下列命令和非链接相对路径均以本 Skill 的目录为基准。

## Fixed Product Mockup

The sample prompt must be adapted to the supplied product. Never invent steel composition, handle ornaments, serrations, utensil placement or background details.

Use this workflow when the user says the second image is the product, asks to turn a provided design image into the product mockup, or uses Chinese phrasing that means "image 3 to image 2", "engrave image 3 onto the product photo", or "keep everything else unchanged".

1. Use the user's supplied product photo as the fixed product photo and preserve its observed product details.
2. Use the user's uploaded design image only as the engraving/layout source.
3. Preserve these product details exactly: two-piece stainless cake knife and cake server set, the reference-verified knife and server geometry, handle design, finish and background, camera angle, crop, spacing, reflections, shadows, side objects, handle collars, serrations, and blade contours.
4. Remove/replace only the existing engraving on the knife/server metal areas. Do not alter the handle pattern, metal shape, serrated edge, product proportions, background, lighting, or perspective.
5. Map design content by object shape, not by vertical order:
   - Wide cake-server outline/design -> the identified wide cake server blade in the product photo.
   - Long narrow knife outline/design -> the identified narrow knife blade in the product photo.
6. Convert black design artwork into realistic laser engraving on reflective stainless steel: subtle gray/dark-gray etched marks, perspective-aligned, slightly embedded in the metal, not printed black ink.
7. Keep the final image a real product photo, not a flat design sheet or line-art template.

Image generation prompt skeleton:

```text
Create a realistic product mockup using the fixed product photo as the uneditable base. Preserve the entire cake knife and cake server set exactly: product shape, ornate embossed handles, serrations, metal reflections, black textured table, camera angle, crop, shadows, spacing, and side objects. Use the uploaded black-and-white design image only as the engraving source. Remove only the old engraving on the metal blade/server areas and replace it with the design: wide server design on the identified cake server, long narrow knife design on the identified knife. Render the design as subtle laser engraving on stainless steel, following the original perspective and reflections. Do not change the product, handles, contours, background, lighting, or composition.
```


## Mockup Rules

When the user provides a blank outline template:

- Preserve the knife, server, handle, serration, contour, spacing, canvas, and background exactly.
- Remove old engraving text cleanly.
- Add only black engraving-style typography and simple line elements inside the metal shapes.
- Keep each design inside the outline with generous margins.

When the user provides a real product photo:

- Preserve product shape, blade shape, handles, cake, flowers, fabric, lighting, shadows, angle, crop, and background.
- Only replace engraving on the knife/server metal areas.
- Make engraving follow the metal perspective as light gray or dark gray laser etching.
- Do not change the product details to make room for text.
- If the user complains that image 2 or later does not match the generated pattern, stop batch generation, re-lock the pattern, and regenerate using the exact approved layout.

When using the fixed house product reference:

- Always include the user's supplied product photo as a reference image together with the user's design image.
- Treat product preservation as the highest priority. A less-perfect engraving is preferable to a changed handle, changed blade, changed table, or changed camera angle.
- If the generation changes product details, tell the user the image model drifted and retry with the fixed product prompt skeleton above.

Default generated files and contact sheets to `./etsy-output\wedding-engraving-designs` unless the user specifies another location.
