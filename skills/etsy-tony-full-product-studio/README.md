# Etsy Theory, Manufacturing & Customization Guided SKUs Studio

这是一套给普通员工使用的 Etsy 实体产品开发 Skills。它把竞品证据、买家需求、产品结构、工艺、设计理论、Design Families、原创 SKUs、定制选项、打样、QC 与 Listing 草稿放进同一条有门禁的工作流。

它不是仿款器、随机元素组合器或自动发布工具。

## 最简使用

1. 复制 templates/employee-input.md。
2. 填写能确认的内容；空白会保留为 Unknown。
3. 调用 $etsy-tony-full-product-studio 并附上输入文件、链接、图片或截图。
4. 默认执行 FULL。若只需要局部工作，在“工作模式”填写 ANALYZE、PROCESS、DESIGN 或 SKUS。
5. 员工按最终的 Design Team、Production Team、Listing Team、Manager Approval 清单执行。

最简提示词：

Use $etsy-tony-full-product-studio in FULL mode. Read my employee input and attached competitor images. Do not invent missing material or machine parameters. Deliver the 36-section report and stop before any Etsy publication.

## 目录

- SKILL.md：总入口、顺序、门禁、输出和状态。
- 同级独立 Skills：1 个主控与 6 个阶段能力，共用本目录参考和模板。
- references/：设计、工艺、编码、定制、原创和质量规则。
- templates/：员工可复制的生产级模板。
- examples/：跨产品品类和压力测试实例。
- scripts/audit_skill.py：检查结构、术语、示例数量、门禁和关键字段。
- agents/openai.yaml：Skill 发现与默认调用元数据。
- suite.yaml：版本、默认模式、子 Skills、证据与生产状态配置。

## 证据类别与验证标记

- Observed Fact：资料中明确可见或明确陈述。
- Reasonable Inference：合理推断，必须带 High/Medium/Low 置信度。
- Unknown：当前无法确认。

验证标记包括 Sample Test Required、Physical Sample Required、Machine Parameter Not Confirmed、IP Verification Required 和 Platform Rule Verification Required。它们说明需要什么验证，不是新的证据类别。

Unknown 不会因为进入后续阶段而自动变成事实。

## 生产状态

Concept Only、Awaiting Machine Parameters、Sample Required、Sample Passed、Approved for Production、Rejected。

只有真实样品记录才能支持 Approved for Production。

Development Readiness 单独记录为 Concept Candidate、Recommended for Sampling、Listing-Ready 或 Approved for Production，不与 Priority 或 Production Approval 混用。

## Etsy 动态规则

本系统在 2026-08-31 使用 Etsy 官方帮助页核对过：Listing 可使用最多 13 个 Tags；标题最多 140 个字符；当前 Listing 可添加最多两个 Variations 属性；Personalization/Custom options 与 Variations 的用途不同。由于平台规则会变化，执行 Listing 阶段时必须重新读取 Etsy 官方文档。当前官方入口记录在 references/etsy-listing-consistency.md。

## 维护

- 新设备或材料测试只更新 references/production-profile-template.md 的实例副本，不把推测写回规则。
- 新增图案、字体或颜色时，先更新兼容矩阵和选项依赖，再进入 SKU。
- 平台规则变更时，更新 Etsy 规则验证日期和来源。
- 新增品类时补充一个最小但完整的 example，并运行审计。

运行验证：

python scripts/audit_skill.py .

再使用 Skill Creator 的 quick_validate.py 分别验证本 Skill 和同级的阶段 Skills。

使用仓库 README 的安装命令安装整个完整版。阶段入口位于同级目录，避免嵌套重复安装。

## 安全边界

输出默认是研究、设计、生产和 Listing 草稿。没有单独明确授权，不编辑或发布 Etsy Listing，不发送客户消息，不创建订单，不读取账户凭据。

## Seller Operations 知识模块

版本 1.1 新增独立子 Skill：etsy-tony-full-seller-operations。它处理店铺国家、账号所有权、KYC、收付款、网络与设备主张、真实发货地、生产合作伙伴、物流候选线路、品类迁移和带日期的 eRank 观察。

- references/seller-operations-knowledge-base.md：已归一化的可复用规则、日期、证据等级、官方政策基线和高风险隔离项。
- templates/seller-knowledge-update.md：每日自动知识合并模板，要求去除人名、账号、凭据、返佣链接和聊天原文。
- examples/seller-operations-decision.md：真实中国发货、美国网络、美国邮编和 SUR 线路冲突的完整只读判断实例。
- ../etsy-tony-full-seller-operations/：可单独调用的 Seller Operations 子 Skill。

该模块不会把账号购买或转让、身份替代、KYC 规避、代理伪装国家、收款主体替换、虚假发货地、按 IP 选择邮编或隐藏真实物流路线转成员工 SOP。遇到这些内容时，它会输出 Do Not Implement、合规替代方案和当前官方验证要求。任何 Etsy 后台、收付款或物流账户写入仍需单独明确授权。

最简调用：

Use $etsy-tony-full-seller-operations. Compare this dated operating note with current official Etsy policy. Return permitted actions, prohibited actions, conflicts, verification needed, and a terminal status. Do not make any Etsy account changes.
