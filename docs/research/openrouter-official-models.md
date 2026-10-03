# 原厂 API 服务状态与思考控制核验

核验日期：**2026-10-01**；调查窗口约 14:57–15:07 UTC。只读查阅官方网页、原厂仓库和已有快照；未向候选模型发补测推理请求，未启动子 agent。本文不核验 OpenRouter（OR）的参数转换或具体请求是否成功。

## 结论与证据边界

- **15 款有原厂公开 API 文档/在售目录证据**；这证明原厂公开提供服务，不保证某个地区、账户或某个 OR 原厂端点此刻可调用。
- **DeepSeek V4 Flash 0731 原厂已退役**：旧 `deepseek-v4-flash` 名称仍被接受，但已改由 V4.1 Flash 服务，不是旧权重仍在线。OR 的第三方旧快照不改变这个结论。
- **MiMo V2.5 / V2.5 Pro 截至核验日仍在售**，将在 **2026-10-21 10:00 北京时间**下线；公告明确无自动替换，到期旧 ID 报错。
- **Step 5 Preview 的官方平台展示已核实**，但精确调用 ID、该型号当前商用 API 可用性和思考控制未证实。
- **Muse Spark 1.3 Contributor 的 MAX 存在明确证据冲突**：Meta 官方文档限定 `max` 仅 Standard 1.3，OR 目录却列 Contributor 支持 `max`。未发推理请求，不能声称 OR 的 MAX 可执行，也不能声称观察到了运行时拒绝。

“effort 集”以下只列模型的实际/原生等级；兼容接受值与映射另列。`off` 是关闭行为，不是 Pi 枚举：分别注明原厂的 `none`、`disabled` 或布尔开关。**独立思考预算**与**思考+答案总输出上限**不是同一种控制。没有找到预算参数时写“未证实”，不据此断言不存在。

## 总表

| 请求型号 | 原厂服务结论（文档级） | 原厂准确 model ID | 实际 effort 集；默认 | 原厂关闭思考 | 独立思考预算 |
| --- | --- | --- | --- | --- | --- |
| DeepSeek V4 Flash 0731 | 已退役；OR 旧快照是另一回事 | 历史 `deepseek-v4-flash`；现已转向 V4.1 | 历史 2026-08-13 公告：`low/high/max`；历史默认未在该公告证实 | 历史 V4 有非思考模式；旧快照现已无原厂服务，不应套用现行 V4.1 参数 | 旧快照未证实 |
| DeepSeek V4.1 Flash | 原厂在售 | **`deepseek-flash`** | `low/high/max`；`high` | `thinking.type: disabled`；或 `reasoning_effort: none` | 未证实；`max_tokens` 是总生成上限 |
| GLM-5.3 Flash | 原厂公开模型 API | `glm-5.3-flash` | `low/high/max`；`max`（文本参数沿用 GLM-5.3） | **不支持**；`thinking.type` 只能 `enabled` | 未证实 |
| GLM-5.3 | 原厂公开模型 API | `glm-5.3` | `low/high/max`；`max` | **不支持** | 未证实 |
| HY3 | 腾讯原厂 API 文档列入支持 | `hy3` | `low/high`；`high` | `reasoning_effort: none`；或 `thinking.type: disabled` | 未证实 |
| HY4 Preview | 腾讯原厂 API 文档列入支持；当前 OR 原厂端点异常不能等同退役 | `hy4-preview` | `high`；`high` | 托管 API：`none` 或 `thinking.type: disabled` | 未证实 |
| MiMo V2.5 | 在售，10 月 21 日下线 | `mimo-v2.5` | **未证实原生离散 effort** | `thinking.type: disabled`；默认 `enabled` | 未证实；`max_completion_tokens` 是总上限 |
| MiMo V2.5 Pro | 在售，10 月 21 日下线 | `mimo-v2.5-pro` | 同上 | 同上 | 同上 |
| MiMo V2.6 Flash | 在售 | `mimo-v2.6-flash` | 同上 | 同上 | 同上 |
| MiMo V2.6 Pro | 在售 | `mimo-v2.6-pro` | 同上 | 同上 | 同上 |
| Muse Spark 1.3 Contributor | Meta 原厂在售 Contributor 层 | `muse-spark-1.3-contributor` | `minimal/low/medium/high/xhigh`；省略时模型决定 | **不支持**；`none` 文档称 HTTP 400 | 未证实；总输出上限计入思考 |
| Muse Spark 1.3（非 Contributor） | Meta 原厂在售 Standard 层 | `muse-spark-1.3` | `minimal/low/medium/high/xhigh/max`；省略时模型决定 | **不支持**；同上 | 同上 |
| Qwen3.8 Max | 阿里云原厂在售 | `qwen3.8-max`；另有 `qwen3.8-max-0902` | `low/medium/xhigh`；`xhigh` | `enable_thinking: false`；`none` 映射到关闭 | Chat：有 `thinking_budget`；Responses：不支持此参数 |
| Qwen3.8 27B | 阿里云原厂在售，不只是开放权重 | `qwen3.8-27b` | `low/medium/xhigh`；`xhigh` | 同上 | 同上 |
| Kimi K3 | Moonshot/Kimi 原厂 API | `kimi-k3` | `low/high/max`；`max` | **不支持**；始终思考 | 未证实 |
| MiniMax M3 | MiniMax 原厂 API 支持列表在列 | **`MiniMax-M3`**（大小写按官方） | **没有已证实的有效离散 effort**；文档明确 effort 仅对 M3.1 Flash Preview 生效 | `thinking.type: disabled`；默认开启，开启值为 `adaptive` | 未证实；生成长度上限计入思考 |
| Step 5 Preview | 官方展示型号；该型号商用 API 明细待证 | **未证实**；不要把猜测的 `step-5-preview` 当已确认 ID | 未证实 | 未证实 | 未证实 |

## 1. DeepSeek：0731 退役与 V4.1 别名

Primary sources（2026-10-01 读取）：

- [Change Log](https://api-docs.deepseek.com/updates/)：**2026-07-31** 写明调用 `deepseek-v4-flash`，并说明 “DeepSeek-V4-Flash-0731 keeps the same model architecture and size as DeepSeek-V4-Flash-Preview, and was only re-post-trained.” 因此 `0731` 是版本标识，不是本次证实的独立原厂 API ID。
- 同页 **2026-08-13**：“The thinking modes of V4-Pro and V4-Flash now support three thinking effort levels: low / high / max.” 这是旧 V4 Flash 的历史能力证据，不是旧快照现仍在售的证据。
- 同页 **2026-09-10**：“The previous-generation models V4 Flash and V4 Flash Vision Exp have been retired”; 原厂最新版本调用名是 `deepseek-flash`，旧名称 “are temporarily routed to V4.1 Flash”。
- [Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing)：当前表 `MODEL deepseek-flash` / `MODEL VERSION DeepSeek-V4.1-Flash`，列出输入输出单价、扣款规则及思考/非思考模式。脚注明确旧名对应模型已经退役。不能因为旧名请求成功就认定 0731 存活。
- [Chat Completions API](https://api-docs.deepseek.com/api/create-chat-completion)：`reasoning_effort` 真实控制为 `none/low/high/max`，`none` 关闭、其余开启，默认 `high`；`thinking.type` 为 `enabled/disabled`，默认开启。
- [Thinking Mode](https://api-docs.deepseek.com/guides/thinking_mode)：兼容映射 `minimal→low`、`medium/xhigh→high`、`ultra→max`。这些**不是新增原生强度**。Responses 使用 `reasoning.effort`，Anthropic effort 使用 `output_config.effort`；不要跨协议原样搬字段。
- [Lists Models](https://api-docs.deepseek.com/api/list-models/) 的 schema：“supported_levels … values accepted by the reasoning_effort parameter; none, which turns thinking mode off, is not included.” 本次只读到接口文档，**没有取得鉴权后的原厂 `/models` 实际响应**。

预算：当前 Chat 文档 `max_tokens` 是生成总上限，1–393216；默认非思考 8K、思考 64K、`max` effort 时 128K。这不等于可以单独限制 CoT 的预算参数。旧 0731 的关闭参数和独立预算不以现行 V4.1 文档倒推。

## 2. 智谱：GLM-5.3 / GLM-5.3 Flash

Primary sources（2026-10-01 读取）：

- [GLM-5.3 原厂文档](https://docs.bigmodel.cn/cn/guide/models/text/glm-5.3)：关键原文：“GLM-5.3 会始终启用思考功能，支持三个思考强度级别：low、high 和 max，并不再支持禁用思考功能。” 参数表 `thinking.type=enabled`；`reasoning_effort=low/high/max`、默认 `max`。
- 同页“模型 API”列 OpenAI Chat `https://open.bigmodel.cn/api/paas/v4`、Responses `https://open.bigmodel.cn/api/v1`、Anthropic `https://open.bigmodel.cn/api/anthropic`。这是公开原厂 API 证据，不依赖 OR。
- [GLM-5.3-Flash/FlashX 原厂文档](https://docs.bigmodel.cn/cn/guide/models/vlm/glm-5.3-flash)：明确 “Model Code：glm-5.3-flash/glm-5.3-flashx”；“文本参数与 GLM-5.3 保持一致”；推荐 `reasoning_effort: max`；“thinking.type 仅支持 enabled，不支持关闭思考”。同页有 API 调用入口及定价比较。

因此两款的实际 effort 集均是 `low/high/max`，不能套上 generic 的 `medium/xhigh` 等等级。独立思考 token 预算未找到型号级证据；128K 最大输出不应被写成独立思考预算。本次确认的是 BigModel 原厂国内平台，**没有逐地区核实 Z.ai 海外账户目录及别名**。

## 3. 腾讯：HY3 / HY4 Preview

Primary sources（2026-10-01 读取）：

- [腾讯云 Deep Reasoning 官方文档](https://intl.cloud.tencent.com/document/product/1300/80637)，页面标注 **Last updated: 2026-09-18 21:58:08**。支持模型表分别列 `hy3`、`hy4-preview`，thinking 默认 `enabled`；通用开关 `thinking.type=enabled/disabled`。
- 同页型号级 effort 表：HY3 “Default high, supports low, high, and none”；HY4 “Default high, supports none, high”。**HY4 没有文档级 `low`**。`none` 是关闭，不是额外原生推理深度。
- [TokenHub 混元调用指南](https://cloud.tencent.com/document/product/1823/132252)：搜索索引可读到 HY4 的 `hy4-preview` 调用示例、默认 `high` 与 `none/high` 支持，以及 HY3 工具调用场景 `low` 自动映射 `high`。该中文网页全文抓取超过工具 5MB 限制，故主要参数结论采用上方已完整读取的国际站原厂文档；工具场景映射保留此抓取限制，不作为已实际执行验证。
- [腾讯原厂 Hy4-preview 模型卡](https://huggingface.co/tencent/Hy4-preview/raw/main/README.md)：自托管示例使用 `model="hy4-preview"`，默认 `high`；直接回答传 `chat_template_kwargs.reasoning_effort="no_think"`。**`no_think` 是该自托管模板用法，不能取代腾讯托管 API 文档中的 `none`。** 开源权重本身也不能证明托管端点在线。

商用服务判断：原厂文档当前明确提供两个型号的托管调用方式；没有找到下架公告。独立预算未证实。账户/区域权限、实时原厂直连可用性、HY4 在 OR 的异常原因没有鉴权实测。

## 4. 小米：MiMo 四款在售与定时下线

Primary sources（2026-10-01 读取）：

- [原厂 API Pricing](https://mimo.mi.com/docs/en-US/price/pay-as-you-go)：实时 API 价格表明确列 `mimo-v2.6-pro`、`mimo-v2.5-pro`、`mimo-v2.6-flash`、`mimo-v2.5`；国内/海外均有输入和输出单价。原文：“Pay-as-you-go … consumes the account balance based on the actual Token usage”。V2.5 两款标为 **to be deprecated**，不是已经下线。
- [模型下线公告](https://mimo.mi.com/docs/zh-CN/updates/deprecate)：V2.5 两款均于 **北京时间 2026.10.21 10:00**下线，“**无系统替换模型，到期直接下线**”。公告定义下线为“旧版本模型名称失效……请求将会收到报错”。
- [Deep Thinking](https://mimo.mi.com/docs/en-US/quick-start/usage-guide/other/deep-thinking)：Supported Models 明确包含上述四款；`thinking.type` 为 `enabled/disabled`，四款均默认 `enabled`；OpenAI 兼容 base URL `https://api.xiaomimimo.com/v1`。
- 同页：“max_completion_tokens limits the total length of thinking content and the final answer.” 这是总长度控制。页面没有给这四款的离散 `reasoning_effort` 枚举或独立 CoT token 预算，**不能依据 OR `reasoning` 能力推导原厂 high/max**。

## 5. Meta：Standard / Contributor 与 MAX 冲突

Primary sources（2026-10-01 读取）：

- [Models](https://dev.meta.ai/docs/models)：在 “Available Muse Spark models” 表分别列 **`muse-spark-1.3` = Standard**、**`muse-spark-1.3-contributor` = Contributor**；两者均托管在 Meta Model API。原厂模型列表可通过 `https://api.meta.ai/v1` 的 `client.models.list()` 查询；本次未鉴权查询。
- [Pricing and rate limits](https://dev.meta.ai/docs/pricing-rate-limits)：两款分属实际计费层，Standard 输入/输出每百万 token $1.25/$4.25；Contributor $0.10/$0.20。Contributor 的低价交换条件是允许使用 prompts/completions 训练，不能把它当同等数据条款的 Standard。
- [Reasoning](https://dev.meta.ai/docs/reasoning?project_id=1082575054202150&team_id=2306091636825706)：本次完整读取的型号限制原文：“\"max\" … Standard-tier muse-spark-1.3 only; not available on Contributor-tier models.” 又重申：“This level is not available on Contributor-tier models.” `minimal/low/medium/high/xhigh` 是其余正向等级。
- 同页：`none` “Not supported by Muse Spark: returns HTTP 400”；省略 effort 时 “the model still reasons at a model-determined level”。Chat 用顶层 `reasoning_effort`，Responses 用 `reasoning.effort`。
- 同页：`max_tokens` / `max_output_tokens` 限制 **reasoning tokens plus visible output tokens combined**。原始 CoT 对外不公开；`reasoning.summary` 的 `auto/concise/detailed` 是摘要档位，不是 effort。

抓取说明：不带查询参数的 `/docs/reasoning` 一次只提取到末尾 672 字符；上方带查询参数的官方同路径返回了完整 9078 字符正文。`models` 页面本身也明确 `max` 是 Standard-only，因此结论不依赖仅一处表格或搜索生成摘要。

**冲突处理**：主会话报告 OR catalog 为 Contributor 列 `minimal/low/medium/high/xhigh/max`，而原厂正式文档禁止该层 `max`。记录为 **catalog–原厂文档冲突；运行时行为未知**。不推测 OR 会拒绝、静默降级、切换层级或实际支持 MAX，也不把其目录当原厂新政策。要解决运行时问题，需要主会话另行获得原厂澄清或经授权的请求证据；本调查不发生成请求。

## 6. 阿里/Qwen：原生等级、兼容映射、预算分别记录

Primary sources（2026-10-01 读取）：

- [qwen3.8-max 型号页](https://help.aliyun.com/en/model-studio/qwen3-8-max)：明确 ID `qwen3.8-max`；另有快照 `qwen3.8-max-0902`（alias `qwen3.8-max-2026-09-02`）；列多地区 API 单价，不只发布或开源公告。别名当前具体落在哪个 checkpoint 未鉴权核实。
- [qwen3.8-27b 型号页](https://help.aliyun.com/en/model-studio/qwen3-8-27b)：原文 “The inference service provider for qwen3.8-27b is Alibaba Cloud Model Studio”，有国内/海外 API 价格，证明原厂也提供托管服务。
- [Deep thinking](https://help.aliyun.com/en/model-studio/deep-thinking)：两款均在 Qwen3.8 hybrid thinking 支持列表，默认开启；`enable_thinking=true/false` 控制开关。
- [Chat 参数参考](https://help.aliyun.com/en/model-studio/qwen-api-via-openai-chat-completions)：**明确点名这两款**实际值 `low/medium/xhigh`，默认 `xhigh`。兼容映射 `minimal→low`、`high/max→xhigh`、`none→enable_thinking=False`。所以不是七档原生等级，更不能把 `max` 宣传成比 `xhigh` 更强。
- 同页：两款支持 `thinking_budget`，但 **不能与 `reasoning_effort` 同时设置，否则报错**。只给 effort 时映射到预算：`low→4096`、`medium→16384`、`xhigh→262144`；只给预算时 `0–4096→low`、`4097–16384→medium`、`16385–262144→xhigh`；两者都不设，文档为默认预算 `131072` 与默认 effort `xhigh`。**预算 0 仍映射 low，不能当 off。**
- [Responses 参数参考](https://help.aliyun.com/en/model-studio/qwen-api-via-openai-responses)：型号级表对两款列支持 `none/low/medium/xhigh`、默认 `xhigh`；其余仍是兼容映射。**generic 七枚举不是每型号原生支持集**。
- [Responses 用法](https://help.aliyun.com/en/model-studio/compatibility-with-openai-responses-api)：`reasoning.effort` 优先于 `enable_thinking`；明确不支持 `thinking_budget` 来限制思考长度。Chat 的预算参数不能直接照搬 Responses。

阿里文档也描述由阿里供应的 DeepSeek/Kimi/GLM，**那些不是相应模型原厂参数证据**。例如该页 Kimi K3 的可关闭行为不能覆盖 Moonshot 原厂“始终思考”的文档。

## 7. Moonshot/Kimi：K3 始终思考

Primary sources（2026-10-01 读取）：

- [MoonshotAI/Kimi-K3 原厂 README](https://raw.githubusercontent.com/MoonshotAI/Kimi-K3/main/README.md)：Deployment 原文 “You can access Kimi K3's API on https://platform.kimi.ai by selecting kimi-k3”，提供 OpenAI/Anthropic 兼容 API；不是仅第三方或仅下载权重。
- 同页 Model Usage：“Kimi K3 always has thinking enabled”；顶层 `reasoning_effort` 支持 `low/high/max`、默认 `max`。
- [Reasoning Effort 原厂 API 文档](https://platform.kimi.ai/docs/guide/use-thinking-effort)：再度明确 K3 “always reasons”；迁移提示：“remove the K2.x thinking configuration and use top-level reasoning_effort as needed”。因此不能为 K3沿用 K2.x 的关闭开关。

未证实独立思考预算；本次未查询账号级价格/权限，也未发请求验证错误码。关闭不支持的结论是型号文档证据，不是运行时实测。

## 8. MiniMax：M3 的开关，不是 M3.1 的 effort

Primary source（2026-10-01 读取）：[OpenAI SDK - MiniMax API Docs](https://platform.minimax.io/docs/api-reference/text-openai-api)。

- Supported Models 表包含 **`MiniMax-M3`**，1M context；MiniMax 原厂兼容 API 确实提供此型号。不要把 OR 的 `minimax/minimax-m3` 原样当原厂 ID。
- “Thinking Control” 型号表：M3 未给 thinking 默认开启；`{"type":"adaptive"}` 开启；`{"type":"disabled"}` 为 “Skips thinking and answers directly”。
- `reasoning_effort` 参数原文：“Thinking depth, effective for MiniMax-M3.1-Flash-Preview only.” `low/medium/high/xhigh/max`、默认 `max`、`none` 禁止全部属于 **M3.1-Flash-Preview**，不是用户所问的 **M3**。
- `reasoning_split` 仅决定思考内容放进 `reasoning_content` 还是 `<think>`，是输出格式控制，不是思考开关。
- `max_tokens` / 新集成推荐的 `max_completion_tokens` 为生成长度上限；文档明确思考 token 也计入。未证实 M3 的独立 CoT 预算或有效离散 effort。不能因为 generic schema 出现 effort 就为 M3配置五档。

## 9. StepFun：Step 5 Preview 的有限证据

Primary source（2026-10-01 读取）：[阶跃星辰开放平台首页](https://platform.stepfun.com/)。

- 实际正文出现 “Step 5 Preview” / “面向真实任务的新一代前沿模型”，并提供统一 API 示例，base URL `https://api.stepfun.com/v1`。
- 但示例用 **`model="YOUR_MODEL_ID"`**，没有给这个型号的准确 ID。本次候选文档路径 `/docs/llm/step-5-preview` 与 `/docs/overview` 返回 Page Not Found；官方域名定向检索没有找到型号级参数页。
- 因此只证实“原厂平台展示该型号”，**不足以证实该型号现已公开商用 API、精确 ID、effort、off 或预算**。搜索摘要曾生成 `step-5-preview` 代码，不采用无对应页面原文的代码作为证据。

## OR 对照线索（主会话负责；不代替原厂证据）

本地目录快照：`/tmp/anteater-openrouter-models-20261001.json`。本调查读取后确认其包含除 Step 5 Preview 外的 16 个目标型号；这只是线索，不证明原厂服务状态。

主会话提供的实时端点结果，来源为 `/tmp/anteater-openrouter-endpoints-20261001.json`（本调查未独立复核其端点解析）：

- V4 Flash 0731 仅第三方端点，没有 DeepSeek 原厂端点；与原厂退役公告一致。
- HY4 Preview 腾讯原厂端点 `status=-2`，DeepInfra/SiliconFlow 在线；**不推断整个腾讯原厂 HY4 服务退役**。原厂目前仍有托管服务文档。
- 其余 14 款有原厂 `status=0`。这是 OR 接入状态观察，不等于此次直接调用原厂验证。
- MiMo 四款 / MiniMax M3 的 reasoning 对象仅 `mandatory=false`，无 `supported_efforts`；不据此臆造 effort。
- Muse Contributor catalog 包含 `max`；与 Meta 文档冲突的处理见上节。

## 尚缺证据与停止边界

1. Step 5 Preview：精确 model ID、型号级商用 API 计费/可用列表、effort、关闭和预算全部待证。
2. HY4：原厂直连当前账户/区域可用性及 OR 腾讯端点 `status=-2` 的原因待证；没有退役公告证据。
3. Muse Contributor：OR `max` 的实际转发/执行/拒绝/降级行为未测试；文档侧已明确 Standard-only，不能写成已执行 MAX。
4. MiMo 四款、MiniMax M3：尚无原生离散 effort 的肯定证据；MiniMax 文档还明确当前 effort 仅 M3.1 生效。独立预算未证实。
5. DeepSeek、GLM、HY、Kimi、Meta 的独立思考 token 预算未证实；总输出 token 限制不能充当其证据。退役 0731 的历史完整参数行为未恢复。
6. 本次没有原厂鉴权 `/models` 响应、没有推理请求或错误码实测；所有“在售/支持/不支持”均限定为上述原厂公开文档证据。GLM 海外区域目录、各平台账号权限、别名实时 checkpoint 未逐项验证。

为遵守时间与只读限制，以上缺口不继续无限检索。本文不修改其他 repo 文件、不提交 git；后续 OR 能力合并和运行时判断由主会话完成。

## OpenRouter 实时能力与补测矩阵（主会话复核）

核验：2026-10-01。候选模型未发推理测试。原厂在售与 OR 原厂端点当时正常是两种状态，不能互相替代。

来源：[实时模型目录](https://openrouter.ai/api/v1/models)、[逐模型端点 API](https://openrouter.ai/docs/api/api-reference/endpoints/list-endpoints)、[reasoning 对象语义](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens)。采样原件暂存 `/tmp/anteater-openrouter-models-20261001.json`、`/tmp/anteater-openrouter-endpoints-20261001.json`，归一化清单 `/tmp/anteater-openrouter-coverage-20261001.json`。

口径：下表“模型缺口”可复用其他渠道的同名档位；**固定 OR 原厂通道覆盖不能这样折抵**。旧 Go 记录不属于 OR；旧 MiMo OR 记录没有已证明的原厂路由锁定。完整固定原厂通道矩阵因此是全部“候选选项”，而不是“模型缺口”。MiMo 旧 high 只有开启思考的证据，不是真正的独立 high 强度。

`supported_efforts` 缺失表示没有 effort 选择，不是通用七档。`mandatory=true` 的 OR 型号不列 off。原厂与 OR 元数据冲突的两个选项单独待确认，不假定请求会成功、拒绝或降级。

| 型号 | OR model ID | 原厂 provider slug | 候选选项 | 已有模型记录 | 模型缺口 |
|---|---|---|---|---|---|
| DeepSeek V4.1 Flash | `deepseek/deepseek-v4.1-flash` | `deepseek` | off, low, high, max | low, high, max（Go） | off |
| GLM-5.3 Flash | `z-ai/glm-5.3-flash` | `z-ai` | low, high, max | max（Go） | low, high |
| HY3 | `tencent/hy3` | `tencent` | off, low, high | high（Go） | off, low |
| MiMo V2.5 | `xiaomi/mimo-v2.5` | `xiaomi` | off, on | on（OR，上游未核实） | off |
| MiMo V2.5 Pro | `xiaomi/mimo-v2.5-pro` | `xiaomi` | off, on | on（OR，上游未核实） | off |
| MiMo V2.6 Flash | `xiaomi/mimo-v2.6-flash` | `xiaomi` | off, on | on（OR，上游未核实） | off |
| MiMo V2.6 Pro | `xiaomi/mimo-v2.6-pro` | `xiaomi` | off, on | on（OR，上游未核实） | off |
| Muse Spark 1.3 Contributor | `meta/muse-spark-1.3-contributor` | `meta` | minimal, low, medium, high, xhigh | xhigh（Go） | minimal, low, medium, high |
| Muse Spark 1.3 | `meta/muse-spark-1.3` | `meta` | minimal, low, medium, high, xhigh, max | 无 | minimal, low, medium, high, xhigh, max |
| Qwen3.8 Max 0902 | `qwen/qwen3.8-max-0902` | `alibaba` | minimal, low, medium, high, xhigh | 无 | minimal, low, medium, high, xhigh |
| GLM-5.3 | `z-ai/glm-5.3` | `z-ai` | low, high, max | 无 | low, high, max |
| Kimi K3 | `moonshotai/kimi-k3` | `moonshotai` | low, high, max | 无 | low, high, max |
| Qwen3.8 27B | `qwen/qwen3.8-27b` | `alibaba` | off, low, medium, xhigh | 无 | off, low, medium, xhigh |
| MiniMax M3 | `minimax/minimax-m3` | `minimax` | off, on | 无 | off, on |

核验时 14 款的原厂端点采样均为 status=0（仅静态端点证据，并非账户调用成功证明）。其模型覆盖尚缺 **36** 条；若做固定 OR 原厂通道的新完整矩阵，则为 **46** 条。

### 条件项、排除项与参数冲突

- **HY4 Preview**：原厂当前仍有托管 API 文档；OR 原厂 Tencent 端点两次采样分别 status=-2 / -5，原因未证实，不宣称整体服务退役。第三方 DeepInfra/SiliconFlow 为 status=0。腾讯原厂确认只有 off/high，已有 Go high，模型层面还缺 off，先等原厂通道恢复或另做第三方组。OR catalog 的 low 未获腾讯原厂型号文档支持，不能作为原厂第三个已确认档位。
- **DeepSeek V4 Flash 0731**：原厂明确退役，OR 仍有第三方旧快照；不纳入“原厂仍提供该版本服务”的补测名单。旧别名现在路由 V4.1，不能以旧名请求成功证明 0731 仍在售。
- **Step 5 Preview**：OR 当前公开目录无此型号，`GET /api/v1/models/stepfun/step-5-preview/endpoints` 也返回 404；该 ID 只是候选探测字符串，不是已确认 OR ID。暂不纳入本轮。
- **Muse Contributor max**：OR 宣称支持，Meta 限 Standard-only，列为待确认；不计进上述 36/46。
- **Kimi K3 off**：OR mandatory=false，但 Kimi 原厂文档 always reasons。关闭行为冲突，列为待确认；不计进上述 36/46。
- **Qwen3.8 Max 0902**：OR 为 mandatory=true，开放 minimal/low/medium/high/xhigh；原厂只有 low/medium/xhigh 三种真实深度，兼容 minimal→low、high→xhigh。按 OR 支持值覆盖仍可列五档，但不称作五种原生强度；原厂直连可关不表示 OR 该 SKU 也开放 off。
- **Qwen3.8 27B**：OR 开放 off/low/medium/xhigh，不补 high/max。
- **MiMo 四款 / MiniMax M3**：仅开/关；不为 absent supported_efforts 臆造 low 至 max。关闭必须实际通过 reasoning.enabled=false，不能只用 exclude 隐藏思考文本。
- **MiMo V2.5 两款**：当前原厂仍在售，2026-10-21 10:00 北京时间直接下线，应优先处理，不能当作已退役。

若只补模型缺口，14 款当前候选 36 条；再加 HY4 需恢复/另选通道的 off 为 37 条。未计两项元数据冲突（Contributor max、Kimi off）及 HY4 第三方 low。若要求本轮统一固定 OR 原厂并严格干净，须重新跑 46 条当前候选，HY4 另计待恢复两档；旧记录全部保留。

上游锁定使用用户提供的 `--openrouter-provider` 参数，provider slug 取上表；OR 的 base slug 会匹配该供应商子端点。支持能力仍需执行时确认，特别是模型参数可能被忽略：OR [provider routing](https://openrouter.ai/docs/guides/routing/provider-selection) 文档说明默认 require_parameters=false 时，未支持参数可能被忽略，锁上游不等于每个参数一定生效。
