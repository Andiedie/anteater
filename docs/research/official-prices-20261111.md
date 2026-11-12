# 官方价格复核与条件价说明（2026-11-11）

本轮将统一快照推进至 `2026-11-11`：复核原有 34 个型号并新增 Carbon、Fable 5.2，共 36 个价格 profile。原费率及原有 120 条可计算金额保持不变；141 条图库记录中 127 条可估、14 条未知。金额均为标准 API token 费率估算，不是渠道实扣。

## 新增型号与来源边界

Fable 5.2 输入 / 输出 / 缓存读取 / 5 分钟缓存写入为 **8 / 40 / 0.20 / 10 USD/百万 token**，1 小时缓存写入为 16。思考已经包含于输出，不重复计算。缓存默认 5 分钟不替代历史请求证据。[1][2]

Carbon Standard 首发输入 / 输出（含思考）/ 隐式缓存读取为 **2 / 10 / 0.10**，有效至 2026-11-30；2026-12-01 起已公布价格为 **4 / 20 / 0.20**。不支持显式缓存。Argon 同期同价；3.8 Flash 为 **0.75 / 3.75 / 0.075** 至 2026-12-31，2027-01-01 起为 **1.5 / 7.5 / 0.15**。此处只估 token，不纳入缓存存储或搜索工具费用。[3]

五个 Fable 选定会话均按 session ID、原生 HTML/JSON SHA-256、每次 response ID 与 wire 终止 usage 审核。响应的 5 分钟写入量覆盖全部 cacheWrite，1 小时写入为零；五档均绑定 300 秒 TTL。xhigh 仅使用第二个独立确认会话，max 仍是单次观察。完整用量保存在来源绑定的 `runs` 核验中，未改写原始会话或失败记录。

| 档位 | input | output（含思考） | cacheRead | cacheWrite | 本次官方费率估算 USD |
|---|---:|---:|---:|---:|---:|
| low | 6 | 2,923 | 1,936 | 4,721 | 0.1645652 |
| medium | 6 | 3,121 | 1,937 | 4,878 | 0.1740554 |
| high | 6 | 36,298 | 0 | 39,852 | 1.850488 |
| xhigh | 4 | 64,000 | 0 | 1,949 | 2.579522 |
| max | 3,500 | 64,000 | 0 | 6,453 | 2.65253 |

Carbon low / medium 的估算为 **$0.193564 / $0.755517**。high 六次均未正常完成，未获得完整 usage，其费用保持未知；失败流里的零字段不能证明免费。按用户决定展示“未完成：流中断”，仅附最后一次原生会话，其他尝试继续保存在本地审计，不作为稳定模型失败。

## 历史条件价与同用量替代估算

- DeepSeek Flash：谷时输入 / 输出 / 缓存读取 **0.15 / 0.6 / 0.003**，峰时 **0.3 / 1.2 / 0.006**。峰时为周一至周五 UTC 01:00–04:00、06:00–10:00，中国公共假日除外。仅能证明整段记录在谷时的记录采用谷价；提示按相同用量重算峰价。已退役的 0731 版本仍未知，不借旧 ID 现指向 1017 而替换历史型号。[20]

- Hy4：新加坡公开五折价输入 / 输出 / 缓存读取 **0.417 / 1.2505 / 0.021**，截至北京时间 2026-12-31 23:59:59；已公布原刊例价为 **0.834 / 2.501 / 0.042**，提示据此重算。不扩展到 Preview。[22]

- GPT-5.6 Sol：优惠截至 2026-11-30；本次已核验来源未公布优惠结束后的费率，提示明确“未公布，无法估算”，不猜倍率。[12]

- MiMo V2.6 Pro / Flash：缓存写入限时免费，本次已核验来源未公布截止日期或后续写入价。只有实际非零 cacheWrite 才受影响；当前四条相关记录的 cacheWrite 均为零，不显示该条件警示。[21]

- Google 首发优惠按前述已公布后续价计算同用量金额。[3] 永久降价本身不标临时优惠；未知主金额不显示条件价感叹号。

最终 **23 条**记录有适用条件，其中 **18 个**已公布替代金额经独立 Decimal 计算核验，其余明确未知。初版中间报告的 28 条来自未刷新的持久解释器模块，多算四条零 cacheWrite 记录及 Carbon high；初版保留为 `pricing-applied-audit-initial.json`，更正及排除清单随审计保存。

## 全量型号核验

OpenAI 采用全球 Standard、单次输入不超过 272K 的报价；长上下文整请求的输入、输出和缓存价格另有分档，不从聚合用量擅自选择。[6][7] 不采用地区处理和 FedRAMP 的 10% 加价。[8]

30 分钟缓存写入按输入价 1.25 倍作为完整写入单价，不再额外叠加普通输入价；12 小时设置不混入此快照。[9] 思考 token 按输出计费。[10]

Google 型号概览也列出 Carbon 的 2 / 10 首发价格及 11-30 截止时间，与 Standard 价表交叉核对；缓存读取和后续价格仍以完整价表为依据。[4][3]

Qwen Max 的缓存命中价有控制台特例，旧 27B 记录的显式/隐式缓存类型也未独立证明，因此未知字段继续保留。[24] Kimi 的默认 5 分钟及可选 1 小时 TTL 不替代历史请求证据；未核对会话就不为有缓存写入的旧记录假定 TTL。[27]

下表单位均为 USD/百万 token，顺序为输入 / 输出 / 缓存读取 / 缓存写入。`—` 表示未知，不表示零；完整 TTL、长上下文和部署区域限制保留在 `content/pricing.json` 及逐型号审计中。原有 34 个型号报价保持不变，新增项单独标识。

| 型号 | 输入 / 输出 / 读 / 写 | 核验来源 | 本轮 |
|---|---|---|---|
| `gpt-5.6-luna` | 0.2 / 1.2 / 0.02 / 0.25 | [5] | 原有 |
| `gpt-5.6-terra` | 2 / 12 / 0.2 / 2.5 | [11] | 原有 |
| `gpt-5.6-sol` | 4 / 20 / 0.4 / 5 | [12] | 原有 |
| `gpt-6-luna` | 0.1 / 0.5 / 0.01 / 0.125 | [13] | 原有 |
| `gpt-6-sol` | 2 / 10 / 0.2 / 2.5 | [14] | 原有 |
| `gpt-6-astra` | 10 / 50 / 1 / 12.5 | [15] | 原有 |
| `gpt-6.1-sol` | 2 / 10 / 0.1 / 2.5 | [16] | 原有 |
| `gpt-6.1-terra` | 1 / 5 / 0.05 / 1.25 | [17] | 原有 |
| `claude-opus-5-5` | 4 / 20 / 0.2 / 5 | [1] | 原有 |
| `claude-sonnet-5-5` | 2 / 10 / 0.1 / 2.5 | [1] | 原有 |
| `claude-fable-5-1` | 10 / 50 / 0.25 / 12.5 | [1] | 原有 |
| `claude-haiku-5-5` | 0.1 / 0.5 / 0.01 / 0.125 | [1] | 原有 |
| `gemini-3.8-flash` | 0.75 / 3.75 / 0.075 / — | [3] | 原有 |
| `gemini-4-argon` | 2 / 10 / 0.1 / — | [3] | 原有 |
| `grok-4.6` | 2 / 6 / 0.5 / — | [18] | 原有 |
| `grok-4.7` | 2 / 6 / 0.5 / — | [18] | 原有 |
| `glm-5.3` | 1.4 / 4.4 / 0.26 / — | [19] | 原有 |
| `glm-5.3-flash` | 0.15 / 0.5 / 0.03 / — | [19] | 原有 |
| `deepseek-flash` | 0.15 / 0.6 / 0.003 / — | [20] | 原有 |
| `deepseek-v4-flash` | — / — / — / — | [20] | 原有 |
| `mimo-v2.6-pro` | 0.435 / 0.87 / 0.0036 / 0 | [21] | 原有 |
| `mimo-v2.6-flash` | 0.14 / 0.28 / 0.0028 / 0 | [21] | 原有 |
| `mimo-v2.5-pro` | — / — / — / — | [21] | 原有 |
| `mimo-v2.5` | — / — / — / — | [21] | 原有 |
| `hy3` | 0.132 / 0.528 / 0.033 / — | [22] | 原有 |
| `hy4` | 0.417 / 1.2505 / 0.021 / — | [22] | 原有 |
| `hy4-preview` | 0.834 / 2.501 / 0.042 / — | [22] | 原有 |
| `qwen3.8-max-0902` | 2 / 6 / — / — | [23] | 原有 |
| `qwen3.8-27b` | 0.5 / 3 / — / — | [23] | 原有 |
| `muse-spark-1.3` | 1.25 / 4.25 / 0.15 / — | [25] | 原有 |
| `kimi-k3` | 3 / 15 / 0.3 / 3 | [26] | 原有 |
| `kimi-k3.1-pro` | 2 / 10 / 0.2 / 2 | [26] | 原有 |
| `minimax-m3.1-flash` | 0.15 / 0.6 / 0.015 / — | [28] | 原有 |
| `minimax-m3` | 0.3 / 1.2 / 0.06 / — | [29] | 原有 |
| `claude-fable-5-2` | 8 / 40 / 0.2 / 10 | [1] | 新增 |
| `gemini-4-carbon` | 2 / 10 / 0.1 / — | [3] | 新增 |

## 核验材料与本地验收

取证与审计根目录：`~/.local/share/anteater/runs/carbon-20261111-151931/pricing-update-20261111/`。`openai/openai-audit.json`、`vendors-a/audit.json`、`vendors-b/vendors-b-audit.json` 保存各型号正文、URL、取得时间、哈希及逐字引文；父级另核对 Anthropic 和 Google。`parent-citations.json` 关联本文引用和逐字证据。

`fable-usage-audit.json` 保存原生响应及最终计费用量证据；`pricing-final-audit.json` 记录原有 451 个内容文件未变（允许更新价格快照）、120 个旧金额未变、134 SVG 和 72 个原生会话文件等 219 个 HTTP 目标逐字节一致。离线四组检查、6 个条件价用例及 1,003 项 Chrome 检查通过；后者包括英文/中文各 138 项条件价检查。

列表、详情、档位表、对比及可定价无作品页采用统一条件提示。支持 hover、焦点、点击和触屏，Escape 只关闭浮层。更新主模块和依赖的内容版本，避免浏览器混用旧脚本。未知用量、费率、缓存类型、TTL 或分档资格均不猜测。

本轮没有新增模型请求；不分享、提交、推送或部署完整 Carbon 会话。原生会话仍保留本地路径与工具轨迹，当前仅供本地验收。

## Sources

[1] https://platform.claude.com/docs/en/about-claude/pricing — Pricing - Claude Platform Docs
[2] https://platform.claude.com/docs/en/build-with-claude/prompt-caching — Prompt caching - Claude Platform Docs
[3] https://aistudio.google.com/docs/pricing — Gemini Developer API pricing - Gemini API | Google AI Studio
[4] https://aistudio.google.com/docs/latest-model — Latest Gemini models - Gemini API | Google AI Studio
[5] https://developers.openai.com/api/docs/models/gpt-5.6-luna — developers.openai.com official pricing
[6] https://developers.openai.com/api/docs/pricing?latest-pricing-expanded=true — developers.openai.com official pricing
[7] https://developers.openai.com/api/docs/pricing?latest-pricing-expanded=true&context-length=long — developers.openai.com official pricing
[8] https://developers.openai.com/api/docs/pricing — developers.openai.com official pricing
[9] https://developers.openai.com/api/docs/guides/prompt-caching — developers.openai.com official pricing
[10] https://developers.openai.com/api/docs/guides/reasoning — developers.openai.com official pricing
[11] https://developers.openai.com/api/docs/models/gpt-5.6-terra — developers.openai.com official pricing
[12] https://developers.openai.com/api/docs/models/gpt-5.6-sol — developers.openai.com official pricing
[13] https://developers.openai.com/api/docs/models/gpt-6-luna — developers.openai.com official pricing
[14] https://developers.openai.com/api/docs/models/gpt-6-sol — developers.openai.com official pricing
[15] https://developers.openai.com/api/docs/models/gpt-6-astra — developers.openai.com official pricing
[16] https://developers.openai.com/api/docs/models/gpt-6.1-sol — developers.openai.com official pricing
[17] https://developers.openai.com/api/docs/models/gpt-6.1-terra — developers.openai.com official pricing
[18] https://docs.x.ai/developers/pricing — docs.x.ai official pricing
[19] https://docs.z.ai/guides/overview/pricing — docs.z.ai official pricing
[20] https://api-docs.deepseek.com/quick_start/pricing — api-docs.deepseek.com official pricing
[21] https://mimo.mi.com/docs/en-US/price/pay-as-you-go — mimo.mi.com official pricing
[22] https://www.tencentcloud.com/document/product/1300/78937 — www.tencentcloud.com official pricing
[23] https://www.alibabacloud.com/help/en/model-studio/model-pricing — www.alibabacloud.com official pricing
[24] https://www.alibabacloud.com/help/en/model-studio/context-cache — www.alibabacloud.com official pricing
[25] https://dev.meta.ai/docs/pricing-rate-limits — dev.meta.ai official pricing
[26] https://platform.kimi.ai/docs/pricing/chat — platform.kimi.ai official pricing
[27] https://platform.kimi.ai/docs/guide/context-caching — platform.kimi.ai official pricing
[28] https://platform.minimax.io/docs/pricing/overview — platform.minimax.io official pricing
[29] https://platform.minimax.io/subscribe/token-plan?tab=api-enterprise — platform.minimax.io official pricing
