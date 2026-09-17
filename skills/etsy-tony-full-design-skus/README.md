# Etsy-Tony Product Design & SKUs Studio

中文名称：Etsy-Tony 设计理论与工艺驱动的 SKUs 开发系统。

这是供普通员工重复使用的 Etsy 实体产品开发 Skill。用户主要想先看产品图片时，VISUAL 会先生成多张独立方案供人工挑选，不先展开长篇 STANDARD 分析；日常完整开发仍使用 STANDARD。Phase 2 为明确批准的 FULL-A/B/C 提供材料/工艺、字体/色彩、可编辑概念图案、生产文件、编码、打样、QC、供应商、成本、设备投资、IP、Listing 和图片模块。它生成开发记录、明确标注的量产前概念图、图案包和草稿，不自动修改或发布 Etsy Listing。

## Runtime Modes

| Mode | 适用问题 | 核心产出 | 明确不做 |
|---|---|---|---|
| VISUAL | 先出图、给几个/各种方案、让我自己挑 | 默认 6 张独立产品概念图，3 个明显不同的 Visual Families × 每个 2 张；等待人工选择 | 出图前的完整 STANDARD 分析、SKU 编码、完整 Gate/评分、擅自选赢家 |
| QUICK | 值不值得做、先判断 | GO/MAYBE/NO-GO、机会、风险、1–3 个工艺候选、最多 3 个概念方向 | 完整 Gate、6 个 SKUs、Listing |
| STANDARD | 日常产品开发；默认模式 | 2 个 Design Families、6 个 SKUs 目标、Gate、Top 3、1 张 Top 3 概念板、员工行动 | 完整 QC、完整 Listing、20 个 SKUs |
| PROCESS | 只问材料、工艺、内部能力、外协、设备 | 工艺比较、能力差距、验证计划 | SKUs |
| DESIGN | 只问元素、风格、字体、构图、系列 | DNA、设计系统、Design Families | 完整生产方案、Listing |
| FULL | 已人工批准的深度开发 | FULL-A/B/C 分阶段交付 | 未授权时不得自动进入 |

未指定模式时通常使用 STANDARD；如果请求的主要结果是“先生成产品图片、给多个方案、由我挑选”，自动使用 VISUAL。FULL 只有在用户明确要求，或已批准的 STANDARD 项目明确进入深度开发时使用。

## Image-first VISUAL workflow

VISUAL 专门解决“分析很多、图片少且不好挑”的问题：

1. 只做紧凑的出图前检查：产品身份与必须保留的结构、已知/Unknown、功能区域、竞品特有表达排除、必要工艺冲突和禁用元素。
2. 默认生成 V01–V06 六张独立图片，而不是一张塞入六个小格子的拼图。通常分为 3 个明显不同的 Visual Families，每个 Family 2 个方向。
3. 每个方向至少在三个维度上有实质差异，并至少包含一个结构性视觉差异，例如构图、层级、Placement、图案语言或定制结构；只换颜色、字体、花种或场景不算新方案。
4. 逐张回读产品几何、零件数量、构图、层级、文字/留白、表面反射及多余物体；不合格图片替换一次，不计入六张合格图。
5. 在对话中实际交付图片、文件路径、Visual ID 和每张一行说明，然后停止，等待用户选择；Skill 不替用户决定赢家。
6. 用户选定 V 编号后，可为每个选定方向最多生成 3 张精修图。只有用户明确要求继续做 SKU、工艺、定制或商业筛选时，才转入 STANDARD。

所有图片仍是 `PRE-PRODUCTION MOCKUP / UNVERIFIED AGAINST PHYSICAL SAMPLE`。如果当前环境没有可用的图片生成能力，结果必须标记 PARTIAL，并说明阻塞；只提供提示词不能冒充完成出图。

## How to start

1. 复制 [templates/employee-input.md](templates/employee-input.md)。
2. 只填写能确认的内容；没有证据的字段保留 `Unknown`。
3. 提供可公开访问的链接、截图、图片或 Listing 文本。链接打不开时，以用户提供的资料继续，不推测网页内容。
4. 指定 Mode；以图片选择为主时填 VISUAL，其他不指定时为 STANDARD。
5. 审阅结果中的 Observed、Inferred、Unknown、Sample Required、Gate 和 Employee Actions。

## Core architecture

执行顺序为：Evidence → Product/Buyer → Architecture/Zones → Ideal Process → Current Capability → Manufacturing Gate → Competitor DNA → Design Gate → Design Families → SKUs → Customization Gate → Originality Gate → Production Readiness → Ranking。

五条最高原则只在 [SKILL.md](SKILL.md) 中完整定义。Reference 文件负责执行细则，不复制最高原则全文。

Phase 1 SKU Code 固定为：

`[PRODUCT]-[FAMILY]-[DESIGN]-[VERSION]`

例如 `CS-MCC-HZN-01`。姓名、日期和定制短句不能写入 Base SKU。Phase 2 扩展选项编码时必须保留 Phase 1 核心代码，不得整体重命名。

## Production profile

[references/production-profile.md](references/production-profile.md) 是当前内部生产能力的配置文件，不是填写模板，也不是全球工艺边界。

使用顺序：

1. 先独立探索最合适的 Ideal Process；
2. 再读取生产档案；
3. 标记 In-house、Outsource、Alternative、Partnership、Experimental 或 Investment 路径；
4. 未记录参数保留 Unknown / To Be Tested / Awaiting Capability Data。

普通产品分析不得修改生产档案。只有用户明确要求更新时才可修改，并记录 Updated Field、Previous Value、New Value、Evidence Source、Test Date 和 Updated By。设备型号或模型常识不能替代实际测试或正式资料。

## Phase 1 behavior remains stable

VISUAL 是轻量的出图选择入口；QUICK、STANDARD、PROCESS 和 DESIGN 仍按 Phase 1 范围运行。STANDARD 在 Top 3 排名后默认生成一张概念板，但不会因为 Phase 2 已安装而自动加载完整 QC、成本、供应商、Listing 或 20-SKU 流程。VISUAL 完成首轮图片后必须等待人工选择，不会自动进入 STANDARD 或 FULL。

所有实物打样前生成的图片都必须标记为 `PRE-PRODUCTION MOCKUP / UNVERIFIED AGAINST PHYSICAL SAMPLE`。这些图片用于比较设计方向，不能证明真实材质、颜色、尺寸、食品接触安全、耐久性、工艺效果或包装结果。

`Sample Required` 表示值得进入实物验证，不表示 `Approved`。没有实际打样记录，不得把方案标记为 Sample Passed 或 Approved。

## Entering Phase 2 and FULL

只有在以下条件同时满足时进入 Phase 2：

- STANDARD 已由人工审核并选定继续开发的 SKUs；
- 用户明确批准深度开发范围；
- 关键材料、供应商、设备或样品信息足以支持下一阶段；
- 仍未确认的事实继续保持 Unknown，不用假设填空。

FULL 可按以下方式执行：

- FULL-A：Research + Process Exploration + 4 Design Families + 最多 20 个合格 SKUs。
- FULL-B：Manufacturing Cards + Customization + Sample Plans + QC + 3 张选定 SKU 量产前概念图 + 可编辑 SVG 概念图案包。
- FULL-C：Listing Launch Pack + Image Plan + Final Ranking；只有样品与生产范围获批后才生成 RELEASE 图案。

Phase 2 模块已经建立，但安装模块不等于批准运行 FULL。每个阶段仍需满足上游 Gate 和人工授权。

## PHASE 2 IMPLEMENTED MODULES

| Backlog module | Implemented resource |
|---|---|
| Typography Library | [typography-and-color-systems.md](references/typography-and-color-systems.md) |
| Color Framework | [typography-and-color-systems.md](references/typography-and-color-systems.md) |
| Material Library | [material-and-process-library.md](references/material-and-process-library.md) |
| Global Process Library | [material-and-process-library.md](references/material-and-process-library.md) |
| Production File Requirements | [production-files-and-sampling.md](references/production-files-and-sampling.md) |
| Advanced Sample Testing | [production-files-and-sampling.md](references/production-files-and-sampling.md), [sample-test-plan.md](templates/sample-test-plan.md) |
| QC Library | [quality-control-library.md](references/quality-control-library.md), [qc-checklist.md](templates/qc-checklist.md) |
| Listing Launch Pack | [listing-and-image-launch-rules.md](references/listing-and-image-launch-rules.md), [listing-launch-pack.md](templates/listing-launch-pack.md) |
| Image Planning | [listing-and-image-launch-rules.md](references/listing-and-image-launch-rules.md), [image-plan.md](templates/image-plan.md) |
| Concept Image Generation | [concept-image-generation.md](references/concept-image-generation.md), [concept-image-manifest.md](templates/concept-image-manifest.md) |
| Editable Design Artwork | [design-artwork-generation.md](references/design-artwork-generation.md), [design-artwork-manifest.md](templates/design-artwork-manifest.md) |
| Option Codes | [coding-and-configuration-system.md](references/coding-and-configuration-system.md), [option-code-register.md](templates/option-code-register.md) |
| Advanced SKU Coding | [coding-and-configuration-system.md](references/coding-and-configuration-system.md) |
| Supplier Evaluation | [supplier-cost-and-investment.md](references/supplier-cost-and-investment.md), [commercial-evaluation.md](templates/commercial-evaluation.md) |
| Cost Model | [supplier-cost-and-investment.md](references/supplier-cost-and-investment.md), [commercial-evaluation.md](templates/commercial-evaluation.md) |
| Equipment Investment Evaluation | [supplier-cost-and-investment.md](references/supplier-cost-and-investment.md) |
| Advanced IP Search | [advanced-ip-search.md](references/advanced-ip-search.md) |

FULL-B 使用 [manufacturing-card.md](templates/manufacturing-card.md)、生产代码登记、打样、QC、商业评估、概念图片和可编辑图案模板。FULL-C 使用 Listing Launch Pack 和 Image Plan；`Listing-Ready` 不等于 `Published`，`CONCEPT VECTOR` 也不等于 `RELEASE`。

## Phase 2 boundaries

- 不因设备型号、供应商名称或模型知识自动补生产参数。
- 不因存在样品文件就自动判定 Sample Passed；必须有完整结果记录。
- FULL-B 图案必须可编辑、可解析、可重新渲染并目视回读；未完成生产验证时统一标记 `CONCEPT VECTOR / NOT FOR PRODUCTION`。
- 不发明 QC 数值、公差、抽样率、供应商能力、报价、平台费率或投资数据。
- Phase 2 保留 Phase 1 Base SKU，并通过 Production SKU 和 Order Configuration 扩展，不把顾客姓名/日期写进编码。
- Etsy 平台规则在 FULL-C 执行时从官方来源重新验证；静态 Skill 不把时效性规则写成永久事实。
- Listing 发布、供应商订单和设备购买始终需要单独明确授权。

## Phase 1 validation example

[examples/wedding-cake-server-standard.md](examples/wedding-cake-server-standard.md) 是完整的 Wedding Cake Server STANDARD 前向测试。它展示了证据限制、先工艺后能力、2 个 Families、6 个 SKUs、Hard Gate 否决、Top 3 乘法排名、生产档案读取和员工行动。
