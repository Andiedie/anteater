"""Offline price-source, unit conversion, and non-guessing checks."""
from copy import deepcopy
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import pricing


def check():
    cost = {"input": 2, "output": 10, "cache_read": .1, "cache_write": 2.5,
            "tiers": [{"tier": {"type": "context", "size": 272000}, "input": 4, "output": 15}]}
    catalogs = {
        "models.dev": {"openai": {"models": {"gpt-test": {"cost": cost}}}},
        "OpenRouter": {"openai/gpt-test": {"pricing": {"prompt": ".000002", "completion": ".00001", "input_cache_read": ".0000001", "input_cache_write": ".0000025"}}},
        "LiteLLM": {"gpt-test": {"litellm_provider": "openai", "input_cost_per_token": .000002, "output_cost_per_token": .00001, "cache_read_input_token_cost": .0000001, "cache_creation_input_token_cost": .0000025}},
    }
    run = {"slug": "gpt-test-max", "vendor": "OpenAI", "model_ids": ["gpt-test"], "providers": ["cliproxyapi"],
           "metrics": {"cost_usd": None, "tokens": {"input": 1000, "output": 200, "cacheRead": 300, "cacheWrite": 0, "reasoning": 100}}}
    profile = pricing.find_price(run, catalogs)
    assert profile['source'] == 'models.dev' and profile['model_id'] == 'openai/gpt-test'
    for source in catalogs:
        found = pricing.find_price(run, {source: catalogs[source]})
        assert found['rates_per_million'] == profile['rates_per_million']
        assert pricing.estimate(run['metrics']['tokens'], found) == (.00403, None)
    assert pricing.rate('NaN') is None and pricing.rate('-1') is None and pricing.rate(True) is None
    assert pricing.find_price({**run, 'model_ids': ['gpt-test-new']}, catalogs) is None
    assert pricing.find_price({**run, 'model_ids': ['gpt-test', 'another-model']}, catalogs) is None
    assert pricing.find_price({**run, 'providers': ['openrouter']}, catalogs)['source'] == 'OpenRouter'
    assert pricing.estimate({**run['metrics']['tokens'], 'input': 272001}, profile)[1] == 'per_request_usage'
    assert pricing.estimate({**run['metrics']['tokens'], 'cacheRead': None}, profile)[1] == 'missing_usage'
    tiered = {'pricing': {**catalogs['OpenRouter']['openai/gpt-test']['pricing'], 'overrides': [{'min_prompt_tokens': 1300}]}}
    tier_profile = pricing.normalize('OpenRouter', tiered)
    assert pricing.estimate(run['metrics']['tokens'], tier_profile)[1] == 'per_request_usage'
    assert pricing.estimate({**run['metrics']['tokens'], 'input': 999}, tier_profile)[0] is not None
    invalid_fee = {**tiered, 'pricing': {**tiered['pricing'], 'request': 'unknown'}}
    assert pricing.estimate(run['metrics']['tokens'], pricing.normalize('OpenRouter', invalid_fee))[1] == 'conditional_price'
    assert pricing.estimate(run['metrics']['tokens'], {**profile, 'input_threshold': 0})[1] == 'per_request_usage'
    assert pricing.find_price(run, {'models.dev': {'cliproxyapi': catalogs['models.dev']['openai']}}) is None
    for vendor, model_id in [('Alibaba', 'qwen/qwen3.8-27b'), ('Moonshot AI', 'moonshotai/kimi-k3'), ('MiniMax', 'minimax/minimax-m3')]:
        new_run = {**run, 'vendor': vendor, 'model_ids': [model_id], 'providers': ['openrouter']}
        exact = pricing.find_price(new_run, {'OpenRouter': {model_id: catalogs['OpenRouter']['openai/gpt-test']}})
        assert exact['model_id'] == model_id and exact['source'] == 'OpenRouter'
    no_cache_rate = deepcopy(profile); no_cache_rate['rates_per_million']['cacheRead'] = None
    assert pricing.estimate(run['metrics']['tokens'], no_cache_rate)[1] == 'missing_cache_price'
    anthropic = {**run, 'vendor': 'Anthropic', 'model_ids': ['claude-test']}
    anthropic_profile = pricing.find_price(anthropic, {'models.dev': {'anthropic': {'models': {'claude-test': {'cost': cost}}}}})
    assert pricing.estimate(run['metrics']['tokens'], anthropic_profile)[0] == .00403
    assert pricing.estimate({**run['metrics']['tokens'], 'cacheWrite': 100}, anthropic_profile)[1] == 'cache_write_duration'
    different_reasoning = deepcopy(profile); different_reasoning['rates_per_million']['reasoning'] = 20
    assert pricing.estimate(run['metrics']['tokens'], different_reasoning) == (.00503, None)
    assert pricing.display_price(run, {})['amount_usd'] is None
    assert pricing.display_price({**run, 'metrics': {**run['metrics'], 'cost_usd': .5}}, {}) == {'amount_usd': .5, 'basis': 'recorded'}
    with TemporaryDirectory() as folder:
        destination = Path(folder) / 'pricing.json'
        def fetch(request):
            name = next(name for name, url in pricing.SOURCES.items() if request.full_url == url)
            data = {'data': list({'id': key, **value} for key, value in catalogs[name].items())} if name == 'OpenRouter' else catalogs[name]
            return json.dumps(data).encode()
        pricing.refresh([run], destination, fetch)
        snapshot = json.loads(destination.read_text())
        assert pricing.display_price(run, snapshot)['amount_usd'] == .00403
        assert run['metrics']['cost_usd'] is None
        original = destination.read_bytes()
        def offline(request):
            raise OSError('offline fixture')
        try:
            pricing.refresh([run], destination, offline)
            raise AssertionError('Failed refresh discarded the old snapshot')
        except ValueError:
            pass
        assert destination.read_bytes() == original
    print('PASS · three price sources, exact IDs, cache/reasoning costs, tier limits, preserved snapshots')


if __name__ == '__main__':
    check()
