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
    assert actual['schema_version'] == 2 and actual['as_of'] == '2026-10-24'
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
