"""Source-bound Qwen scenarios are assumptions, never historical mode proof."""
from contextlib import redirect_stdout
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
import io
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import pricing

EXPECTED = {
    'qwen3.8-27b-off': ('0.0293931', '0.0290603'),
    'qwen3.8-max-0902-minimal': ('0.036418', '0.03633608'),
    'qwen3.8-max-0902-low': ('0.029134', '0.02897016'),
    'qwen3.8-max-0902-medium': ('0.051748', '0.05114384'),
    'qwen3.8-max-0902-high': ('0.938232', '0.88193248'),
    'qwen3.8-max-0902-xhigh': ('0.627134', '0.58682936'),
}
FIELDS = ('input', 'output', 'cacheRead', 'cacheWrite')


class CacheAssumptionTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = json.loads((ROOT / 'content/pricing.json').read_text())
        self.records = {slug: json.loads((ROOT / 'content' / slug / 'run.json').read_text())
                        for slug in EXPECTED}
        self.run = self.records['qwen3.8-max-0902-low']

    def test_six_real_records_expose_implicit_assumption_and_explicit_same_usage(self):
        frozen = deepcopy((self.snapshot, self.records))
        for slug, (implicit, explicit) in EXPECTED.items():
            with self.subTest(slug=slug):
                run = self.records[slug]
                result = pricing.display_price(run, self.snapshot)
                self.assertEqual(result['amount_usd'], float(implicit))
                self.assertEqual(result['basis'], 'official')
                self.assertEqual(result.get('estimate_kind'), 'conditional_assumption')
                self.assertEqual(result.get('assumption_label'),
                                 {'en': 'Assumes implicit cache', 'zh': '假定隐式缓存'})
                self.assertIn('historical_cache_mode', result)
                self.assertIsNone(result['historical_cache_mode'])
                conditions = [c for c in result['conditions'] if c['kind'] == 'cache_mode_assumption']
                self.assertEqual(len(conditions), 1)
                alternative = conditions[0]['alternatives'][0]
                self.assertEqual(alternative['id'], 'explicit_same_recorded_usage')
                self.assertEqual(alternative['amount_usd'], float(explicit))
                for amount, rates in ((implicit, result['rates_per_million']),
                                      (explicit, alternative['rates_per_million'])):
                    calculated = sum(Decimal(run['metrics']['tokens'][key]) * Decimal(str(rates[key] or 0))
                                     for key in FIELDS) / Decimal(1000000)
                    self.assertEqual(calculated, Decimal(amount))
                self.assertIn('原始创建量未独立证明', conditions[0]['description']['zh'])
                self.assertIn('替代情景不构成实际账单区间', conditions[0]['description']['zh'])
                self.assertIn('not independently verified', conditions[0]['description']['en'])
        self.assertEqual((self.snapshot, self.records), frozen)

    def assert_unavailable(self, run=None, snapshot=None):
        result = pricing.display_price(run or self.run, snapshot or self.snapshot)
        self.assertIsNone(result['amount_usd'])
        self.assertEqual(result['basis'], 'unknown')
        self.assertEqual(result['conditions'], [])
        self.assertNotIn('estimate_kind', result)

    def test_each_source_pin_change_invalidates_all_six_reviews(self):
        for slug, run in self.records.items():
            for key in self.snapshot['runs'][slug]['source']:
                with self.subTest(slug=slug, field=key):
                    changed = deepcopy(run)
                    changed['source'][key] = 'changed'
                    self.assert_unavailable(changed)

    def test_each_billing_quantity_change_invalidates_all_six_reviews(self):
        for slug, run in self.records.items():
            for key in FIELDS:
                with self.subTest(slug=slug, field=key):
                    changed = deepcopy(run)
                    changed['metrics']['tokens'][key] += 1
                    self.assert_unavailable(changed)

    def test_nonzero_writes_are_rejected_even_if_review_tokens_match(self):
        self.run['metrics']['tokens']['cacheWrite'] = 100
        self.snapshot['runs'][self.run['slug']]['reviewed_tokens']['cacheWrite'] = 100
        self.assert_unavailable()

    def test_unreviewed_run_stays_unknown_even_with_zero_cache_reads(self):
        self.run['slug'] = 'unreviewed-qwen'
        self.run['metrics']['tokens']['cacheRead'] = 0
        self.assert_unavailable()

    def test_missing_review_stays_unknown_even_with_zero_cache_reads(self):
        del self.snapshot['runs'][self.run['slug']]
        self.run['metrics']['tokens']['cacheRead'] = 0
        self.assert_unavailable()

    def test_changed_exact_model_cannot_inherit_a_review(self):
        self.run['model_ids'] = ['qwen/qwen3.8-27b']
        self.assert_unavailable()

    def test_incomplete_or_unsupported_review_is_unavailable(self):
        invalid_reviews = []
        original = self.snapshot['runs'][self.run['slug']]
        for field in ('source', 'model_id', 'reviewed_tokens', 'historical_cache_mode',
                      'estimate_assumptions', 'assumption_label', 'condition'):
            changed = deepcopy(original)
            changed.pop(field)
            invalid_reviews.append((field, changed))
        for field in original['source']:
            changed = deepcopy(original)
            changed['source'].pop(field)
            invalid_reviews.append(('missing source ' + field, changed))
        for value in ('implicit', 'explicit', True):
            changed = deepcopy(original)
            changed['historical_cache_mode'] = value
            invalid_reviews.append(('historical mode ' + str(value), changed))
        for mode in ('explicit', 'guessed', None):
            changed = deepcopy(original)
            changed['estimate_assumptions']['cache_mode'] = mode
            invalid_reviews.append(('mode ' + str(mode), changed))
        for name, changed in invalid_reviews:
            with self.subTest(review=name):
                self.snapshot['runs'][self.run['slug']] = changed
                self.assert_unavailable()

    def test_missing_bilingual_disclosure_makes_estimate_unavailable(self):
        for locale in ('en', 'zh'):
            for field in ('assumption_label', 'label', 'description', 'alternative_label'):
                for value in (None, '', '   '):
                    with self.subTest(locale=locale, field=field, value=value):
                        snapshot = deepcopy(self.snapshot)
                        review = snapshot['runs'][self.run['slug']]
                        target = (review['assumption_label'] if field == 'assumption_label' else
                                  review['condition']['alternatives'][0]['label'] if field == 'alternative_label' else
                                  review['condition'][field])
                        target[locale] = value
                        self.assert_unavailable(snapshot=snapshot)

    def test_missing_explicit_scenario_makes_estimate_unavailable(self):
        for missing in ('options', 'implicit', 'explicit', 'explicit_read', 'explicit_write', 'alternatives'):
            with self.subTest(missing=missing):
                snapshot = deepcopy(self.snapshot)
                model = snapshot['models']['qwen3.8-max-0902']
                if missing == 'options':
                    model.pop('cache_rate_options')
                elif missing in ('implicit', 'explicit'):
                    model['cache_rate_options'].pop(missing)
                elif missing.startswith('explicit_'):
                    model['cache_rate_options']['explicit'].pop('cacheRead' if missing.endswith('read') else 'cacheWrite')
                else:
                    snapshot['runs'][self.run['slug']]['condition']['alternatives'] = []
                self.assert_unavailable(snapshot=snapshot)

    def test_zero_reads_preserve_the_assumption_condition(self):
        self.run['metrics']['tokens']['cacheRead'] = 0
        review = self.snapshot['runs'][self.run['slug']]
        review['reviewed_tokens']['cacheRead'] = 0
        review['condition']['applies_to'] = ['cacheRead']
        result = pricing.display_price(self.run, self.snapshot)
        self.assertIsNotNone(result['amount_usd'])
        self.assertEqual(result['conditions'][0]['kind'], 'cache_mode_assumption')
        self.assertEqual(result['conditions'][0]['alternatives'][0]['amount_usd'], result['amount_usd'])

    def test_token_bindings_reject_missing_and_non_integer_counts(self):
        for value in (None, '4090', 4090.0, False):
            with self.subTest(value=value):
                run = deepcopy(self.run)
                run['metrics']['tokens']['input'] = value
                self.assert_unavailable(run)

    def test_report_marks_each_conditional_amount(self):
        output = io.StringIO()
        with redirect_stdout(output):
            pricing.report(list(self.records.values()), self.snapshot)
        lines = output.getvalue().splitlines()
        self.assertEqual(len(lines), len(EXPECTED))
        for line in lines:
            self.assertIn('conditional assumption: Assumes implicit cache', line)
            self.assertIn('historical cache mode unverified', line)

    def test_public_profile_excludes_research_metadata_and_unselected_options(self):
        self.snapshot['models']['qwen3.8-max-0902']['rate_evidence'] = {
            'raw_path': '/Users/private/research.html', 'quote': 'long raw evidence'}
        result = pricing.display_price(self.run, self.snapshot)
        for private in ('rate_evidence', 'cache_rate_options', 'reviewed_tokens', 'estimate_assumptions'):
            self.assertNotIn(private, result)
        self.assertNotIn('/Users/', json.dumps(result))

    def test_snapshot_keeps_base_cache_rates_unknown_and_only_six_bound_reviews(self):
        self.assertEqual(self.snapshot['as_of'], '2026-11-11')
        reviewed = {slug for slug, review in self.snapshot['runs'].items() if 'estimate_assumptions' in review}
        self.assertEqual(reviewed, set(EXPECTED))
        for model_id in ('qwen3.8-max-0902', 'qwen3.8-27b'):
            profile = self.snapshot['models'][model_id]
            self.assertIsNone(profile['rates_per_million']['cacheRead'])
            self.assertIsNone(profile['rates_per_million']['cacheWrite'])
            self.assertEqual(set(profile['cache_rate_options']), {'implicit', 'explicit'})
            self.assertIn(model_id.replace('-0902', '').replace('.', '-'), profile['source_url'])
        for slug in EXPECTED:
            review = self.snapshot['runs'][slug]
            self.assertIsNone(review['historical_cache_mode'])
            self.assertEqual(review['estimate_assumptions'], {'cache_mode': 'implicit'})
            self.assertNotIn('recorded_zero_cache_write_is_complete', json.dumps(review))

    def test_existing_zero_cache_qwen_records_keep_ordinary_estimates(self):
        expected = {'low': .033221, 'medium': .013797, 'xhigh': .1972005}
        for level, amount in expected.items():
            with self.subTest(level=level):
                slug = 'qwen3.8-27b-' + level
                run = json.loads((ROOT / 'content' / slug / 'run.json').read_text())
                result = pricing.display_price(run, self.snapshot)
                self.assertEqual(result['amount_usd'], amount)
                self.assertNotIn('estimate_kind', result)
                self.assertEqual(result['conditions'], [])
                changed = deepcopy(run)
                changed['metrics']['tokens']['cacheRead'] = 1
                self.assert_unavailable(changed)
                changed = deepcopy(run)
                changed['source']['gist_revision'] = 'changed'
                self.assert_unavailable(changed)
                changed = deepcopy(run)
                changed['slug'] = 'new-unreviewed-zero-cache-qwen'
                self.assert_unavailable(changed)

    def test_existing_ordinary_amounts_and_metadata_stay_unchanged(self):
        expected = {'gpt-6.1-terra-max': .1559598, 'kimi-k3.1-pro-high': .0704588,
                    'claude-fable-5.2-low': .1645652, 'hy4-high': .077454915}
        for slug, amount in expected.items():
            with self.subTest(slug=slug):
                run = json.loads((ROOT / 'content' / slug / 'run.json').read_text())
                result = pricing.display_price(run, self.snapshot)
                self.assertEqual(result['amount_usd'], amount)
                for field in ('estimate_kind', 'assumption_label', 'historical_cache_mode'):
                    self.assertNotIn(field, result)


if __name__ == '__main__':
    unittest.main()
