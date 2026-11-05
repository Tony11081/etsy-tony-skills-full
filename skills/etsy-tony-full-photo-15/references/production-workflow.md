# 图片制作流程

仅在制作或重新规划图片时读取；只审图用 [final-audit.md](final-audit.md)。下列相对路径以本 Skill 目录为基准。

## 1. 工作流

1. 查看全部所需参考，完成 SKILL.md 的产品事实门与来源分类。
2. 读 [category-adaptation.md](category-adaptation.md) 与 [shot-roles-and-views.md](shot-roles-and-views.md)：写 `category_adapter`（6 项），把 15 个角色映射到买家问题与来源证据，完成每张图的 `view` / `visible_view_cues` / `evidence_source` / `information_gain`，通过视角预检。**在选装饰环境或写 prompt 之前保存这些。**
3. 若 `scene_capacity` 为 experience_led / balanced 且有生活场景，读 [scene-planning.md](scene-planning.md)：围绕已分配的视角设计场景世界与 `scene_anchor`，填 `scene_counts`，检查前五张混合与序列门。家具产品读 [furniture-scale.md](furniture-scale.md) 并填 `furniture_scale` 与每张的 `lived_in`。
4. 填 `publish_readiness`、`dimension_data_locked`、`non_included_items`，有 Variation 时填 `variation_mapping`。
5. 每张图写一份**自包含**的 prompt 文件（见第 4 节模板），带上它的姿态、朝向、相机、框取、可见线索、白平衡、`anti_template`。不把完整计划 schema 复制进每个 prompt，不通过 shell 传大 JSON。
6. 按第 2 节生成并检视风险探针，再按有界批次生成其余图。
7. 所有精确测量与选项图用确定性叠加。
7a. 每批生成后立即跑 `python scripts/color_cast_check.py <out-dir> --json <out-dir>/color-cast-report.json`（脚本随本 Skill 附带）。`reject` 一律重生成；`borderline` 按 [scene-planning.md](scene-planning.md) 第 3 节决定修正或重生成；`palette_warm_dominant` / `no_neutral_anchor` 是场景规划问题，改该 shot 的 `Palette` 与 `Scene` 再生成，不靠白平衡修正掩盖。
8. 每张渲染结果先描述再对照（参考图 → 锁定事实 → 最近的相似图 → shot 计划）。默认只有 `pass` 进候选集。
9. 拼样片墙做整套审查：对照 `view` 与 `visible_view_cues` 看实际产品-相机关系（忽略造型）；重新分类实际背景模式；区分独立构图组与复用底图；审决策覆盖与重复。单张可接受的图在整套里仍可能冗余；只替换无理由的重复，然后重读修订后的样片墙。
10. 运行 [final-audit.md](final-audit.md)。生图工具返回成功或文件存在都不是可用证据。

## 2. 快速执行模式（默认）

用户已提供可读参考、且未要求逐阶段审批时默认启用。它只改变执行顺序与资产构建方式；所有产品事实、来源、尺寸、场景、人物比例、保真、发布就绪门照常适用。

- **shot-01 是保守的保真探针**：对 exact-detail 产品，用保留产品的编辑或主要只换环境的克制场景；不把第一枪花在容易被重设计的激进构图上。
- shot-01 同时是**色温探针**：先跑 `scripts/color_cast_check.py`，`neutral_b` ≤ 3 且无 `palette_warm_dominant` 才算通过。shot-01 就偏暖说明本次产品/类目在把模型往暖色拉（金色、木质、婚礼、节日类尤其常见），此时先收紧全部剩余 prompt 的 `White balance` / `Palette` 行（换掉暖色台面、加大中性锚点、去掉蜡烛/灯串/夕阳），再继续；不要带着偏暖的基线批量生成 14 张后再逐张修。
- shot-01 通过后按下面的风险规则选其余探针。独立探针在工具支持并发时可同时跑。**通过的探针就是它计划的最终图，不因为它是探针而重生成。**
- 探针通过后，其余图按每批最多 5 个独立调用生成，一图一调用。每批后检视每张的产品保真与买家问题，再与已接受的图比较有用差异或有意复用；多张结果坍缩成同一个无信息构图时，先改剩余 brief 再继续。
- 脆弱的雕刻、浮雕、缝线、五金、标签等精确微距，优先用来源裁切或另一张已通过的保留参考图；只有需要新视角时才生成微距。
- 生成的选项/颜色比较只用于卖家事实支持的变体；无视觉证据的变体即便比较图看起来合理也是 borderline 或 BLOCKED。
- 请求生图工具的最高支持输出一次即可，不在每个 prompt 重复不支持的像素请求。需要更大像素时在确定性后处理中放大一次，并记录放大不增加来源细节。
- 生产期间用普通 PNG 编码；不做最慢的最大化 PNG 优化。保留原图，只在目标有真实上传大小限制时再优化。
- 只重试失败的那张，并在重试 prompt 里点名观察到的**单个**缺陷。复用每张已通过的图。记录有意义保真失败的被拒输出放 `rejected/`。
- 参考裁切与确定性资产不消耗生图调用，但仍需事实与覆盖检查。
- 只在用户要求、或某个无法安全推断的实质性用户选择未解决时暂停。否则应用探针结果并完成授权的 campaign。

快速路径成功的唯一标准是最终文件仍通过同样的 Etsy 审计。更少调用、更快完成、文件数齐，都补不了错误的产品几何、虚构细节、错误尺寸、失败的人物比例或无支撑的发布主张。

## 3. 风险探针

记录未解决的风险与将测试它的镜头；一张图可覆盖多个风险。产品、参考、风险条件都不变时复用已通过的结果。不对每个类目强加同样数量或类型的探针。

- **身份/结构风险**：先对照来源检视第一张保守产品图，再做依赖工作。
- **比例/合身/空间风险**：检视第一张带受支持锚点的情境/穿着/房间图。
- **功能/状态/选项/数字内容风险**：检视第一张困难的接口、来源细节、受控比较或实际页面/工作流视图；情境或情绪场景可能不需要。
- **多样性风险**：把计划的买家问题与视角组的代表并排检视。计划依赖改变的朝向或相机视角时，先用一张代表性的换视角图对照保守探针，再扩展该方向。核对计划的 `visible_view_cues`：新背景、新裁切、新反射而无所需几何变化 → 该角度要求不通过。物理角度变化不适用时改用内容/状态/细节探针。
- **人物风险**：允许可见人物使用时，检视第一次出现，再生成后续含人图。出现玩具感比例、前景肢体主导、透视不匹配或用户不适 → `human_probe_result: reject`，剩余人物预算归零，改用隐含使用者或无人替代；除非用户后来要求，不再尝试其他人物路线。

探针失败只修正失败的方向，保留已通过的图。缺失的来源证据不能靠虚构探针修补。

## 4. 生成要点

默认加载 `../etsy-tony-full-photo-engine/SKILL.md` 的 Non-Negotiables、Exact-Detail Products、Generate directly 三节。该文件不可用时，以下内置要点足以继续：

- 参考图是**产品真实**的唯一来源，不是场景真实的来源。先写 `product_truth_from_reference`（必须精确保留的一切）和 `reference_scene_to_ignore`（背景、台面、道具、光线、裁切、排列）。除非用户要求或安全/细节镜头需要，不复制参考场景。
- 绝不重设计结构、比例、轮廓、颜色、材质、缝线、五金、接口、logo、雕刻、印刷、浮雕或内含物；无镜像、变形、缺件、加件或买家关键裁切。
- exact-detail 产品（个性化、名字、日期、logo、雕刻/印刷艺术、密集浮雕、缝线、五金、孔位、形状敏感部件）先写可测量的 `reference_invariants`：部件数与关系、各部件长宽比、雕刻文字/位置/字体/所在面、图案类型/密度/边界、五金/缝线/孔/边缘位置、材质/表面/颜色。每个相关 prompt 点名脆弱细节；"preserve details" 一句不够。脆弱细节生成失败两次后停止重试该微距，改用参考裁切、更宽视角，或请用户批准保守替代。
- 不加文字、水印、logo、脸、角标、箭头、标签或信息图元素（除非明确要求）。
- 每个镜头一次生图调用，不合并。每张选 2–4 张原始参考：一张干净完整视图 + 只为证明该镜头脆弱不变量所需的细节视图。不超过工具参考图上限，不用拼图绕过。每次重试保留硬不变量。

**prompt 模板**（只写实质约束当前镜头的字段；`Lighting` / `White balance` / `Palette` 三行每张必写，不得删成一句 `neutral white balance`——用**正向可见锚点**写，不写 `no yellow / no amber` 这类否定清单，否定词对生图模型基本无效且会把这些词喂进去）：

```text
Use case: ecommerce product photo for an Etsy listing
Reference images: the only source of product truth; do not copy their scene
Product: <name and reference-verified identity>
Product lock: do not change structure, proportions, outline, color, material, hardware, engraving, motifs, or included items; no mirrored redesign; no added or removed parts
Exact-detail lock: <fragile details and verbatim text; small changes are failures>

Shot <N>: <role> — answers: <buyer_question>
View: <product face toward camera, turn/tilt, camera direction and height, distance, crop focus>
Must be visible: <visible_view_cues>
Scene: <scene_anchor or studio spec; product-environment contact; fore/mid/background>
Product state and interaction: <state/action; human plan if any: crop, action, contact point, details kept unobstructed>
Lighting: <source, direction, softness, shadows, reflection control>; <daylight type: overcast / north-facing window / open shade / softbox — never sunset, golden hour, candle, tungsten or string-light unless this shot is a recorded color_temperature_exception>
White balance: calibrated neutral daylight, about 5500 K, as if set from a gray card; <name the largest white or gray object in frame> renders paper-white / neutral gray, not ivory or cream; shadows neutral to slightly cool; skin natural; the product's own colors stay exactly as in the reference images
Palette: <dominant surface colors>; neutral anchor: <the one large true-white, gray, black, silver, glass, stone, green or blue element that stays neutral>; warm materials (wood, linen, beige, cream, gold, brass, terracotta) cover no more than about one third of the frame
Anti-template: <the repeated treatment this shot must avoid>
Framing: 1:1 safe area with breathing room for 4:5 and landscape crops
No text, watermarks, logos, faces, badges, arrows, labels, or infographic elements.
```

**工具路由**：用当前环境内置的图像生成能力（Codex `image_gen`；Cursor `GenerateImage`）。不调用外部规划或图像 API，不读取 API key。工具不支持参考图输入、或同一网络错误重复出现 → 先检查输出目录是否已有新文件；无则用更少参考与更短 prompt（仅保留身份、脆弱不变量、场景、构图、排除项）恢复一次；仍失败则报 `BLOCKED`，保存计划、prompt、已完成与被拒输出、缺失镜头列表，以便下次续跑。提交了请求、等待很久、工具返回完成但没有图片文件，都不是成功。
