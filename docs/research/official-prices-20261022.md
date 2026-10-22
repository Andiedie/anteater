# 全站官方价格快照：2026-10-22

## 用途与口径

用户要求全站只展示一种「价格估算」，不再混用 Pi、聚合目录和官方价格。`content/pricing.json`（schema 2）是当前数值来源，`scripts/pricing.py` 负责计算。按同一核价日期的厂商标准按量 API 价格重算记录用量，而不是模拟历史账单；不修改原始会话、SVG 或 SDK 费用字段。

这份记录取代当天先前仅覆盖三款新模型的核价说明。旧价格快照及两份费用事实改动前备份保存在 `~/Downloads/anteater-ui-pricing-20261022-230400/`。这里描述的是当前选入图库的 attempt，不含已废弃测试。

统一采用厂商公布的全球标准价；没有全球美元价时明确使用海外/新加坡美元价，不自行换算人民币。公开发布优惠和永久降价是该日期有效的公示价，不是私有折扣。排除 Batch、Flex、Priority、Contributor、订阅和渠道折扣。只计算 token 费用，不含缓存存储、搜索及工具附加费，不代表实际实扣。

## 核实的官方单价

均为 USD / 1M token。缓存写入没有用量时不补造用量；表中未列写入不表示免费。原始官方模型页优先于发布时的旧报价或搜索摘要。

| 模型 | 输入 | 输出（含思考） | 缓存读取 | 官方来源与条件 |
|---|---:|---:|---:|---|
| GPT-5.6 Luna | 0.20 | 1.20 | 0.02 | [模型页](https://platform.openai.com/docs/models/gpt-5.6-luna)，≤272K 输入 |
| GPT-5.6 Terra | 2.00 | 12.00 | 0.20 | [模型页](https://platform.openai.com/docs/models/gpt-5.6-terra)，≤272K 输入 |
| GPT-5.6 Sol | 4.00 | 20.00 | 0.40 | [模型页](https://platform.openai.com/docs/models/gpt-5.6-sol)，≤272K；优惠至少持续至 11-21 |
| GPT-6 Luna | 0.10 | 0.50 | 0.01 | [模型页](https://platform.openai.com/docs/models/gpt-6-luna)，≤272K 输入 |
| GPT-6 Sol | 2.00 | 10.00 | 0.20 | [模型页](https://platform.openai.com/docs/models/gpt-6-sol)，≤272K 输入 |
| GPT-6 Astra | 10.00 | 50.00 | 1.00 | [模型页](https://platform.openai.com/docs/models/gpt-6-astra)，≤272K 输入 |
| GPT-6.1 Sol | 2.00 | 10.00 | 0.10 | [模型页](https://platform.openai.com/docs/models/gpt-6.1-sol)，≤272K 输入 |
| Claude Fable 5.1 | 10.00 | 50.00 | 0.25 | [Anthropic 定价](https://platform.claude.com/docs/en/about-claude/pricing)，全球标准价 |
| Claude Opus 5.5 | 4.00 | 20.00 | 0.20 | 同上 |
| Claude Sonnet 5.5 | 2.00 | 10.00 | 0.10 | 同上 |
| Claude Haiku 5.5 | 0.10 | 0.50 | 0.01 | 同上，单次输入（含缓存）≤100K |
| Gemini 3.8 Flash | 0.75 | 3.75 | 0.075 | [Google 定价](https://ai.google.dev/gemini-api/docs/pricing?authuser=6)，标准优惠价截至 12-31 |
| Gemini 4 Argon | 2.00 | 10.00 | 0.10 | [Argon 定价](https://ai.google.dev/gemini-api/docs/latest-model#pricing)，标准优惠价截至 11-30 |
| Grok 4.6 / 4.7 | 2.00 | 6.00 | 0.50 | [xAI 定价](https://docs.x.ai/developers/pricing)，全球价，单次输入严格低于 200K |
| GLM-5.3 | 1.40 | 4.40 | 0.26 | [Z.ai 定价](https://docs.z.ai/guides/overview/pricing) |
| GLM-5.3 Flash | 0.15 | 0.50 | 0.03 | 同上 |
| DeepSeek Flash API | 0.15 | 0.60 | 0.003 | [DeepSeek 定价](https://api-docs.deepseek.com/quick_start/pricing/)，谷时价，见下文 |
| MiMo V2.6 Pro | 0.435 | 0.87 | 0.0036 | [小米定价](https://platform.xiaomimimo.com/docs/en-US/price/pay-as-you-go)，海外实时 API |
| MiMo V2.6 Flash | 0.14 | 0.28 | 0.0028 | 同上 |
| Hunyuan 3 | 0.132 | 0.528 | 0.033 | [腾讯定价](https://www.tencentcloud.com/document/product/1300/78937)，新加坡 |
| Hunyuan 4 Preview | 0.834 | 2.501 | 0.042 | 同上 |
| Qwen3.8 Max 0902 | 2.00 | 6.00 | 待核实 | [阿里定价](https://www.alibabacloud.com/help/en/model-studio/model-pricing)，新加坡国际价；缓存率需控制台 |
| Qwen3.8 27B | 0.50 | 3.00 | 依缓存类型 | 同上；无法从聚合 usage 判断缓存类型 |
| Muse Spark 1.3 | 1.25 | 4.25 | 0.15 | [Meta 定价](https://dev.meta.ai/docs/pricing-rate-limits)，Standard，非 Contributor |
| Kimi K3 | 3.00 | 15.00 | 0.30 | [Kimi 官方首页](https://platform.kimi.ai/)的 K3 报价卡；缓存写入 3.00 |
| MiniMax M3 | 0.30 | 1.20 | 0.06 | [MiniMax 定价](https://platform.minimax.io/subscribe/token-plan?tab=api-enterprise)，Standard，≤512K，永久降价后公示价格 |

### 缓存、阶梯与峰谷

- OpenAI [官方价格页](https://platform.openai.com/pricing)区分 30 分钟和 12 小时写入；快照中的写入单价是基础输入价的 1.25 倍，对应 30 分钟。本批 OpenAI 记录无缓存写入；将来出现写入时必须核实 TTL，不能套默认值。
- Anthropic 5 分钟写入为基础输入价的 1.25 倍，1 小时为 2 倍。Haiku 六档的原始消息均明确记录 `cacheWrite1h=0`，该结论绑定对应 `session_sha256`；其他模型当前无写入用量。阶梯价格以单次输入决定，聚合用量超过首档上限时不猜。
- DeepSeek 峰时为周一至周五 UTC 01:00–04:00、06:00–10:00，中国法定节假日除外；峰时价格为谷时两倍。当前八份 Flash 记录的整段运行区间都在这些窗口外。代码检查完整区间和 UTC 时区，而不只看开始小时；遇到可能跨峰或需假日判定时留空，不猜峰价或谷价。
- DeepSeek 当前 `deepseek-flash` 对应 1017；图库中未固定版本的 V4.1 Flash 与 1017 使用同一公开 API 报价。明确记录为 **V4 Flash 0731** 的旧样本不沿用这个映射：官方说旧 `deepseek-v4-flash` ID 已改路由，不能据此把旧版本当成 1017。这是目标 SKU 估价，不鉴定中转后端身份。
- [阿里 Context Cache](https://www.alibabacloud.com/help/en/model-studio/context-cache)区分显式/隐式缓存。27B 的一般命中价分别为输入价的 10%/20%；Max 0902 的隐式命中价明确要求查控制台，不能套通用 20%。已记录缓存命中却缺确切类型或报价时，不计算金额；27B 的三份零命中记录可计算。
- Google 输出价含思考。3.8 Flash 从 2027-01-01 起输入/输出/缓存读取为 1.50/7.50/0.15；Argon 从 2026-12-01 起为 4.00/20.00/0.20。存储费不包含在本工具的 token 估算中。

公式：`(input × 输入价 + output × 输出价 + cacheRead × 读取价 + cacheWrite × 已核实 TTL 的写入价) / 1,000,000`。输入、读取、写入不重复累计；reasoning 是 output 子集，不再加一次。

## 覆盖与缺口

31 个展示模型、118 条记录全部核对；30 个官方 SKU 条目包含三个明确不可报价的旧版本。**105 条可估算，13 条显示「暂无法估算」**：

| 缺口 | 条数 | 处理 |
|---|---:|---|
| MiMo V2.5 / V2.5 Pro 已于 10-21 退役 | 4 | 官方现行表没有旧版报价，不改用 V2.6 或 Pi 费用 |
| DeepSeek V4 Flash 0731 退役、旧 ID 改路由 | 1 | 不用新版本代价 |
| Qwen3.8 Max 0902 缓存价格未核实 | 5 | 保留已知输入/输出单价，金额留空 |
| Qwen3.8 27B off 缓存类型未记录 | 1 | 其余三档零缓存命中可估算 |
| 旧 Opus / Sonnet max 失败档案只有输出事实 | 2 | 不把缺失输入当作零，不由输出上限推算总费 |

两个 Haiku 截断档有完整用量，在失败详情使用同一估价引擎，但仍无成功指标或作品。三款新模型当前 13 条记录的未按展示精度舍入合计仍为 `$1.218548669`；这不是本次模型调用账单。

## 更新与验证

- 价格按模型集中保存，不再复制到每个档位。`runs` 仅保留必要的、源哈希绑定的 TTL/失败用量审核。换会话后重新核实，源变更不能继续套用审核结论。
- `python3 scripts/gallery.py prices` 只离线报告覆盖率，不联网刷新、不覆盖快照。更新时必须复核全部官方来源，再统一更改 `as_of`；CI 构建不访问价格网站。
- 展示层不读取 `metrics.cost_usd` 作为金额或排序备用值。保留它仅为原始证据。无法计算时不用第三方估价补位。
- 价格测试覆盖官方来源限制、精确 ID、旧 schema 拒绝、无 Pi 回退、TTL、缺失/非法用量、思考不重复收费、阶梯和跨峰边界。图库和浏览器检查覆盖失败不伪造作品、统一标签、默认折叠的计价详情、排序、双语和明暗占位。
- 核验命令：`python3 tests/test_pricing.py`、`python3 tests/test_gallery.py`、`node tests/browser-smoke.mjs http://localhost:8765`。

更新触发：模型/价格/优惠期变化、替换会话、出现新的缓存 TTL/类型、跨计价阶梯或峰谷窗口。缺证据时留空，不为了提高覆盖率猜价。此次不重跑测试模型、不上传会话、不推送或发布。
