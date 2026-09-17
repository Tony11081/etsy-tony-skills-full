# 工具与配置

安装仅把 Skills 文件放进客户端，不会自动登录服务、授予店铺写入权限或安装所有运行环境。使用对应能力时再准备下面的依赖。

| 任务 | 依赖 | 未具备时 |
| --- | --- | --- |
| 标题、文案、已有资料分析 | 支持 Skills 的 AI 客户端 | 不需要额外 API Key |
| 商品图、设计概念图 | 可看图且有内置 `image_gen` 的 Codex 环境 | 保存计划与输入，准确报告无法出图 |
| 当前公开市场/政策研究 | 浏览或网页读取工具 | 只分析已有资料，不伪称实时验证 |
| eRank 会员证据 | 使用者自己的会员浏览器会话或 CSV/HTML/JSON 导出 | 不把公开样本/本地估算当会员数据 |
| eRank CLI、定价、校验脚本 | Python 3.10+；CLI 另需 click、requests、Pillow | 可先做不依赖脚本的部分，真实计算与验证状态单列 |
| GigaB2B OpenAPI | Node.js 20+ 与使用者自己的 OpenAPI 配置 | 可使用已登录主商品图库提取，按实际工具能力执行 |
| 店铺保存/外部队列 | 可用浏览器或连接器，正确目标和明确授权 | 交付本地草稿；外部动作标为受阻 |

## eRank CLI 源码随包提供

打开安装后的 `etsy-tony-full-erank-tools` 目录，在自己的 Python 环境中执行：

```bash
python -m pip install ./harness
python scripts/run_erank.py -- --help
python scripts/run_erank.py -- --json live sources
```

程序使用 `ERANK_SESSION` 指定的本地状态文件，否则使用运行目录的 `.erank_session.json`。不要将研究记录、订单导出或账号配置提交到公共仓库。公开 API 的可用性会变化，现场回读优先。

## GigaB2B 素材脚本

在 `etsy-tony-full-gigab2b-assets` 目录执行 `node scripts/etsy-tony-full-gigab2b-assets.mjs --help` 查看参数，无需凭据。

实际请求使用使用者自行配置的 `GIGAB2B_CLIENT_ID`、`GIGAB2B_CLIENT_SECRET`；可选 `GIGAB2B_API_BASE`，默认官方 OpenAPI。也可显式指定一个仓库外的私有 `--env-file`。不要把凭据贴进对话、命令示例、截图或提交。

该脚本保留 SKU 下载、收藏读取、商品详情、价格、库存、图片/附件与恢复交接；下载完成后仍需实际看图核验。账号未配置时不能把素材提取报为成功。

## 可选的 Clawlist Gemini 流程

普通 Listing 使用当前模型，无需 Clawlist。只有用户明确选择 `etsy-tony-full-erank-listing` 的 eRank + Clawlist 流程，或请求旧式 Clawlist 脚本时，才使用 `https://clawlist.best/v1`。

使用者通过自己的安全配置提供 `CLAWLIST_API_KEY`；模型可由 `ETSY_LISTING_GEMINI_MODEL` 指定。默认模型名是原流程配置，服务支持情况需执行时确认。此路径会将明确提交的商品事实、关键词证据和参考图片发往该服务，可能计费；不要把与任务无关的客户或店铺私有资料加入请求。未选择该路径时不调用。

## 本地队列与外部队列

本地状态与串行批量流程随包提供。飞书、Dashi 等外部队列需使用者自己的连接器、项目/表格和权限；原作者的私有适配器不在公开包内。既有本地批量能力不依赖这些账号。脚本不是常驻调度服务，多执行者需要真正的锁/原子认领支持。

## 常见阻塞

- `node` / `npx` 找不到：先安装 Node.js，再重新打开终端。
- 安装成功但列表没出现：新开对话，并核对安装到的是正在使用的客户端。
- GitHub 克隆失败：检查自己的网络与代理设置；不要关闭证书验证，也不要把账号密码发给作者。
- 无图片工具、会员未登录或 API 未配置：按对应依赖补齐后从已保存阶段继续，不能用虚构输出顶替。

需要跟做说明：抖音搜索 **93440780745（Etsy-Tony）**，私信 **「Skills」**，只提供不含隐私的错误信息和当前步骤。
