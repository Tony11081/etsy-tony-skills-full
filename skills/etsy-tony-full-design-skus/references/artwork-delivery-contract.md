# 可编辑设计稿交付

仅在 FULL-B 或明确要求对应设计稿时读取，未完成精确实物验证的文件保持概念标记。

下列命令和非链接相对路径均以本 Skill 的目录为基准。

## Design-artwork gate

Apply [references/design-artwork-generation.md](../references/design-artwork-generation.md) whenever FULL-B runs. After the selected Base SKU, customization architecture, and originality decision are locked, create an editable concept vector, an editable personalization-state vector, rendered previews, and a completed [templates/design-artwork-manifest.md](../templates/design-artwork-manifest.md).

Until exact physical dimensions, material/process, bridge/gap/counter rules, font and license, equipment or supplier requirements, and physical test results are confirmed, label every artwork file and manifest `CONCEPT VECTOR / NOT FOR PRODUCTION`. Use deterministic native vector geometry such as SVG; a raster mockup or image-generation output does not satisfy this deliverable. Keep structure, editable personalization, guides, and metadata separable. Use a `viewBox` without invented physical units or machine settings. Text may stay editable in concept files, but `RELEASE` artwork requires the exact licensed font converted to paths and verified across approved input states.

Delivery requires successful vector parsing, deterministic preview rendering, visual reread, and manifest completion. A missing, corrupt, unrendered, or unlabeled required vector makes FULL-B `PARTIAL`. FULL-C must not create or label machine-ready or `RELEASE` artwork until the exact scope is `Sample Passed` or `Approved` and the production-file requirements are verified.
