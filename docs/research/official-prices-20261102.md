# 全站官方价格复核与 GPT-6.1 Terra 五档估算：2026-11-02

## 结论与适用边界

**2026-11-02 直接复核了旧快照全部 32 个 SKU、20 个不同 `source_url`，另核新 SKU `gpt-6.1-terra`。29 个在售 SKU 已录入的非空费率，在原选定地区、服务等级和首档条件下均核实不变；3 个退役 SKU 仍无当前原版本报价。** 两个 Qwen 的“已核实不变”仅指已录入的输入/输出，绝不表示缓存缺口已补齐。全部来源都取得了正文，没有把抓取失败算成价格未变。

**证据支持在保留既有 tariff、`null`、退役标记和用量/TTL 审核限制的前提下，将统一 `as_of` 推进到 2026-11-02，并新增 Terra 报价。** 本研究本身只创建此文档，不修改价格 JSON、源码、测试或原始记录；快照落地与全站测试由协调者处理。Terra 五档官方 token 估算合计 **USD 0.2297748**，不是渠道实扣或订阅费用。

- 抓取日期：**2026-11-02，Asia/Shanghai（UTC+8）**。使用 `fetch_content` 直接取得下列原厂页面正文；Kimi 动态表另直接读取同 URL 原始 HTML 的内嵌 MDX。没有用搜索摘要、聚合目录、SDK 内置价格或旧研究替代当日原厂证据，也没有登录控制台、访问凭据或发送模型请求。
- 基线：[2026-10-24 全站核价](official-prices-20261024.md)、[同日补入的 MiniMax M3.1 Flash](minimax-m3.1-commandcode-20261024.md#3-次要原厂公开-api-价格)，以及任务开始时 `as_of=2026-10-24` 的 [`content/pricing.json`](../../content/pricing.json)。规则见 [README / Price estimates](../../README.md#price-estimates)。旧文档只用于比较，不是今日费率的证据。
- 单位均为 **USD / 1,000,000 token**；下文 `I/O/R/W` 依次表示非缓存输入、输出（已含思考）、缓存读取、缓存写入。`—` 表示未公布、无法核实或不适用，**不是 0**。写入价格是对应 TTL 的完整 token 单价，不在同一批 token 上重复收普通输入价。
- 保留全球 Standard，或既定 Overseas / Singapore International tariff。不采用 Batch、Flex、Fast、Priority、Ultrafast、Contributor、订阅、免费额度或账户/渠道折扣；不改选阿里命名为 `Global` 的其他地区部署。存储、工具、搜索附加费不计入本站 token 估算。
- “不变”限定为本次查到的费率和列明条件；未列优惠期限不等于永久承诺。补充发现的文档细节，若没有旧正文对照，不能声称是 10-24 后才生效的变更。摘录中的 `…` 表示省略，换行和表格空格做了归一化。

## 1. 新增 GPT-6.1 Terra：原厂 SKU、价格、阶梯与 TTL

直接来源：[模型页](https://developers.openai.com/api/docs/models/gpt-6.1-terra)、[价格页 / Standard pricing data](https://developers.openai.com/api/docs/pricing)、[Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching)、[Reasoning models](https://developers.openai.com/api/docs/guides/reasoning)。

模型页明确 `Model ID: gpt-6.1-terra`，唯一列出的 snapshot/alias 也是该 ID；不是 5.6 Terra、6.1 Sol 或其他厂商同名项。官方 effort 为 `none, low, medium (default), high, xhigh, max`；本次只估算已存在的 **low / medium / high / xhigh / max** 五份本地记录，不添加 `none` 测试、不纳入 `ultra`。

| 单次总输入条件 | I | O（含 reasoning） | R | W：30 分钟 | W：12 小时 |
|---|---:|---:|---:|---:|---:|
| ≤272,000 | 1.00 | 5.00 | 0.05 | 1.25 | 2.50 |
| >272,000 | 2.00 | 7.50 | 0.10 | 2.50 | 5.00 |

关键正文：

> 模型页：`Input | $1 | 1M tokens`；`Cached input | $0.05 | 1M tokens`；`Cache writes | $1.25 | 1M tokens`；`Output | $5 | 1M tokens`。
>
> `Standard cache writes cost $1.25 per million tokens for 30-minute retention and $2.50 for 12-hour retention, before long-context adjustments.`
>
> `Prompts with more than 272K input tokens are priced at 2x input and cache rates and 1.5x output for the full request.`
>
> Reasoning 指南：`While reasoning tokens are not visible via the API, they still occupy space in the model's context window and are billed as output tokens.`

总价表直接列出以上两档的全部五项费率；**高档作用于整次请求，不是只对超出 272K 的部分加价**。模型规格是 **1,050,000 上下文、922,000 最大输入、128,000 最大输出**，不能把上下文容量当作首档计价上限。

缓存指南的 GPT-5.6 and later 小节及 Cache lifetime 小节明确：

- `"30m" (default)` 对应最低 **30 分钟**，写入 1.25×；`"12h"` 对应最低 **12 小时**，写入 2.5×。Terra 读取为普通输入价 **0.05×**，两种 TTL 相同。
- `These are total write rates, not surcharges on top of ordinary input.`；`OpenAI may retain entries longer than the requested minimum`。12h 不是删除期限，不是最大数据保留承诺。
- 30m 读取刷新到至少读取后 30 分钟；已有 12h 覆盖不因一次 30m 读取重启 12h 时钟。升级 30m→12h 会产生新的 12h 写入费，不返还旧费。同请求可混合 TTL；重叠部分按覆盖它的最长写入 TTL 计一次。
- 隐式/显式缓存均支持，最低可缓存前缀 **1,024 token**。这些是服务规则，不证明某份会话用了默认 TTL；非零写入仍需源绑定审核，混合 TTL 不能只用一个首档单价硬算。

**优惠与服务等级：**上述三个 Terra/价格/缓存页面未列 Terra 的限时优惠结束日或峰谷价。价格页的“至少到 2026-11-21”只属于 **GPT-5.6 Sol**，不得借给 Terra。Terra Batch/Flex 为 Standard 的 50%，Fast 为 2×，地区处理可加 10%，均排除；未发现 Terra 退役标记。

### 五档本地用量与公式

来源为各目录中已导入的 `run.json → metrics.tokens`；下表链接指向对应记录。逐份验证其 `source.session_sha256`、`source.export_sha256` 与本地 `session.json`、`session.html` 字节一致，验证四个计费字段都是非负整数、四项和等于 `totalTokens`。本次不重新解释模型表现，不改写源数据，也不以 `metrics.cost_usd` 或 `recorded_cost_usd` 作为估算输入。

通用首档公式：

```text
USD = (I × 1 + O × 5 + R × 0.05 + W30m × 1.25 + W12h × 2.50) / 1,000,000
```

五份记录的 `cacheWrite` 均为 **0**，因此无需假设写入 TTL；公式简化为 `(input + output × 5 + cacheRead × 0.05) / 1,000,000`。`reasoning` 已含在 `output`，不再加一次。五份各自的聚合 `I+R+W` 均低于 272,000，因此其非负逐请求输入也不会越过首档；max 为 **55,380**，不是把整会话输出拿来判断输入价格档。

| 档位 / 本地记录 | I | O（含思考） | R | W | reasoning（仅说明子集） | 官方估算 USD |
|---|---:|---:|---:|---:|---:|---:|
| [low](../../content/gpt-6.1-terra-low/run.json) | 4,320 | 2,248 | 0 | 0 | 0 | 0.0155600 |
| [medium](../../content/gpt-6.1-terra-medium/run.json) | 4,657 | 2,585 | 0 | 0 | 17 | 0.0175820 |
| [high](../../content/gpt-6.1-terra-high/run.json) | 4,652 | 2,572 | 0 | 0 | 14 | 0.0175120 |
| [xhigh](../../content/gpt-6.1-terra-xhigh/run.json) | 5,581 | 3,516 | 0 | 0 | 201 | 0.0231610 |
| [max](../../content/gpt-6.1-terra-max/run.json) | 1,364 | 30,379 | 54,016 | 0 | 21,790 | 0.1559598 |
| **合计** | | | | | | **0.2297748** |

用 `Decimal` 独立重算上述结果。这里的用量沿用已导入的 selected-branch 汇总；哈希校验不等于对渠道上报是否完整或后端内部计量的独立审计。任何源文件变更都需重新核验，不能将此表视为永久豁免。

本次校验的 `session.json` SHA-256：

```text
low     4bc1f65786bc6a081ffbd057f1d579b84f3daa61cae1f627854a5409704f2458
medium  0ce59c67327d704e321e35c6639c7bae927ab055de1da8350822fe614850125f
high    40ddb1ccc5566e355d7383ea796e8cc83fd96b8f883611ea47f765d9d9b7a108
xhigh   e74106bebf48ebe7b268d81941dcc68c4334ed9c0fad1fccd07e3bc84a5f7429
max     b458105a3749768945181dc20c2d4eb3b241ff2383112ca8888638667dd02939
```

## 2. OpenAI：原有 7 SKU，7 个快照 source_url

下列每个模型链接均在本次直接抓取；总价表与缓存条件同第 1 节。各行 **I/O/R/W30m 均与 10-24 不变**。

| SKU / 原快照官方 URL | I | O | R | W30m | W12h | 模型页价格短摘录（I / R / O） |
|---|---:|---:|---:|---:|---:|---|
| [gpt-5.6-luna](https://platform.openai.com/docs/models/gpt-5.6-luna) | 0.20 | 1.20 | 0.02 | 0.25 | 0.50 | `Input $0.2`；`Cached input $0.02`；`Output $1.2` |
| [gpt-5.6-terra](https://platform.openai.com/docs/models/gpt-5.6-terra) | 2.00 | 12.00 | 0.20 | 2.50 | 5.00 | `Input $2`；`Cached input $0.2`；`Output $12` |
| [gpt-5.6-sol](https://platform.openai.com/docs/models/gpt-5.6-sol) | 4.00 | 20.00 | 0.40 | 5.00 | 10.00 | `Input $4`；`Cached input $0.4`；`Output $20` |
| [gpt-6-luna](https://platform.openai.com/docs/models/gpt-6-luna) | 0.10 | 0.50 | 0.01 | 0.125 | 0.25 | `Input $0.1`；`Cached input $0.01`；`Output $0.5` |
| [gpt-6-sol](https://platform.openai.com/docs/models/gpt-6-sol) | 2.00 | 10.00 | 0.20 | 2.50 | 5.00 | `Input $2`；`Cached input $0.2`；`Output $10` |
| [gpt-6-astra](https://platform.openai.com/docs/models/gpt-6-astra) | 10.00 | 50.00 | 1.00 | 12.50 | 25.00 | `Input $10`；`Cached input $1`；`Output $50` |
| [gpt-6.1-sol](https://platform.openai.com/docs/models/gpt-6.1-sol) | 2.00 | 10.00 | 0.10 | 2.50 | 5.00 | `Input $2`；`Cached input $0.1`；`Output $10` |

**条件不变：**首档均为单次输入 **≤272K**；缓存写入采用 **1,800 秒**，12h 不能按 30m 报价。6/6.1 模型页明确高档输入/缓存 2×、输出 1.5×；5.6 模型页的简略注释只写输入 2×、输出 1.5×，但今日总价表直接列出其长上下文缓存价：Luna **R/W30m/W12h=0.04/0.50/1.00**，Terra **0.40/5.00/10.00**，Sol **0.80/10.00/20.00**。这是补足 10-24 文档未展开的证据，不是已证明的新变价，也不扩张本站首档估算覆盖。

5.6 Sol 仍写：`promotional pricing is available at least through November 21, 2026`；不能把“至少”写成确定终止日或预填后续费率。其他六项未见公开优惠截止日、峰谷价或退役标记；6 Sol 推荐 6.1 Sol 不等于其自身退役。

**已到生效日但排除的条件：**总价表写 `Starting Nov 1, 2026, FedRAMP endpoints are also charged a 10% uplift.`；11-02 应视为已生效，不再写“将生效”。全球 Standard 不使用 FedRAMP/地区加价；Fast、Ultrafast、Batch、Flex 和 Codex/ChatGPT 订阅计量不进入快照。原有会话 TTL 审核未重做，全部源绑定限制保留。

## 3. Anthropic：4 SKU，1 个快照 source_url

来源：[Model pricing](https://platform.claude.com/docs/en/about-claude/pricing)，表头为 `Base input tokens | 5m cache writes | 1h cache writes | Cache hits and refreshes | Output tokens`，页面明确 USD。

| SKU | I | O | R | W5m | W1h | 对比 10-24 |
|---|---:|---:|---:|---:|---:|---|
| `claude-opus-5-5` | 4 | 20 | 0.20 | 5 | 8 | 已录入价与条件不变 |
| `claude-sonnet-5-5` | 2 | 10 | 0.10 | 2.50 | 4 | 已录入价与条件不变 |
| `claude-fable-5-1` | 10 | 50 | 0.25 | 12.50 | 20 | 已录入价与条件不变 |
| `claude-haiku-5-5`，≤100K 输入 | 0.10 | 0.50 | 0.01 | 0.125 | 0.20 | 已录入价与条件不变 |

原表短摘录按其列顺序：

> `Claude Opus 5.5 … $4 / MTok … $5 / MTok … $8 / MTok … $0.20 / MTok … $20 / MTok`。
>
> `Claude Sonnet 5.5 … $2 / MTok … $2.50 / MTok … $4 / MTok … $0.10 / MTok … $10 / MTok`。
>
> `Claude Fable 5.1 … $10 / MTok … $12.50 / MTok … $20 / MTok … $0.25 / MTok … $50 / MTok`。
>
> `Claude Haiku 5.5 (for prompts up to 100,000 tokens) … $0.10 / MTok … $0.125 / MTok … $0.20 / MTok … $0.01 / MTok … $0.50 / MTok`。

- Haiku >100,000 输入时 **I/O/R/W5m/W1h=0.50/2.50/0.05/0.625/1.00**，整请求分档，`prompt length counts all of its input tokens, including cache reads and cache writes`。其他三款全 1M 窗口标准价；价页明确 Claude 4.6 及以后除 Haiku 5.5 外无该长上下文溢价。
- [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)：`By default, the cache has a 5-minute lifetime.`；`The lifetime is measured from the start of the request that writes or reads the cache entry, not from the end of its response.` 命中刷新。1h 写入为输入 2×，5m 为 1.25×；Fable 读取 2.5%，Opus/Sonnet 5%，Haiku 10%，不能一律套 10%。
- 保留全球默认，不用 `inference_geo: "us"` 的 1.1×、Fast 或 Batch。四个目标 SKU 未列公开优惠终止日、峰谷价或退役标记；Sonnet **5** 的旧优惠永久化注释不是 Sonnet **5.5**。
- 没有新的费率变化。六份 Haiku 源绑定 300 秒审核仍按原文件有效性判断；混合 TTL 必须分开，官网默认值不能代替会话事实。旧 Opus/Sonnet max 的不完整用量仍不可估。

## 4. Google：2 SKU，2 个快照 source_url

| SKU / 原快照官方 URL | I | O（含思考） | R | 对比 10-24 / 期限 |
|---|---:|---:|---:|---|
| [gemini-3.8-flash](https://ai.google.dev/gemini-api/docs/pricing?authuser=6) | 0.75 | 3.75 | 0.075 | 不变；至 2026-12-31 |
| [gemini-4-argon](https://ai.google.dev/gemini-api/docs/latest-model#pricing) | 2.00 | 10.00 | 0.10 | 不变；至 2026-11-30 |

Flash 的 **Standard / Paid Tier, per 1M tokens in USD** 原文：`$0.75 through December 31, 2026. $1.50 starting January 1, 2027.`；输出 `including thinking tokens` 为 **3.75→7.50**，读取 **0.075→0.15**。存储为 **0.50 / 1M token-hour** 至 12-31，随后 **1.00**；不是独立写入 token 价。

Argon Pricing 原文：`Input tokens: $2.00 per 1M tokens ($4.00 starting December 1, 2026)`；`Implicit caching discounts cached input by 95%, to $0.10 per 1M tokens ($0.20 starting December 1, 2026)`；`Output tokens, including thinking tokens: $10.00 … ($20.00 starting December 1, 2026)`。两项所选行没有长度阶梯或峰谷价，不使用 Free、Batch、Flex、Priority、Contributor。

**本次补足缓存协议边界，不改费率：**

- [主缓存指南](https://ai.google.dev/gemini-api/docs/caching)现在明确 Interactions 只支持隐式缓存；Gemini 2.5 以后默认启用隐式缓存。Flash/Argon 最低输入均 **4,096**，没有固定隐式 TTL 保证。
- 同指南的 Argon 多轮说明：`caches the full previous request only if the new request adds at least 2,050 tokens`；更少增量会将上一请求末 **2,050 token** 按普通输入重处理，模型输出、thought、函数结果都计入增量。只按已报告的命中用量估算，不据此猜或重分配历史用量。
- 指南直接链接的 [generateContent 缓存文档](https://ai.google.dev/gemini-api/docs/generate-content/caching)给出 `model='models/gemini-3.8-flash'` 的显式缓存示例；`If not set, the TTL defaults to 1 hour.` 显式缓存可配置 TTL、按存储时长计费，当前为 Beta。Argon 明确不支持显式缓存。
- 10-24 记录未确认 Flash 显式接口，今日有上述正文可补证；**没有旧全文依据将接口拆分或 2,050 规则称为近期新变更**。两项 `cacheWrite=null` 仍保留：未见可独立填入当前 token 快照的写入单价，不把存储价或默认 1h 套成会话写入费。

### Argon 2,050-token 规则对现有三份记录的影响

按协调者要求，额外读取 [low](../../content/gemini-4-argon-low/run.json)、[medium](../../content/gemini-4-argon-medium/run.json)、[high](../../content/gemini-4-argon-high/run.json) 对应本地 `session.json` 的 **selected branch**，核对 JSON/HTML 与 `run.json` 的源哈希。每份两次 assistant 请求，六次请求全部明确 **R=0、W=0**；逐请求计费字段非负、I+O+R+W=totalTokens，逐项相加精确等于已导入汇总：

| 档位 | 第一次 I / O | 第二次 I / O | 聚合 I / O | 按今日官方价估算 USD |
|---|---|---|---|---:|
| low | 1,322 / 11,460 | 12,943 / 11,419 | 14,265 / 22,879 | 0.257320 |
| medium | 1,323 / 12,626 | 14,110 / 11,935 | 15,433 / 24,561 | 0.276476 |
| high | 1,322 / 29,123 | 30,477 / 17,505 | 31,799 / 46,628 | 0.529878 |

**在本站“按已报告用量估算”的口径下，三条估值保持不变。** 当前计算把全部 reported input 按 I=2 计费，没有将任何 2,050-token 尾段按缓存价优惠；指南描述的是哪些输入会重新按标准价处理，**不是每轮在已报告输入外另加 2,050 token 的固定附加费**。所以公式仍是 `(2×I + 10×O)/1,000,000`，不重新分配或补猜缓存。

边界：本地证据是 `google-generative-ai` 通道的 **Pi 归一化 usage**，不是独立保存的 Google 原生 `usageMetadata`、账单或后端缓存生效证据；不能据此保证渠道没有漏报。本次只证明六次现有记录没有给已报告输入套用缓存折扣、汇总无误，不能把文档规则逆推出历史实际命中量或额外费用。

## 5. xAI：2 SKU，1 个快照 source_url

来源：[Pricing](https://docs.x.ai/developers/pricing)，原表列 `Model | Context | Input / 1M tokens | Cached input / 1M tokens | Output / 1M tokens`。

| SKU | I | O | R | 首档 / 对比 10-24 |
|---|---:|---:|---:|---|
| `grok-4.6` | 2 | 6 | 0.50 | 输入严格 <200K；不变 |
| `grok-4.7` | 2 | 6 | 0.50 | 输入严格 <200K；不变 |

> `grok-4.6 (< 200k prompt tokens) | 500k | $2.00 | $0.50 | $6.00`；4.7 同价。
>
> `grok-4.7 (≥ 200k prompt tokens) | 500k | $4.00 | $1.00 | $12.00`；4.6 同价。

≥200K 整请求 **I/O/R=4/12/1**；以明确价表为准，维持 `input_threshold=199999`。[Usage & Pricing](https://docs.x.ai/developers/advanced-api-usage/prompt-caching/usage-and-pricing)确认总输入含 cached tokens，reasoning 为 `Full completion token price`，其通用 `exceed` 措辞不覆盖价表 ≥ 边界。[缓存 FAQ](https://docs.x.ai/developers/advanced-api-usage/prompt-caching/best-practices)：`Cache entries can be evicted at any time due to server load or restarts.` 无固定 TTL 或独立写入价，`cacheWrite=null` 保留。

两个目标行无公开限时终止日、峰谷价或退役标记。Batch 20% 折扣、Priority 2×、US regional 1.1×及仅 Cursor/Grok Build 的 Fast 均排除；当前 500K 上下文不改变 200K 计价阈值。没有所选 token 费率/条件变化。

## 6. Z.ai：2 SKU，1 个快照 source_url

来源：[Pricing](https://docs.z.ai/guides/overview/pricing)，`All prices are in USD`、`Prices per 1M tokens`。

| SKU | I | O | R | 对比 10-24 |
|---|---:|---:|---:|---|
| `glm-5.3` | 1.40 | 4.40 | 0.26 | 已录入价不变 |
| `glm-5.3-flash` | 0.15 | 0.50 | 0.03 | 已录入价不变 |

原表 Input / Cached Input / Cached Input Storage / Output：

> `GLM-5.3 | $1.4 | $0.26 | Limited-time Free | $4.4`。
>
> `GLM-5.3-Flash | $0.15 | $0.03 | Limited-time Free | $0.50`。

[Context Caching](https://docs.z.ai/guides/capabilities/cache.md)：`New content tokens: Billed at standard prices`；`Cache has reasonable time limits, will recalculate after expiration`。通用 `usually 50% of standard price` 不是这两款的实际命中报价，应采用专属表价。

目标行未列长度阶梯、峰谷或退役条件。**存储**限时免费未给终止日；没有固定 TTL 或独立写入 token 价，`cacheWrite=null` 不变。不能把存储免费当输入/写入免费。

## 7. DeepSeek：2 SKU，1 个快照 source_url

来源：[Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing/)。

| SKU | I | O | R | 对比 10-24 |
|---|---:|---:|---:|---|
| `deepseek-flash` | 0.15 | 0.60 | 0.003 | 谷时价、峰谷条件不变；当前型号为 V4.1-Flash-1017 |
| `deepseek-v4-flash`（样本 0731） | — | — | — | 原版本仍退役，继续 unavailable |

原表 Flash 列：`1M INPUT TOKENS (CACHE HIT) OFF-PEAK $0.003 PEAK $0.006`；CACHE MISS **0.15/0.30**；OUTPUT **0.60/1.20**。峰时原文：`01:00 - 04:00 and 06:00 - 10:00 UTC, Monday through Friday, excluding Chinese public holidays`；其余包括周末与中国公共假日全天为谷时。没有列出该 token 规则的到期日或长度阶梯。

退役原文：`The legacy names deepseek-v4-flash and deepseek-v4-flash-vision-exp are still accepted, but the corresponding models have been retired, their requests are served by the DeepSeek-V4.1-Flash-1017 model and billed at the Flash price.` 新请求的旧 ID 改路由不允许把旧 0731 样本冒用 1017 现价；不以腾讯/阿里转售行补原厂旧版价。

[Context Caching](https://api-docs.deepseek.com/guides/kv_cache)默认启用、best-effort；不活跃缓存 `usually within a few hours to a few days` 清除，不是固定 TTL。独立写入价未公布，保留 `null`；整段会话不能证明避开峰时就不采用谷价，既有区间审核未重做。

**跨日期条件：**当前原厂价页仍保留 `currently free of charge; per-request billing starts at 00:00 Beijing time on November 1, 2026` 的未来式，并列 Search/Fetch 各 **USD 0.75 / 1,000 successful requests**。11-02 已过公告生效点，不能延用“当前免费”；这是被本站排除的工具附加费，不是 Flash token 优惠结束或单价变化。

## 8. Xiaomi：4 SKU，1 个快照 source_url

来源：[Pay-as-you-go](https://platform.xiaomimimo.com/docs/en-US/price/pay-as-you-go)，采用 **Overseas / Real-time API**；页面明确 `Overseas: dollar / M tokens`。

| SKU | I | O | R | W | 对比 10-24 |
|---|---:|---:|---:|---:|---|
| `mimo-v2.6-pro` | 0.435 | 0.87 | 0.0036 | 0，限时免费 | 数值与条件不变 |
| `mimo-v2.6-flash` | 0.14 | 0.28 | 0.0028 | 0，限时免费 | 数值与条件不变 |
| `mimo-v2.5-pro` | — | — | — | — | 原版本仍退役 |
| `mimo-v2.5` | — | — | — | — | 原版本仍退役 |

原价表 Cache Hit / Cache Miss / Output：`mimo-v2.6-pro … $0.0036 … $0.435 … $0.87`；`mimo-v2.6-flash … $0.0028 … $0.14 … $0.28`；写入条款 `Cache Write: Limited-time Free`。没有目标实时海外行的长度阶梯或峰谷价；不取国内人民币、Batch、ultraspeed。

价格页仍写旧两项 `were officially deprecated at 10:00 (Beijing time) on October 21,2026`。[原厂下线公告](https://mimo.mi.com/docs/zh-CN/updates/deprecate)再确认系统替换 **10-14 18:00 UTC+8**、下线 **10-21 10:00 UTC+8**，超过替换点旧名称请求自动转新版并按新版价，超过下线点旧名称失效。不能回填历史旧版本的当前价。

无法核实：写入免费终止日、收费后单价、固定缓存 TTL；未在公示价格页给出。免费写入 0 不等于永久免费，两个退役 SKU 不得用 V2.6 替价。

## 9. Tencent：2 SKU，1 个快照 source_url

来源：[Model pricing](https://www.tencentcloud.com/document/product/1300/78937)，**Language models / Singapore**，单位 `USD / million tokens`。页面更新时间现为 **2026-11-01 12:02:55**（10-24 研究记录的是 10-03）；这是原页更新标记，不等于 Hy3/Hy4 改价日期。

| SKU | 原厂表名 | I | O | R | 对比 10-24 |
|---|---|---:|---:|---:|---|
| `hy3` | Hy3 | 0.132 | 0.528 | 0.033 | 不变 |
| `hy4-preview` | Hy4 preview | 0.834 | 2.501 | 0.042 | 不变 |

> `Hy3 … 0.132 … 0.528 … 0.033`；`Hy4 preview … 0.834 … 2.501 … 0.042`。

两行 Condition、Peak/Off-Peak、Cache Write - 5min、Cache Write - 1h 均为 `-`；没有目标条目的长度阶梯、峰谷价、公开优惠到期日。写入 `-` 不是免费，保持 `cacheWrite=null`，TTL 未核实。页首 DeepSeek 峰谷规则以及其他厂商转售价不外推给 Hunyuan，也不作为其他模型的原厂证据。

## 10. Alibaba：2 SKU，1 个快照 source_url

来源：[Model inference pricing](https://www.alibabacloud.com/help/en/model-studio/model-pricing)，仍选 **Singapore / International**。

| SKU | I | O（Chain of thought + answer） | 原表条件 | 对比 10-24 |
|---|---:|---:|---|---|
| `qwen3.8-max-0902` | 2.00 | 6.00 | `0<Token≤1M`，Thinking / Non-Thinking 相同 | 输入/输出不变；缓存仍缺 |
| `qwen3.8-27b` | 0.50 | 3.00 | `0<Token≤1M`，Thinking / Non-Thinking 相同 | 输入/输出不变；实际缓存类型仍缺 |

短摘录：`qwen3.8-max-0902 … International … Non-Thinking and Thinking modes … 0<Token≤1M … $2 … $6`；Qwen3.8 开源小节 Singapore 行：`qwen3.8-27b … International … 0<Token≤1M … $0.5 … $3`。总则 `K means 1,000 and M means 1,000,000`，按单请求总输入决定整请求档位；所选两行各只有一个档，没有峰谷或限时折扣标记。

[Context Cache](https://www.alibabacloud.com/help/en/model-studio/context-cache)当日重新核对 Supported models、Billing、FAQ：

| 模型 | 显式写入（5m） | 显式命中 | 隐式命中 | 仍不得填补的缺口 |
|---|---:|---:|---:|---|
| Qwen Max 0902 | 2.50（I×125%） | 未公布具体值，指向控制台 | 未公布具体值，指向控制台 | R 继续 null；不能套 10%/20% |
| Qwen 27B | 0.625（I×125%） | 0.05（I×10%） | 0.10（I×20%） | 源记录没有类型，不能挑更便宜的一项 |

关键例外：`qwen3.8-max, qwen3.8-max-0902 … the cache hit price is not 10% of the standard input token price`；隐式也明确 `not 20%`；`For specific pricing, see the Model Studio console.` 未访问控制台。

显式有效期 `5 minutes (resets on hit)`；隐式 `Indeterminate. The system periodically clears old, unused cache data.` 两项都在新加坡 International 的两类支持名单；模式互斥。上述推导出的条件价是研究结果，不表示已解决实际记录的缓存类型/TTL，也不自动填进 JSON。未命中隐式输入按基础价，不额外造写入 SKU。

**地区口径不迁移：**其他地区的 `Global` Max 0902 仍有 **1.65/4.951**，例如 Hong Kong；不是所选 Singapore **2/6** 降价。其他地区页首关于限时夜间折扣的通用说明也不外推到新加坡两行。价页仍声明 `This document only lists standard prices. For the latest promotions, visit the Model Studio console.`；没有核验账户优惠，不声称所有账户绝无其他价格。

## 11. Meta：1 SKU，1 个快照 source_url

来源：[Pricing and rate limits](https://dev.meta.ai/docs/pricing-rate-limits)。

| SKU | I | O | R | 对比 10-24 |
|---|---:|---:|---:|---|
| `muse-spark-1.3` | 1.25 | 4.25 | 0.15 | Standard 价与无长上下文溢价条件不变 |

> `Models: muse-spark-1.3, muse-spark-1.2, and muse-spark-1.1 in Standard mode`。
>
> `Cached input $0.15`；`Input $1.25`；`Output $4.25`。
>
> `No long-context premium: you pay the same rate whether your context window is mostly empty or almost full.`

Contributor 是另一个模型 ID/数据使用条件和报价（I/O/R=0.10/0.20/0.002），不采用。目标 Standard 行没有峰谷、公开限时结束日或退役标记。[Prompt caching](https://dev.meta.ai/docs/prompt-caching)默认 `in_memory`，可因内存压力/不活跃淘汰；Responses `prompt_cache_retention: "24h"` 为 `up to 24 hours`，不是固定保证。没有独立写入报价，继续 `cacheWrite=null`，不把可选 TTL 当现有会话事实。

## 12. Moonshot AI：2 SKU，1 个快照 source_url

来源：[Model Inference Pricing](https://platform.kimi.ai/docs/pricing/chat)。**当日可读提取仍只有空 `<tbody />`，因此另直接抓取同一原站原始 HTML，定位内嵌 `DocTable` 的 `columns` 与 `rows`。** 不是从空表推价，也不是借用腾讯或聚合商报价。

表头 `Input | Output | Cached Input | 5m writes | 1h writes`，`1 MTok = 1,000,000 tokens`：

| SKU | I | O | R | W5m | W1h | 对比 10-24 |
|---|---:|---:|---:|---:|---:|---|
| `kimi-k3` | 3 | 15 | 0.30 | 3 | 6 | 数值与条件不变 |
| `kimi-k3.1-pro` | 2 | 10 | 0.20 | 2 | 4 | 数值与条件不变 |

HTML 的目标 `rows` 单元格短摘录：

```text
children:`kimi-k3.1-pro` … `$2.00 / MTok`,`$10.00 / MTok`,`$0.20 / MTok`,`$2.00 / MTok`,`$4.00 / MTok`
children:`kimi-k3` … `$3.00 / MTok`,`$15.00 / MTok`,`$0.30 / MTok`,`$3.00 / MTok`,`$6.00 / MTok`
```

同表 `kimi-k3.1-pro-highspeed` 是 **4/20/0.20/4/8**，不能匹配 Standard SKU。价格表 K3 系列统一 **1,048,576** 上下文，没有输入长度分价行；[K3.1 Pro FAQ](https://platform.kimi.ai/docs/guide/kimi-k3-1-pro-quickstart)直接确认 `flat pay-as-you-go pricing — there is no tiering by context length`。当前两个目标行未列公开优惠截止日、峰谷或退役标记；10-31 起限制新注册用户的公告属于 **K2 系列**，不属于本次 K3。

[Context caching](https://platform.kimi.ai/docs/guide/context-caching)：默认 `5m`，另有 `1h`；`cache reads, cache writes, and the uncached remainder are mutually exclusive and sum to total input tokens`。写入已包含在原输入成本拆分中，不重复计费；TTL 首次写入锁定，命中按原 TTL 免费续期，等原项完全过期后才能改 TTL 重写。两款快照仍采用 **300 秒**写入价；官网默认行为不证明历史会话 TTL。Batch 为标准价 60%，不采用；价格不含适用税款。

## 13. MiniMax：2 SKU，2 个快照 source_url

本次分别直接获取 [M3.1 Flash 的 Pricing Overview](https://platform.minimax.io/docs/pricing/overview)和 [M3 原 source_url](https://platform.minimax.io/subscribe/token-plan?tab=api-enterprise)，后者正常返回同一新版 Pricing Overview 正文，不是失败或登录后的报价。

| SKU | I | O | R | 条件 / 对比 10-24 |
|---|---:|---:|---:|---|
| `minimax-m3.1-flash` | 0.15 | 0.60 | 0.015 | 固定 Standard 单价，不按长度分档；不变 |
| `minimax-m3` | 0.30 | 1.20 | 0.06 | ≤512K 输入，永久降价后；不变 |

> Overview：`MiniMax-M3.1-Flash … $0.15 … $0.60 … $0.015`。
>
> Standard：`MiniMax-M3 ≤ 512k input tokens Permanent 50% off … $0.30 … $1.20 … $0.06`。
>
> [M3.1 原厂发布文](https://www.minimax.io/blog/minimax-m31f)：`Flat pricing per 1M tokens: $0.15 input · $0.60 output · $0.015 cached input.`

M3 >512K 为 **I/O/R=0.60/2.40/0.12**；Priority 1.5× 排除。`Permanent 50% off` 已包含在当前价，不造结束日期；M3.1 没有该分档或独立公开优惠截止日。两项未见峰谷或退役条件。

[Prompt Caching](https://platform.minimax.io/docs/api-reference/text-prompt-caching.md)明确同时支持 M3.1 Flash 和 M3，最低 512 输入；`New input tokens: Billed at standard input price`；公式只分新输入、命中、输出。未公布独立写入 token 单价或固定 TTL，两项 `cacheWrite=null` 保留。兼容 Anthropic SDK 不等于采用 Anthropic 的 TTL/写入价。

## 14. 对比汇总、保留缺口与可追溯性

### 逐项覆盖结论

原有 **32 = 7 OpenAI + 4 Anthropic + 2 Google + 2 xAI + 2 Z.ai + 2 DeepSeek + 4 Xiaomi + 2 Tencent + 2 Alibaba + 1 Meta + 2 Moonshot + 2 MiniMax**，加新 Terra 为 **33**。各节表格逐项列出精确快照 key，包含不可报价的 3 项。旧快照 **20 个不同 source_url = OpenAI 7 + Google 2 + MiniMax 2 + 其余 9 家各 1**，均已直接取得正文并核对目标行；新 Terra 使用独立官方模型 URL。

| 分类 | 本次结论 |
|---|---|
| 已核实不变 | 原有 29 个在售 SKU 已录入非空单价、所选地区/服务档位及本文列明的首档/优惠条件；Qwen 仅输入/输出数值获确认 |
| 新增可核实 | Terra 的全部 I/O/R、30m/12h 写入与长上下文单价、五份本地估算 |
| 确定 token 单价变化 | **未发现**所选 tariff 从 10-24 到 11-02 的数值变化 |
| 到达既有公告生效点 | OpenAI FedRAMP 10% 加价、DeepSeek Search/Fetch 11-01 开始收费；不属于本站选定全球 token 基础价 |
| 证据补充，不冒称新变价 | 5.6 长上下文缓存明码表；Google generateContent 显式缓存与 Argon 2,050-token 规则；Kimi TTL 锁定续期说明；Tencent 页面更新标记 |
| 无法核实 | 3 个退役原版本现价、Qwen Max 命中价、27B 样本缓存类型、未公示的独立写入价/固定 TTL/免费结束日、缺失的历史用量 |

继续保留 10-24 研究列出的 **13 条记录级缺口**，本次不通过猜测提高覆盖率；下列计数是旧审核清单，不冒充本次执行全站价格命令的结果：

| 原缺口 | 旧记录数 | 本次处理 |
|---|---:|---|
| MiMo V2.5 / V2.5 Pro 退役 | 4 | 下线仍确认，不替用 V2.6 |
| DeepSeek V4 Flash 0731 退役 | 1 | 原版本无现价，不替用 1017 |
| Qwen Max 0902 缓存命中价 | 5 | 显式/隐式均需控制台，未访问，继续未知 |
| Qwen 27B off 缓存类型 | 1 | 显式与隐式读取价不同，不从聚合字段猜 |
| 旧 Opus / Sonnet max 只有输出事实 | 2 | 官方价格不能补出未记录的输入/缓存用量 |

此外：源记录变更使既有 TTL/用量审核失效；不完整用量、混模型、超档聚合、未审 TTL 非零写入、DeepSeek 跨峰/假日不明均不得按首档硬算。`reasoning` 不重复加进输出或总量。MiMo 限时免费写入、Z.ai 限时免费存储与 5.6 Sol“至少”期限仍需将来复查。

### 本次抓取记录索引

以下是本次工具响应标识，供恢复当日取得的原站正文；稳定引用仍为各节官方 URL 与短摘录。它们不是页面版本号或发布日期，也不是第三方价格来源。

| 抓取响应标识 | 原厂正文覆盖 |
|---|---|
| `mvz3q51h7oalhe` | Terra 模型、OpenAI 总价表、OpenAI prompt caching |
| `mvz3qnw2ne416l` | OpenAI reasoning 计费与 7 个原快照模型 URL |
| `mvz3r06wzrtuy6` | 其余 13 个不同快照 URL：Anthropic、Google 两页、xAI、Z.ai、DeepSeek、Xiaomi、Tencent、Alibaba、Meta、Kimi、MiniMax 两页 |
| `mvz3s2wxg0ycv4` | Kimi 同价格 URL 的原始 HTML，内嵌 MDX `DocTable` 完整表头与费率行 |
| `mvz3s59yct5wc8` | 各厂商缓存补充页、Xiaomi 退役公告、Kimi K3.1 FAQ、MiniMax M3.1 发布文 |
| `mvz3tkj32fbjoe` | Google generateContent 显式/隐式缓存正文 |

### 验证与后续操作边界

- 已做：32 个旧 SKU / 20 个原 URL 的覆盖核对；33 SKU 逐项费率/条件对照；Terra 五份 session JSON/HTML 源哈希校验、token 非负/合计/首档断言与 `Decimal` 精确估算；Argon 三份源哈希、六次逐请求 usage、聚合一致性及新缓存说明的计价影响核对。
- 未做：全站构建、单元/浏览器回归、旧会话重新导入或其他历史用量全面重审；本 worker 只写本文，不修改价格快照，不重跑模型，不分享、提交、推送或部署。
- 协调者落地快照后仍需按 README 执行离线 coverage、pricing/gallery 测试、build 和浏览器检查；未知条目继续显式保留。来源页面变化、到达优惠时间点、拟迁移地区/服务等级、出现新缓存写入或源文件变化时重新核验，不能只改 `as_of` 而跳过全量原厂复核。
