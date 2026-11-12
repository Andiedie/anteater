"""Historical manufacturer quotes must stay tied to their model and period."""
from copy import deepcopy
from pathlib import Path
import importlib
import json
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
pricing = importlib.import_module('pricing')


class HistoricalPriceTests(unittest.TestCase):
    def test_five_real_records_select_reviewed_historical_prices(self):
        root = Path(__file__).resolve().parents[1]
        snapshot = json.loads((root / 'content/pricing.json').read_text())
        expected = {
            'deepseek-v4-flash-0731-max': .01693866,
            'mimo-v2.5-high': .0025284224,
            'mimo-v2.5-off': .0038224256,
            'mimo-v2.5-pro-high': .0084188388,
            'mimo-v2.5-pro-off': .0073885542,
        }
        for slug, amount in expected.items():
            with self.subTest(slug=slug):
                record = json.loads((root / 'content' / slug / 'run.json').read_text())
                price = pricing.display_price(record, snapshot)
                self.assertEqual(price['amount_usd'], amount)
                self.assertEqual(price['basis'], 'official')
                self.assertEqual(price['checked_at'], snapshot['as_of'])
                self.assertEqual(price['conditions'][0]['kind'], 'historical')
                self.assertIsNone(price['rates_per_million']['cacheWrite'])
                self.assertEqual(record['metrics']['tokens']['cacheWrite'], 0)
                changed = deepcopy(record)
                changed['source']['gist_revision'] = 'changed'
                self.assertEqual(pricing.display_price(changed, snapshot)['reason'], 'source_changed')
                if slug.startswith('deepseek'):
                    self.assertEqual(price['historical_rate_period'], {'valid_from': '2026-08-17', 'valid_until': '2026-09-08'})
                    self.assertEqual(price['conditions'][1]['kind'], 'off_peak')
                    self.assertEqual(price['conditions'][1]['alternatives'][0]['amount_usd'], .03387732)
                else:
                    self.assertEqual(price['historical_rate_period'], {'valid_from': '2026-05-28', 'valid_until': '2026-10-13'})
                    self.assertEqual(len(price['conditions']), 1, 'Permanent MiMo reduction is not a V2.6 promotion')

    def test_real_tariffs_exclude_partial_boundary_days(self):
        root = Path(__file__).resolve().parents[1]
        snapshot = json.loads((root / 'content/pricing.json').read_text())
        boundaries = {
            'deepseek-v4-flash-0731-max': ('2026-08-16T20:00:00Z', '2026-09-09T13:00:00Z', '2026-09-08T23:59:59Z'),
            'mimo-v2.5-high': ('2026-05-27T13:00:00Z', '2026-10-14T00:00:00Z', '2026-10-13T23:59:59Z'),
            'mimo-v2.5-pro-high': ('2026-05-27T13:00:00Z', '2026-10-14T00:00:00Z', '2026-10-13T23:59:59Z'),
        }
        for slug, dates in boundaries.items():
            record = json.loads((root / 'content' / slug / 'run.json').read_text())
            for date in dates:
                with self.subTest(slug=slug, date=date):
                    self.assertIsNone(pricing.display_price({**record, 'date': date}, snapshot)['amount_usd'])
            record['metrics']['tokens']['cacheWrite'] = 1
            self.assertEqual(pricing.display_price(record, snapshot)['reason'], 'missing_cache_price')

    def test_retired_model_uses_its_own_official_period_quote(self):
        old = {'vendor': 'Maker', 'source_kind': 'official', 'source': 'Maker',
               'source_url': 'https://example.com/retired', 'unavailable': True,
               'rates_per_million': {'input': None, 'output': None, 'cacheRead': None, 'cacheWrite': None, 'reasoning': None},
               'historical_rates': [{'valid_from': '2026-08-01', 'valid_until': '2026-09-30',
                                     'source_kind': 'official', 'source': 'Maker historical tariff',
                                     'source_url': 'https://example.com/archive/20260801/pricing',
                                     'rates_per_million': {'input': 2, 'output': 10, 'cacheRead': .1, 'cacheWrite': None, 'reasoning': None},
                                     'rate_note': {'en': 'Historical official quote.', 'zh': '历史官方价格。'}}]}
        snapshot = {'schema_version': 2, 'as_of': '2026-11-11', 'models': {'retired-id': old}, 'runs': {}}
        record = {'slug': 'old-high', 'vendor': 'Maker', 'model_ids': ['retired-id'],
                  'date': '2026-09-23T13:46:17Z',
                  'metrics': {'tokens': {'input': 1000, 'output': 200, 'cacheRead': 300, 'cacheWrite': 0, 'reasoning': 100},
                              'cost_usd': 999, 'duration_seconds': 1}}
        original = deepcopy(record)
        quoted = pricing.display_price(record, snapshot)
        self.assertEqual(quoted['amount_usd'], .00403)
        self.assertEqual(quoted['checked_at'], snapshot['as_of'])
        self.assertEqual(quoted['source_url'], old['historical_rates'][0]['source_url'])
        self.assertEqual(quoted['historical_rate_period'], {'valid_from': '2026-08-01', 'valid_until': '2026-09-30'})
        self.assertTrue(quoted['conditions'], 'Historical tariffs need a visible distinction from current quotes')
        self.assertEqual(quoted['conditions'][0]['kind'], 'historical')
        self.assertEqual(record, original)
        self.assertIsNone(pricing.display_price({**record, 'date': '2026-10-01T00:00:00Z'}, snapshot)['amount_usd'])
        self.assertIsNone(pricing.display_price({**record, 'model_ids': ['replacement-id']}, snapshot)['amount_usd'])
        old['historical_rates'][0]['source_kind'] = 'aggregator'
        self.assertIsNone(pricing.display_price(record, snapshot)['amount_usd'])

    def test_earlier_daily_peak_rule_does_not_assume_free_weekends(self):
        profile = {'vendor': 'Maker', 'source_kind': 'official', 'off_peak_only': True,
                   'off_peak_weekdays_only': False,
                   'rates_per_million': {'input': 1, 'output': 2, 'cacheRead': .1}}
        snapshot = {'schema_version': 2, 'as_of': '2026-11-11', 'models': {'old': profile}}
        record = {'slug': 'old', 'vendor': 'Maker', 'model_ids': ['old'],
                  'date': '2026-08-29T02:00:00Z',
                  'metrics': {'duration_seconds': 60,
                              'tokens': {'input': 100, 'output': 100, 'cacheRead': 0, 'cacheWrite': 0}}}
        self.assertIsNone(pricing.display_price(record, snapshot)['amount_usd'])
        self.assertEqual(pricing.display_price(record, snapshot)['reason'], 'conditional_price')
        self.assertIsNotNone(pricing.display_price({**record, 'date': '2026-08-29T13:00:00Z'}, snapshot)['amount_usd'])
        del profile['off_peak_weekdays_only']
        self.assertIsNotNone(pricing.display_price(record, snapshot)['amount_usd'], 'Existing weekday-only tariffs stay unchanged')

    def test_entire_run_must_fit_complete_utc_days(self):
        profile = {'historical_rates': [
            {'source_kind': 'official', 'valid_from': '2026-08-17', 'valid_until': '2026-09-08'}]}
        record = {'date': '2026-09-08T23:59:59Z', 'metrics': {'duration_seconds': 2}}
        self.assertIsNone(pricing.historical_price(record, profile), 'A run crossing the last reviewed day is not covered')
        for duration in (None, -1, float('nan'), float('inf')):
            with self.subTest(duration=duration):
                self.assertIsNone(pricing.historical_price(
                    {**record, 'metrics': {'duration_seconds': duration}}, profile))
        self.assertIsNone(pricing.historical_price({**record, 'date': '2026-09-08T12:00:00'}, profile))
        self.assertIsNone(pricing.historical_price({**record, 'date': '2026-08-16T23:00:00Z'}, profile))
        self.assertIsNotNone(pricing.historical_price(
            {'date': '2026-09-09T00:59:58+01:00', 'metrics': {'duration_seconds': 1}}, profile))
        duplicate = deepcopy(profile)
        duplicate['historical_rates'] *= 2
        self.assertIsNone(pricing.historical_price(
            {'date': '2026-08-29T12:00:00Z', 'metrics': {'duration_seconds': 1}}, duplicate))


if __name__ == '__main__':
    unittest.main()
