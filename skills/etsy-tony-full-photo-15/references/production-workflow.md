# 图片制作流程

仅在制作或重新规划图片时读取；只审图用 [final-audit.md](final-audit.md)。下列相对路径以本 Skill 目录为基准。

## 1. 工作流

1. 查看全部所需参考，完成 SKILL.md 的产品事实门与来源分类。
1a. 读 `../etsy-tony-full-photo-engine/references/art-direction.md`，再读同目录 `scene-library.md` 里对得上的产品家族、场合、风格条目，写 `art_direction`：读懂产品 → 读懂买家 → 按同目录 `composition-library.md` 列卖点、给每张图配构图 → 定视觉世界（光、色板、台面、道具卡司、镜头、`mood_profile`）。`buyer_reading.worry` 进入下一步的 `buyer_questions`。这一步不分配每张图的场景，只定整套的世界。 同时按同目录 `scale-realism.md` 写 `scale_lock`（真实尺寸、参照物、落点）；每张带环境的图的 prompt 都要有尺度句。
2. 读 [category-adaptation.md](category-adaptation.md) 与 [shot-roles-and-views.md](shot-roles-and-views.md)：写 `category_adapter`（6 项），把 15 个角色映射到买家问题与来源证据，完成每张图的 `view` / `visible_view_cues` / `evidence_source` / `information_gain`，通过视角预检。**在选装饰环境或写 prompt 之前保存这些。**
3. 若 `scene_capacity` 为 experience_led / balanced 且有生活场景，读 [scene-planning.md](scene-planning.md)：在 `art_direction` 的视觉世界之内，围绕已分配的视角设计各镜头的时刻与 `scene_anchor`，填 `scene_counts`，检查前五张混合与序列门。家具产品读 [furniture-scale.md](furniture-scale.md) 并填 `furniture_scale` 与每张的 `lived_in`。
4. 填 `publish_readiness`、`dimension_data_locked`、`non_included_items`，有 Variation 时填 `variation_mapping`。
5. 每张图写一份**自包含**的 prompt 文件（按第 4 节的三段写法），带上它的姿态、朝向、相机、框取、可见线索、该镜头 `mood_profile` 的色彩要求、`anti_template`。不把完整计划 schema 复制进每个 prompt，不通过 shell 传大 JSON。
6. 按第 2 节生成并检视风险探针，再按有界批次生成其余图。
7. 所有精确测量与选项图用确定性叠加。
7b. 每批生成后，对每张有稳定参照物的图跑 `scale_check.py`，结果记入该图的 `scale_status`（pass / borderline / reject / no_anchor）。`reject` 重生成，重试只改尺度句和景别；同一景别连续两次偏大，换近一档并改用与产品同量级的参照物。
7a. 每批生成后立即跑 `python scripts/color_cast_check.py <out-dir> --json <out-dir>/color-cast-report.json`（脚本随本 Skill 附带；`warm_scene` 镜头用 `--warm-shots 1,7,9` 列出编号）。`reject` 一律重生成；`borderline` 按 [scene-planning.md](scene-planning.md) 第 3 节决定修正或重生成；`palette_warm_dominant` / `no_neutral_anchor` 是场景规划问题，改该 shot 的 `Palette` 与 `Scene` 再生成，不靠白平衡修正掩盖。
8. 每张渲染结果先描述再对照（参考图 → 锁定事实 → 最近的相似图 → shot 计划），再过审美门（art-direction.md 第 7 节：`thumbnail`、`eye_path`、`light`、`color`、`real`，主图加 `click`）。保真和审美都 `pass` 才进候选集。
9. 拼样片墙做整套审查：对照 `view` 与 `visible_view_cues` 看实际产品-相机关系（忽略造型）；重新分类实际背景模式；区分独立构图组与复用底图；审决策覆盖与重复。单张可接受的图在整套里仍可能冗余；只替换无理由的重复，然后重读修订后的样片墙。
10. 运行 [final-audit.md](final-audit.md)。生图工具返回成功或文件存在都不是可用证据。

## 2. 快速执行模式（默认）

用户已提供可读参考、且未要求逐阶段审批时默认启用。它只改变执行顺序与资产构建方式；所有产品事实、来源、尺寸、场景、人物比例、保真、发布就绪门照常适用。

- **shot-01 是保守的保真探针**：对 exact-detail 产品，用保留产品的编辑或主要只换环境的克制场景；不把第一枪花在容易被重设计的激进构图上。
- shot-01 同时是**色彩探针**：先跑 `scripts/color_cast_check.py`，按该镜头的 `mood_profile` 判定。`true_color`：`neutral_b` ≤ 3 且无 `palette_warm_dominant`；没过说明本次产品/类目在把模型往暖色拉（金色、木质、婚礼、节日类尤其常见），先收紧全部剩余 prompt 的 `Color` 一句和场景材质（换掉暖色台面、加大中性锚点、去掉蜡烛/灯串/夕阳）。`warm_scene`：`neutral_b` ≤ 8、无 `no_neutral_anchor`，并且产品颜色与参考图并排一致；没过就把暖光源挪到背景、加强产品一侧的中性补光。不要带着有问题的基线批量生成 14 张后再逐张修。
- shot-01 还是**审美探针**：过不了审美门，先改 `art_direction`（光、色板、台面、道具），再生成其余的图；平庸的基线批量生成出来还是平庸。
- 第一张带环境的图是**尺度探针**：量产品长边和一个稳定参照物的已知边，跑 photo-engine 的 `scripts/scale_check.py`（规则见 scale-realism.md 第 5 节）。偏差超过 30% 就重做，并先改完所有剩余场景 prompt 的尺度句再继续；模型一旦在这套图里把产品画大，后面的远景都会跟着大。
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

默认加载 `../etsy-tony-full-photo-engine/SKILL.md` 的 Image Backend、Art Direction Gate、Non-Negotiables、Exact-Detail Products、Build one prompt per shot、Generate directly 六节，以及 `../etsy-tony-full-photo-engine/references/art-direction.md`。这些文件不可用时，以下内置要点足以继续：

- **美术方向简版**（art-direction.md 不可用时）：写 prompt 前先回答五件事并记入 `art_direction`——这个产品最值钱的那一个特征是什么；买家想象的是到手后的哪一幕；主光是什么、从哪一侧来、多软；背景的明度与产品相反，环境色比产品淡，产品是画面里最抢眼的东西；整套只用五六件说得出用处的道具。
- 参考图是**产品真实**的唯一来源，不是场景真实的来源。先写 `product_truth_from_reference`（必须精确保留的一切）和 `reference_scene_to_ignore`（背景、台面、道具、光线、裁切、排列）。除非用户要求或安全/细节镜头需要，不复制参考场景。
- 绝不重设计结构、比例、轮廓、颜色、材质、缝线、五金、接口、logo、雕刻、印刷、浮雕或内含物；无镜像、变形、缺件、加件或买家关键裁切。
- exact-detail 产品（个性化、名字、日期、logo、雕刻/印刷艺术、密集浮雕、缝线、五金、孔位、形状敏感部件）先写可测量的 `reference_invariants`：部件数与关系、各部件长宽比、雕刻文字/位置/字体/所在面、图案类型/密度/边界、五金/缝线/孔/边缘位置、材质/表面/颜色。每个相关 prompt 点名脆弱细节；"preserve details" 一句不够。脆弱细节生成失败两次后停止重试该微距，改用参考裁切、更宽视角，或请用户批准保守替代。
- **印花、刺绣、插画类图案会被生图模型重画一点**（脸、卷纹、小装饰），这是工具的已知局限。分两层判：产品层（形状、比例、部件、颜色、材质、饰边、定制文字本身、图案的位置大小布局配色）必须通过；图案微细节的偏差记 `motif_redraw`。只有 `motif_redraw` 一个问题的图判 `borderline` 而不是 `reject`：最多生成两次，留较好的一张放进 `borderline/`，在审计里写清看得见的差异，**不允许一张图最后没有文件**。图案的精确证据按计划里的 `motif_proof` 另行提供；以图案本身为主体的微距一律用实拍或参考裁切，不生成。
- 锁定段写明图案和文字的做法：印花或转印写 `a flat print, not embroidery, no raised relief`。把印花画成刺绣或浮雕是对产品的错误描述，判 `reject`。
- 不加文字、水印、logo、脸、角标、箭头、标签或信息图元素（除非明确要求）。
- 每个镜头一次生图调用，不合并。每张选 2–4 张原始参考：一张干净完整视图 + 只为证明该镜头脆弱不变量所需的细节视图。不超过工具参考图上限，不用拼图绕过。每次重试保留硬不变量。

**prompt 写法：三段自然英文，不是字段表。** 生图模型吃的是一段画面描述；字段越多画面越僵。买家问题、角色名、信息增益、审计字段留在计划里，不进 prompt。发出去的 prompt 不带下面的尖括号标签：

```text
<锁定，两三句>
Product photo for an Etsy listing. The attached reference images are the only source of truth for the product: <name and reference-verified identity>. Keep its structure, proportions, outline, colors, material, hardware, engraving, motifs and included items exactly as in the references<; fragile details named one by one, any text quoted verbatim>. Ignore the references' background and lighting.

<画面，四到七句，像摄影师描述一张已经拍好的照片>
<scene_anchor: where and when; what the product rests on or hangs from and how it touches it; fore/mid/background>. <scale, when a size-stable anchor is in frame: real size in inches and cm; one or two relations to the anchor; where the product ends and what it leaves uncovered; its share of the frame at this camera distance>. <view: which face is toward the camera, turn/tilt, camera height, distance, lens feel>. <light from art_direction: source, side, softness, what the shadows do>. <the two or three surrounding materials and colors; the product is the strongest color or value in the frame>. <one trace of real life; human plan if any: crop, action, contact point, details kept unobstructed>.

<收尾，一到三句>
Color: <true_color → neutral daylight; name the largest white or gray object, it renders paper-white or neutral gray; name one large neutral or cool anchor | warm_scene → name the warm sources and where they sit; the light on the product is neutral daylight; name one white object that reads as soft white; the product matches the reference colors>. Must be visible: <visible_view_cues>. Square frame with breathing room for 4:5 and landscape crops. <anti_template: the one repeated treatment this shot must avoid>. No added text, watermarks, logos, faces, badges, arrows or labels.
```

- 画面段落写镜头看得见的东西，不写 `beautiful`、`luxury`、`cozy`、`8k`、`highly detailed` 这类评价词；材质和颜色说具体；光必须有来源、方向、软硬；控制在约 180 个英文单词以内。完整示例见 art-direction.md 第 6 节。
- `Color` 一句每张必写，按该镜头的 `mood_profile`，用**正向可见锚点**，不写 `no yellow / no amber` 这类否定清单（规则见 scene-planning.md 第 3 节）。

**工具路由**：按计划里的 `image_backend`。

- `builtin`（默认）：当前环境内置的图像生成能力（Codex `image_gen`；Cursor `GenerateImage`）。
- `openrouter`（用户要求用 OpenRouter 或 GPT 图片 API 时）：`python ../etsy-tony-full-photo-engine/scripts/openrouter_image.py --prompt-file <out-dir>/prompts/shot-NN.txt --ref <参考图> [--ref ...] --out <out-dir>/shot-NN.png`。密钥只从环境变量 `OPENROUTER_API_KEY` 读。默认 `--quality medium`；主图和材质、细节镜头用 `--quality high`。每次调用计费：第一次调用前说明计划张数，结束时汇总 `<out-dir>/generation-log.jsonl` 里的 `cost_usd`。退出码 3 是余额不足，停止并报告，不重试；退出码 5 且提示超时，先确认那张图有没有生成和计费，再决定是否重试。
- 不调用外部规划 API；不调用这两个通道以外的图像服务；不中途换通道，除非用户明确同意。

工具不支持参考图输入、或同一网络错误重复出现 → 先检查输出目录是否已有新文件；无则用更少参考与更短 prompt（仅保留身份、脆弱不变量、场景、构图、排除项）恢复一次；仍失败则报 `BLOCKED`，保存计划、prompt、已完成与被拒输出、缺失镜头列表，以便下次续跑。提交了请求、等待很久、工具返回完成但没有图片文件，都不是成功。
