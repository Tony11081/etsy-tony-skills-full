# 美术指导：读懂产品 → 读懂买家 → 定画面

任何出图任务，在选场景、写 prompt 之前读取本文件，再按产品读 [scene-library.md](scene-library.md) 里对应的那一条。

分工一句话：**保真规则管「产品不能变」，本文件管「其余一切要好看」**——场景、光、色、构图、道具、镜头。两者冲突时产品事实优先，换一个不需要改产品的画面。

「好看」在这里不是形容词。下面每一步都要落成能照着拍、也能照着验的决定。顺序不能反：先懂产品，再懂买家，最后才定画面。跳过前两步直接挑场景，出来的就是「漂亮房间里放了个东西」。

## 1. 先读懂产品

写 `product_reading`，每项一句。只写参考图和已确认事实撑得住的；看不出来的写 `unknown`，不编。

| 项 | 回答什么 | 它决定画面的什么 |
| --- | --- | --- |
| `what_it_is` | 它是什么，平时挂在、放在、戴在、用在哪里 | 场景地点，产品怎么和环境接触 |
| `signature_feature` | 买家愿意为它多付钱的那**一个**特征：绣上去的名字、手工缝线、木纹、雕刻、镶嵌 | 主图必须让它看得清；光为它打 |
| `material_character` | 材质的脾气：吸光还是反光，软还是硬，粗还是细 | 用什么光，配什么台面 |
| `color_and_value` | 主色，明度（深 / 中 / 浅），有没有图案 | 背景的明度和整套色板 |
| `occasion_and_season` | 为什么事买，哪个季节买 | 场合线索，时间与光 |
| `making_method` | 图案和文字是怎么做上去的：印花、转印、刺绣、雕刻、压印、手绘 | 画面里它该是平的还是有起伏；写进 prompt 的锁定段，不让模型把印花画成刺绣 |
| `giver_and_receiver` | 谁掏钱，给谁用（自用，还是送谁） | 画面里隐含的那个人，买家时刻 |
| `price_position` | 看得见的品质撑得起的定位：平价可爱 / 中档用心 / 高档传家 | 造型多克制，空间什么档次 |

**材质决定用光。** 看到材质先想光，这是好照片和普通照片最大的差别：

| 材质 | 光怎么打 | 配什么表面 |
| --- | --- | --- |
| 丝绒、毛绒、针织、毛毡 | 低角度侧光或侧逆光扫过，绒面才有明暗起伏；深色要更大的柔光面加一点补光，否则一片死黑 | 硬而哑的表面（漆木、石、墙）衬它的软 |
| 抛光金属、首饰 | 大面积柔光加黑白卡塑形，高光是一条干净的渐变，不是一个亮点 | 哑光低饱和的底：石、亚麻、纸、皮肤 |
| 玻璃、亚克力、树脂 | 逆光或侧逆光勾边，背景比主体略暗，边缘才立得住 | 干净、简单、偏深的背景 |
| 木、雕刻、激光切割 | 低角度侧光把木纹和刻痕的深度扫出来；正面平光会把雕刻抹平 | 浅亚麻、白墙、石、绿植；不要木头压木头 |
| 陶瓷、釉面 | 侧上方柔光，一块宽而软的高光 | 粗麻、原木、石 |
| 亚麻、棉、刺绣、印花 | 窗边侧光，织纹和线迹的起伏看得见 | 干净的硬表面，或同色系更浅的布 |
| 皮革 | 侧光加克制的反光，显出粒面和缝线 | 木、金属、羊毛 |
| 纸品、印刷、墙面艺术 | 均匀、正对、无眩光；垂直线横平竖直 | 真实的墙和家具关系 |
| 蜡烛、皂、半透明物 | 柔光加一点逆光透出质地 | 石、陶、木托 |

## 2. 再读懂 Etsy 买家

来 Etsy 的人不是来比价的。她（买家多数是女性）在找**别处买不到、带着心意的东西**：手工的、能定制的、送得出手的。写 `buyer_reading`：

- `who`：谁在搜。具体到人：给孙辈买袜子的奶奶，备婚的新娘，给闺蜜挑生日礼的人，刚搬家的年轻夫妇。
- `moment`：东西到手之后，她脑子里的那一幕。平安夜一家人的袜子按名字挂成一排；婚礼上两个人一起切蛋糕的那一下。**主图和生活图拍的就是这一幕。**
- `worry`：下单前最怕什么。名字绣得丑、颜色和图不一样、比想的小、看着廉价、赶不上节日。证据图一条一条回答。
- `taste`：她想要的家长什么样，决定视觉世界的风格（见 scene-library 的风格层）。

没有店铺数据时，从产品本身、同类热卖品的主图和评论去推，并写明是推断。

**Etsy 买家的眼睛认这七样：**

1. **是照片，不是效果图。** 像一个有品位的手作人在自己家里、窗边拍的。不是 CG，不是白底目录，不是图库。
2. **手作的痕迹看得见。** 线迹、木纹、织纹、釉面的细小不匀。磨得太光滑反而不值钱。
3. **定制内容是主角。** 名字、日期、首字母在缩略图里就读得出来，而且是一个已经做好的真实样例。
4. **看得到送出去的那一刻。** 能想象它被拆开、被挂上、被戴上。
5. **「我家也能这样」。** 向往但够得着：真实住家的一角，不是豪宅样板间。
6. **应季应景。** 圣诞像圣诞，婚礼像婚礼，一眼对上她正在准备的那件事。
7. **小图里立得住。** 她是在手机的搜索结果格子里第一次看见这张图的。轮廓清楚，和背景分得开。

| 像 Etsy | 不像 Etsy |
| --- | --- |
| 自然光，看得出窗在哪边 | 四面打亮、没有影子 |
| 真实住家的一个角落 | 样板间、空展厅、豪宅 |
| 两三件说得出用处的道具 | 道具堆满，产品要找 |
| 亚麻有褶，木头有纹 | 塑料感、蜡感、磨皮过度 |
| 做好的名字清清楚楚 | `Your Name Here` 占位 |
| 环境色克制，产品最跳 | 满屏高饱和，青橙调色 |
| 白底图只做证据 | 整套白底加信息图 |

**季节层。** 当季流行什么要现查，不凭记忆：读 Etsy Seller Handbook 当季的 Seller Trend Report，把里面点名的颜色、材质、场合当成风格候选，再看它和当前产品配不配。不配就不用，趋势不是硬塞的理由。

> 快照（2026 秋冬，二手转述，用前以官方原文为准；过季即删）：Etsy 2026-10-14 发布的秋冬卖家趋势报告里，节日装饰往更大、更亮、更有童趣的方向走，餐桌布置和朋友之间过节互送是明确的购物场合；eRank 对同一季的解读另有传家怀旧、格纹丝绒深色木的经典风、霜白冰蓝的冷调节日。

## 3. 定视觉世界

一套图只有一个世界。把前两步的结论写成 `art_direction`，存进计划，后面每张图的场景都从这里取，不各写各的。

```json
"art_direction": {
  "product_reading": { "...": "第 1 节八项" },
  "selling_points": [{ "point": "", "proof": "", "compositions": ["F", "C"] }],
  "buyer_reading": { "who": "", "moment": "", "worry": "", "taste": "" },
  "visual_world": "一句话：地点 + 时刻 + 气质。例：平安夜前的客厅壁炉边，安静，等待",
  "library_entry": "scene-library 里选的 产品家族 / 场合 / 风格",
  "light": "主光是什么、从哪边来、多软、大约几点钟；环境里还有什么光",
  "palette": { "dominant": "约六成", "secondary": "约三成", "accent": "约一成", "product_role": "产品在色板里的位置" },
  "surfaces": ["两三种衬托产品材质的台面和背景"],
  "prop_cast": ["整套最多五六件道具，每件写它证明什么"],
  "camera": "镜头感（焦段）、常用机位高度、景深",
  "mood_profile": "true_color | warm_scene",
  "why_this_product": "换成别的产品，这个世界就不成立的理由"
}
```

- **一个世界，多个时刻。** 统一靠光、色板、材质；变化靠时刻、距离、角度、产品状态。
- **卖点决定构图。** 按 [composition-library.md](composition-library.md) 列三到五条 `selling_points`，每条配至少两种构图；每张图标一个 `composition` 代号和它证明的卖点。一套图里一半以上是「产品居中摆着」，就是没做这一步。
- **色板六三一。** 大面积背景色、次要表面色、一点强调色，总共不超过三个色相加中性色。产品必须是画面里最浓的颜色，或者明度反差最大的东西。
- **明度先分开。** 深色产品配中浅背景，浅色产品配中深背景。浅配浅、深配深，缩略图里就糊成一片。
- **道具卡司固定。** 整套就这五六件轮流出场，每张最多三件。每件都要答得出「它在这里证明什么」。
- **`why_this_product` 过不了就重来。** 把产品换成一件不相干的东西，世界照样成立，说明方向太泛。
- **单张图**不写完整对象，三五行写清：产品的招牌特征、买家那一幕、光、色板、台面。

出现下面任一种，方向作废重写：没有列卖点，或有卖点没有任何一张图在证明；照搬了上一个产品的方案；选的是品类套路但 `product_reading` 里找不到依据；说不出光从哪来；产品不是画面里最抢眼的东西。

## 4. 硬标准

顶级和普通的差别就在这几条。写场景时逐条落实，验图时逐条对。

**光**

- 只有一个主光，而且说得出它是什么：哪扇窗，哪一侧，几点钟。其他光都是它的补光或背景点缀。
- 主光从侧面或侧后方来（和镜头夹角大约 45° 到 90°），质感才出得来。正面平光只用于纸品和墙面艺术。
- 影子要有形状，边缘柔和但看得见，并且和产品接触。没有影子的东西是飘着的。
- 产品落在画面最亮的三分之一里。背景可以暗下去，产品不行。
- 蜡烛、灯串、炉火是背景里的点缀，虚成光斑；不拿它们当主光照产品。

**构图**

- 一张图一个主角。阅读顺序是：产品 → 招牌特征 → 环境。第一眼落在道具或背景上就是失败。
- 留白是有意的。小件产品在主图里占画面三成半到六成，四边有呼吸空间，裁成横图竖图都还完整。
- 生活图要有前、中、后三层：一点虚掉的前景，清楚的产品，交代环境的背景。
- 线要正：墙和门框垂直，桌沿水平，桌沿不从产品正中间切过去，道具的边不贴着产品的轮廓。
- 道具成奇数、成三角、有高有低，朝向把视线引回产品；没有任何道具比产品更亮、更艳。
- 机位跟着产品形态走：平的东西正上方俯拍，立着的东西平视或略高（10° 到 25°），挂着的东西正对它的中段，一桌子东西 45°。

**色**

- 环境的饱和度低于产品。想让产品显得贵，就把周围的颜色收一收。
- 用互补或邻近色托产品：红的产品配深绿、奶白和原木，不配红。
- 白是白。画面里最大的那块白或灰是什么颜色，决定了整张图干不干净（按 `mood_profile`，见 15 图 Skill 的 scene-planning 第 3 节）。
- 产品颜色和参考图一致，在任何光下都一样。

**造型**

- 用真材料：亚麻有自然的褶，木有纹，石有哑光。
- 「住过，但收拾过」：留一处生活的痕迹（半杯咖啡、搭在椅背上的毯子、翻开的书），不是堆杂物。摆完之后拿走一件。
- 季节线索两三样就够，不要十样。
- 道具的大小和产品相称，不让买家误会尺寸，也不让人以为道具包含在内。

**镜头**

- 产品用中长焦的透视（相当于 50 到 85 毫米），不变形；房间场景可以到 35 毫米；细节用微距。
- 产品从头到尾是清楚的，招牌特征尤其清楚；背景柔和虚化，但还认得出是什么。
- 保留一点真实照片的质地。不要 HDR，不要过度锐化。

## 5. 一眼假的画面

出现任一条就重做，并在重试的 prompt 里只点名这一条：

- 表面像塑料或蜡，材质没有纹理；
- 摆得过分对称、过分完美，一尘不染；
- 影子飘着、没有接触，或者光的方向前后不一致；
- 所有东西一样亮、一样清楚，没有主次；
- 道具变形：乱码的字、融化的装饰、多出来的手指、长得一模一样的重复松枝；
- 过饱和，青橙调色，整片泛光发雾；
- 产品像贴上去的：边缘发白，光和环境对不上；
- 套路道具叠满（花、亚麻、咖啡、书一起上）。

## 6. 把画面写成 prompt

生图模型吃的是**一段画面描述**，不是一张字段表。字段越多，画面越僵。每张图的 prompt 就三段，用自然的英文写：

1. **锁定**（两三句）：这是 Etsy 商品照；参考图是产品唯一的事实来源；逐项点名不能变的东西和易错细节；写明图案和文字的做法（例：`the crest and the name are a flat print on the velvet, not embroidery, no raised relief`）；不要照搬参考图的背景和光。
2. **画面**（四到七句）：像摄影师描述一张已经拍好的照片。在哪里、什么时刻；产品挂在或放在什么上面、怎么接触；哪个面朝镜头、机位多高多远、什么镜头感；光从哪来、多软、影子怎样；周围是哪两三种材质和颜色；一处生活的痕迹。
3. **收尾**（一两句）：颜色怎么保证（见 scene-planning 第 3 节）；画幅和留白；不要什么（只写这张图真正有风险的两三样）。

写法：

- 写镜头看得见的东西，不写评价。`beautiful, luxury, stunning, cozy, 8k, masterpiece, highly detailed` 这类词一个都不要。
- 材质和颜色说具体：`white-painted wooden mantel`，不是 `nice fireplace`。
- 光必须有来源、方向、软硬。
- 画面段落控制在 180 个英文单词以内。计划里的买家问题、角色名、审计字段留在计划里，不进 prompt。

示例（丝绒圣诞袜，warm_scene）：

```text
Product photo for an Etsy listing. The attached reference photos are the only source of truth for the product: a burgundy velvet Christmas stocking with a white faux-fur cuff and the name "Emma" embroidered in gold script on the cuff. Keep its shape, proportions, colors, fabric, cuff, hanging loop and the embroidered name exactly as in the references. Ignore the references' background and lighting.

The stocking hangs from a small brass hook on a white-painted wooden mantel, slightly left of center, the cuff at eye level and the name facing the camera. A garland of fresh cedar with a few pinecones runs along the mantel top; below, the edge of a brick hearth falls softly out of focus. Late-afternoon window light comes from the left at a low angle and rakes across the velvet, so the pile shows soft highlights and deep folds; a white wall on the right bounces a gentle fill. Far behind, the lights of a Christmas tree dissolve into small glowing circles. The colors stay quiet: white mantel, deep green cedar, a touch of brass, so the burgundy stocking is the richest color in the frame. Shot straight-on at cuff height with an 85mm look; the whole stocking is sharp, the background soft.

The glow comes only from the tree lights in the background; the light on the stocking is neutral daylight, the fur cuff reads as clean soft white and the velvet matches the reference color. Square frame with breathing room on all sides. No added text, no logos, no people, no extra stockings.
```

同一个产品的反例，两种都不要：

```text
Beautiful luxury cozy Christmas stocking hanging on fireplace, warm lighting, bokeh, professional product photography, 8k, highly detailed
```

```text
Shot role: hero / Commercial intent: conversion / Buyer question answered: what is it / Scene: fireplace / Lighting: warm / Props: garland / Mood: cozy / ...
```

## 7. 审美门

每张图除了保真，还要过这一关。逐项写 `pass` 或 `fail`，各带一句画面里看得见的证据，记在 `aesthetic_check`：

| 项 | 怎么验 |
| --- | --- |
| `thumbnail` | 把图缩到手机搜索结果里的大小（边长大约 150 到 200 像素）。还能一眼认出是什么、看到招牌特征吗？产品和背景分得开吗？ |
| `eye_path` | 第一眼落在哪里。不是产品或它的招牌特征就是 fail。 |
| `light` | 说得出光从哪边来吗？材质的质感出来了吗？影子有形状、有接触吗？ |
| `color` | 色板在 `art_direction` 之内吗？产品是最抢眼的颜色或明度吗？白是干净的吗？ |
| `real` | 像真人在真地方拍的吗？对照第 5 节逐条排查。 |

主图再加一项 `click`：和同类商品的主图放在一起，它是不是让人想点的那一张。手头有竞品主图就真的并排看，没有就写 `unverified`，不写 pass。

任一项 fail 都重做，重试的 prompt 只改那一处。整套审完再看一次样片墙：十几张图是不是看得出来自同一个世界，同时没有两张在讲同一件事。
