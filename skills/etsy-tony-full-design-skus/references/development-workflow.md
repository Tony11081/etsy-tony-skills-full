# 开发与评分流程

STANDARD 和 FULL 开始前读取；VISUAL 第一轮采用 mode-details 中的精简预筛，不提前运行整套评分。

下列命令和非链接相对路径均以本 Skill 的目录为基准。

## Workflow and Gate order

Canonical Gate order for STANDARD and FULL:

1. Evidence Gate
2. Manufacturing Gate
3. Design Gate
4. Customization Gate
5. Originality Gate
6. Production Readiness Gate
7. Ranking

For STANDARD and FULL, execute in this order:

1. Evidence Gate: separate Observed, Inferred, and Unknown.
2. Product and Buyer: identify the physical Product, buyer job, occasion, value, premium drivers, concerns, and risks before motifs.
3. Product Architecture: classify form, components, materials, surfaces, zones, size, finish, type, pattern, personalization, assembly, and packaging.
4. Ideal Process Exploration: compare only 3–5 relevant processes before reading current capability.
5. Current Capability Check: then read [references/production-profile.md](../references/production-profile.md); do not modify it during ordinary analysis.
6. Manufacturing Gate: apply [references/manufacturing-engineering-gate.md](../references/manufacturing-engineering-gate.md).
7. Competitor DNA: separate generic category/style language, competitor-specific expression, and potentially protected expression.
8. Design Theory and Design Gate: apply [references/design-theory-framework.md](../references/design-theory-framework.md).
9. Design Families, then meaningful SKUs; never use a Cartesian product or isolated flower/font/color swaps.
10. Customization Gate: apply [references/customization-architecture.md](../references/customization-architecture.md).
11. Originality Gate: apply [references/originality-and-ip-rules.md](../references/originality-and-ip-rules.md).
12. Production Readiness Gate, then Ranking.

Hard Gate failures cannot enter Top 3 or be marked Recommended. Use only `Redesign Required`, `Sample Required`, `Hold`, or `Reject` as the disposition, and use the exact Production Status vocabulary in the manufacturing reference.

Base SKU codes use exactly `[PRODUCT]-[FAMILY]-[DESIGN]-[VERSION]`, uppercase ASCII, with a two-digit version. Do not include customer text. Phase 2 must preserve this core and use the production/configuration rules in [references/coding-and-configuration-system.md](../references/coding-and-configuration-system.md). Create a Separate SKU when a material/process/structure/size/supplier/cost/lead-time/quality identity changes materially.

Rank only qualified SKUs with:

`Core Ranking Score = Originality Distance × Production Feasibility × Commercial Potential`

Maximum 125. Minimums: Originality ≥4, Production Feasibility ≥3, Commercial Potential ≥3, Core Score ≥48, Option Error Risk Low or Medium-Low, and Design Gate Average ≥3.5. Break ties by originality, feasibility, commercial potential, lower option risk, higher design average, lower uncertainty, then fewer manual steps.
