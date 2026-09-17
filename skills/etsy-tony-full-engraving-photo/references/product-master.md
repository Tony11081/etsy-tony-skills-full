# 建立产品母版

母版制作前读取；先验收精确文字和产品细节，再开展场景图。

下列命令和非链接相对路径均以本 Skill 的目录为基准。

The quoted prompt is a template: replace product-specific observations using the actual input. Do not assume stainless steel, a particular finish or handle pattern without confirmation.

## Stage 0: lock the two truth sources

Treat the files as two different authorities:

- **Engraving truth**: the uploaded design controls all words, spelling, dates, graphics, hierarchy and knife/server mapping.
- **Product truth**: the real product photo controls utensil count, blade/server shapes, serrations, ornate handles, collars, proportions, silver material and physical details.

Map by object geometry, not by top/bottom order in the design image:

- long narrow design -> serrated cake knife;
- wide paddle design -> cake server.

Record the exact visible text before generating. Never rewrite, improve or translate personalization unless explicitly asked.


## Stage 1: create the product master

Call Codex's built-in `image_gen` as an edit/compositing operation with both the product base and engraving source as references. The product photo is the uneditable base; the design is used only inside the metal engraving zones.

Use this prompt structure:

```text
Use case: compositing
Asset type: photorealistic cake knife/server product master
Input images: Image 1 is the edit target and product truth; Image 2 is the supporting engraving source and text/layout truth.
Primary request: replace only the engraving on Image 1 with the engraving design from Image 2.

Create one photorealistic product master by editing the provided real product photo. Treat the product photo as an uneditable base layer. Preserve exactly the reference-verified cake knife and cake server set, the reference-verified knife, server and handles, handle collars, metal contours, proportions, reflections, original surface, camera angle, crop, spacing, shadows and side objects.

Use the provided black-and-white design only as the engraving source. Replace only the existing marks inside the blade/server metal surfaces. Map the long narrow design to the serrated knife and the wide design to the cake server. Preserve every word, name, date, skyline and ornament exactly as shown. Render it as subtle gray laser etching embedded in reflective stainless steel, perspective-aligned with the metal; never as black ink, a sticker or raised print.

Do not change, simplify, restyle, add, remove or multiply any product part. Do not alter the handles, serrations, blade contours, metal color, background, lighting, composition or personalization. Output one real product photo, not line art, not a design sheet and not a collage.
```

Generate only one master first. Do not begin the lifestyle set until it passes the gate below.

### Product-master quality gate

Inspect at original resolution and require all checks to pass:

- Every name, phrase, place and date matches the engraving source character-for-character.
- The long design is on the knife and the wide design is on the server.
- Skyline, dividers and ornaments keep the source layout and relative placement.
- There are exactly two utensils with the correct blade/server contours.
- Serrations, reference-verified handles, collars and proportions match the product base.
- The result remains a realistic reflective-steel photo with subtle etched marks.

If a check fails, call the built-in tool again from the original two truth sources with the failed constraint stated first. Never regenerate from a failed output. After repeated text drift, stop and report the exact mismatch instead of approving it or silently switching to CLI, API, third-party generation or another compositor.
