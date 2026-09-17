# 阶段验收规则

执行 PROCESS、DESIGN、SKUS 或 FULL 前读取相关阶段；制造判断在推荐设计前，设计与原创性在推荐 SKUs 前，样品与真实事实在就绪声明前。

下列命令和非链接相对路径均以本 Skill 的目录为基准。

## Manufacturing gate

Read [references/manufacturing-engineering-gate.md](../references/manufacturing-engineering-gate.md), [references/material-process-matrix.md](../references/material-process-matrix.md), and [references/process-style-compatibility.md](../references/process-style-compatibility.md) before any Design Family is recommended.

Gate results:

- PASS TO DESIGN: materials, zones, and process path are credible; untested parameters remain explicit.
- CONDITIONAL PASS: design work may continue only inside stated constraints and concepts may be Recommended for Sampling; they are not Listing-Ready or production-ready. Production Approval remains Concept Only, Sample Required, or Awaiting Machine Parameters.
- FAIL / REQUIRES REDESIGN: do not create recommended SKUs until the conflict is translated or removed.

Never invent machine power, speed, work area, line width, text size, stitch density, heat settings, UV parameters, wash cycles, cost, or timing. Without real results, use Machine Parameter Not Confirmed, Requires Cost Input, Requires Time Study, and Sample Validation Required. AI cannot set Approved for Production without recorded sample evidence.


## Design and originality gates

For DESIGN, SKUS, or FULL work that creates or evaluates Design Families, read [references/design-theory-framework.md](../references/design-theory-framework.md), [references/element-style-library.md](../references/element-style-library.md), and only the relevant typography, color, composition, and surface references.

Every Design Family and SKU must explain semantic coherence, style coherence, hierarchy, Gestalt use, balance, negative space, proportion/scale/rhythm, typography, color, material honesty, process compatibility, function, personalization usability, and commercial feasibility. Reject style soup.

Learn the design grammar, not the finished design. Do not copy complete artwork, distinctive composition, unique motif combinations, copywriting, branding, logo, characters, protected works, or distinctive personalization structures. A recommended SKU must materially depart from competitor-specific expression in several meaningful dimensions and pass [references/originality-and-ip-rules.md](../references/originality-and-ip-rules.md). When current trademark or copyright search is unavailable, state IP Verification Required, never “risk-free.”


## SKUs and customization gate

For requested SKU or customization work, read only the needed parts of [references/customization-architecture.md](../references/customization-architecture.md), [references/option-dependency-rules.md](../references/option-dependency-rules.md), and [references/sku-coding-system.md](../references/sku-coding-system.md).

- Keep placements fixed unless the product, process, and images can support a safe buyer choice.
- Keep process fixed within a listing unless the process change is operationally equivalent and truthful; otherwise use a Separate SKU or Separate Listing.
- Limit buyer choices to the smallest set that is clear, valuable, photographable, and production-safe.
- Test short, long, dual-name, date, surname, multiline, case, punctuation, and required language characters.
- Prohibit invalid combinations in the dependency matrix; do not rely on employees to remember exceptions.
- Every generated SKU receives a manufacturing card. Every recommended SKU receives a SKU-specific sample plan. Every distinct Production Process receives a process QC checklist, and each recommended SKU points to that checklist with SKU-specific additions.

Production Approval Status is exactly one of: Concept Only, Awaiting Machine Parameters, Sample Required, Sample Passed, Approved for Production, Rejected.


## Listing gate

Only when the requested deliverable includes a Listing pack, read [references/etsy-listing-consistency.md](../references/etsy-listing-consistency.md) and use [templates/listing-launch-pack.md](../templates/listing-launch-pack.md).

Verify time-sensitive Etsy rules against current official Etsy documentation at execution time. Preserve this user's standing rule of exactly 13 accurate, comma-separated English tags unless current official rules or the user explicitly change it. Never add nonexistent product claims for SEO. For personalized commercial products, distinguish real finished-item evidence from mockups and disclose pre-production visuals.
