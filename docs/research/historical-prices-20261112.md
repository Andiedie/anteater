# 历史官方价格接入复核（2026-11-12）

本次仅接入 DeepSeek V4 Flash 0731 与 MiMo V2.5 / V2.5 Pro 的 5 条既有记录。统一价格快照 `as_of` 保持 `2026-11-11`；本次是已保存历史证据的复核，不代表重新核验所有厂商现价。新金额经过正式 `display_price` 路径和独立 Decimal 分项计算双重确认，均是原厂 token 费率估算，不是代理账单。

## 原型号、原报价与适用区间

单位为 USD/百万 token；输入、缓存读取分别计费，输出已包含思考。三个历史 SKU 均未恢复独立缓存写入价，继续保存 `null`；5 条记录的 `cacheWrite` 均为 0，因此不阻塞本次计算。非零未知写入量仍会使估价不可计算。

| 历史型号 | 输入未命中 | 输出 | 缓存命中 | 接入的完整 UTC 日期 | 价格依据 |
|---|---:|---:|---:|---|---|
| DeepSeek-V4-Flash-0731（谷时） | 0.22 | 0.66 | 0.007 | 2026-08-17 至 2026-09-08 | [28][30] |
| DeepSeek-V4-Flash-0731（峰时替代） | 0.44 | 1.32 | 0.014 | 同上，仅重算同用量 | [28][30] |
| MiMo-V2.5 | 0.14 | 0.28 | 0.0028 | 2026-05-28 至 2026-10-13 | [16][19] |
| MiMo-V2.5-Pro | 0.435 | 0.87 | 0.0036 | 2026-05-28 至 2026-10-13 | [16][19] |

DeepSeek 原价表同时列明 API ID `deepseek-v4-flash` 和版本 `DeepSeek-V4-Flash-0731`，8 月 13 日公告给出生效时刻 `2026-08-16 16:00 UTC`。9 月 10 日更新说明旧 V4 Flash 已退役，旧 ID 临时路由到 V4.1 Flash；不能把仍可调用的旧 ID 当成原型号仍在服务。[8][9][30]

DeepSeek 早期配图及 8 月 16 日存档把峰时写为每日 UTC `01:00–04:00 / 06:00–10:00`，8 月 29 日存档加入周一至周五条件；来源没有明确这项条件改变的精确生效时刻。[11][28][30]

本次取两种规则的共同谷时区间，历史 profile 使用每日时间窗作保守筛选。目标运行是 `2026-08-29T13:31:56.272Z` 至 `13:34:38.437Z`，满足两种规则；同用量峰价为 `$0.03387732`。[32]

接入日期是保守覆盖范围，不是推定的精确费率起止时间。DeepSeek 排除生效当天，且因 9 月 10 日替换仅给出日期、没有精确时刻及明确时区，排除该日期和前一 UTC 日；最后完整覆盖日取 9 月 8 日。运行必须从开始到最后回复全部落在覆盖范围内，跨过末日午夜也拒绝套用历史价。

MiMo 公告正文与中文公告均写北京时间 `2026-05-27 00:00`，换算为 `2026-05-26 16:00Z`；英文美元价图却写 `May 26 at 6:00 PM PDT`，换算为 `2026-05-27 01:00Z`，相差 9 小时。这里保留两种原文，完整 UTC 日从较晚时刻后的 5 月 28 日开始。[16][19][24]

MiMo 退役公告表格写系统替换时刻为 `2026-10-14 10:00 UTC+8`（`02:00Z`），注释写 `18:00 UTC+8`（`10:00Z`），相差 8 小时。页面明确系统替换后使用新模型、按新模型计费，而旧 ID 失效是 10 月 21 日；因此完整覆盖末日取 10 月 13 日，不能延至 ID 退役日。[23]

MiMo 这次调整是永久降价，且取消输入长度分档；没有把它标为临时促销，也没有把 V2.6 的缓存免费政策外推到 V2.5。[16][19][24]

## 所选原会话与实际计算

复核固定 Gist revision 返回的 `session.html` 原始 raw URL，文件 raw revision 可以不同于 Gist revision。四条 MiMo 原始 HTML 在本次重新取得，DeepSeek 使用已保存并重新校验哈希的固定原始 HTML。解码后从 `leafId` 沿 `parentId` 还原所选分支，独立汇总四个计费字段，并核对原型号、起止时间、结束状态及图库原始作品哈希。

| 记录 | input | output（含思考） | cacheRead | cacheWrite | 正式 computed USD | 原始会话 |
|---|---:|---:|---:|---:|---:|---|
| `deepseek-v4-flash-0731-max` | 21846 | 18179 | 19200 | 0 | 0.01693866 | [32] |
| `mimo-v2.5-high` | 6822 | 5605 | 1408 | 0 | 0.0025284224 | [36] |
| `mimo-v2.5-off` | 10318 | 8305 | 18752 | 0 | 0.0038224256 | [34] |
| `mimo-v2.5-pro-high` | 7342 | 6000 | 1408 | 0 | 0.0084188388 | [35] |
| `mimo-v2.5-pro-off` | 6527 | 5223 | 1472 | 0 | 0.0073885542 | [33] |

5 条合计 `$0.0390969010`。使用 `sum(tokens[field] × rate[field]) / 1_000_000` 逐项计算；没有加入 SDK cost，也没有再次计入 reasoning。每条 `runs` 核验绑定 Gist ID、revision 和 session ID；任一来源字段改变，现有核验即失效。会话内的型号及用量是记录证据，不独立证明代理后端真实修订或实际扣款。

## 修改与回归

- `content/pricing.json`：仅给 3 个已退役 profile 新增 `historical_rates`，并给 5 条记录新增来源绑定；原来所有 36 个顶层费率表、其他 profile 和既有核验条目不变。
- `scripts/pricing.py`：历史日期匹配改为验证完整 UTC 运行区间，拒绝无时区、缺失或非法时长、重叠报价及越界；历史每日峰时与现有工作日峰时分开选择，现有默认行为不变。
- `tests/test_historical_pricing.py`：5 个测试方法覆盖 5 条真实金额、来源改变、原型号/官方来源、未知缓存写入、完整日期边界、重叠报价和历史每日峰时。

最终执行使用 Python 3.12.13，新解释器读取当前文件：

| 命令 | 真实结果 |
|---|---|
| `python3.12 tests/test_historical_pricing.py` | `Ran 5 tests`，`OK`，exit 0 |
| `python3.12 tests/test_price_conditions.py` | `Ran 6 tests`，`OK`，exit 0 |
| `python3.12 tests/test_pricing.py` | exit 1，仅全部正常 SVG 应可估价的验收断言失败，准确列出下述 6 条 Qwen |

仍缺价的是 `qwen3.8-27b-off`、`qwen3.8-max-0902-{high,low,medium,minimal,xhigh}`，属于独立的缓存类型适用性任务，本次未修改。没有删除或降低全价验收要求。

基线比较验证 127 条旧可计算金额、36 个原费率表、453 个原内容文件保持不变。5 条真实价格另通过 10 次双语静态 `price_html` 渲染检查；未运行 build、gallery 或真实浏览器检查，留给父级统一串行验收。该核验时点全库 141 条中 132 条可估，28 条有适用条件；这些是本次代码实际结果，不沿用早期报告的条件数。

## 证据位置与边界

旧证据根：`~/.local/share/anteater/runs/carbon-20261111-151931/pricing-update-20261111/historical-retired/`。本次重验其中 49 项文件哈希及 14 段原逐字引文，验证两份 gzip 归档正文与保存解码 HTML 一致；直接查看 DeepSeek 及 MiMo 美元价图，核对型号、列、单位、数字与生效文字。9 月 6 日错页存档及 404 入口未用作报价证据。没有重新抓取全部官方当前价格。

新证据根：`~/.local/share/anteater/runs/carbon-20261111-151931/resume-20261112/historical/`：

- `baseline.json`、`pricing.before.json`：改前实际金额和内容哈希。
- `evidence-review.json`：每条原 Gist/raw URL、完整 SHA-256、selected leaf、所选分支响应、原型号、起止时间、完整 token 及独立分项金额。
- `*.gist.json`、`*.session.html`、`*.meta.json`、`*.session.decoded.json`：本次原始公开响应、取得时刻、哈希及解码衍生文件。
- `integration-verification.json`：实际 computed 结果、同用量峰价、基线比较、日期时区换算、完整测试 stdout/exit code。
- `test_*.log`、`*.resume.diff`：测试原始输出和相对本次恢复前的精确差异。
- `citations.json`、`citation-verification.json`：沿用历史引用编号并增补固定 MiMo 原会话及 DeepSeek 日期引文的引用账本、严格证据校验。

来源内仍保留 MiMo 两类时刻冲突、DeepSeek 峰时星期条件差异、三个历史 SKU 缺独立缓存写入报价等不足。五条目标运行均远离日期边界，且全部写入量为零；这些不足没有被补成假定值。未新增模型请求、分享、提交或发布。

## Sources

[8] https://api-docs.deepseek.com/news/news260813.md
[9] https://api-docs.deepseek.com/updates.md
[11] https://api-docs.deepseek.com/img/v4_260813_price_en.png
[16] https://mimo.mi.com/docs/en-US/news/latest/v2.5-price-update
[19] https://aistudio-cdn.xiaomimimo.com/xiaomimimo-static/mimo-docs-figures/display/KxrVbPwOMofb91xhtzucgLxBnVg.png
[23] https://mimo.mi.com/docs/en-US/updates/deprecate
[24] https://mimo.mi.com/docs/zh-CN/news/latest/v2.5-price-update
[28] https://web.archive.org/web/20260816171438id_/https://api-docs.deepseek.com/quick_start/pricing
[30] https://web.archive.org/web/20260829155750id_/https://api-docs.deepseek.com/quick_start/pricing/?article_id=article_1779470751466_8
[32] https://gist.githubusercontent.com/Andiedie/22d8f2a1b9a4affba61e7ab27498d6e7/raw/e9d13617f6ea061f53b20dddbe9df5de99559cfc/session.html — deepseek-v4-flash-0731-max pinned native session
[33] https://gist.githubusercontent.com/Andiedie/b484e9d0aa799e6924b613a3d84e1635/raw/aa8005c810e45d57a4e797c544737d89138fa747/session.html — mimo-v2.5-pro-off pinned native session
[34] https://gist.githubusercontent.com/Andiedie/5e94e4de3616ac5f72be6b3e4763ae76/raw/184bcd35d3d9e3af873ba6aacf206593e46512ee/session.html — mimo-v2.5-off pinned native session
[35] https://gist.githubusercontent.com/Andiedie/cc082ba8fdc8f5f1b9b1c92f8542ae16/raw/5dde261a000505d8337a94e3c88dfdcd4fac971e/session.html — mimo-v2.5-pro-high pinned native session
[36] https://gist.githubusercontent.com/Andiedie/2d5763aae707c6fa61c5eb2f91945bc3/raw/ef25b62edb6291670bc8249050b738a74b87d2cc/session.html — mimo-v2.5-high pinned native session
