# Seller Operations Decision Example

## Scenario

Account Acquisition Claim：团队称已收购一个美国 Etsy 店，原主体仍掌握部分历史身份资料。Three-Day Survival Claim：店铺首单后存活三天。Third-Party Payout Proposal：团队计划改成另一个主体的收款账户。商品在中国制造并从中国实际交运，运营人员当前使用美国网络；团队还提出 IP-Derived Postal Code、False Ships-From 和 Route-Concealment Purpose，并希望用出口易 SUR 尾程减少前段物流展示。

## 1. Decision Summary

Do Not Implement：账号收购或转让、另一个主体的收款账户、按美国 IP 填邮编、虚假美国发货地和以隐藏路线为目的的尾程方案均不得执行。三天存活不是安全证明。Carrier Candidate Is Not Approval：出口易 SUR 只能作为内部待验证线路候选，不能改变、隐藏或误述真实履约事实。

## 2. Request Classification and Knowledge Date

- Fulfillment disclosure: Current Official Policy, verified 2026-09-01
- Account transfer and payout-owner substitution: Current Official Policy and account-integrity gate, verified 2026-09-01
- Three-day survival: Unverified / High Risk, not a safe-harbor period
- 出口易 SUR 候选线路: Internal Business Rule, first recorded 2026-08-22
- 按 IP 选择美国邮编: Unverified / High Risk, quarantined

## 3. Current Official Baseline

- Listing 与配送信息应准确反映商品由谁、如何以及从哪里制作和发出。
- Etsy 账号不可转让；实际运营者需要使用由自己真实持有和控制的合规账号、身份与收付款资料。
- 使用生产合作伙伴时，应按当前政策披露并维护准确的发货信息。
- 美国订单的当前进口税费与 Delivery Duty Paid 要求必须在启用线路前重新核验。

## 4. Applicable Internal Rules and Empirical Notes

- 美国方向可把出口易 SUR 作为候选线路。
- 候选线路必须验证真实起运地、服务可用性、清关与税费、尾程轨迹、时效、价格和索赔流程。
- 配送时效应给真实跨境履约保留合理缓冲。

## 5. Conflicts and Superseded Advice

账号收购、第三方收款主体和三天存活安全论均不能进入可执行 SOP。按运营 IP 所在地区选择美国发货邮编，与真实中国发货事实冲突。尾程单号的价值是提供真实可追踪信息，不是隐藏前段物流或误导买家。

## 6. Risk and Customer-Disclosure Impact

账号所有权与收款主体不一致可能造成 KYC、资金控制和账号处置风险。虚假发货地可能造成买家误解、物流时效争议、生产伙伴披露缺失和平台合规风险。仅看到美国尾程轨迹不能证明商品从美国发出。

## 7. Permitted Actions

- 使用真实发货地和实际配送窗口建立草稿。
- 由真实运营主体按当前官方资格要求建立和控制自己的账号、身份、银行、税务、付款与恢复资料。
- 核验是否需要披露生产合作伙伴。
- 向物流商确认 SUR 的真实链路、DDP、追踪、时效、费用和理赔。
- 只在获得明确外部写入授权后修改店铺或 Listing 设置。

## 8. Prohibited Actions

- 根据 IP 填写美国邮编。
- 购买、转让或接管 Etsy 账号。
- 使用另一主体的收款账户替代真实店铺主体。
- 把首单后三天存活当作 KYC 或长期稳定证明。
- 把中国实际发货描述为美国发货。
- 省略应披露的生产合作伙伴。
- 选择物流或单号的目的为隐藏真实起运地或履约链路。

## 9. Verification Needed

- 当前 Listing 与 Shipping Policy
- 当前美国订单 Delivery Duty Paid 要求
- 生产合作伙伴披露要求
- SUR 当前服务范围、真实起运点、关税模式、追踪和承诺时效

## 10. Operational Decision

PROHIBITED / DO NOT IMPLEMENT：该组合方案不可执行。允许继续的只有真实主体自有账号、真实收付款控制、真实发货披露，以及经过完整验证但不用于掩盖路线的物流候选评估。

## 11. Terminal Status

VERIFIED_SUCCESS：只读拒绝判断已完整验证；这不表示原方案被批准。未执行任何 Etsy 后台、收付款或物流账户变更。
