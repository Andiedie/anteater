# Muse Standard 官方价格与本轮计量核验（2026-11-17）

本次使用 Meta Model API 公开 Standard 按量美元报价。[1][13] 官方精确型号为 `muse-ember-1.0`、`muse-wonder-1.0`、`muse-spark-1.3`。[4][5][6] 对应本轮渠道标识分别为 `openrouter/meta/muse-ember`、`openrouter/meta/muse-wonder`、`openrouter/meta/muse-spark-1.3`。本轮不混用 Wonder Full、Contributor 或订阅价格；渠道标识不证明后台日期后缀与厂商固定快照等价。

单位为 USD／百万 token：[1][13]

| 型号及单请求范围 | 普通输入 | 输出（已含思考） | 缓存读取 | 独立缓存写入 |
|---|---:|---:|---:|---|
| Ember，全部输入不超过 200K | 0.10 | 0.50 | 0.004 | 未公布 |
| Ember，全部输入超过 200K | 0.30 | 1.50 | 0.012 | 未公布 |
| Wonder Standard | 4.00 | 20.00 | 0.20 | 未公布 |
| Spark 1.3 Standard | 1.25 | 4.25 | 0.15 | 未公布 |

Ember 阈值包含缓存输入；超过阈值时整笔请求按长上下文价，不只计超过部分。本轮逐笔核对完整 Chat Completions 请求和终止用量，没有使用 `previous_response_id`，全部请求低于首档阈值。估价器继续保守拒绝聚合输入超过 200K 的记录；已核实的高档单价仅作证据，不据聚合值自动选档。[1]

思考按输出同价，且已经包含在报告输出 token 中。计算采用 `(input × 输入价 + output × 输出价 + cacheRead × 读取价) / 1,000,000`，不再加算 reasoning。[3]

本轮 18 个所选原生会话共 57 次请求。逐一将原生 `responseId` 对应到终止 SSE usage 和独立 generation 账单，核对普通输入、输出、缓存读取及思考数量。全部终止 SSE 均明确含 `prompt_tokens_details.cache_write_tokens: 0`；零写入依据是该原始字段，不是 SDK 缺省值。generation 账单的 `native_tokens_cache_write` 为 null，仍按未知保留，不把它当作零。

原厂通用缓存说明包含自动前缀复用和可选保留 hint。[2][11] Messages 文档另有显式 breakpoint 与 5m 支持范围。[9][10] 它们不能证明本轮 OpenRouter／Magpie 的内部转发、实际缓存模式、保留时长或完整上游创建量。公开价表没有给出独立写入费率，故 `cacheWrite` 报价保持 null。[1] 本轮按渠道明确报告的零写入及已公开的非零组件单价估算，不把未知写入报价设为免费，也不虚构 TTL。未找到影响本轮 Standard token 费率的公开限时条件，不新增促销标记。[1]

以下金额从所选原生分支的真实用量独立用 Decimal 计算；包括工具续轮及获准 XML 反馈，不包括旧 Spark 六档历史样本：

| 思考档位 | Ember | Wonder | Spark 1.3 |
|---|---:|---:|---:|
| minimal | $0.002195664 | $0.090796 | $0.0184142 |
| low | $0.0033921 | $0.2169808 | $0.02290185 |
| medium | $0.004583792 | $0.3934968 | $0.03235615 |
| high | $0.00372216 | $0.255772 | $0.0803309 |
| xhigh | $0.005858104 | $0.2544776 | $0.0720049 |
| max | $0.003982228 | $0.4426736 | $0.05818675 |

18 档官方估价合计 **$1.962125598**。57 笔 OpenRouter generation 实扣此次恰好也合计 **$1.962125598**；二者来自独立证据和计算，不能将这种相等推广到其他渠道或测试，图库继续展示原厂估价。

所有原始响应均保存到协议 `[DONE]`，并与元数据字节数及 SHA-256 一致；57 次观察器均在 SDK 收尾时记录 `TypeError: Invalid state: Controller is already closed`，这些原始错误和字节没有改写。原生会话、工具链、自然 settled 与账单完成状态独立核对，不以观察器错误推定上游失败，也不宣称已验证 HTTP EOF 或代理内部行为。本轮保留 11 次工具错误及 Spark high 一轮原样 XML 反馈，均计入原会话指标。

共享价格快照仍为 **2026-11-17**。前批已复核的旧 profile 不因本次局部补入而推进日期；新增 Ember／Wonder，重新核对 Spark Standard 的原有单价并补准确渠道别名。旧 Spark 六档源文件与固定分享来源保存在批次完整备份中，当前图库选择本轮重测。

原始价表、协议说明、逐字引用与来源哈希保存在本地批次 `muse-release-sort-20261117-144053/muse-pricing/`；所选原生来源、账单和父级核验分别位于三个模型目录及 `parent-integration/native-billing-audit.json`。这些私有审计文件不随静态网站发布。完整入库还须以本轮最终浏览器验收及独立审查为准。

## Sources

[1] https://dev.meta.ai/docs/pricing-rate-limits
[2] https://dev.meta.ai/docs/prompt-caching
[3] https://dev.meta.ai/docs/reasoning
[4] https://dev.meta.ai/docs/muse-ember
[5] https://dev.meta.ai/docs/muse-wonder
[6] https://dev.meta.ai/docs/muse-spark
[9] https://dev.meta.ai/docs/api-reference/messages/create-message
[10] https://dev.meta.ai/docs/api-reference/messages/schemas
[11] https://dev.meta.ai/docs/protocols/chat-completions
[13] https://dev.meta.ai/resources/blog/build-with-muse-wonder
