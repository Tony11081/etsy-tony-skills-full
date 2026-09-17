# 按当前交付选择能力

只把这份表用于挑选候选。最终以当前可访问的 Skill 正文、用户材料和本轮目标为准，不凭一个关键词启动流程。

| 用户现在要的结果 | 优先候选 | 选择边界 |
| --- | --- | --- |
| 看竞品、买家需求、页面事实和矛盾 | `etsy-tony-full-competitor` | 研究结论，不自动生成新款或虚构销量 |
| 还没定产品，先判断机会或开发问题 | `etsy-tony-full-product-studio` | 用 ANALYZE 或最小适用阶段；缺市场证据就保留缺口 |
| 判断材料、结构、工艺和打样条件 | `etsy-tony-full-manufacturing` | 只做具体工艺判断；用户明确选择其他匹配入口时沿用 |
| 根据已通过工艺的产品建立设计系列 | `etsy-tony-full-design-system` | 设计系统，不自动创建完整 SKUs |
| 先给几张新款方案让我挑 | `etsy-tony-full-design-skus` | VISUAL；通用默认六张独立图，用户数量要求优先 |
| 从竞品需求重新开发原创产品 | `etsy-tony-full-original-product` | 产品本身改变；默认三款原创概念并等待选款 |
| 产品已定，只做编码、选项和依赖 | `etsy-tony-full-skus` | 名字或日期输入不等于新 SKU；维护不重做开发 |
| 明确要求跨研究、工艺、设计、SKUs 开发 | `etsy-tony-full-product-development` | 一个产品开发主流程，复用通过的上游 gate |
| 给已审查新品整理英文上架资料 | `etsy-tony-full-launch-pack` | SKU 到文案和选项一致性交接，草稿不等于发布 |
| 改标题、描述、标签、翻译或客户回复 | `etsy-tony-full-listing` | 小任务直接写；要求研究时再取所需竞品和 eRank 证据 |
| 明确要求 eRank + Clawlist Gemini 工具链 | `etsy-tony-full-erank-listing` | 不因提到 eRank 就强迫普通文案用外部模型 |
| 现有产品的 15 张 Etsy 图，或审查该套图 | `etsy-tony-full-photo-15` | 保留产品；审图不生成。不是平台图片上限说明 |
| 竞品拍摄研究，并给自己的产品做 15 张图 | `etsy-tony-full-competitor-photo-15` | 两项都需要才选；竞品不能作图像生成参考 |
| 只给现有产品改一张图或其他数量场景 | `etsy-tony-full-photo-engine` | 共享图片能力；沿用产品事实，不扩展成 15 张 |
| 蛋糕刀铲刻字设计或把图案放到产品上 | `etsy-tony-full-engraving` | 只动指定雕刻区，以使用者提供的真实产品底图为准 |
| 雕刻稿到母版再到完整刀铲场景组 | `etsy-tony-full-engraving-photo` | 母版通过前不开启场景批量生成 |
| 现有相框做婚礼桌牌、换字体或内芯 | `etsy-tony-full-table-number` | 专用局部设计边界优先；不重做指定边框 |
| 合作售价、分成与广告上限估算 | `etsy-tony-full-pricing` | 用已存在的合作模型；非账单实际利润核算 |
| GigaB2B 原图、SKU、尺寸资料整理 | `etsy-tony-full-gigab2b-assets` | 只准备素材时到准备验收就结束 |
| GigaB2B 主商品原图到完整商品图 | `etsy-tony-full-gigab2b-photos` | 共享生产能力；沿用已有引擎和图像验收规则 |
| GigaB2B 商品准备为草稿或明确授权保存草稿 | `etsy-tony-full-gigab2b-draft` | 检查真实商品适用性和必要披露；授权保存后才写目标店铺 |
| 开店、经营主体、KYC、收款和真实发货信息 | `etsy-tony-full-seller-operations` | 当前官方依据的只读判断；不操作账户、不保证安全 |

| 只做标题 | `etsy-tony-full-title` | 只交付请求的标题与必要事实缺口 |
| 查看已有图片 | `etsy-tony-full-photo-review` | 诊断完成后，用户已要求修改时继续交给出图能力 |
| eRank 命令、导出和计算 | `etsy-tony-full-erank-tools` | 包内提供可移植 harness；会员证据仍需本人账号或导出 |

## 容易误选的情况

- “这张白字桌牌只换内芯”：已有产品局部改图。保持边框和白字，不能进入自由开发六个新款。
- “商品二十天出了七单，帮我看标签”：先核对不准确或证据薄弱的词。订单表现是用户给出的背景，不是允许重写整套字段的理由。
- “eRank 显示 Unknown 和 < 20”：照原样保留。无法推得精确销量，也不能以模型推荐词代替实测。
- “先算每单实际利润”：需要订单对应到账与成本等实际数据。合作售价脚本的估算不满足这个任务。
- “帮我回复客户”：只生成回复草稿；不发送消息，不获取与回复无关的后台信息。
- “参考这张竞品图做同样的产品”：先区分通用需求与独特表达；不能以“学习”名义复刻。
- “保存到刚才确认的店铺草稿”：继承已明确的目标和保存授权，读取当前状态防重复；不再索要同范围授权。

如果没有一个登记 Skill 适配，使用环境中实际可用的专用能力或直接处理明确的小任务，并准确说明边界。不要为填满这张表而虚构 Etsy 能力。
