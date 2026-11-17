# 2026-11-17 官方价格复核与两款新模型

本轮核对原有 37 个 profile 的全部官方来源，并独立审核 Hy4 flash、Qwen4 Max 两个新 profile，将统一复核日期推进至 **2026-11-17**。原有费率、活动条件、历史适用区间及来源绑定的用量/缓存核验均保留，原有可计算金额不变。Tencent 价表新增 Hy4 preview 的 **To Be Discontinued** 标记，但未给出精确停用时刻；该生命周期变化不改写原有测试或历史价格。

## 新增报价

沿用项目已审核的海外口径：Tencent 选 Singapore，Alibaba 选 Singapore / International。单位为 USD / 百万 token，不使用 OpenRouter、Magpie 或 SDK 金额替代厂商报价。

| 精确型号与费率 | 普通输入 | 输出（含思考） | 缓存读取 | 缓存写入 |
|---|---:|---:|---:|---:|
| Hy4 flash，公开五折 | 0.035 | 0.1405 | 0.0015 | 未公布 |
| Hy4 flash，已公布刊例 | 0.07 | 0.281 | 0.003 | 未公布 |
| Qwen4 Max，标准按量 | 1.5 | 4.5 | 0.075 | 5 分钟 1.875；1 小时 3 |

Hy4 flash 的原厂活动于 **北京时间 2026-11-30 12:00:00（UTC 04:00:00）** 截止，随后恢复原刊例价。七份所选记录中，Hy4 三档的完整运行区间均位于活动期。三档估价的条件按钮同时展示同一用量按刊例价计算的结果，未把活动结束误写成当天午夜。[1][2]

Qwen 型号价表明确为 Singapore / International、思考与非思考同价、单请求输入不超过 1M token 不分档；输出栏为 “Chain of thought + answer”。其专用缓存表同时公布显式和隐式读取均为 0.075，因此不继承旧 Qwen 的“假定隐式缓存”情景。[3][4]

Qwen4 显式缓存默认 5 分钟、可选 1 小时。自动断点缓存即使参数 mode 为 implicit 仍遵循显式写入计费；无缓存参数的隐式缓存是另一条路径。非零写入仍须核验逐响应的 TTL，不能从省略参数推出代理实际采用的 TTL；写入别名不相加，输出中的思考不再重复计费。[5]

## 所选测试估价

| 记录 | 官方估价 USD | Hy4 未打折同用量 USD |
|---|---:|---:|
| hy4-flash-off | 0.0008309335 | 0.001661867 |
| hy4-flash-low | 0.0007750355 | 0.001550071 |
| hy4-flash-high | 0.001671042 | 0.003342084 |
| qwen4-max-off | 0.0285495 | — |
| qwen4-max-low | 0.0432825 | — |
| qwen4-max-high | 0.041181 | — |
| qwen4-max-xhigh | 0.1428564 | — |

七档估价合计 **$0.2591464110**；独立 generation 账单核对的 OpenRouter 实扣合计 **$0.246352939**，二者口径不同。16 笔请求各自绑定原生 response ID、终止 SSE 和 generation 账单；原生 prompt/completion/cached 与会话用量一致。每一笔最终渠道 usage 均明确包含 `cache_write_tokens=0`，不是因字段缺失生成的 SDK 占位零。以上估价使用渠道明确报告的四项用量，不能据此声称原厂隐藏转发和完整创建量已独立观测。

Hy4 未公布独立写入价，保留 null；本轮写入为零，不影响估价。Qwen 本轮写入同样明确为零，无须选择非零写入 TTL。OpenRouter 报告的日期后缀保留为渠道证据，不提升为厂商承诺的快照 ID。

## 取证与复核

原有 37 个 profile 的本日复核保存 47 份原始 HTTP 正文、102 条本日逐字引文及逐字段结论；父级逐项确认 profile 清单等于旧快照，独立核对 204 个归档文件的 hash，所有引文均存在于所指正文。新两款专项另保存 14 份来源、完整地区表头和缓存说明，父级核对 75 个归档文件的 hash 和 20 条逐字引文。没有将聚合目录报价用作厂商报价。

完整私有证据分别位于：

- `~/.local/share/anteater/runs/hy4flash-qwen4max-20261117-105500/existing-price-review/`：`audit.json`、`retrievals.json`、`evidence-quotes.json`、`artifact-manifest.json`，记录全部旧型号和活动/历史边界。
- `~/.local/share/anteater/runs/hy4flash-qwen4-pricing-20261117T025523Z/`：原厂原始正文、完整地区表、引用账本、`current-run-cache-audit.json` 及独立 Decimal 复算。
- 本轮执行批次：`~/.local/share/anteater/runs/hy4flash-qwen4max-20261117-105500/`，逐档会话、请求、原始响应和账单均分开保存。

退役型号仍采用原有保守历史日期区间；Sol 优惠后费率、MiMo 免费写入结束日与后续价、旧 Qwen 的历史缓存模式/创建量和历史时间冲突继续保留未知。没有因本日复核就改写历史请求事实。本轮仅本地入库和预览，不分享、提交、推送或部署。

## Sources

[1] https://www.tencentcloud.com/document/product/1300/78937 — Singapore 原厂价表、Hy4 flash 五折活动和准确截止时刻

[2] https://www.tencent.com/tencent-launches-hy4-flash-to-power-high-speed-cost-efficient-ai-deployment-for-everyday-workflows/ — Hy4 flash 官方发布稿与刊例交叉核对

[3] https://docs.modelstudio.console.alibabacloud.com/en/model-studio/model-pricing — Singapore / International 精确型号与两种缓存读取及写入报价

[4] https://docs.modelstudio.console.alibabacloud.com/en/model-studio/qwen4-max — 精确型号与思考/非思考模式

[5] https://docs.modelstudio.console.alibabacloud.com/en/model-studio/explicit-cache-qwen4 — Qwen4 专用缓存、TTL、自动断点和计量字段
