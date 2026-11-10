"""Offline checks for shared, evidence-preserving outcome reports."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
assert importlib.util.find_spec('reporting') is not None, 'Missing shared outcome reporting layer'
import reporting


def check():
    legacy = {
        'slug': 'old-max', 'outcome': 'no_artwork',
        'source': {'gist_id': 'example', 'gist_revision': 'pinned'},
        'failure': {
            'status': 'Output truncated',
            'summary': {'en': 'Only thinking was returned.', 'zh': '仅返回思考内容。'},
            'explanation': {'en': 'The original evidence.', 'zh': '原始证据。'},
            'limitation': {'en': 'No native reasoning breakdown.', 'zh': '没有原生思考用量明细。'},
            'facts': [
                {'label': {'en': 'Reported output', 'zh': '报告输出'}, 'value': '128,000 tokens'},
                {'label': {'en': 'Termination', 'zh': '终止记录'}, 'value': 'length / incomplete.max_output_tokens'},
                {'label': {'en': 'Pi warning', 'zh': 'Pi 提示'}, 'value': 'Response was truncated before completion'},
            ],
        },
    }
    fresh = deepcopy(legacy)
    fresh.update(slug='new-xhigh', output_budget_per_request=64000)
    fresh['failure']['facts'] = [
        {'label': {'en': 'Requests / tool calls (selected attempt)', 'zh': '请求 / 工具调用（选定测试）'}, 'value': '1 / 0'},
        {'label': {'en': 'Termination', 'zh': '终止记录'}, 'value': 'length'},
        {'label': {'en': 'XML-feedback turns', 'zh': 'XML 反馈轮数'}, 'value': '0'},
        {'label': {'en': 'Reported output (selected attempt)', 'zh': '报告输出（选定测试）'}, 'value': '64,000 tokens'},
    ]
    before = deepcopy((legacy, fresh))
    reports = [reporting.describe(run) for run in (legacy, fresh)]
    labels = ['Requests / tool calls', 'Termination', 'Output budget / request (incl. reasoning)', 'XML feedback rounds', 'Reported output']
    assert all([fact['label']['en'] for fact in report['facts']] == labels for report in reports)
    assert reports[0]['summary'] == reports[1]['summary']
    assert reports[0]['explanation'] == reports[1]['explanation']
    assert reports[0]['facts'][2]['value'] is None, 'Do not infer a request ceiling from reported output'
    assert reports[0]['facts'][3]['value'] is None, 'Missing feedback count is not zero'
    assert reports[1]['facts'][2]['value'] == '64,000 tokens'
    assert reports[1]['facts'][3]['value'] == '0'
    assert reports[0]['facts'][1]['value'] == 'length'
    notes = ' '.join(note['en'] for note in reports[0]['notes'])
    assert 'incomplete.max_output_tokens' in notes and 'Response was truncated before completion' in notes
    assert (legacy, fresh) == before, 'Presentation must not mutate original evidence'
    unfamiliar = deepcopy(legacy)
    unfamiliar['failure']['facts'][1]['value'] = 'length_unexpected'
    assert reporting.describe(unfamiliar)['facts'][1]['value'] == 'length_unexpected', 'Preserve unfamiliar native termination identifiers'
    for lang in ('en', 'zh'):
        html = reporting.render_html(reports[0], lang)
        assert 'report-notes' in html and 'case-facts' in html
        assert ('Additional notes' if lang == 'en' else '补充说明') in html
        assert ('Not recorded' if lang == 'en' else '未记录') in html
    unsafe = deepcopy(reports[0])
    unsafe['notes'].append({'en': '<script>unsafe</script>', 'zh': '<script>unsafe</script>'})
    assert '&lt;script&gt;unsafe&lt;/script&gt;' in reporting.render_html(unsafe, 'en')
    assert '<script>' not in reporting.render_html(unsafe, 'en')
    delivered = {
        'slug': 'corrected-high', 'follow_up_count': 1,
        'source': {'kind': 'local', 'session_sha256': 'json-sha', 'export_sha256': 'html-sha'},
        'metrics': {'errors': 1, 'tool_errors': 2},
    }
    unknown = reporting.describe(delivered)
    assert unknown is not None, 'Delivered artwork with interventions needs the same report structure'
    assert unknown['counts']['xml_feedback'] is None, 'A user follow-up is not automatically XML feedback'
    assert [b['label']['en'] for b in unknown['badges']] == ['Follow-up prompts', 'Request errors', 'Tool errors']
    reviews = {'schema_version': 1, 'runs': {'corrected-high': {
        'source': deepcopy(delivered['source']), 'xml_feedback_count': 1,
        'notes': [{'en': 'Historical browser XML feedback.', 'zh': '历史浏览器 XML 反馈。'}],
    }}}
    confirmed = reporting.describe(delivered, reviews)
    assert confirmed['notes'][-1] == reviews['runs']['corrected-high']['notes'][0]
    assert confirmed['counts']['xml_feedback'] == 1
    assert [b['label']['en'] for b in confirmed['badges']] == ['XML feedback rounds', 'Request errors', 'Tool errors']
    assert [f['label']['en'] for f in confirmed['facts']] == ['Follow-up prompts', 'XML feedback rounds', 'Request errors', 'Tool errors']
    changed_source = deepcopy(delivered)
    changed_source['source']['session_sha256'] = 'another-session'
    assert reporting.describe(changed_source, reviews)['counts']['xml_feedback'] is None
    impossible = deepcopy(reviews)
    impossible['runs']['corrected-high']['xml_feedback_count'] = 2
    try:
        reporting.describe(delivered, impossible)
        raise AssertionError('Accepted more XML feedback rounds than follow-up prompts')
    except ValueError:
        pass
    clean = deepcopy(delivered)
    clean.update(follow_up_count=0, metrics={'errors': 0, 'tool_errors': 0})
    assert reporting.describe(clean) is None
    legacy_review = {'schema_version': 1, 'runs': {'old-max': {
        'source': deepcopy(legacy['source']), 'request_count': 1, 'tool_calls': 0,
        'follow_up_count': 0, 'xml_feedback_count': 0,
    }}}
    reviewed = reporting.describe(legacy, legacy_review)
    assert reviewed['facts'][0]['value'] == '1 / 0'
    assert reviewed['facts'][3]['value'] == 0
    assert reviewed['facts'][2]['value'] is None
    print('PASS · shared reports, source-bound XML reviews, distinct error counts, unknown evidence and safe bilingual rendering')


if __name__ == '__main__':
    check()
