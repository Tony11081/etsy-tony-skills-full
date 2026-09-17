# 批量队列、状态与恢复

仅当用户要求批量、收藏同步、排队或无人值守时使用。保留批量生产能力；没有可用调度器时不能声称会在对话结束后持续运行。

## 任务来源与去重

GigaB2B 收藏清单或用户指定商品列表是真实任务来源。可在用户自己的已配置 OpenAPI 上读取 Saved Items，也可读取已登录浏览器收藏页。只读取已授权范围，不修改收藏。

以 product_id 为唯一键；接口仅返回 SKU 时暂用精确 SKU，浏览器补足 product_id 后合并同一任务，不创建第二项。逐项比对本地任务状态、完整输出、现有 Etsy 草稿和用户明确连接的外部队列。没有剩余商品时停止，不制造任务。

## 本地队列可以独立使用

每个商品使用独立 `<RUN_DIR>/automation-state.json`，脚本相对于本 Skill 目录：

```powershell
python scripts/update_job_state.py --path "<RUN_DIR>/automation-state.json" --product-id "<PRODUCT_ID>" --stage QUEUED
python scripts/update_job_state.py --path "<RUN_DIR>/automation-state.json" --product-id "<PRODUCT_ID>" --expected-stage QUEUED --stage CLAIMED --lease-owner "<WORKER_ID>" --lease-minutes 30
```

状态：`QUEUED → CLAIMED → FACTS_READY → IMAGES_READY → ETSY_EDITING → ETSY_DRAFT_SAVED → ETSY_DRAFT_VERIFIED → IN_REVIEW`；异常使用 `WAITING_LOGIN`、`WAITING_CAPTCHA`、`WAITING_RUNTIME` 或 `FAILED`。

每完成一个真实验收步骤才推进状态。写入 draft ID，保存事实、图片及最终回读证据。`lastVerifiedAt` 仅记录真正完成独立回读的时间，脚本输出不构成验收证据。

本地状态脚本用于单个执行者串行写入，不提供跨进程锁。需要多执行者时，必须先具备用户已配置的原子认领/锁服务；不能把 `--expected-stage` 当成分布式锁。默认同一时间只有一个 Etsy 编辑任务。

## 接续与失败恢复

- 使用 30 分钟租期，执行时至少每 5 分钟更新一次心跳。仅当租约属于自己、不存在或已过期时接续；接续前重新核对原结果。
- 保留已完成的文案、参考和图片，仅重做缺失或拒收部分。
- 任何 Etsy 操作结果不明时先回读 Draft ID、目标商品与状态，再决定是否有必要重试；每项外部写入最多一次有依据的幂等重试。
- 先在目标店铺去重，防止保存超时后再次创建同一商品。
- 登录、验证码或交互工具失效时保存阻塞原因与恢复位置，在当前任务中清楚报告。发送外部通知另需用户明确授权。
- 只统计独立重新打开并确认图片、价格、数量、标签和 Draft 状态的唯一商品；模板、重复项、部分完成、仅保存点击都不能计入完成量。

## 飞书、任务看板与其他外部队列

完整保留外部队列的连接流程，但本仓库不附带作者的飞书应用、表格、Dashi 项目、Token 或私有 CLI。先发现使用者已经安装的连接器/CLI 并读其说明，不臆造工具名、表格 ID 或接口。

用户已经指定且授权后，核对目标项目/表格，读取当前记录，按商品唯一键去重创建或更新；字段至少包含商品身份、source URL、stage、lease owner/expiry、run folder、Draft ID、blocker 和 evidence。使用服务真正支持的条件写入或原子认领，不模拟并发安全。

操作后重新读取同一记录 ID，核对图片数量、目录/附件、SHA-256、Draft ID 和状态。用户仅要求本地队列时无需连接外部服务；用户明确要求外部同步但工具缺失时，该同步标 BLOCKED，保留已经完成的本地结果。

上传附件或安排持续调度必须在用户授权范围内，并验证最终目标。不可把本地目录、ZIP、HTTP 200 或命令退出码当作上传完成。
