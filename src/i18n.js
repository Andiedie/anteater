'use strict';

// English keys are the fallback; identifiers and original artwork stay untranslated.
const chinese = {
  'Anteater Acrobatics Test': '食蚁兽杂技测试',
  'Testing animated SVG generation across AI models with the same prompt, recording run times, token usage, and estimated costs.': '使用同一提示词生成 SVG 动画，比较不同模型的作品、耗时、token 用量与估算费用。',
  'A gallery of AI-generated animated SVGs, with reasoning levels, run times, tokens, and costs.': 'AI 生成的 SVG 动画作品集，展示推理级别、耗时、token 用量与费用。',
  'Skip to the collection': '跳到作品集', 'Anteater home': 'Anteater 首页', 'Main': '主导航',
  'The prompt': '提示词', 'Language': '语言', 'Auto · {language}': '自动 · {language}',
  '{count} performances': '{count} 项测试',
  '{works} artworks · {failed} without SVG': '{works} 件作品 · {failed} 项未交付',
  'No SVG delivered': '未交付 SVG', 'Output truncated': '输出被截断',
  'Read failure notes': '查看失败说明', 'Read failure notes for {model}, max reasoning': '查看 {model}，max 档位失败说明',
  'Skip to the test result': '跳到测试结果', '← Collection': '← 返回作品集', 'References': '参考资料',
  'View the': '查看', 'artwork →': '作品 →', 'Report dated': '报告日期',
  'A recorded test without a delivered SVG, with evidence and limitations.': '未交付 SVG 的测试记录，说明已知情况与证据边界。',
  '{count} model makers': '{count} 家厂商', 'The brief': '原始提示词', 'Run with Pi': '使用 Pi 生成',
  'Each performance starts with this exact prompt. Models can read, write, and edit files. Reasoning levels are recorded as configured, not normalized across model makers.': '每件作品都从这句原始英文提示词开始。模型可以读取、写入和编辑文件。推理级别按测试配置记录，不代表不同厂商之间的统一标准。',
  'Some runs include a follow-up correction or a retry. These are marked in the run details. This is a collection of individual runs, not a ranked benchmark.': '部分测试包含追加纠错或重试，详情中会标明。这里展示单次测试，不是模型排行榜。',
  'Model performances': '模型作品', 'The collection': '作品集', 'Pause animation': '暂停动画', 'Play animation': '播放动画',
  'Pause animations': '暂停动画', 'Play animations': '播放动画', 'Filter by model maker': '按模型厂商筛选',
  'All models': '全部模型', 'Find a model…': '搜索模型…', 'Search model names or makers': '搜索模型名称或厂商',
  'Reasoning level': '推理级别', 'All reasoning': '全部推理级别',
  'Sort performances': '作品排序', 'Newest first': '最新测试优先', 'Best match': '最相关优先', 'Time: shortest': '耗时：从短到长',
  'Cost: lowest': '费用：从低到高', 'Tokens: fewest': 'Token：从少到多', 'TPS: highest': 'TPS：从高到低', 'Model: A–Z': '模型名称：A–Z',
  'Clear filters': '清除筛选', '{shown} of {total} performances': '显示 {shown} / {total} 项测试',
  '{count} performances found': '找到 {count} 项测试', 'No performances found.': '没有找到作品。',
  'Try another model name or reset the filters.': '试试其他模型名称，或重置筛选。', 'Reset filters': '重置筛选',
  'Enable JavaScript to play the animations, filter models, and see run details. Original SVGs are available in the': '启用 JavaScript 后可以播放动画、筛选模型和查看详情。原始 SVG 可在以下位置查看：', 'repository': '代码仓库',
  'Updated': '更新于', 'Made by Andie': '由 Andie 制作',
  'Selected performances': '已选作品', 'Compare': '比较', 'Clear': '清空', 'Choose one more': '再选一件作品',
  '{count} / 4 selected': '已选 {count} / 4', 'Compare {count} ↗': '比较 {count} 件 ↗', 'View {model}, {level} reasoning': '查看 {model},{level}推理',
  'Compare {model}, {level} reasoning': '比较 {model}，{level}推理', '{model} animated SVG': '{model} SVG 动画',
  'Remove {model} from comparison': '从比较中移除 {model}', 'Compare up to four performances. Remove one to change your selection.': '最多比较 4 件作品，请先移除一件再更换。',
  'Loading artwork': '正在加载作品', 'Preview unavailable · open run details': '预览不可用 · 点击查看详情',
  'Preview unavailable · download the SVG below': '预览不可用 · 可在下方下载 SVG', 'Close performance': '关闭作品详情',
  'Close comparison': '关闭作品比较', 'Restart': '重新播放', '← Previous': '← 上一件', 'Next →': '下一件 →',
  'Copy link': '复制链接', 'Copy comparison link': '复制比较链接', 'Link copied ✓': '链接已复制 ✓',
  'Copy unavailable. Copy this page’s address from your browser.': '无法自动复制，请复制浏览器地址栏中的链接。',
  'Performance comparison': '作品比较',
  'Time': '耗时', 'Tools': '工具调用', 'Pi · USD': 'Pi 估算 · USD', 'Public · USD': '公开价 · USD', 'Cost · USD': '费用 · USD',
  'Unknown': '未知', '{seconds}s': '{seconds}秒', '{minutes}m {seconds}s': '{minutes}分{seconds}秒',
  '{level} reasoning': '{level}推理', '{count} follow-up corrections': '{count} 次追加纠错',
  'Includes errors / retries': '包含错误或重试', 'Total run time': '总耗时', 'Average output TPS': '平均输出 TPS',
  'Tool calls': '工具调用次数', 'Pi estimate · USD': 'Pi 记录估算 · USD', 'Public estimate · USD': '公开价格估算 · USD',
  'Estimated cost · USD': '估算费用 · USD', 'Tokens': 'Token 用量', 'Input': '输入', 'Output': '输出', 'Reasoning': '推理',
  'Cache read': '缓存读取', 'Cache write': '缓存写入', 'Recorded total': '记录总量', 'The run': '测试记录',
  'Tested': '测试日期', 'Model ID': '模型 ID', 'Request time': '请求耗时', 'Assistant turns': '模型回复轮数',
  'Tool breakdown': '工具调用明细', 'Available tools': '可用工具', 'Errors recorded': '记录错误数', 'No tool calls': '未调用工具',
  'Not recorded': '未记录', 'How these numbers are measured': '统计口径',
  'Total run time includes tool execution, retries, and any wait for a follow-up prompt. Request time is the sum of recorded assistant request intervals.': '总耗时包含工具执行、重试及等待追加提示的时间。请求耗时是各轮模型请求时间的总和。',
  'Average output TPS = reported output tokens ÷ request time. It includes first-token latency and reasoning time; it is not a streaming decode benchmark. Output may include reasoning tokens.': '平均输出 TPS = 输出 token ÷ 请求耗时，包含首字延迟和推理时间，并非流式解码速度。输出用量可能包含推理 token。',
  'Token totals follow the exported usage. Reasoning is a breakdown, not an extra amount added to the total. Input and cache usage can recur across turns.': 'Token 总量按导出记录展示。推理用量是输出的组成部分，不另行相加。输入和缓存用量可能在多轮请求中重复产生。',
  'Costs are estimates, not billing receipts. Unverified zero costs are not treated as free.': '费用是估算值，不是实际账单。未经核实的零费用不代表免费。',
  'Price reference': '价格参考', 'Pi recorded this estimate in the shared session.': '此费用来自分享会话中 Pi 记录的估算。',
  'The share records $0; the displayed estimate uses public text-token rates.': '会话记录费用为 0；此处按公开文本 token 价格补算。',
  'Public catalog rates at the checked date, not the actual bill. Excludes search, tool surcharges, discounts, and subscriptions.': '按查询日期的公开目录价估算，不代表实际账单；不包含搜索及工具附加费、折扣或订阅费用。',
  'Price source': '价格出处', 'Catalog model': '目录模型', 'Checked': '查询时间', 'USD / 1M tokens': '美元 / 百万 token',
  'No exact public model price was found.': '没有找到准确对应的公开模型价格。',
  'Required usage fields are missing.': '缺少计算费用所需的用量字段。',
  'Cache-write duration is not recorded.': '未记录缓存写入的有效期，无法确定费用。',
  'Cache pricing is missing for the recorded cache usage.': '已记录缓存用量，但缺少对应缓存价格。',
  'Per-request usage is needed to apply context price tiers.': '需逐轮请求用量才能确定长上下文阶梯价格。',
  'Conditional pricing cannot be resolved from this export.': '无法根据现有记录确定条件价格。',
  'Pi conversation ↗': 'Pi 对话 ↗', 'Download SVG ↓': '下载 SVG ↓', 'Source snapshot ↗': '会话快照 ↗',
  'Model maker': '模型厂商', 'Avg. output TPS': '平均输出 TPS', 'Follow-up prompts': '追加提示次数',
  'Input tokens': '输入 token', 'Output tokens': '输出 token', 'Reasoning tokens': '推理 token',
  'Cache read tokens': '缓存读取 token', 'Cache write tokens': '缓存写入 token', 'Recorded total tokens': '记录 token 总量',
  'Performance metrics comparison': '作品生成数据比较', 'Run details': '测试指标',
  'Individual runs, not normalized benchmarks. Run time includes any follow-up waits; average TPS includes request latency and reasoning. Costs are estimates; public-rate estimates are marked ≈.': '这里展示单次测试，并非统一基准。总耗时包含等待追加提示，平均 TPS 包含请求延迟和推理。费用均为估算；公开价格补算以 ≈ 标记。',
  'That performance link is unavailable. Browse the collection below.': '该作品链接不可用，请浏览下方作品集。'
};

function storedLanguage() {
  try { return localStorage.getItem('anteater-language') || 'auto'; }
  catch { return 'auto'; }
}
function chooseLanguage(choice) {
  if (choice === 'zh' || choice === 'en') return choice;
  for (const language of navigator.languages?.length ? navigator.languages : [navigator.language || 'en']) {
    if (/^zh(?:-|$)/i.test(language)) return 'zh';
    if (/^en(?:-|$)/i.test(language)) return 'en';
  }
  return 'en';
}
let languageChoice = storedLanguage();
if (!['auto', 'en', 'zh'].includes(languageChoice)) languageChoice = 'auto';
let language = chooseLanguage(languageChoice);
const locale = () => language === 'zh' ? 'zh-CN' : 'en-US';
function t(key, values = {}) {
  return (language === 'zh' ? chinese[key] ?? key : key).replace(/\{(\w+)\}/g, (match, name) => values[name] ?? match);
}
function translate(root = document) {
  for (const node of root.querySelectorAll('[data-i18n]')) node.textContent = t(node.dataset.i18n);
  for (const attribute of ['aria-label', 'placeholder', 'content']) {
    for (const node of root.querySelectorAll(`[data-i18n-${attribute}]`)) node.setAttribute(attribute, t(node.getAttribute(`data-i18n-${attribute}`)));
  }
}
function setupLanguage(render) {
  const select = document.querySelector('#language');
  const refresh = () => {
    document.documentElement.lang = locale(); translate();
    select.value = languageChoice;
    select.querySelector('[value="auto"]').textContent = t('Auto · {language}', {language: language === 'zh' ? '中文' : 'EN'});
    render();
  };
  select.addEventListener('change', () => {
    languageChoice = select.value; language = chooseLanguage(languageChoice);
    try { if (languageChoice === 'auto') localStorage.removeItem('anteater-language'); else localStorage.setItem('anteater-language', languageChoice); } catch { /* Browser preferences still work without storage. */ }
    refresh();
  });
  window.addEventListener('languagechange', () => { if (languageChoice === 'auto') { language = chooseLanguage('auto'); refresh(); } });
  refresh();
}
document.documentElement.lang = locale();
