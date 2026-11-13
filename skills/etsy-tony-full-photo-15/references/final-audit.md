# Etsy 最终审计与审图模式

接受整套或交付最终审计时读取；用户只要求审图时走第 4 节。**先看图，再看标签**：检视实际图片之后，才读它的场景名、先前分数或通过声明，然后对照来源与买家问题。记录审查过的最终文件名；一张替换图使它先前的单图审查失效，并要求重跑受影响的整套比较。

## 1. 每张图的记录

**必填 8 项**

| 字段 | 内容 |
| --- | --- |
| `observed` | 读角色前先写：画面里实际有什么——产品哪个面朝相机、相机方位/高度、距离、产品状态或动作、与环境的接触、背景实际模式 |
| `fidelity` | 对照参考与锁定事实：结构、比例、部件数、材质、颜色、五金、图案、文字、内含物；`pass / borderline / reject` + 理由。只有图案微细节被重画（`motif_redraw`）记 `borderline` 并列出差异；印花被画成刺绣或浮雕记 `reject` |
| `planned_requirement_met` | 计划的 `visible_view_cues`、买家关键内容、距离、动作、空间关系是否真的出现；列出漏掉的项。不假定 prompt 里的度数被达成 |
| `nearest_comparison` | 最相似的图或组（shot 编号）+ 可见差异；有共用构图时写 `reuse_reason`（实际新增的选项/步骤/来源细节/数值）；无可比图时写 `not_applicable` + 原因 |
| `information_gain` | 这张图**实际**新增的受支持买家信息 |
| `color_cast_status` | 来自 `color-cast-report.json` 的 `profile` / `neutral_b` / `frame_rb` / status + 一句可见证据（哪块白/灰物体是否真的干净）；`warm_scene` 镜头另写产品颜色与参考图并排是否一致；`wb_corrected` 时附增益；有登记暖光例外时引用 `warm_light_source`。没跑脚本 → 写 `UNVERIFIED`，不写 pass |
| `aesthetic_check` | photo-engine 的 art-direction.md 第 7 节：`thumbnail` / `eye_path` / `light` / `color` / `real` 各写 pass 或 fail 加一句可见证据；主图加 `click`（没有竞品主图可比时写 `unverified`）。任一项 fail，该图 verdict 不得为 pass |
| `verdict` | `pass / borderline / reject` + 理由 |

**按条件必填**

- 有尺寸/比例内容：`dimension_check`（每个数字、单位、端点核对结果；不含道具是否清楚标注）。
- 有个性化或 Variation 标签：`label_accuracy`。
- 场景型镜头：`scene_mode_actual`（studio_evidence / contextual_evidence / functional_use / ownership_story / deterministic_graphic，按渲染结果归类）+ 场景承载测试是否通过。
- 生活/拥有/使用场景：scene-planning.md 第 4 节的五项创意分及各自可见证据；总分单独写不算完成。
- 画面里有尺寸稳定的参照物（门、壁炉、桌椅、台面、手）：`scale_status`（pass / borderline / reject，附 `scale_check.py` 的输出：产品被画成多少厘米、真实多少、偏差多少；规则见 photo-engine 的 scale-realism.md 第 5 节）。没有稳定参照物写 `no_anchor`。`reject` 的图 verdict 不得为 pass。
- 出现可见人体：`human_scale_status`（pass / borderline / reject：第一眼是否像迷你/玩具、肢体是否主导前景、透视是否一致）。
- 家具场景：`lived_in_evidence`（见 furniture-scale.md 第 5 节）。
- 带文字的图：手机宽度下可读性。

## 2. 整套检查

- 主要买家问题 → 实际图证据的映射；未满足的问题保留为明确缺口。
- 忽略装饰色、场地名、说明文字，按实际构图分组；每个保留成员都有新增受支持信息或合理的 `reuse_reason`。
- 对照计划的 `view` 组与 `restricted_views`：在可比的视觉尺寸下检视产品，区分几何变化与框取/背景变化；新裁切算细节/框取证据，不算新角度。记录缺失的计划视角，**不事后从输出反推一个通过的计划**。
- 分别计数场景承载图与独立底层构图组；共用底图或换选项不自动增加新场景。
- 比较、序列、状态、数字内容图按其实际任务审，不强加生活多样性。
- 主图是清楚的成品，不是拼贴或文字海报；前五张回答主要购买问题。
- `category_adapter` 与产品形态、主导决策匹配；每个不适用或无支撑的模板角色都被证据支持的类目原生证据替换。
- 没有从无关 campaign 继承的色板、道具簇、动作或故事。
- 实际场景承载数 ≥ 该档下限（proof_led 无情境例外需明确处理）；纯底/棚拍/确定性图数在预算内；坍缩成彩色底的场景已重新分类而非被原谅。`experience_led` 集前五张至少两张场景承载，且任何位置不连续超过两张纯底/信息板。
- 家具：达到 `lived_in_floor`，前五张至少一张 lived-in，无被装饰道具伪装的空展厅簇；紧凑家具在 `human_presence_budget` 内，用户否决的人物路线已移除。
- 尺度一致：所有带环境的图里，产品相对参照物的大小都与 `scale_lock` 相符，且彼此一致；不能这张袜子到壁炉一半、那张只到四分之一。远景里产品占画面的比例符合「产品尺寸 ÷ 取景范围」。
- 构图多样：每张都有 `composition` 代号；15 张至少 7 种构图，同一种最多 3 张，相邻两张不同种；远、中、近、特写四档景别都有；`selling_points` 排前三的每条至少有两张不同构图的图在证明；没有两张图只差背景。
- 整套看得出来自 `art_direction` 的同一个视觉世界：光的方向与质地、色板、台面材质、道具卡司一致；没有哪张像从别的产品的 campaign 里拿来的。每张的 `aesthetic_check` 无 fail。
- 清单、比较、细节、尺寸底图共享中性色彩准确的基线（`true_color`）；`true_color` 整套的主图也在其中。样片墙中无未记录的黄/橙偏色；`warm_scene` 镜头之间暖的程度一致，产品颜色在每张图里都和参考图一样。以最终文件重跑 `scripts/color_cast_check.py`（替换过任何一张都要重跑，`warm_scene` 镜头用 `--warm-shots` 列出）：`true_color` 镜头的 `median_neutral_b` ≤ 3；无 `reject`；`borderline` 仅限用户明确批准的图；`palette_warm_dominant` 的图不超过登记的暖光例外数（≤ 2），且不含证据镜头；`no_neutral_anchor` 为 0；标为 `warm_scene` 的镜头里没有颜色/材质比较、清单、细节、尺寸底图。任一不满足 → `set_coverage_diversity_status` 不得为 `VERIFIED_SUCCESS`。
- 真实产品证据与许可 mockup 使用满足发布就绪门；关键排除项、尺寸信息、限制没被埋在最后；不暗示未验证的价格、发货、送达、评价或转化主张。
- 正方形、横向、纵向、移动端裁切下产品可辨。
- 可选视频简报彼此不同、无声优先、技术合规。

## 3. 状态位

分别记录并给理由：`product_fidelity_status`、`shot_effectiveness_status`、`set_coverage_diversity_status`、`publish_readiness`。

- `VERIFIED_SUCCESS` 仅当 15 张最终图全部存在、各自独立通过保真与 Etsy 审计、每个来源/事实门满足。
- 缺观察或无支撑的通过声明 → `UNVERIFIED`；已知缺口 → `PARTIAL` 或 `BLOCKED`。
- 无理由的重复或漏掉的买家关键要求使相应门失败，不论总分、文件数或场景数。漏掉的产品朝向或相机视角不因场景变了而通过；记录在案的匹配视角比较仍合格。
- 资产未在 Etsy 上传核对时，资产生产与在线 Listing 核验分开报告。
- 自动检查可发现缺字段、过期文件、计数错误、矛盾状态，但不能从标签认证视觉多样性或产品保真。

## 4. 审图模式（用户只提供图，没有本 Skill 的计划）

审别人的图或历史产出时，不存在 `category_adapter`、`view`、`scene_counts` 等计划字段。不启动生成流程，按下面重建最小基准后审：

1. 从用户提供的参考图/产品说明建立 `product_truth`（已确认 + unknowns）和来源分类；用户没给参考图时，只能审整套内部一致性与 Etsy 合规，`product_fidelity_status` 记 `UNVERIFIED`。
2. 按 category-adaptation.md 第 1 节写 3–6 个 `buyer_questions`，判定 `scene_capacity`；家具产品读 furniture-scale.md。这些是审计基准，记为 `plan_source: reconstructed`。
3. 逐张按第 1 节记录，其中 `planned_requirement_met` 改为 `buyer_question_served`：这张图服务哪个重建的买家问题，若一个都不服务则记 `none`。`color_cast_status` 同样用脚本测（文件名不是 `shot-*.png` 时把图片路径逐个传给脚本），用户抱怨"太暖"时先给出整套数值再谈感受，并按 scene-planning 第 3 节把原因归到 A 白平衡 / B 色板 / C 暖光源。`aesthetic_check` 照做；用户说"不好看""没质感""不像 Etsy"时，按 art-direction.md 第 4、5 节逐条指出是光、构图、色、造型还是 AI 痕迹的问题，并说明这个产品和它的买家本该对应什么画面（第 1、2 节加 scene-library 的对应条目）。
4. 整套按第 2 节检查，跳过"对照计划视角组"，改为按实际构图分组并报告未被任何图回答的买家问题、重复组、场景计数与下限差距。
5. 报告四个状态位、每张图的 verdict、最小修改建议（哪几张换、换成什么角色）。不生成替代图，除非用户另行要求。
