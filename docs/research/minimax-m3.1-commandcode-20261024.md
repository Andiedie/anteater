# MiniMax M3.1 Flash：原厂思考档位与 Command Code Provider API

核查日期：**2026-10-24，Asia/Shanghai（UTC+8）**。用于准备 `minimax/minimax-m3.1-flash` 经 Command Code GOAT Provider API 的测试；执行及入库仍遵守[测试规范](../testing-protocol.md)和 [README](../../README.md)。第 1–3 节为本日直接取得的公开一手文档、公开目录或官方客户端源码；第 4 节补充渠道探测证据。动态网页未提供固定修订日期，不把抓取日期写成发布日期。

## 结论

- **原厂完整 effort 枚举是 `low / medium / high / xhigh / max`，默认 `max`；没有 `off` 或 `none` 档。** Chat Completions 的请求体顶层字段是 `reasoning_effort`。无需额外开关；可显式传 `thinking: {"type":"adaptive"}`，不能关闭思考。
- **Command Code 已核实模型 ID、GOAT API 权限和 `/provider/v1/chat/completions` 路由；未从公开一手资料核实该模型逐档的服务端转发、映射或实际生效。** 原厂五档只能作为待验证集合，不能仅凭 CLI 档位菜单、客户端发送字段或 HTTP 200 宣称渠道五档已验证。
- **本次渠道探测确认五档请求被接受，`off` 被该模型明确拒绝。** 证据见第 4 节；这不补足服务端映射的独立证明。价格快照只补入本模型原厂单价，既有报价和统一日期不变。

## 1. 原厂参数：已核实

权威来源：[MiniMax OpenAI SDK / Request Parameters 与 Thinking Control](https://platform.minimax.io/docs/api-reference/text-openai-api)、[Model Invocation / Thinking](https://platform.minimax.io/docs/guides/text-generation)。官方 [MiniMaxAI 模型卡](https://huggingface.co/MiniMaxAI/MiniMax-M3.1-Flash/blob/main/README.md)的 Inference Settings 也列出相同五档，但模型卡谈的是 chat template，不单独作为托管 API 证据。

| 项目 | 原厂 OpenAI-compatible Chat Completions 行为 |
|---|---|
| 模型 ID | `MiniMax-M3.1-Flash`；不是 Command Code 的带前缀 ID |
| 档位字段 | 顶层 `reasoning_effort`，字符串 `low`, `medium`, `high`, `xhigh`, `max` |
| 默认 | 省略 effort 为 `max`；省略 `thinking` 仍开启思考 |
| 开关 | `thinking: {"type":"adaptive"}` 可显式开启；`thinking: {"type":"disabled"}` 返回 400 |
| `none` / `off` | `reasoning_effort:"none"` 明确返回 400；`off` 不在原厂枚举中，不能当第六档 |
| 输出 | 思考在 `reasoning_content`；`reasoning_split:false` 不支持，不能用它“关闭思考” |
| 输出预算 | 思考计入 `max_tokens`；新集成推荐 `max_completion_tokens`，小预算可导致 `finish_reason:"length"` 且正文为空 |

关键原文：

> “Accepts `low`, `medium`, `high`, `xhigh`, and `max` … Defaults to `max` when omitted. `none` is not supported.”
>
> “`MiniMax-M3.1-Flash` always thinks and returns `400` if `disabled` is sent.”
>
> `model "MiniMax-M3.1-Flash" requires adaptive thinking; thinking.type="disabled" (including reasoning.effort=none) is not allowed (2013)`

这里的错误文案含 `reasoning.effort`，**不改变 Chat Completions 的正确 wire 字段 `reasoning_effort`**；原厂另两种协议分别为 Anthropic `output_config.effort` 和 Responses `reasoning.effort`。不要把这些字段混发到本任务的 Chat Completions 路由。

原厂最小参数片段（非完整请求，未执行）：

```json
{
  "model": "MiniMax-M3.1-Flash",
  "reasoning_effort": "max"
}
```

原厂 [Tool Use & Interleaved Thinking](https://platform.minimax.io/docs/guides/text-m3-function-call)另有两项执行约束：

- “the entire `response_message`, including `reasoning_content`, must be kept in the message history and passed back … in the next request”；保留完整 assistant 消息，包括 `tool_calls`，不能仅保存正文。
- “for simple tool calls, the model may call the tool directly without producing thinking content”；因此某轮没有 `reasoning_content` 不证明思考被关闭，也不证明 effort 被忽略。档位并不是每次必定消耗某个 token 数的固定预算。

## 2. Command Code：权限与路由成立，转发仍有证据缺口

### Provider API，而非 CLI / BYOK

[Provider API](https://commandcode.ai/docs/provider)明确：

> “This page is about calling Command Code's models from your own code. Going the other way, bringing a third-party endpoint into the Command Code CLI is in BYOK Providers.”
>
> “GOAT, Pro, Max, and Team have API access.”

目标为 `POST https://api.commandcode.ai/provider/v1/chat/completions`。[GOAT 文档](https://commandcode.ai/docs/plans/goat)也明确 API usage 计入 GOAT credits，并列出 MiniMax M3.1 Flash。模型页的 “Available on Go and above” 不等于 Go 有外部 API 权限；Provider 文档明确 Go 无 API 权限。

无需认证的公开 [GET `/provider/v1/models`](https://api.commandcode.ai/provider/v1/models)在本次核查返回以下目标字段（省略无关字段）：

```json
{
  "id": "minimax/minimax-m3.1-flash",
  "name": "MiniMax M3.1 Flash",
  "context_length": 1000000,
  "supported_endpoints": ["/chat/completions"]
}
```

这确认**该模型仅公布 Chat Completions 路由**，不能套用其他模型的 `/responses` 或 `/messages`。目标条目没有 `reasoning`、effort 枚举、输出上限或参数映射元数据。

### 为什么菜单和官方 Pi 插件不足以证明转发

- [CLI `/model` 功能公告](https://commandcode.ai/blog/configurable-reasoning-effort-in-model)写 “Set it from low through max. Auto for provider default”，标注 v0.26.5；[Settings](https://commandcode.ai/docs/settings)的 `reasoningEffort` 是按模型 ID 存储的 CLI 设置，枚举五档。
- [BYOK](https://commandcode.ai/docs/byok)的 `reasoningEfforts` 是自定义第三方 endpoint 的客户端能力配置，方向与 Provider API 相反。这些资料均不是 Command Code 服务端对 MiniMax 参数的转发契约。
- 官方 [Pi provider README](https://github.com/CommandCodeAI/pi-commandcode-provider/blob/26e5fe68c2ab4c4d92216cc6114b27eb9401b516/README.md)明确：“Models are assumed to support reasoning, preserving the provider's existing behavior.”
- 对应 [index.ts](https://github.com/CommandCodeAI/pi-commandcode-provider/blob/26e5fe68c2ab4c4d92216cc6114b27eb9401b516/index.ts)（提交 `26e5fe68`，2026-09-21）为 `reasoning: item.reasoning ?? family?.reasoning ?? true`，Chat Completions 注册标准 `openAICompletionsApi()`，并设置 `supportsDeveloperRole:false, maxTokensField:"max_tokens"`。它没有 MiniMax 特定 effort 枚举或服务端实现；`maxTokens` 缺失时的 **32,768 是客户端回退值，不是已核实的渠道输出上限**。

**未验证项：** Provider API 顶层 `reasoning_effort` 是否按原值透传、是否重映射/钳位；`thinking` 是否透传或需要；缺省 effort 的渠道行为；完整通用 API 枚举是否含 `off`；上游选择、回传 reasoning 的转换以及实际后端版本。本次未找到可回答这些问题的公开服务端源码或该模型专属参数文档。“OpenAI-compatible”不等于保证每个扩展参数均生效。

后续证据应区分三层：**客户端出网请求准确**、**渠道接受/拒绝该参数**、**服务端确实传递并应用相应控制**。即使通用 schema 接受 `off`，也不能推出 MiniMax 支持它；即使五档均返回 200，也不能把不同耗时/token 数当作确定的映射证据。原厂禁止关闭思考，故不应为了菜单齐全而新增 `off` 测试档。

### GOAT 并发与限额

核查 [GOAT](https://commandcode.ai/docs/plans/goat)、[Usage Limits](https://commandcode.ai/docs/resources/usage-limits)、[Provider API](https://commandcode.ai/docs/provider)及 [Pricing & Limits](https://commandcode.ai/docs/resources/pricing-limits)，**未找到适用于此模型/GOAT Provider API 的明确最大并发、RPM 或 TPM 数字**。Usage Limits 描述的是 credits 时间窗口，不是并发承诺；Provider 错误表注明 429 为 “Rate-limited by the upstream”。不能把营销文案 “Fast, no limits” 或额外 credits 不受窗口限制理解成无限并发。

## 3. 次要：原厂公开 API 价格

[MiniMax 官方 Pricing Overview](https://platform.minimax.io/docs/pricing/overview#models/text)与[官方发布文](https://www.minimax.io/blog/minimax-m31f)相互印证：

> “Flat pricing per 1M tokens: $0.15 input · $0.60 output · $0.015 cached input.”

单位为 **USD / 1M token**；本次未见 M3.1 Flash 独立缓存写入价或优惠截止日，不填零、不借用 M3 的分档或 Priority 价。原厂 OpenAI 文档明确 M3.1 Flash 不支持 `service_tier`。

Command Code [模型营销页](https://commandcode.ai/models/minimax-m3-1-flash)显示缓存读取 `$0.01`，而 [GOAT](https://commandcode.ai/docs/plans/goat)与[价格总表](https://commandcode.ai/docs/resources/pricing-limits)显示 `$0.015`；不能用前者较短精度覆盖原厂报价。总表还说明开放模型跨多个上游，表中为 mean per-provider price，单次实际价格可能变化。**厂商价格估算不等于 GOAT credits 扣减或渠道实扣**。`content/pricing.json` 在既有 `2026-10-24` 日期下新增本模型的精确 ID/别名及原厂单价；缓存写入保持 `null`，不修改其他模型的报价或源绑定审核。

## 4. 渠道参数探测与测试范围

协调者在同日向上述 Provider API 发送独立合成请求，prompt 为 `Reply with only OK.`，预算 512 token；不使用绘图 prompt，不计入正式测试成绩，也不预热正式会话。

- 无效 `reasoning_effort:"anteater_invalid_probe"` 返回 HTTP 400，`param:"reasoning_effort"`；通用校验枚举为 `off|low|medium|high|xhigh|max`。
- `off` 返回 HTTP 400、`code:"unsupported_value"`，原文：`Model "minimax/minimax-m3.1-flash" does not support reasoning_effort "off". Only models that can turn thinking off accept it.`
- `low / medium / high / xhigh / max` 分别返回 HTTP 200、`finish_reason:"stop"`，并提供 usage；响应包含 `MiniMax-M3.1-Flash` 和渠道规范 ID。这确认 API 对该模型的接受/拒绝行为，仍不证明渠道内部没有映射或钳位。

原始请求与响应保存在 `~/Downloads/anteater-commandcode-minimax-levels-20261024-203404/probes/`，不含 Authorization。正式测试按上述五档逐个新建会话，出网前断言 `reasoning_effort` 和 64,000 输出预算；完整回传思考，关闭重试/预热/压缩，不设总时长截止。测试结果与入库清单见[执行规范](../testing-protocol.md#当前处理决定)。原先未传 effort 的默认配置样本留在旧批次，不改称 `max`，不替代本次显式档位。

## 更新触发

Command Code 发布模型参数 schema/服务端实现、MiniMax 修改 effort/开关规则、官方插件改变能力映射或原厂价格变化时重查。维护时始终区分出网参数、渠道接受性和内部生效证据；不修改原始 SVG 或会话来补足证据。
