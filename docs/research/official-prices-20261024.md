# 全站官方价格快照：2026-10-24

## 结论与边界

**现有快照选定的地区、服务等级和首档条件下，26 个在售 SKU 的已知单价均与 2026-10-22 快照一致；另外 3 个退役 SKU 仍无可替代的当前原厂报价。** 其中两个 Qwen SKU 只能确认输入/输出及部分缓存规则，不能声称缓存缺口已解决。29 项逐项列于下文，覆盖快照中的全部 **18 个不同 `source_url`**，另抓取必要的缓存规则和退役公告。

**统一日期决定：已补齐文末 Moonshot AI 核查，保留既有地区/部署口径和所有未定价缺口，将 `as_of` 更新为 2026-10-24。** 新增 `kimi-k3.1-pro`，旧 Kimi K3 改用完整报价页链接；原有 30 个 SKU 的单价和条件不变。该阶段 31 个 SKU、121 条记录中，108 条可估算，13 条仍保持未知。

同日后续补入 MiniMax M3.1 Flash 的原厂固定单价，来源与渠道边界见[独立核查](minimax-m3.1-commandcode-20261024.md#3-次要原厂公开-api-价格)。此次仅新增该模型报价，不再推进统一日期，也不改动下述既有单价、条件或缺口。

- **抓取日期：2026-10-24，Asia/Shanghai（UTC+8）**。以下页面均在本次直接通过 `fetch_content` 获取正文，不以搜索摘要、旧研究或聚合商报价代替当前官方证据。长页面取得完整提取正文，再定位目标模型表及相关计费条件；不是仅抓搜索结果摘要。
- 比较基线：[2026-10-22 核价记录](official-prices-20261022.md)及其价格快照；当前数值来源为 [`content/pricing.json`](../../content/pricing.json)，操作与展示约定见 [README](../../README.md#price-estimates)。原快照、Kimi 官方页面全文和变更前内容哈希保存在本地测试目录的 `pricing-review/`，不是公开发布材料。
- 单位均为 **USD / 1M token**。采用既定全球标准 API 价，或已明确选定的海外/新加坡美元价；排除 Batch、Flex、Fast/Priority/Ultrafast、Contributor、套餐、免费配额和私有折扣。存储、搜索、工具费用不纳入 token 估算。
- 下文的“已核实不变”只针对列明的价格字段及适用条件；**未公布不等于免费，`null` 不等于 0**。未核实独立缓存写入价/TTL 的字段继续保持缺口，不能凭通用缓存说明补值。
- 表格原文摘录合并了网页换行和单元格间距，`...` 表示省略；金额后的单位以各表说明为准，不把排版分隔符当原文标点。
- 未发现现有选定 tariff 的数值变化；“发现变化/差异”也记录这次补充发现的文档限制或口径冲突，**不把缺少旧页面对照的事项声称为 10-22 到 10-24 新发生的变价**。

## OpenAI（7 SKU；7 个快照 URL）

### 已核实不变

下表每行链接均为本次抓取的该模型官方页面；最后一列是模型页价格表短原文，次序为输入、缓存读取、输出，均标注 `1M tokens`。

| SKU / 官方模型页 | 输入 | 输出 | 缓存读取 | 写入：30 分钟 | 模型页短原文 |
|---|---:|---:|---:|---:|---|
| [gpt-5.6-luna](https://platform.openai.com/docs/models/gpt-5.6-luna) | 0.20 | 1.20 | 0.02 | 0.25 | `Input $0.2`; `Cached input $0.02`; `Output $1.2` |
| [gpt-5.6-terra](https://platform.openai.com/docs/models/gpt-5.6-terra) | 2.00 | 12.00 | 0.20 | 2.50 | `Input $2`; `Cached input $0.2`; `Output $12` |
| [gpt-5.6-sol](https://platform.openai.com/docs/models/gpt-5.6-sol) | 4.00 | 20.00 | 0.40 | 5.00 | `Input $4`; `Cached input $0.4`; `Output $20` |
| [gpt-6-luna](https://platform.openai.com/docs/models/gpt-6-luna) | 0.10 | 0.50 | 0.01 | 0.125 | `Input $0.1`; `Cached input $0.01`; `Output $0.5` |
| [gpt-6-sol](https://platform.openai.com/docs/models/gpt-6-sol) | 2.00 | 10.00 | 0.20 | 2.50 | `Input $2`; `Cached input $0.2`; `Output $10` |
| [gpt-6-astra](https://platform.openai.com/docs/models/gpt-6-astra) | 10.00 | 50.00 | 1.00 | 12.50 | `Input $10`; `Cached input $1`; `Output $50` |
| [gpt-6.1-sol](https://platform.openai.com/docs/models/gpt-6.1-sol) | 2.00 | 10.00 | 0.10 | 2.50 | `Input $2`; `Cached input $0.1`; `Output $10` |

共同条件与一手证据：

- **首档为单次输入 ≤272,000**，不是上下文最大长度。三款 5.6 页面均写：`Prompts with >272K input tokens are priced at 2x input and 1.5x output for the full request.` 四款 6/6.1 页面明确写：`2x input and cache rates and 1.5x output for the full request.` 本报告不扩展快照覆盖到长上下文档，也不由较简略的 5.6 注释额外推算其长上下文缓存价。
- [官方总价表](https://platform.openai.com/pricing)列出 `30m write` / `12h write`；[Prompt caching](https://platform.openai.com/docs/guides/prompt-caching)的 **GPT-5.6 and later** 章节明确：`cache writes cost 1.25× ... for the default 30-minute lifetime`，12 小时为 `2.5× ordinary input`。因此上表对应 30 分钟，12 小时写入依次为 **0.50 / 5.00 / 10.00 / 0.25 / 5.00 / 25.00 / 5.00**。
- 缓存写入不是基础输入价之外再加费：`These are total write rates, not surcharges on top of ordinary input. Cache-read rates are the same for both lifetimes.` 30 分钟命中刷新至少 30 分钟；12 小时是最短有效期而非删除期限。同一请求可混用 TTL；实际写入须由源记录核实，不能将平台默认值当会话证据。
- **5.6 Sol 优惠至少到 2026-11-21**：`GPT-5.6 Sol’s promotional pricing is available at least through November 21, 2026.` “至少”不是确定结束日；其他六项上述页面未列该类优惠到期日。
- 总价表说明区域处理/FedRAMP 10% 加价，Priority 已改名 Fast；模型页另列 Batch/Flex/Fast，6.1 Sol 还列 Ultrafast。均不混入本次全球 Standard 报价。未见所核七项的峰谷价或退役标记；6 Sol 页面推荐较新的 6.1，但仍给出自己的报价，不能因此替换 SKU。

### 发现变化

未发现与快照数值、272K 首档、30 分钟写入价或 5.6 Sol 优惠期冲突的变化。

### 无法核实

本次只核官方报价，未重新审核各会话 TTL/缓存用量。5.6 Sol 在 11-21 之后的优惠终止日及届时价格未获确定公告，不能预填。

## Anthropic（4 SKU；1 个快照 URL）

### 已核实不变

来源：[Model pricing](https://platform.claude.com/docs/en/about-claude/pricing)。原表列顺序是 `Base input tokens | 5m cache writes | 1h cache writes | Cache hits and refreshes | Output tokens`。

| SKU | 输入 | 输出 | 缓存读取 | 写入：5 分钟 | 写入：1 小时 |
|---|---:|---:|---:|---:|---:|
| `claude-opus-5-5` | 4.00 | 20.00 | 0.20 | 5.00 | 8.00 |
| `claude-sonnet-5-5` | 2.00 | 10.00 | 0.10 | 2.50 | 4.00 |
| `claude-fable-5-1` | 10.00 | 50.00 | 0.25 | 12.50 | 20.00 |
| `claude-haiku-5-5`，输入 ≤100K | 0.10 | 0.50 | 0.01 | 0.125 | 0.20 |

价格行原文单元格摘录（保留原表顺序，省略脚注标号）：

> `Claude Opus 5.5`：`$4 / MTok`、`$5 / MTok`、`$8 / MTok`、`$0.20 / MTok`、`$20 / MTok`。
>
> `Claude Sonnet 5.5`：`$2 / MTok`、`$2.50 / MTok`、`$4 / MTok`、`$0.10 / MTok`、`$10 / MTok`。
>
> `Claude Fable 5.1`：`$10 / MTok`、`$12.50 / MTok`、`$20 / MTok`、`$0.25 / MTok`、`$50 / MTok`。
>
> `Claude Haiku 5.5 (for prompts up to 100,000 tokens)`：`$0.10 / MTok`、`$0.125 / MTok`、`$0.20 / MTok`、`$0.01 / MTok`、`$0.50 / MTok`。

- Haiku **>100,000 输入**时，输入/输出/读取/5m 写入/1h 写入为 **0.50 / 2.50 / 0.05 / 0.625 / 1.00**。原文：`A request's prompt length counts all of its input tokens, including cache reads and cache writes. Each request is priced on its own`。其余三项全 1M 窗口按标准价，不因长上下文加价。
- 缓存读取不能一律套 10%：Fable 为输入的 **2.5%**；Opus/Sonnet 为 **5%**；Haiku 为 **10%**。5m 写入 1.25×、1h 写入 2×，与快照 300 秒写入一致。
- [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)：`By default, the cache has a 5-minute lifetime.`；`The lifetime is measured from the start of the request that writes or reads the cache entry, not from the end of its response.` 命中刷新有效期；混合 TTL 的 `ephemeral_5m_input_tokens` / `ephemeral_1h_input_tokens` 必须分开。
- 全球 Standard 不含 US-only `inference_geo` 的 1.1×、Fast 或 Batch。四项现行模型行未列公开限时结束日、峰谷价或退役标记。

### 发现变化

未发现上述四项的价格、缓存倍率或 Haiku 阶梯变化。定价页提到 **Sonnet 5** 的旧发布优惠已永久化，但不是本次 SKU **Sonnet 5.5**，不得混同。

### 无法核实

没有重新审计原会话。既有 Haiku 六份源哈希绑定的 `cacheWrite1h=0` 审核不能由官网默认 TTL 取代；旧 Opus/Sonnet max 只有输出事实的两份用量缺口继续保留。

## Google（2 SKU；2 个快照 URL）

### 已核实不变

| SKU / 来源 | 输入 | 输出（含思考） | 缓存读取 | 有效期及下一档 |
|---|---:|---:|---:|---|
| `gemini-3.8-flash`：[定价页](https://ai.google.dev/gemini-api/docs/pricing?authuser=6) | 0.75 | 3.75 | 0.075 | 至 2026-12-31；2027-01-01 起 1.50 / 7.50 / 0.15 |
| `gemini-4-argon`：[官方最新模型页 Pricing](https://ai.google.dev/gemini-api/docs/latest-model#pricing) | 2.00 | 10.00 | 0.10 | 至 2026-11-30；2026-12-01 起 4.00 / 20.00 / 0.20 |

- Flash 的 **Standard / Paid Tier, per 1M tokens in USD** 原文分别为：`$0.75 through December 31, 2026. $1.50 starting January 1, 2027.`；`$3.75 ... $7.50 ...`；`$0.075 ... $0.15 ...`。页面输出标签明确为 `Output price (including thinking tokens)`。[3.8 发布说明](https://ai.google.dev/gemini-api/docs/whats-new-gemini-3.8)独立确认模型名称与期限：`Gemini 3.8 Flash ... $0.75/1M input tokens and $3.75/1M output tokens through December 31, 2026`。
- Argon 原文：`Input tokens: $2.00 per 1M tokens ($4.00 starting December 1, 2026)`；`Implicit caching discounts cached input by 95%, to $0.10 per 1M tokens ($0.20 starting December 1, 2026)`；输出含思考 **10 / 20**。
- 所核 Standard 行没有输入长度阶梯或峰谷价。不是 Free、Batch、Flex、Priority 或 Contributor。Flash 当前缓存存储列为 **$0.50 / 1M token-hour** 至 12-31，随后 **$1.00**；它不是每次写入 token 价，不纳入本站估算。
- [Context caching](https://ai.google.dev/gemini-api/docs/caching)（页面标注 `Last updated 2026-10-23 UTC`）：`Implicit caching is enabled by default for all Gemini 2.5 and newer models.` Flash/Argon 最低隐式缓存输入均 **4,096**。Argon 模型页明确：`Explicit caching ... is not supported on Gemini 4 Argon.`

### 发现变化

未发现两项有效优惠价或期限变化。缓存指南本次正文只介绍隐式缓存；不因 Flash 价格表仍列存储费就断言它当前支持哪些显式缓存接口。这是证据边界补充，不是已证实的两日内 API 变更。

### 无法核实

上述隐式缓存指南不保证固定 TTL；两项价格表未给出可直接填入快照的独立缓存写入 token 单价，`cacheWrite=null` 保留。未以存储价格推算写入价格，也未测试接口支持情况。

## xAI（2 SKU；1 个快照 URL）

### 已核实不变

来源：[Pricing](https://docs.x.ai/developers/pricing)。原表列顺序为 Model、Context、Input、Cached input、Output；短原文：

> `grok-4.7 (< 200k prompt tokens) | 500k | $2.00 | $0.50 | $6.00`
>
> `grok-4.6 (< 200k prompt tokens) | 500k | $2.00 | $0.50 | $6.00`

| SKU | 输入 | 输出 | 缓存读取 | 首档 |
|---|---:|---:|---:|---|
| `grok-4.6` | 2.00 | 6.00 | 0.50 | 单次输入严格 <200,000 |
| `grok-4.7` | 2.00 | 6.00 | 0.50 | 单次输入严格 <200,000 |

两项 **≥200K** 行均为输入 **4.00**、输出 **12.00**、缓存读取 **1.00**，适用于整次请求：`billed at the higher rate for all tokens in the request`。缓存[Usage & Pricing](https://docs.x.ai/developers/advanced-api-usage/prompt-caching/usage-and-pricing)说明阈值包含缓存输入，reasoning 用 `Full completion token price`。

[缓存 FAQ](https://docs.x.ai/developers/advanced-api-usage/prompt-caching/best-practices)原文：`Cache entries can be evicted at any time due to server load or restarts.` 因此没有可保证的 TTL，不为其补固定 TTL。主价页两项未列限时优惠截止日、峰谷价或退役标记；Batch 20% 折扣、Priority 2×、US 区域 1.1×、仅 Cursor/Grok Build 的 Fast 价均排除。

### 发现变化

未发现选定全球标准价变化。通用缓存页用 `exceed` 描述阈值，主报价表明确为 **≥200K**；继续采用更明确且保守的 `input_threshold=199999`，不把恰好 200K 当首档。

### 无法核实

未公布独立缓存写入 token 价，`cacheWrite=null` 保留；不把自动缓存当作可以任意填 0 的写入 SKU。

## Z.ai（2 SKU；1 个快照 URL）

### 已核实不变

来源：[Pricing](https://docs.z.ai/guides/overview/pricing)，原文 `All prices are in USD`、`Prices per 1M tokens`。表列为 Input / Cached Input / Cached Input Storage / Output：

> `GLM-5.3 | $1.4 | $0.26 | Limited-time Free | $4.4`
>
> `GLM-5.3-Flash | $0.15 | $0.03 | Limited-time Free | $0.50`

| SKU | 输入 | 输出 | 缓存读取 |
|---|---:|---:|---:|
| `glm-5.3` | 1.40 | 4.40 | 0.26 |
| `glm-5.3-flash` | 0.15 | 0.50 | 0.03 |

[Context Caching](https://docs.z.ai/guides/capabilities/cache.md)说明隐式自动缓存，`New content tokens: Billed at standard prices`。该价表对上述两项未列长度阶梯、峰谷或退役标记；缓存存储是限时免费，不是 token 输入/输出永久免费。

### 发现变化

未发现模型价表变化。缓存指南的通用 `usually 50% of standard price` 不适用于上面明确列出的模型读取单价；以模型专属价格表为准，不以通用示例覆盖。

### 无法核实

缓存指南只说 `Cache has reasonable time limits, will recalculate after expiration`，没有固定 TTL；`Limited-time Free` 未注明存储优惠截止日期。独立缓存写入价未列，继续 `null`，不把存储免费解释为输入写入免费。

## DeepSeek（2 SKU；1 个快照 URL）

### 已核实不变

来源：[Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing/)。模型行直接对应 `deepseek-flash` → `DeepSeek-V4.1-Flash-1017`。

| SKU | 输入 | 输出 | 缓存读取 | 条件 |
|---|---:|---:|---:|---|
| `deepseek-flash` | 0.15 | 0.60 | 0.003 | 谷时；峰时为 0.30 / 1.20 / 0.006 |
| `deepseek-v4-flash`（记录中的 0731） | 未知 | 未知 | 未知 | 退役，保留 `unavailable=true` |

原表 Flash 列短原文：`1M INPUT TOKENS (CACHE HIT) OFF-PEAK $0.003 PEAK $0.006`；`(CACHE MISS) ... $0.15 ... $0.3`；`1M OUTPUT TOKENS ... $0.6 ... $1.2`。

- 峰谷原文：`Peak hours are 01:00 - 04:00 and 06:00 - 10:00 UTC, Monday through Friday, excluding Chinese public holidays.`；`All other hours are off-peak, including weekends and Chinese public holidays in full.` 谷时是峰时的一半，未列该规则的优惠终止日或按长度加价档。
- 退役/路由原文：`The legacy names deepseek-v4-flash and deepseek-v4-flash-vision-exp are still accepted, but the corresponding models have been retired, their requests are served by the DeepSeek-V4.1-Flash-1017 model and billed at the Flash price.` 这是**今天用旧 ID 发新请求**的计价规则，不是旧 0731 样本可冒用 1017 报价的依据。
- [Context Caching](https://api-docs.deepseek.com/guides/kv_cache)默认启用磁盘缓存；`Once the cache is no longer in use, it will be automatically cleared, usually within a few hours to a few days.` 是 best-effort，不是固定 TTL 或 TTL 阶梯写入价。

### 发现变化

未发现 Flash 单价、峰谷窗口或旧模型退役结论变化。主页面另列 Search/Fetch 的服务端工具调用当前免费、**2026-11-01 北京时间 00:00 起收费**；这是被本项目排除的工具附加费，不能混入 token 价格或称为 Flash token 优惠到期。

### 无法核实

0731 原模型没有当前可用报价；不采用腾讯/阿里等平台仍展示的同名旧版价格。未公布独立缓存写入 token 价，`null` 保留。本次未重新核对八份 Flash 会话区间；旧审核关于整段均在谷时的结论沿用，跨峰/假日歧义仍须留空。

## Xiaomi（4 SKU；1 个快照 URL）

### 已核实不变

来源：[Pay-as-you-go](https://platform.xiaomimimo.com/docs/en-US/price/pay-as-you-go)，明确 `Overseas: dollar / M tokens`；下列只用 **Overseas / Real-time API**，不采用国内人民币价、Batch 或 ultraspeed。

| SKU | 输入 | 输出 | 缓存读取 | 缓存写入 |
|---|---:|---:|---:|---:|
| `mimo-v2.6-pro` | 0.435 | 0.87 | 0.0036 | 0（限时免费） |
| `mimo-v2.6-flash` | 0.14 | 0.28 | 0.0028 | 0（限时免费） |
| `mimo-v2.5-pro` | 未知 | 未知 | 未知 | 未知；退役 |
| `mimo-v2.5` | 未知 | 未知 | 未知 | 未知；退役 |

价格表短原文按 Cache Hit / Cache Miss / Output 顺序：

> `mimo-v2.6-pro`：`$0.0036`、`$0.435`、`$0.87`；`mimo-v2.6-flash`：`$0.0028`、`$0.14`、`$0.28`。
>
> `Cache Write: Limited-time Free`

价页未对这两个实时海外条目列输入长度阶梯或峰谷价格。旧两项原文：`were officially deprecated at 10:00 (Beijing time) on October 21,2026`。

另核[官方模型下线公告](https://mimo.mi.com/docs/zh-CN/updates/deprecate)：两项系统替换时间为 **2026-10-14 18:00 UTC+8**，下线时间为 **2026-10-21 10:00 UTC+8**；原文：`使用旧版本模型名称的请求将会自动替换成对应的新版模型，并按照新版模型计价`。此规则不允许把旧样本当 V2.6 估价。

### 发现变化

未发现两项当前价或两项退役结论变化。缓存写入的 0 是**当前限时免费**，不能表述为永久免费；旧快照数值无需因此改变，但后续应以该条件复核。

### 无法核实

官网价页没有给出缓存写入免费截止日、固定保留 TTL 或收费后的写入价。搜索未取得可补足这些条件的一手正文，不采用摘要中其他功能的“5 分钟”作为 prompt cache TTL。两个退役 SKU 继续没有当前官方原版本价，不由替换模型或第三方补齐。

## Tencent（2 SKU；1 个快照 URL）

### 已核实不变

来源：[Model pricing](https://www.tencentcloud.com/document/product/1300/78937)，本次页面标注 `Last updated: 2026-10-03 12:35:12`（这是页面更新时间，不是本次抓取日期）。采用 Language models 的 **Singapore**，表头 `Input Tokens / Output Tokens / Cache (USD / million tokens)`。

| SKU | 官方表名 | 输入 | 输出 | 缓存读取 |
|---|---|---:|---:|---:|
| `hy3` | Hy3 | 0.132 | 0.528 | 0.033 |
| `hy4-preview` | Hy4 preview | 0.834 | 2.501 | 0.042 |

短原文：`Hy3 ... 0.132 ... 0.528 ... 0.033`；`Hy4 preview ... 0.834 ... 2.501 ... 0.042`；两行 Condition、Peak/Off-Peak 均为 `-`。没有这两项的长度阶梯、峰谷或公开优惠到期日。

### 发现变化

未发现这两项新加坡报价变化。该页还包含其他厂商模型，**仅 Hy3/Hy4 是本次用于腾讯原厂报价的证据**；页首 DeepSeek 峰谷计费规则不得外推给 Hunyuan，也不作为 DeepSeek 原厂来源。

### 无法核实

该页未列两项独立缓存写入价或 TTL，保持写入 `null`；没有拿其他腾讯产品的 Anthropic 兼容缓存示例填入 Hunyuan 的 TTL。

## Alibaba（2 SKU；1 个快照 URL）

### 已核实不变

来源：[Model inference pricing](https://www.alibabacloud.com/help/en/model-studio/model-pricing)，采用现有快照注明的 **Singapore / International**，不是其他区域同名 SKU。

| SKU | 输入 | 输出（含思考） | 当前首档条件 | 缓存现状 |
|---|---:|---:|---|---|
| `qwen3.8-max-0902` | 2.00 | 6.00 | `0<Token≤1M`；Thinking / Non-Thinking 相同 | 命中价需控制台，不补数值 |
| `qwen3.8-27b` | 0.50 | 3.00 | `0<Token≤1M`；Thinking / Non-Thinking 相同 | 类型未知的命中用量仍不可估 |

原表短原文：

> `qwen3.8-max-0902 ... International ... Non-Thinking and Thinking modes ... 0<Token≤1M ... $2 ... $6`
>
> `qwen3.8-27b ... International ... Non-Thinking and Thinking modes ... 0<Token≤1M ... $0.5 ... $3`

该范围只有一个价格档；定价总则以单次输入决定整次请求的档位，`K means 1,000 and M means 1,000,000`。两项新加坡行未标峰谷优惠或限时折扣；90 天新客/模型免费额度不属于标准单价优惠，不套入估算。

另核 [Context Cache](https://www.alibabacloud.com/help/en/model-studio/context-cache) 的显式/隐式 Supported models、Billing 和 FAQ：

- 两项都列入新加坡 International 的显式和隐式支持名单，两种模式互斥。
- 显式：有效期 **5 分钟**，命中重置；一般写入输入价 **125%**，命中 **10%**。27B 对应写入 **0.625**、命中 **0.05**；这是以公示倍率和基础价计算的条件值，不是向快照补值。Max 写入同样明确 125%（即 **2.50**），但读取属于例外：`qwen3.8-max, qwen3.8-max-0902 ... the cache hit price is not 10% of the standard input token price.`；`For specific pricing, see the Model Studio console.`
- 隐式：无额外启用费，未命中按普通输入价；一般命中 **20%**。27B 对应 **0.10**。Max 同样被明确排除：`The unit price of cached_token is not 20% ... For specific pricing, see the Model Studio console.`
- TTL 原文：显式 `5 minutes (resets on hit)`；隐式 `Indeterminate. The system periodically clears old, unused cache data.` 不因看到 `cached_tokens` 就认定显式或隐式。

### 发现变化/口径差异

**未发现现有新加坡 tariff 的单价变化；另一个 Global 部署 tariff 不能默默替换现有选定地区/部署。** 同一原厂页面也在 Hong Kong / Frankfurt / Virginia / Tokyo 的 **Global** 部署范围列出 `qwen3.8-max-0902` 输入 **$1.65**、输出 **$4.951**（仍 `0<Token≤1M`）。例如 Hong Kong 小节原文：

> `qwen3.8-max-0902 ... Global ... Non-Thinking and Thinking modes ... 0<Token≤1M ... $1.65 ... $4.951`

**本次确认新加坡 2/6 没变，但不声称官网只有新加坡美元价。** 项目的“全球标准价”不应机械匹配厂商命名的 `Global` 部署档位。本次只补新模型，保留旧快照已明确选择、今天仍有效的 Singapore International tariff，不迁移部署地区，也不改写旧记录的估价口径。未来若改用其他地区的 Global 部署，须一起核查对应缓存价；不能只因基础价较低就替换。没有旧页面证据判断 Global tariff 何时出现，不称其为两日内降价。

缓存文档同时确认 Max 的**显式和隐式**命中价都要查控制台；旧研究只突出隐式例外，本次补全这个限制，不称为已知价变动。

### 无法核实

- Max 两种缓存命中价仍缺；不登录控制台、不启动请求、不套通用 10%/20%。即使只看已选择的新加坡 tariff，五条命中记录仍不能据此补金额。
- 27B 官方两种缓存价可分别算出，但既有 off 记录的聚合用量未标缓存类型；该记录继续不可估，三份零命中记录原口径不受影响。本次不读取或改写会话来猜类型。
- 价页声明 `This document only lists standard prices. For the latest promotions, visit the Model Studio console.` 未核验登录后或账户专属报价，不能把“公开价表无优惠标记”写成“所有账户绝无其他优惠”。

## Meta（1 SKU；1 个快照 URL）

### 已核实不变

来源：[Pricing and rate limits](https://dev.meta.ai/docs/pricing-rate-limits)。`muse-spark-1.3` 的 **Standard** 输入 **1.25**、输出 **4.25**、缓存读取 **0.15**。

短原文：

> `Models: muse-spark-1.3, muse-spark-1.2, and muse-spark-1.1 in Standard mode`
>
> `Cached input $0.15`；`Input $1.25`；`Output $4.25`。
>
> `No long-context premium: you pay the same rate whether your context window is mostly empty or almost full.`

Contributor 模型 ID 与价格另列，不采用其 **0.10 / 0.20 / 0.002**。该 Standard 行未列峰谷价、限时优惠截止日或退役标记。

[Prompt caching](https://dev.meta.ai/docs/prompt-caching)为自动前缀缓存；默认 `in_memory`，会因内存压力或不活跃淘汰。Responses 可设置 `prompt_cache_retention: "24h"`，原文 `up to 24 hours`；不是保证固定存活 24 小时，也未公布对应差异化写入价。

### 发现变化

未发现该 SKU Standard 价或无长上下文溢价条件变化。

### 无法核实

没有独立写入 token 价可核对，`cacheWrite=null` 保留；不把可选 24h 保留参数套用为现有会话已审核 TTL。

## MiniMax（1 SKU；1 个快照 URL）

### 已核实不变

来源：[快照原 URL](https://platform.minimax.io/subscribe/token-plan?tab=api-enterprise)，本次返回官方 **Pricing Overview** 正文；使用 **LLM / Standard** 下的 MiniMax-M3，不是首页另列的 M3.1-Flash，也不是订阅 Token Plan。

| SKU | 输入 | 输出 | 缓存读取 | 条件 |
|---|---:|---:|---:|---|
| `minimax-m3` | 0.30 | 1.20 | 0.06 | 单次输入 ≤512K；永久降价后 |

原表短原文（划线价为旧价，以下只摘当前价）：

> `MiniMax-M3 ≤ 512k input tokens Permanent 50% off ... $0.30 ... $1.20 ... $0.06`
>
> `MiniMax-M3 > 512k input tokens ... $0.60 ... $2.40 ... $0.12`

高档输入/输出/读取为 **0.60 / 2.40 / 0.12**。`Permanent 50% off` 是永久降价，不造一个优惠结束日期；Priority 为 Standard 的 1.5×，不采用。未见 M3 峰谷或退役条件。

[Prompt Caching](https://platform.minimax.io/docs/api-reference/text-prompt-caching.md)明确支持 MiniMax-M3、最低 **512 输入 token**，`New input tokens: Billed at standard input price`。公式只分新输入、命中输入、输出，没有另列 TTL 写入收费。

### 发现变化

未发现 M3 已选 Standard 首档价、512K 阶梯或永久降价条件变化。原链接返回新版定价总览，不是抓取失败；新模型/页面导航的变化不表示现有 M3 价变动。

### 无法核实

缓存指南未给固定 TTL 或独立写入单价，保留 `cacheWrite=null`。不因 Anthropic SDK 兼容示例就套用 Anthropic 的 5m/1h 写入价。

## 覆盖清单与仍须保留的缺口

以上共 **29 项 = 7 + 4 + 2 + 2 + 2 + 2 + 4 + 2 + 2 + 1 + 1**；各节逐项列出精确快照 key，没有漏掉不可报价的三个条目。快照 source URL 数量为 **18 = OpenAI 7 + Google 2 + 其余 9 家各 1**。这 18 个来源本次均取得价格正文，无抓取失败被记成“价格未变”的情况。搜索没有补足的信息保持未知，未引用聚合商价格。

按结果分类：

- **已核实不变：**24 个非退役、非 Qwen SKU 的已录入单价和所列首档条件；另两项 Qwen 的已录入输入/输出价在原选定新加坡条件下不变。三个退役条目的退役/旧 ID 替换原因重新获得官方支持。
- **发现变化：**未找到现有选定地区/服务档位的确定数值变价。阿里另有 Global 部署 tariff；本次明确保留已选新加坡国际版，不变更地区/部署。没有历史页面依据，不称其为新降价。其余补充条件详见各厂商节。
- **无法核实：**三个退役版本的当前原厂价、Max 缓存读取价、27B 实际缓存类型、部分厂商未公布的 TTL/独立写入价及限时免费结束日。Moonshot 的补充证据见末节。

继续保留以下记录级缺口；本次离线重算确认仍有 13 条无法估算：

| 缺口 | 旧记录数 | 本次结论 |
|---|---:|---|
| MiMo V2.5 / V2.5 Pro 退役 | 4 | 官方下线公告确认；不替用 V2.6 |
| DeepSeek V4 Flash 0731 退役/旧 ID 改路由 | 1 | 原厂报价页确认；不替用 1017 |
| Qwen3.8 Max 0902 缓存价未核实 | 5 | 显式、隐式命中均存在控制台缺口 |
| Qwen3.8 27B off 缓存类型缺失 | 1 | 官方两种模式不同；不从聚合 usage 猜 |
| 旧 Opus / Sonnet max 档只有输出事实 | 2 | 官方单价复核不能补齐输入用量 |

其他不放宽的条件：出现缓存写入时核实源绑定 TTL；跨长上下文阶梯不按首档硬算；DeepSeek 整段运行不能证明避开峰时则不猜；`reasoning` 不重复加到已含思考的输出；原会话变更使已有用量/TTL 审核失效。

## Moonshot AI（2 SKU；1 个价格来源）

2026-10-24 核对 [Model Inference Pricing](https://platform.kimi.ai/docs/pricing/chat)。页面可读提取会漏掉动态价格表；本次读取原站 HTML 的内嵌 MDX `DocTable`，核对完整表头和行，而不是以空表或聚合商价格补证。

表头原文为 `Input` / `Output` / `Cached Input` / `5m writes` / `1h writes`，单位 `MTok = 1,000,000 tokens`：

| 原厂模型 ID | 输入 | 输出 | 缓存读取 | 写入：5 分钟 | 写入：1 小时 |
|---|---:|---:|---:|---:|---:|
| `kimi-k3` | 3.00 | 15.00 | 0.30 | 3.00 | 6.00 |
| `kimi-k3.1-pro` | 2.00 | 10.00 | 0.20 | 2.00 | 4.00 |

标准版行的原始单元格为 `kimi-k3.1-pro`、`$2.00 / MTok`、`$10.00 / MTok`、`$0.20 / MTok`、`$2.00 / MTok`、`$4.00 / MTok`。同表的 `kimi-k3.1-pro-highspeed` 为 **4 / 20 / 0.20 / 4 / 8**，是另一报价，不能匹配标准版。

- [K3.1 Pro 指南 FAQ](https://platform.kimi.ai/docs/guide/kimi-k3-1-pro-quickstart)明确：`uses flat pay-as-you-go pricing — there is no tiering by context length`。不增加上下文首档限制；当前价格页未列该标准版的公开优惠到期日。K3 原有报价未变。
- [Context caching](https://platform.kimi.ai/docs/guide/context-caching)明确默认 `5m`，另有 `1h`，报价不同。快照写入价取 5 分钟，并保留 `cache_write_ttl_seconds=300`；非零写入仍须源绑定审核，不由默认 TTL 猜会话条件。
- 缓存指南原文：`cache reads, cache writes, and the uncached remainder are mutually exclusive and sum to total input tokens`。估算使用 Pi 已归一化的三个独立字段，不再次加上总输入。输出用已含思考的 `output`，不另加 `reasoning`。
- 仅新增精确原厂 ID `kimi-k3.1-pro` 和已有记录中的别名 `moonshotai/kimi-k3.1-pro`，不匹配 highspeed 或旧 K3。旧 K3 的来源由首页报价卡改为同一个完整价格页，单价不变。

### 三档估算

三份原始记录的缓存写入均明确为 0，因此不需要假设 TTL；缓存读取按 $0.20 / MTok 计入。公式沿用现有引擎：`(input × 2 + output × 10 + cacheRead × 0.20) / 1,000,000`。

| 档位 | 非缓存输入 | 输出（含思考） | 缓存读取 | 估算 USD |
|---|---:|---:|---:|---:|
| low | 8,097 | 6,724 | 1,024 | 0.0836388 |
| high | 7,077 | 5,610 | 1,024 | 0.0704588 |
| max | 39,098 | 28,434 | 31,232 | 0.3687824 |

合计 **$0.52288**。本次恰与已核实的 OpenRouter 实扣一致，但展示金额来自**官方费率 × 记录用量**，不读取或回退到 `metrics.cost_usd`。页面仍标「价格估算 / Cost estimate · USD」和 `≈`，不是实扣账单。

## 验证与维护

- `python3 tests/test_pricing.py`：覆盖三档精确估值、原厂/渠道 ID、highspeed 不误匹配、旧 K3 不混价、缓存写入 TTL 和污染原始成本不影响估算。
- `python3 tests/test_gallery.py`、`python3 scripts/gallery.py build`：通过；全站 121 条中 108 条可估价，13 条保留上述缺口。
- `node tests/browser-smoke.mjs http://127.0.0.1:8765`：真实 Chrome 255 项交互、语言、布局与价格检查通过。本地对比页已核对三档分别展示 `≈$0.084`、`≈$0.070`、`≈$0.369`，来源及统一核价日期正确。
- 变更前后哈希核对：所有原始 SVG、会话、`run.json` 和源绑定 TTL 审核均不变；原有 118 条记录的估算金额也不变。未重跑测试模型；以上为发布前的本地验证。后续发布授权范围见[执行规范的当前处理决定](../testing-protocol.md#当前处理决定)。

更新触发：任何厂商报价/优惠期变化、拟切换地区或部署档位、替换会话、出现非零缓存写入或跨档/跨峰用量。仍须复核全部来源后统一更新 `as_of`；不能为提高覆盖率猜价，也不能把聚合商账单塞入官方快照。
