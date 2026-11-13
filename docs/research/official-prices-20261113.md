# 2026-11-13 官方价格复核

本轮为 Gemini 4 Hydrogen 测试补入准确型号的 Standard 付费层报价，并将全站统一核验日期从 2026-11-11 推进至 2026-11-13。原有 36 个价格 profile 已全部复核：OpenAI / Anthropic 13 个、既有 Google 3 个、其余九个厂商 20 个；既有费率、活动条件、历史覆盖范围和来源绑定的缓存核验均不变。

## Hydrogen

精确原厂 ID 为 `gemini-4-hydrogen`；匹配的渠道别名仅为 `google/gemini-4-hydrogen` 和 `openrouter/google/gemini-4-hydrogen`。Standard 付费层美元单价如下，单位为每百万 token。[1]

| 用量 | 单价 |
|---|---:|
| 普通输入 | $1.50 |
| 输出，包含思考 | $7.50 |
| 隐式缓存命中输入 | $0.075 |
| 显式缓存写入 | 不适用；型号不支持显式缓存 |

价表未列 Hydrogen 首发优惠期或未来费率，不继承 Carbon、Argon 或 Flash 的活动条件。统一上下文不采用输入长度分档。未公布的独立写入单价保持 `null`，不能当成零；归一化 output 已包含思考，不再加一次 reasoning。[1]

low / medium / high 选定会话的官方估价分别为 **$0.0454545 / $0.10962 / $0.26833395**。这些金额只使用各自选定原生会话的输入、输出和缓存计量，不合并旧 64,000-token 批次或弃用 attempt，也不等同于 OpenRouter 实扣。

补取第三次 `attempt-03` 的 generation 账单并与网关、原生会话及 JSON/HTML hash 绑定后，xhigh 选定会话的完整原生计量已核验：`input=1171`、`output=65536`（已含 `reasoning=54201`）、`cacheRead=0`、`cacheWrite=0`，按上述官方费率估价为 **$0.4932765**。SDK 原始错误会话中的零占位保持不变，不作为免费用量；完整计量保存在 `content/pricing.json` 的 `runs['gemini-4-hydrogen-xhigh']` 独立、固定来源的价格 review 中。三次无人工预算尝试的渠道实扣合计 **$1.4798295**，与选定会话的官方估价分开记录，不混入旧 64,000-token 批次。核验过程及边界见[测试规范第 32 项](../testing-protocol.md)与只读证据 `/Users/andie/.local/share/anteater/runs/hydrogen-native-20261113-194531/retry-audit/exhaustion-admission-audit.json`。

## 复核与保留边界

原有 36 个 profile 的核验清单并集与当前旧快照逐项相等；父级核验了 80 份原文或派生文本的 hash。Hydrogen 专项另保留 9 份原始 HTTP 正文及对应文本，并重新核对其 hash。原有历史费率时段、Qwen 的六份来源绑定条件假设、缓存模式未知和其他缺口保持原状。没有把当前默认缓存规则追溯当成历史请求事实。

完整本地证据在 `~/.local/share/anteater/runs/hydrogen-native-20261113-194531/`：`full-price-review/parent-audit.json`、两组厂商核验报告、`google-existing-price-review.json` 和 `hydrogen-pricing-evidence/`。原始网页、响应元数据和账本留在本地证据目录，不随图库入库。

新测试按用户澄清省略人为输出和思考预算；历史会话及其 64,000 等预算记录原样保留。客户端省略上限不证明渠道无限输出，也不能单独判定某次截断的底层原因。测试执行和结果证据以原生会话、最终请求审计及 [测试规范](../testing-protocol.md) 为准。

## Sources

[1] https://aistudio.google.com/docs/pricing — Google 官方 Standard 报价
