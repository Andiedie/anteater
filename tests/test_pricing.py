"""Offline checks for official-only estimates, unknowns, and preserved source evidence."""
from copy import deepcopy
from pathlib import Path
import contextlib
import io
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import pricing


def check():
    tokens = {'input': 1000, 'output': 200, 'cacheRead': 300, 'cacheWrite': 0, 'reasoning': 100}
    profile = {'vendor': 'OpenAI', 'source_kind': 'official', 'source': 'OpenAI',
               'source_url': 'https://platform.openai.com/pricing', 'aliases': ['native-test'],
               'rates_per_million': {'input': 2, 'output': 10, 'cacheRead': .1, 'cacheWrite': 2.5, 'reasoning': None},
               'input_threshold': 272000, 'cache_write_ttl_seconds': 1800}
    snapshot = {'schema_version': 2, 'as_of': '2026-10-22', 'currency': 'USD', 'models': {'gpt-test': profile}, 'runs': {}}
    run = {'slug': 'gpt-test-high', 'model_ids': ['gpt-test'], 'vendor': 'OpenAI',
           'metrics': {'tokens': tokens, 'cost_usd': 99, 'duration_seconds': 60},
           'source': {'session_sha256': 'verified'}, 'date': '2026-10-22T13:50:00Z'}
    baseline = deepcopy(run)
    price = pricing.display_price(run, snapshot)
    assert price['basis'] == 'official' and price['amount_usd'] == .00403
    assert price['checked_at'] == snapshot['as_of'] and run == baseline
    for amount in (None, 0, 99):
        candidate = {**run, 'metrics': {**run['metrics'], 'cost_usd': amount}}
        assert pricing.display_price(candidate, {})['amount_usd'] is None
        assert pricing.display_price(candidate, snapshot)['amount_usd'] == .00403
    assert pricing.display_price(run, {'schema_version': 1, 'runs': {run['slug']: profile}})['amount_usd'] is None
    third_party = deepcopy(snapshot); third_party['models']['gpt-test']['source_kind'] = 'aggregator'
    assert pricing.display_price(run, third_party)['amount_usd'] is None
    assert pricing.find_price({**run, 'model_ids': ['native-test']}, snapshot)['model_id'] == 'gpt-test'
    for changed in ({'model_ids': ['gpt-test-new']}, {'model_ids': ['gpt-test', 'gpt-other']}, {'vendor': 'Google'}):
        assert pricing.find_price({**run, **changed}, snapshot) is None
    for value in (None, -1, float('inf'), float('nan')):
        assert pricing.estimate({**tokens, 'input': value}, profile)[1] == 'missing_usage'
    assert pricing.estimate({**tokens, 'input': 272001}, profile)[1] == 'per_request_usage'
    assert pricing.estimate({**tokens, 'input': 271700}, profile)[0] is not None
    assert pricing.estimate({**tokens, 'cacheWrite': 100}, profile)[1] == 'cache_write_duration'
    assert pricing.estimate({**tokens, 'cacheWrite': 100}, profile, 1800) == (.00428, None)
    assert pricing.estimate({**tokens, 'cacheWrite': 100}, profile, 43200)[1] == 'cache_write_duration'
    missing_cache = {**profile, 'rates_per_million': {**profile['rates_per_million'], 'cacheRead': None}}
    assert pricing.estimate(tokens, missing_cache)[1] == 'missing_cache_price'
    assert pricing.estimate({**tokens, 'cacheRead': 0}, missing_cache)[0] is not None
    separate_reasoning = {**profile, 'rates_per_million': {**profile['rates_per_million'], 'reasoning': 20}}
    assert pricing.estimate(tokens, separate_reasoning) == (.00503, None)
    assert pricing.estimate({**tokens, 'reasoning': 201}, separate_reasoning)[1] == 'missing_usage'
    assert pricing.estimate(tokens, {**profile, 'unavailable': True})[1] == 'not_found'
    reviewed = deepcopy(snapshot)
    reviewed['runs'][run['slug']] = {'source': {'session_sha256': 'verified'}, 'cache_write_ttl_seconds': 1800, 'tokens': tokens}
    stale = {**run, 'source': {'session_sha256': 'changed'}}
    assert pricing.display_price(stale, reviewed)['reason'] == 'source_changed'
    failure = {**run, 'outcome': 'no_artwork'}; failure.pop('metrics')
    assert pricing.display_price(failure, snapshot)['reason'] == 'missing_usage'
    assert pricing.display_price(failure, reviewed)['amount_usd'] == .00403 and 'metrics' not in failure
    assert pricing.off_peak(run)
    for stamp, duration, expected in [('2026-10-22T04:58:00Z', 240, True), ('2026-10-22T05:59:00Z', 120, False),
                                      ('2026-10-22T06:00:00Z', 0, False), ('2026-10-22T03:59:00Z', 120, False),
                                      ('2026-10-24T06:00:00Z', 3600, True), ('2026-10-25T23:59:00Z', 7200, False),
                                      ('2026-10-22T13:50:00+08:00', 60, True), ('2026-10-22', 60, False)]:
        candidate = {**run, 'date': stamp, 'metrics': {**run['metrics'], 'duration_seconds': duration}}
        assert pricing.off_peak(candidate) == expected, (stamp, duration)
    timed = deepcopy(snapshot); timed['models']['gpt-test']['off_peak_only'] = True
    assert pricing.display_price({**run, 'date': '2026-10-22T06:00:00Z'}, timed)['reason'] == 'conditional_price'
    frozen = deepcopy(snapshot)
    with contextlib.redirect_stdout(io.StringIO()):
        pricing.report([run], snapshot)
    assert snapshot == frozen
    actual = json.loads((Path(__file__).resolve().parents[1] / 'content/pricing.json').read_text())
    assert actual['schema_version'] == 2 and actual['as_of'] == '2026-11-11'
    kimi = actual['models'].get('kimi-k3.1-pro')
    assert kimi is not None, 'Kimi K3.1 Pro needs an official price profile'
    assert kimi['source_url'] == 'https://platform.kimi.ai/docs/pricing/chat'
    assert kimi['rates_per_million'] == {'input': 2, 'output': 10, 'cacheRead': .2, 'cacheWrite': 2, 'reasoning': None}
    assert kimi['cache_write_ttl_seconds'] == 300
    content = Path(__file__).resolve().parents[1] / 'content'
    for level, expected in [('low', .0836388), ('high', .0704588), ('max', .3687824)]:
        recorded = json.loads((content / f'kimi-k3.1-pro-{level}' / 'run.json').read_text())
        estimated = pricing.display_price(recorded, actual)
        assert estimated['amount_usd'] == expected and estimated['basis'] == 'official'
        assert estimated['checked_at'] == actual['as_of']
        candidate = deepcopy(recorded)
        candidate['metrics'].update(cost_usd=999, recorded_cost_usd=999)
        assert pricing.display_price(candidate, actual)['amount_usd'] == expected
    assert pricing.find_price({**recorded, 'model_ids': ['kimi-k3.1-pro']}, actual)['model_id'] == 'kimi-k3.1-pro'
    assert pricing.find_price({**recorded, 'model_ids': ['moonshotai/kimi-k3.1-pro-highspeed']}, actual) is None
    assert pricing.find_price({**recorded, 'model_ids': ['moonshotai/kimi-k3']}, actual)['rates_per_million']['input'] == 3
    cache_write = {'input': 0, 'output': 0, 'cacheRead': 0, 'cacheWrite': 100}
    assert pricing.estimate(cache_write, kimi)[1] == 'cache_write_duration'
    assert pricing.estimate(cache_write, kimi, 300) == (.0002, None)
    assert pricing.estimate(cache_write, kimi, 3600)[1] == 'cache_write_duration'
    minimax = actual['models']['minimax-m3.1-flash']
    assert minimax['source_url'] == 'https://platform.minimax.io/docs/pricing/overview'
    assert minimax['rates_per_million'] == {'input': .15, 'output': .6, 'cacheRead': .015, 'cacheWrite': None, 'reasoning': None}
    assert pricing.estimate(tokens, minimax) == (.0002745, None)
    assert pricing.estimate({**tokens, 'reasoning': None}, minimax) == (.0002745, None)
    assert pricing.estimate({**tokens, 'cacheWrite': 100}, minimax)[1] == 'missing_cache_price'
    for identifier in ('minimax-m3.1-flash', 'minimax/minimax-m3.1-flash', 'MiniMax-M3.1-Flash'):
        assert pricing.find_price({'model_ids': [identifier], 'vendor': 'MiniMax'}, actual)['model_id'] == 'minimax-m3.1-flash'
    assert pricing.find_price({'model_ids': ['minimax/minimax-m3.1'], 'vendor': 'MiniMax'}, actual) is None
    assert pricing.find_price({'model_ids': ['minimax/minimax-m3'], 'vendor': 'MiniMax'}, actual)['rates_per_million']['input'] == .3
    terra = actual['models'].get('gpt-6.1-terra')
    assert terra is not None, 'GPT-6.1 Terra needs an official price profile'
    assert terra['source_url'] == 'https://platform.openai.com/docs/models/gpt-6.1-terra'
    assert terra['rates_per_million'] == {'input': 1, 'output': 5, 'cacheRead': .05, 'cacheWrite': 1.25, 'reasoning': None}
    assert terra['input_threshold'] == 272000 and terra['cache_write_ttl_seconds'] == 1800
    for level, expected in [('low', .01556), ('medium', .017582), ('high', .017512), ('xhigh', .023161), ('max', .1559598)]:
        recorded = json.loads((content / f'gpt-6.1-terra-{level}' / 'run.json').read_text())
        estimated = pricing.display_price(recorded, actual)
        assert estimated['amount_usd'] == expected and estimated['basis'] == 'official'
        assert estimated['checked_at'] == actual['as_of']
        candidate = deepcopy(recorded)
        candidate['metrics'].update(cost_usd=999, recorded_cost_usd=999)
        candidate['metrics']['tokens']['reasoning'] = None
        assert pricing.display_price(candidate, actual)['amount_usd'] == expected
    assert pricing.estimate(cache_write, terra)[1] == 'cache_write_duration'
    assert pricing.estimate(cache_write, terra, 1800) == (.000125, None)
    assert pricing.estimate(cache_write, terra, 43200)[1] == 'cache_write_duration'
    assert pricing.estimate({**tokens, 'input': 272001}, terra)[1] == 'per_request_usage'
    assert pricing.find_price({**recorded, 'model_ids': ['gpt-6.1-terra-unreviewed']}, actual) is None
    assert pricing.find_price({**recorded, 'model_ids': ['gpt-5.6-terra']}, actual)['rates_per_million']['output'] == 12
    hy4 = actual['models']['hy4']
    assert hy4['source_url'] == 'https://www.tencentcloud.com/document/product/1300/78937'
    assert hy4['rates_per_million'] == {'input': .417, 'output': 1.2505, 'cacheRead': .021, 'cacheWrite': None, 'reasoning': None}
    assert all('2026-12-31 23:59:59' in note for note in hy4['rate_note'].values())
    for level, expected in [('off', .0117715595), ('high', .077454915)]:
        recorded = json.loads((content / f'hy4-{level}' / 'run.json').read_text())
        assert recorded['name'] == 'Hy4'
        estimated = pricing.display_price(recorded, actual)
        assert estimated['basis'] == 'official' and estimated['amount_usd'] == expected
        assert estimated['checked_at'] == actual['as_of']
        candidate = deepcopy(recorded)
        candidate['metrics'].update(cost_usd=999, recorded_cost_usd=999)
        candidate['metrics']['tokens']['reasoning'] = None
        assert pricing.display_price(candidate, actual)['amount_usd'] == expected
    for identifier in ('hy4', 'tencent/hy4'):
        assert pricing.find_price({'model_ids': [identifier], 'vendor': 'Tencent'}, actual)['model_id'] == 'hy4'
    assert pricing.find_price({'model_ids': ['tencent/hy4'], 'vendor': 'Other'}, actual) is None
    assert pricing.find_price({'model_ids': ['tencent/hy4-flash'], 'vendor': 'Tencent'}, actual) is None
    assert pricing.find_price({'model_ids': ['tencent/hy4-preview'], 'vendor': 'Tencent'}, actual)['rates_per_million']['input'] == .834
    assert pricing.estimate(cache_write, hy4)[1] == 'missing_cache_price'
    fable = actual['models']['claude-fable-5-2']
    assert fable['rates_per_million'] == {'input': 8, 'output': 40, 'cacheRead': .2, 'cacheWrite': 10, 'reasoning': None}
    assert fable['cache_write_ttl_seconds'] == 300
    for level, expected in [('low', .1645652), ('medium', .1740554), ('high', 1.850488),
                            ('xhigh', 2.579522), ('max', 2.65253)]:
        recorded = json.loads((content / f'claude-fable-5.2-{level}' / 'run.json').read_text())
        assert pricing.display_price(recorded, actual)['amount_usd'] == expected
        candidate = deepcopy(recorded)
        candidate['source']['session_sha256'] = 'changed'
        assert pricing.display_price(candidate, actual)['reason'] == 'source_changed'
    carbon = actual['models']['gemini-4-carbon']
    assert carbon['rates_per_million'] == {'input': 2, 'output': 10, 'cacheRead': .1, 'cacheWrite': None, 'reasoning': None}
    for level, expected in [('low', .193564), ('medium', .755517)]:
        recorded = json.loads((content / f'gemini-4-carbon-{level}' / 'run.json').read_text())
        quoted = pricing.display_price(recorded, actual)
        assert quoted['amount_usd'] == expected and quoted['conditions']
        candidate = deepcopy(recorded)
        candidate['metrics'].update(cost_usd=999, recorded_cost_usd=999)
        assert pricing.display_price(candidate, actual)['amount_usd'] == expected
    interrupted = json.loads((content / 'gemini-4-carbon-high' / 'run.json').read_text())
    assert 'metrics' not in interrupted and interrupted['failure']['status'] == 'Incomplete: stream interrupted'
    unknown = pricing.display_price(interrupted, actual)
    assert unknown['amount_usd'] is None and unknown['reason'] == 'missing_usage' and unknown['conditions'] == []
    missing_svg_estimates = []
    for path in sorted(content.glob('*/run.json')):
        recorded = json.loads(path.read_text())
        if recorded.get('outcome') != 'no_artwork' and pricing.display_price(recorded, actual)['amount_usd'] is None:
            missing_svg_estimates.append(recorded['slug'])
    assert not missing_svg_estimates, f'Every delivered SVG needs a reviewed current or historical estimate: {missing_svg_estimates}'
    identifiers = set()
    for model_id, quote in actual['models'].items():
        assert quote['source_kind'] == 'official' and quote['source_url'].startswith('https://')
        assert not any(host in quote['source_url'] for host in ('gpt.ge', 'models.dev', 'openrouter', 'litellm'))
        for identifier in (model_id, *quote.get('aliases', [])):
            pair = (quote['vendor'], identifier)
            assert pair not in identifiers; identifiers.add(pair)
        if not quote.get('unavailable'):
            assert all(pricing.rate(quote['rates_per_million'][key]) is not None for key in ('input', 'output'))
    print('PASS · official-only pricing, exact IDs, cache TTLs, tiers, reasoning, off-peak bounds, pinned evidence and no raw-cost fallback')


if __name__ == '__main__':
    check()
