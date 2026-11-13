# 一页执行清单

整套 Skill 加起来很长，一次读完会被截断。按这一页的顺序做，每一步只读它写的那一段；拿不准时再去翻全文。

## A. 生成前（不发任何生图调用）

1. **产品事实**：SKILL.md「产品事实门」「发布就绪门」。参考图只有 AI 图时是 `concept_only`：照常生产，`publish_readiness` 写 `BLOCKED`，在报告里说清楚。
2. **美术方向**：`../etsy-tony-full-photo-engine/references/art-direction.md` 第 1–3 节 → `art_direction`。
3. **氛围**：同目录 `atmosphere.md` 第 1–3 节 → `atmosphere`，每张标 `scene_level`。
4. **尺寸**：同目录 `scale-realism.md` 第 1–2 节 → `scale_lock`。
5. **卖点和构图**：同目录 `composition-library.md` 第一、二节 + 本品类那一条 → `selling_points`，每张标 `composition`。
6. **15 个角色和视角**：`references/shot-roles-and-views.md`、`references/category-adaptation.md`。
7. **每张写 prompt 文件**：三段写法见 art-direction.md 第 6 节；场景图加尺度句（scale-realism.md 第 4 节）和氛围句（atmosphere.md 第 4 节）。计划里每张写 `prompt_file`。
8. **跑 `scripts/plan_check.py <out-dir>/plan.codex-direct.json`**，pass 才往下走。

## B. 生成

9. 保真探针：一张正面完整的证据图（`L0`/`L1`）。
10. 氛围探针：主图（shot-01）。过 atmosphere.md 第 5 节三问，再用 scale-realism.md 第 5 节量一次尺寸。
11. 其余分批，每批最多 5 张。每批后跑 `color_cast_check.py` 和 `scale_check.py`。

## C. 验收

12. 每张：保真（参考图逐项）、审美门（art-direction.md 第 7 节）、氛围三问（`L2`/`L3`）、尺度（有参照物的都量，主图也量）。
13. 按实际画面填 `scene_level_actual`，跑 `plan_check.py --actual`，pass。
14. `references/final-audit.md` 出审计；拼样片墙看整套。

## 每张图的 prompt 必须有

产品锁定（名字原文、颜色、结构、图案做法）· 在哪里、什么时刻 · 产品挂在或放在哪 · 尺度句（场景图）· 场合信号和发光物各在哪层（`L2`/`L3`）· 光的来源方向 · 机位和镜头感 · 色彩一句（按 `mood_profile`）· 两三条真正有风险的排除项。

## 几条容易打架的规则，按这里的理解做

- **人物**：必带 prompt 里的「人物使用效果展示」是展示使用意图，人物预算可以是零，用手、使用痕迹、产品状态代替。
- **产品状态**：袜子装着东西、项链戴着、蜡烛点着，是在展示正常用法，可以拍；装进去的东西是道具，写进 `non_included_items`，不暗示容量或附赠。产品事实里写明不能这样用的除外。
- **场合信号和道具卡司**：`prop_cast`（五六件）管的是产品旁边、和产品一起出现的道具；树、灯串、窗外的雪这类背景里的场合信号另算，不占卡司名额。
- **图案被微重画的图**：判 `borderline`，文件照常放在 `shot-NN.png`，审计里逐条写差异；`borderline/` 目录只放同一镜头的备选稿。用户没批准前，报告里明确标出这些镜头。
- **15 张凑不出新信息时**：参考图只有正面，就别硬编新角度。用不同场景、时刻、距离、产品状态补足；实在没有新信息的位置，用确定性的细节板或尺寸图，并在审计里写明。
