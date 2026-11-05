# Hy4 正式名称与全站官方价格复核：2026-11-05

## 结论与范围

- 腾讯正式名称是 **Hy4**，不是将缩写展开后的 “Hunyuan 4”。[腾讯 11 月 4 日发布公告](https://www.tencent.com/zh-cn/tencent-launches-hy4-joining-the-ranks-of-the-worlds-leading-open-source-ai-models/)原文：“腾讯混元发布最新一代大语言模型 Hy4”；[型号文档](https://intl.cloud.tencent.com/document/product/1300/80637)明确名称 `Hy4`、API 参数 `hy4`。图库仅更正正式版 off/high 的展示名，保留 slug、请求 ID、原始会话及作品；不改历史 Preview 的展示名或样本。
- [腾讯云官方价表](https://www.tencentcloud.com/document/product/1300/78937)的 Singapore 刊例价为输入 **0.834**、输出 **2.501**、缓存读取 **0.042 USD/百万 token**。页面明确 Hy4 于公告日起至北京时间 **2026-12-31 23:59:59 按刊例价五折计费**，所以本次快照采用 **0.417 / 1.2505 / 0.021**，不是从 OpenRouter 目录或账单抄价。
- 当日直接复核了原快照 **33 个 SKU / 21 个不同 source_url**，包括 3 个退役原版本。30 个在售 SKU 已录入的非空单价均未变；Qwen 的缓存缺口和其他未知条件不因此消失。GPT-5.6 Sol 的优惠期限文字更新为 **2026-11-30**，数值未变。
- 据此将统一 `as_of` 从 2026-11-02 更新到 **2026-11-05**，加入 `hy4`。全站 133 条中 **120 条可估、13 条仍未知**；原有 131 条估算金额不变。
- 核价阶段只补官方 token 估算和名称，未发模型请求、分享、提交、推送或部署。完整会话仍含本地路径和工具轨迹；后续单独发布授权及范围见[测试协议第 23 项](../testing-protocol.md#当前处理决定)。

规则来源：[README / Price estimates](../../README.md#price-estimates)。沿用全球 Standard，或既定 Overseas / Singapore tariff；排除 Batch、Flex、Priority、Fast、高速版、Contributor、订阅、免费额度和账户/渠道折扣。公开、当日有效的厂商活动价适用。输出已含思考；不把思考重复加价，也不把存储、工具或搜索费用混入 token 估算。

## 1. Hy4：名称、价格与优惠边界

### 官方名称

发布公告标题为“腾讯混元发布Hy4，跻身最强开源模型之列”，正文区分 `Hy4`、`Hy4 preview` 和尚待发布的 `Hy4 Flash`。型号文档使用：

> Model Name: Hy4；Model (API Parameter): `hy4`。

图库原来的 “Hunyuan 4” 来自 `scripts/gallery.py::model_label` 对 `hy` 前缀的通用展开，并非核实后的官方名称。正式版改为 `Hy4`，厂商仍为 `Tencent`；导入器只对精确 `hy4` stem 更正默认名称，不批量改写旧型号。OpenRouter 的请求 ID `tencent/hy4` 保留；generation 返回的 `tencent/hy4-20261104` 是渠道版本证据，不新增未经审阅的官方价格别名。

### Singapore 美元价格

官方价表更新时间为 **2026-11-04 12:10:59**。原表头为 Input Tokens / Output Tokens / Cache / Cache Write - 5min / Cache Write - 1h，单位均为 USD / million tokens：

| 型号 | 输入 | 输出 | 缓存读取 | 5m 写入 | 1h 写入 |
|---|---:|---:|---:|---|---|
| Hy4 刊例价 | 0.834 | 2.501 | 0.042 | — | — |
| **Hy4 本次活动价** | **0.417** | **1.2505** | **0.021** | **—** | **—** |
| Hy4 preview | 0.834 | 2.501 | 0.042 | — | — |
| Hy3 | 0.132 | 0.528 | 0.033 | — | — |

页首明确：

> “From the date of this notice until 23:59:59 on December 31, 2026 (Beijing Time), Hy4 model inference fees are settled at 50% of the list price.”
>
> “The discount applies only to usage actually incurred during the above period. After the period expires, the model fees will be settled at the list price again.”

[发布公告](https://www.tencent.com/zh-cn/tencent-launches-hy4-joining-the-ranks-of-the-worlds-leading-open-source-ai-models/)也写明“即日起至2026年12月31日，Hy4在腾讯云TokenHub按刊例价五折计费”，并给出人民币刊例价 6 / 18 / 0.3 元。本站直接采用官方 Singapore 美元价，不用汇率换算人民币，不把 WorkBuddy/CodeBuddy 的免费额度视为 API 免费。

三项美元刊例价分别乘 50%，优惠不再重复打折。该条只指 **Hy4**，不能扩张到 Preview；两者刊例价相同也不等于同一 SKU。Hy4 行没有长度阶梯或峰谷条件，其他厂商转售行的条件不外推给它。独立写入价以 `—` 标记，仍保存为 `null`，不是 0；非零 cacheWrite 的未来记录不能靠这份快照硬算。

这是 **2026-11-05 固定快照**，不是随访问时间自动变价的报价服务。更新快照至活动结束之后时，应重新核价并移除或替换活动费率，不能仅更新日期或依赖旧说明。

### 两档估算

来源：[off run.json](../../content/hy4-off/run.json)、[high run.json](../../content/hy4-high/run.json)。按 selected branch 的已报告用量计算，缓存输入与普通输入分开；两档 cacheWrite 均为 0，不需要猜写入 TTL。

```text
USD = (input × 0.417 + output × 1.2505 + cacheRead × 0.021) / 1,000,000
```

| 档位 | 非缓存输入 | 输出（含思考） | 缓存读取 | 写入 | 思考（输出子集） | 官方估算 USD |
|---|---:|---:|---:|---:|---:|---:|
| off | 8,376 | 6,227 | 23,424 | 0 | 0 | 0.0117715595 |
| high | 80,502 | 30,546 | 270,848 | 0 | 21,137 | 0.0774549150 |
| **合计** | | | | | | **0.0892264745** |

用 `Decimal` 独立复算，四项计费 token 合计与 totalTokens 一致。high 包含那一轮 XML 修正及后续请求，不排除修正消耗。

此前核对的 OpenRouter generation 实扣合计为 **0.089226472 USD**，与估算相差 **0.0000000025 USD**。这种数值接近不改变证据分类：页面只显示“价格估算 · USD”，不用账单或 Pi cost 字段作输入；原始账单仍保留于本地审计目录。

## 2. 既有 33 个 SKU 当日复核

下面 I/O/R/W 分别为普通输入、输出、缓存读取、缓存写入，单位 USD/百万 token。`—` 表示未填或未核实，不是 0。各行是今日直接取得的原厂正文证据，与 [11-02 基线](official-prices-20261102.md)比较；旧研究仅用于比对，不替代今日来源。

| 原快照 SKU | 今日 I / O / R / W | 条件及直接来源 |
|---|---|---|
| gpt-5.6-luna | 0.2 / 1.2 / 0.02 / 0.25 | [模型页](https://platform.openai.com/docs/models/gpt-5.6-luna)，≤272K，W30m |
| gpt-5.6-terra | 2 / 12 / 0.2 / 2.5 | [模型页](https://platform.openai.com/docs/models/gpt-5.6-terra)，≤272K，W30m |
| gpt-5.6-sol | 4 / 20 / 0.4 / 5 | [模型页](https://platform.openai.com/docs/models/gpt-5.6-sol)，≤272K，W30m；优惠至 11-30 |
| gpt-6-luna | 0.1 / 0.5 / 0.01 / 0.125 | [模型页](https://platform.openai.com/docs/models/gpt-6-luna)，≤272K，W30m |
| gpt-6-sol | 2 / 10 / 0.2 / 2.5 | [模型页](https://platform.openai.com/docs/models/gpt-6-sol)，≤272K，W30m |
| gpt-6-astra | 10 / 50 / 1 / 12.5 | [模型页](https://platform.openai.com/docs/models/gpt-6-astra)，≤272K，W30m |
| gpt-6.1-sol | 2 / 10 / 0.1 / 2.5 | [模型页](https://platform.openai.com/docs/models/gpt-6.1-sol)，≤272K，W30m |
| gpt-6.1-terra | 1 / 5 / 0.05 / 1.25 | [模型页](https://platform.openai.com/docs/models/gpt-6.1-terra)，≤272K，W30m |
| claude-opus-5-5 | 4 / 20 / 0.2 / 5 | [Anthropic 价格](https://platform.claude.com/docs/en/about-claude/pricing)，W5m |
| claude-sonnet-5-5 | 2 / 10 / 0.1 / 2.5 | 同上，W5m |
| claude-fable-5-1 | 10 / 50 / 0.25 / 12.5 | 同上，W5m |
| claude-haiku-5-5 | 0.1 / 0.5 / 0.01 / 0.125 | 同上，≤100K，W5m |
| gemini-3.8-flash | 0.75 / 3.75 / 0.075 / — | [Google 价格](https://ai.google.dev/gemini-api/docs/pricing?authuser=6)，Standard 优惠至 12-31；存储另计 |
| gemini-4-argon | 2 / 10 / 0.1 / — | [Argon Pricing](https://ai.google.dev/gemini-api/docs/latest-model#pricing)，优惠至 11-30；输出含思考 |
| grok-4.6 | 2 / 6 / 0.5 / — | [xAI 价格](https://docs.x.ai/developers/pricing)，输入严格 <200K |
| grok-4.7 | 2 / 6 / 0.5 / — | 同上，输入严格 <200K |
| glm-5.3 | 1.4 / 4.4 / 0.26 / — | [Z.ai 价格](https://docs.z.ai/guides/overview/pricing)，限时免费的是存储 |
| glm-5.3-flash | 0.15 / 0.5 / 0.03 / — | 同上 |
| deepseek-flash | 0.15 / 0.6 / 0.003 / — | [DeepSeek 价格](https://api-docs.deepseek.com/quick_start/pricing/)，仍需证明整个区间为谷时 |
| deepseek-v4-flash（0731） | — / — / — / — | 同上明确原版本退役、旧 ID 路由至 1017；不替价 |
| mimo-v2.6-pro | 0.435 / 0.87 / 0.0036 / 0 | [MiMo 价格](https://platform.xiaomimimo.com/docs/en-US/price/pay-as-you-go)，Overseas / Real-time；写入限时免费 |
| mimo-v2.6-flash | 0.14 / 0.28 / 0.0028 / 0 | 同上，写入限时免费，未公布结束日 |
| mimo-v2.5-pro | — / — / — / — | 同上仍声明 10-21 退役 |
| mimo-v2.5 | — / — / — / — | 同上仍声明 10-21 退役 |
| hy3 | 0.132 / 0.528 / 0.033 / — | [腾讯价表](https://www.tencentcloud.com/document/product/1300/78937)，Singapore |
| hy4-preview | 0.834 / 2.501 / 0.042 / — | 同上，不能套 Hy4 正式版五折 |
| qwen3.8-max-0902 | 2 / 6 / — / — | [阿里价表](https://www.alibabacloud.com/help/en/model-studio/model-pricing)，Singapore / International，0<Token≤1M |
| qwen3.8-27b | 0.5 / 3 / — / — | 同上，同地区/档位；缓存类型未知 |
| muse-spark-1.3 | 1.25 / 4.25 / 0.15 / — | [Meta 价格](https://dev.meta.ai/docs/pricing-rate-limits)，Standard，无长上下文溢价 |
| kimi-k3 | 3 / 15 / 0.3 / 3 | [Kimi 价格](https://platform.kimi.ai/docs/pricing/chat)，W5m，无长度档位 |
| kimi-k3.1-pro | 2 / 10 / 0.2 / 2 | 同上，标准 API，非 highspeed；W5m |
| minimax-m3.1-flash | 0.15 / 0.6 / 0.015 / — | [MiniMax Overview](https://platform.minimax.io/docs/pricing/overview)，固定价 |
| minimax-m3 | 0.3 / 1.2 / 0.06 / — | [原快照入口](https://platform.minimax.io/subscribe/token-plan?tab=api-enterprise)返回 Overview，Standard ≤512K，永久降价已含 |

### 条件复核及抓取边界

- [OpenAI 总价表](https://developers.openai.com/api/docs/pricing)直接列出全部 8 个目标型号的 Standard I/O/R/W30m/W12h。Short context **≤272K**，Long context **>272K**；高档整请求输入/缓存 2×、输出 1.5×。[缓存文档](https://developers.openai.com/api/docs/guides/prompt-caching)仍区分 30m 1.25× 与 12h 2.5×，写入是完整价而非普通输入之上的附加费。非零写入仍需对应 TTL 审核。
- GPT-5.6 Sol 的模型页与总价表现在一致写 `promotional pricing is available until November 30, 2026`，因此更新原注释中的“至少 11-21”。这是本次看到的期限文字变化，不能据此推断变更公告发布的确切时刻，也不预填活动之后的未知费率。
- Anthropic 表仍同时列出 5m/1h 写入；Haiku 超过 100K 时 I/O/R/W5m 为 0.5/2.5/0.05/0.625，输入阈值包含缓存。其他目标三款仍无该长上下文分档，全球默认不加 US-only 10%。
- Google 价表明确 Flash 的 12-31 截止、Argon 的 11-30 截止；读取分别 0.075/0.1，输出均含思考。缓存存储不是独立写入 token 价。未重新审计旧请求是否准确上报缓存，只使用既有报告量。
- xAI 价表的 **≥200K** 整请求 I/O/R 为 4/12/1；保持首档阈值 199999，不采用页面其他 Fast、Batch、Priority 或 US regional 报价。
- DeepSeek 仍声明峰时为工作日 UTC 01:00–04:00 / 06:00–10:00，排除中国公共假日；谷时为峰时半价。旧 0731 样本不因 API ID 仍可调用而套当前 1017 的价。
- [阿里缓存文档](https://www.alibabacloud.com/help/en/model-studio/context-cache)仍明确 Max 0902 命中价 **不是**通用显式 10% / 隐式 20%，须看控制台；未访问控制台。27B 的两种比例不同，不能从现有聚合缓存字段猜类型。显式 5m（命中刷新）、写入通常 125%；快照保留既有 `null` 和审核限制。不将其他地区名为 Global 的 1.65/4.951 误当 Singapore 降价。
- Kimi 可读页面仍是空表；本次另取**同一官方 URL 原始 HTML**，检查内嵌 DocTable 的列顺序 `Input / Output / Cached Input / 5m writes / 1h writes`。K3.1 Pro 行为 `$2 / $10 / $0.20 / $2 / $4`；K3 为 `$3 / $15 / $0.30 / $3 / $6`。默认 TTL 5m 的官网说明不替代现有会话的源绑定 TTL 证据。
- MiniMax 两个原入口均取得正文。M3 >512K 为 0.6/2.4/0.12；Priority 排除。M3.1 Flash 没有该长度阶梯。没有把任何未公布的写入价补成 0。

**保留的 13 条记录级缺口：**MiMo V2.5 / V2.5 Pro 4 条、DeepSeek 0731 1 条、Qwen Max 缓存价 5 条、Qwen 27B off 缓存类型 1 条、旧 Opus/Sonnet max 不完整输入用量 2 条。没有通过猜测提高覆盖率；原有源绑定 TTL/失败用量审核不变。

## 3. 可复核产物与维护触发

实现涉及 `content/pricing.json`、两份 Hy4 `run.json`、导入器精确型号名称和回归测试；原始 SVG、HTML/JSON 会话、usage 与其他 131 条源记录不改。官方快照全站日期统一，但旧记录金额保持不变；仅名称、快照日期、Hy4 新价格及 Sol 优惠期限说明变化。

核验命令：

```sh
python3 tests/test_pricing.py
python3 tests/test_gallery.py
python3 scripts/gallery.py prices
python3 scripts/gallery.py build
node tests/browser-smoke.mjs http://localhost:8765
```

上述图库/价格测试、构建和 **335 项 Chrome 交互检查**均通过；本地对比页已确认名称为 Hy4、估价显示 ≈$0.012 / ≈$0.077。

本地基线、改前价表和最终核验保存在 `~/Downloads/anteater-hy4-20261105-173838/pricing-update/`。测试覆盖精确厂商/ID 匹配、不把 Preview/Flash 当 Hy4、思考不重复计费、不读取原始 cost、未公布写入价保持未知、两个档位的官方估价与活动截止说明。

当日正文取回标识：腾讯价表/型号 `mw3djk8o6c8i24`；发布公告 `mw3dmq3692u081`；OpenAI 8 个模型页、总价表及缓存 `mw3dkb0u4k4tkc`；Anthropic/Google/xAI/Z.ai/DeepSeek/MiMo `mw3dke8k7y6i4o`；阿里/Meta/Kimi/MiniMax `mw3dkfqgxbra1x`；Kimi 原始 HTML `mw3dlomcuwuds5`。这些只用于定位当日取回内容，稳定引用是上面的官方 URL，不是独立页面版本号。

**更新触发：**优惠到期、原厂单价/地区/阶梯/缓存条件变化、价格 ID 新别名、非零缓存写入或源记录变化。活动到期不授权重跑绘图；发布本地会话仍需独立批准。
