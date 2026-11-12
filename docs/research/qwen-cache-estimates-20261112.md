# Qwen 缓存假设条件估价接入（2026-11-12）

指定六条记录现可显示带明确假设的原厂费率估价：主金额假定隐式缓存，替代金额对同一记录用量采用显式缓存费率。六条均保留 `historical_cache_mode: null`；这次接入没有证明历史缓存模式，也没有补出缺失的原始创建用量。统一价格快照 `as_of` 保持 `2026-11-11`。

## 官方报价与边界

本次重新核对已有研究保存的官方原文、SHA-256、准确型号和 Singapore / Scope: International 表格。Max 使用 `Snapshot Versions → qwen3.8-max-0902` 下的报价；27B 使用其准确型号页，单位均为 USD/百万 token。[1][2]

| 精确型号 | 普通输入 | 输出 | 隐式读取 | 显式读取 | 显式创建 |
|---|---:|---:|---:|---:|---:|
| qwen3.8-max-0902 | 2 | 6 | 0.25 | 0.17 | 2.5 |
| qwen3.8-27b | 0.5 | 3 | 0.1 | 0.05 | 0.625 |

Max 原文为 `Input(Implicit Cache) / 0.25 / Per 1M tokens`、`Explicit Cache Read / 0.17 / Per 1M tokens` 和 `Explicit Cache Creation / 2.5 / Per 1M tokens`。[1]
27B 原文对应为 `0.1`、`0.05`、`0.625`，没有用通用折扣比例推导任一值。[2]
官方缓存文档将隐式与显式模式分开，并说明创建量字段是 `cache_creation_input_tokens`；规范中的模式和字段定义不能代替历史请求或账单证据。[3]

两份官方原始 HTML 的 SHA-256 为：

- Max：`f1f760b166f178d9020d4973d80039a9dbf99e5c411df843b0f1b8aa8d3f702a`；对应文本 `4b101683031875cc050311eb8aaf0000d8e0c6f91f7900fddf8730df0f5fba17`。
- 27B：`a9b5fdf6f2c4f465dd4f623a0d82ccf039865b1e9e63949d209f3e02433706c7`；对应文本 `110278c7fa67d9aa3c7219edc3e6ceaacf2ce41f4ed516136240534e72422e19`。

## 六条实际计算

固定会话原始 HTML、解码 JSON、会话 ID、作品 hash 与当前记录一致；沿所选 leaf 父链重新汇总 31 个唯一响应的四项计费用量。下表的来源指向这些不可变会话；金额为独立 Decimal 复算结果。

| 记录 | input / output / cacheRead / cacheWrite | 假定隐式 USD | 显式同用量 USD | 固定会话 |
|---|---|---:|---:|---|
| qwen3.8-27b-off | 15497 / 6993 / 6656 / 0 | 0.0293931 | 0.0290603 | [10] |
| qwen3.8-max-0902-minimal | 5814 / 4089 / 1024 / 0 | 0.036418 | 0.03633608 | [14] |
| qwen3.8-max-0902-low | 4090 / 3407 / 2048 / 0 | 0.029134 | 0.02897016 | [13] |
| qwen3.8-max-0902-medium | 7416 / 5838 / 7552 / 0 | 0.051748 | 0.05114384 | [12] |
| qwen3.8-max-0902-high | 111931 / 89739 / 703744 / 0 | 0.938232 | 0.88193248 | [9] |
| qwen3.8-max-0902-xhigh | 78088 / 57501 / 503808 / 0 | 0.627134 | 0.58682936 | [11] |

计算为四项记录用量乘对应单价后除以 1,000,000；输出已含思考，不重复计入。使用的零写入只是原记录计数，没有写入 `recorded_zero_cache_write_is_complete: true`，也没有把真实完整用量标成已证明。

每条条件说明明确写明：**历史缓存模式未核实；写入按原记录 0 计算，原始创建量未独立证明；替代情景不构成实际账单区间。** 这六条条件估价是指定假设下的算术结果，不能用于声称历史实扣或发票上下界。

## 数据与失效规则

两个基础 profile 的 `cacheRead`、`cacheWrite` 继续为 `null`。`cache_rate_options` 仅保存官方准确型号的 `implicit` / `explicit` 单价；没有把研究 raw 内容、取证路径或预计结果复制进公开 profile。

六份假设 review 绑定 `gist_id`、`gist_revision`、`session_id`、`artwork_sha256`、准确 `model_id` 及四项 `reviewed_tokens`。只有这些绑定匹配，且写入为零、双语标签与说明完整、显式替代费率齐全时，才选择隐式主情景。返回 `basis: official` 表示费率来源，额外返回：

```json
{
  "estimate_kind": "conditional_assumption",
  "assumption_label": {"en": "Assumes implicit cache", "zh": "假定隐式缓存"},
  "historical_cache_mode": null
}
```

`cache_mode_assumption` 条件不因缓存读取为零而隐藏。来源、四项计费用量、型号或 review 失效，缺少双语条件文案/显式选项，以及非零写入都会返回未知；新记录不能自动继承假设。命令行 `pricing.report` 同样标明 `conditional assumption` 和历史模式未核实。

回归发现已有 `qwen3.8-27b-low / medium / xhigh` 的缓存读写均为零，原本普通估价分别为 `$0.033221 / $0.013797 / $0.1972005`。为保留这些金额且不放行新的未审核同型号记录，另外绑定这三份现有导入记录的来源和用量，记录 `cache_rates_unused: true`。它只说明此算式没有使用缓存单价，不证明历史没有创建缓存；三条继续采用基础普通费率，不添加缓存模式假设标签。六条隐式假设 review 的数量未变。

## 验证与交付范围

新增 `tests/test_cache_assumptions.py` 已完成真实记录、绑定失效、双语说明、零读取条件、公开数据、CLI 标记及原有零缓存估价的红→绿验证。最终新增测试 17 项、历史价格测试 5 项、条件价格测试 13 项及 `tests/test_pricing.py` 均通过。离线独立审计确认接入前 132 条可计算金额全部不变，历史费率配置与已有历史选择函数未被改写。

本次工作区共有 141 条记录、138 条可估，其中六条为本次明确假设的条件估价；正常交付 SVG 的估价缺口为零。三条无作品记录仍未知。并发父任务更新了 Carbon high 的三个源文件，独立审计将它们明确列为本子任务范围外变更，其他 451 个基线内容文件 hash 一致。

仓库内仅修改 `scripts/pricing.py`、`content/pricing.json`，新增本测试和本文档。红绿日志、逐条输出、基线、源码/数据差异及最终哈希保存于本轮恢复审计的 `qwen-integration` 目录。引用沿用原 `qwen/citations.json` 编号，不重置 ledger；严格核验只取本文实际引用的原 ledger 条目，并逐条核对证据原文。本子任务未运行 build/gallery/browser、付费推理、提交或发布；页面各价格表面的可见假设标签由父任务接入并验收。

## Sources

[1] https://www.alibabacloud.com/help/en/model-studio/qwen3-8-max — official-max-details
[2] https://www.alibabacloud.com/help/en/model-studio/qwen3-8-27b — official-27b-details
[3] https://www.alibabacloud.com/help/en/model-studio/context-cache — official-cache
[9] https://gist.githubusercontent.com/Andiedie/2a62bf005f4c8a245dffc621d6b7d297/raw/8edef1fd595ca35cef82234aabde3aa41ed5dc75/session.html — qwen3.8-max-0902-high fixed native session
[10] https://gist.githubusercontent.com/Andiedie/95b07dd2b398da3f6faccd9bf0520a2b/raw/40474208653d7c1c8551093694ab6ef5db097a86/session.html — qwen3.8-27b-off fixed native session
[11] https://gist.githubusercontent.com/Andiedie/f656526cafff4d0d2a17f26fc543e765/raw/ebd4f6643fcaefa2e0165b7e6b4b20887b15679a/session.html — qwen3.8-max-0902-xhigh fixed native session
[12] https://gist.githubusercontent.com/Andiedie/81fdc626a2bb0e1752216f16a11d78ee/raw/d32119f735601c73e194e79840b15860764944f6/session.html — qwen3.8-max-0902-medium fixed native session
[13] https://gist.githubusercontent.com/Andiedie/0e54f71c0a5c9855bac57adc923da69a/raw/22be21cf8640da655e5e3c816df10682de7bcdc2/session.html — qwen3.8-max-0902-low fixed native session
[14] https://gist.githubusercontent.com/Andiedie/58e7fe6bb5c6f21aa491b6988cf8d617/raw/e531eb9b640d1fe12d0768268c3615e2f456760f/session.html — qwen3.8-max-0902-minimal fixed native session
