"""Shared presentation of recorded outcomes; never rewrite measured source data."""
from copy import deepcopy
from html import escape


def text(en, zh):
    return {'en': en, 'zh': zh}


FAILURE_LABELS = [
    text('Requests / tool calls', '请求 / 工具调用'),
    text('Termination', '终止记录'),
    text('Output budget / request (incl. reasoning)', '每请求输出预算（含思考）'),
    text('XML feedback rounds', 'XML 反馈轮数'),
    text('Reported output', '报告输出'),
]
ALIASES = [
    ('Requests / tool calls', 'Requests / tool calls (selected attempt)'),
    ('Termination',),
    ('Output budget per request', 'Output budget / request (incl. reasoning)'),
    ('XML-feedback turns', 'XML feedback rounds'),
    ('Reported output', 'Reported output (selected attempt)'),
]


COUNT_LABELS = {
    'follow_up': text('Follow-up prompts', '后续提示'),
    'xml_feedback': text('XML feedback rounds', 'XML 反馈轮数'),
    'request_errors': text('Request errors', '请求错误'),
    'tool_errors': text('Tool errors', '工具错误'),
}


def reviewed(run, reviews):
    if not reviews:
        return {}
    if reviews.get('schema_version') != 1:
        raise ValueError('Unsupported outcome review schema')
    review = reviews.get('runs', {}).get(run['slug'], {})
    source = run.get('source', {})
    required = ('session_sha256', 'export_sha256') if source.get('kind') == 'local' else ('gist_id', 'gist_revision')
    if not all(source.get(key) and review.get('source', {}).get(key) == source[key] for key in required):
        return {}
    for key in ('xml_feedback_count', 'follow_up_count', 'request_count', 'tool_calls'):
        if key in review and (type(review[key]) is not int or review[key] < 0):
            raise ValueError(f'Invalid reviewed {key} for {run["slug"]}')
    follow_up = run.get('follow_up_count', review.get('follow_up_count'))
    if 'follow_up_count' in run and 'follow_up_count' in review and run['follow_up_count'] != review['follow_up_count']:
        raise ValueError(f'Reviewed follow-up count disagrees for {run["slug"]}')
    if follow_up is not None and review.get('xml_feedback_count', 0) > follow_up:
        raise ValueError(f'XML feedback exceeds follow-up prompts for {run["slug"]}')
    return review


def intervention(run, review):
    metrics = run['metrics']
    follow_up = run.get('follow_up_count')
    counts = {
        'follow_up': follow_up,
        'xml_feedback': 0 if follow_up == 0 else review.get('xml_feedback_count'),
        'request_errors': metrics.get('errors'),
        'tool_errors': metrics.get('tool_errors'),
    }
    if not any(counts[key] for key in ('follow_up', 'request_errors', 'tool_errors')):
        return None
    badges = []
    notes = []
    if counts['xml_feedback']:
        badges.append({'label': COUNT_LABELS['xml_feedback'], 'count': counts['xml_feedback']})
        notes.append(text('Follow-up prompts included SVG XML diagnostics. Subsequent turns remain part of this test.', '后续提示包含 SVG XML 诊断反馈，后续轮次计入同一次测试。'))
    if follow_up and (counts['xml_feedback'] is None or follow_up > counts['xml_feedback']):
        badges.append({'label': COUNT_LABELS['follow_up'], 'count': follow_up})
        if counts['xml_feedback'] is None:
            notes.append(text('Additional user prompts were recorded; their type has not been separately verified.', '记录中有额外用户提示，其类型尚未单独核验。'))
    for key in ('request_errors', 'tool_errors'):
        if counts[key]:
            badges.append({'label': COUNT_LABELS[key], 'count': counts[key]})
    notes.extend(deepcopy(review.get('notes', [])))
    return {
        'kind': 'intervention', 'counts': counts, 'badges': badges,
        'summary': text('An SVG was delivered with recorded feedback or errors.', '已交付 SVG，过程中有反馈或错误记录。'),
        'facts': [{'label': deepcopy(label), 'value': counts[key]} for key, label in COUNT_LABELS.items()],
        'explanation': text('The reporting scope includes follow-up turns and error records on the selected branch.', '统计范围包含所选分支中的后续轮次与错误记录。'),
        'limitation': text('The source session contains the exact feedback and error messages.', '具体反馈与错误原文见所附原始会话。'),
        'notes': notes,
    }


def describe(run, reviews=None):
    """Normalize comparable displays, retaining authored evidence in extra notes."""
    review = reviewed(run, reviews)
    if run.get('outcome') != 'no_artwork':
        return intervention(run, review)
    failure = run['failure']
    raw = {fact['label']['en']: fact['value'] for fact in failure['facts']}
    values = [next((raw[key] for key in aliases if key in raw), None) for aliases in ALIASES]
    if values[0] is None and ('request_count' in review or 'tool_calls' in review):
        values[0] = f"{review.get('request_count', '—')} / {review.get('tool_calls', '—')}"
    if values[3] is None:
        values[3] = review.get('xml_feedback_count')
    if run.get('output_budget_per_request') is not None:
        values[2] = f"{run['output_budget_per_request']:,} tokens"
    termination = values[1]
    if isinstance(termination, str) and termination.startswith('length / '):
        values[1] = 'length'
    truncated = failure['status'] == 'Output truncated'
    summary = text('The response was truncated before an SVG was delivered.', '响应被截断，未交付 SVG。') if truncated else deepcopy(failure['summary'])
    explanation = text(
        'The recorded termination and usage are listed above. Thinking and answer text share the output limit.',
        '上表列出记录中的终止状态与用量；思考与正文共用输出上限。',
    ) if truncated else deepcopy(failure['explanation'])
    limitation = text(
        'Reported output and requested budget are recorded separately. Actual billing and the internal cause require additional evidence.',
        '报告输出与请求预算分别记录。实际扣费及内部原因需另有证据。',
    ) if truncated else deepcopy(failure['limitation'])
    notes = []
    for key in ('summary', 'explanation', 'limitation'):
        note = failure.get(key)
        if note and note not in (summary, explanation, limitation) and note not in notes:
            notes.append(deepcopy(note))
    if termination != values[1]:
        notes.append(text(f'Termination detail: {termination}', f'终止详情：{termination}'))
    mapped = {key for aliases in ALIASES for key in aliases}
    for fact in failure['facts']:
        if fact['label']['en'] not in mapped:
            notes.append(text(f"{fact['label']['en']}: {fact['value']}", f"{fact['label']['zh']}：{fact['value']}"))
    return {
        'kind': 'failure', 'summary': summary, 'explanation': explanation,
        'limitation': limitation, 'notes': notes, 'badges': [],
        'facts': [{'label': deepcopy(label), 'value': value} for label, value in zip(FAILURE_LABELS, values)],
    }


def value_text(value, lang):
    if value is None:
        return '未记录' if lang == 'zh' else 'Not recorded'
    return str(value[lang] if isinstance(value, dict) else value)


def render_html(report, lang, extra_facts=(), extra_html=()):
    """Render the same bilingual report structure used by the gallery dialog."""
    facts = ''.join(f'<div><dt>{escape(fact["label"][lang])}</dt><dd>{escape(value_text(fact["value"], lang))}</dd></div>' for fact in (*report['facts'], *extra_facts))
    # Only caller-rendered components belong here; record fields stay escaped above.
    facts += ''.join(extra_html)
    notes = ''
    if report['notes']:
        paragraphs = ''.join(f'<p>{escape(note[lang])}</p>' for note in report['notes'])
        notes = f'<details class="metric-notes report-notes"><summary>{"补充说明" if lang == "zh" else "Additional notes"}</summary>{paragraphs}</details>'
    return f'''<div class="run-report" data-report-kind="{escape(report['kind'], quote=True)}">
  <p class="case-summary report-summary">{escape(report['summary'][lang])}</p>
  <dl class="case-facts">{facts}</dl>
  <p class="report-explanation">{escape(report['explanation'][lang])}</p>
  {notes}
  <p class="case-limitation">{escape(report['limitation'][lang])}</p>
</div>'''
