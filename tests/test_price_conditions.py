"""Conditional estimates compare the same usage under reviewed rates."""
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
import importlib
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
pricing = importlib.import_module('pricing')


class PriceConditionTests(unittest.TestCase):
    def setUp(self):
        self.tokens = {'input': 1000, 'output': 200, 'cacheRead': 300, 'cacheWrite': 0, 'reasoning': 100}
        self.record = {'slug': 'conditional-test', 'vendor': 'DeepSeek', 'model_ids': ['test-flash'],
                    'date': '2026-10-24T06:00:00Z', 'metrics': {'tokens': self.tokens, 'duration_seconds': 1},
                    'source': {'session_sha256': 'original'}}
        self.profile = {'vendor': 'DeepSeek', 'source_kind': 'official', 'source': 'DeepSeek',
                        'source_url': 'https://api-docs.deepseek.com/quick_start/pricing/',
                        'rates_per_million': {'input': .15, 'output': .6, 'cacheRead': .003,
                                              'cacheWrite': None, 'reasoning': None},
                        'off_peak_only': True,
                        'conditions': [{'kind': 'off_peak', 'label': {'en': 'Off-peak', 'zh': '谷时'},
                                        'description': {'en': 'Off-peak hours.', 'zh': '谷时时段。'},
                                        'applies_to': ['input', 'output', 'cacheRead'],
                                        'alternatives': [{'label': {'en': 'Peak', 'zh': '峰时'},
                                                          'rates_per_million': {'input': .3, 'output': 1.2,
                                                                                'cacheRead': .006, 'cacheWrite': None,
                                                                                'reasoning': None}}]}]}
        self.snapshot = {'schema_version': 2, 'as_of': '2026-11-11', 'models': {'test-flash': self.profile}, 'runs': {}}

    def test_other_rate_reprices_same_usage_without_adding_reasoning(self):
        frozen = deepcopy(self.snapshot)
        result = pricing.display_price(self.record, self.snapshot)
        expected = float((Decimal(1000) * Decimal('.3') + Decimal(200) * Decimal('1.2')
                          + Decimal(300) * Decimal('.006')) / Decimal(1000000))
        self.assertTrue(result.get('conditions'), 'A priced off-peak record must expose its condition')
        self.assertIn('amount_usd', result['conditions'][0]['alternatives'][0],
                      'Alternative amounts must be calculated from this record, not just expose unit rates')
        self.assertEqual(result['conditions'][0]['alternatives'][0]['amount_usd'], expected)
        self.assertEqual(self.snapshot, frozen)


    def test_unpublished_alternative_stays_unknown(self):
        self.profile['conditions'][0]['alternatives'][0]['rates_per_million'] = None
        alternative = pricing.display_price(self.record, self.snapshot)['conditions'][0]['alternatives'][0]
        self.assertIsNone(alternative['amount_usd'])
        self.assertEqual(alternative['reason'], 'not_announced')

    def test_unused_discount_does_not_mark_the_estimate(self):
        self.profile['conditions'][0]['applies_to'] = ['cacheWrite']
        self.assertEqual(pricing.display_price(self.record, self.snapshot)['conditions'], [])

    def test_source_pinned_failure_uses_reviewed_usage_for_alternatives(self):
        self.profile.pop('off_peak_only')
        self.profile['conditions'][0]['kind'] = 'promotion'
        failure = deepcopy(self.record)
        failure.pop('metrics')
        failure['outcome'] = 'no_artwork'
        self.snapshot['runs'][failure['slug']] = {'source': failure['source'].copy(), 'tokens': self.tokens}
        valid = pricing.display_price(failure, self.snapshot)
        self.assertEqual(valid['conditions'][0]['alternatives'][0]['amount_usd'],
                         pricing.display_price(self.record, self.snapshot)['conditions'][0]['alternatives'][0]['amount_usd'])
        failure['source']['session_sha256'] = 'changed'
        stale = pricing.display_price(failure, self.snapshot)
        self.assertIsNone(stale['amount_usd'])
        self.assertEqual(stale['reason'], 'source_changed')
        self.assertEqual(stale['conditions'], [])

    def test_incomplete_usage_never_produces_conditional_amounts(self):
        self.record['metrics']['tokens']['output'] = None
        result = pricing.display_price(self.record, self.snapshot)
        self.assertIsNone(result['amount_usd'])
        self.assertEqual(result['conditions'], [])


    def test_static_conditional_price_escapes_labels_and_exposes_the_other_amount(self):
        gallery = importlib.import_module('gallery')
        renderer = getattr(gallery, 'price_html', None)
        assert callable(renderer), 'The server-rendered price needs the same conditional marker as the live UI'
        price = pricing.display_price(self.record, self.snapshot)
        price['conditions'][0]['label']['en'] = '<img src=x onerror=alert(1)>'
        html = renderer(price, 'en', 'test-price')
        assert isinstance(html, str)
        self.assertIn('data-price-hint="test-price"', html)
        self.assertIn('popover="manual"', html)
        self.assertIn('role="tooltip"', html)
        self.assertIn('aria-describedby="test-price"', html)
        self.assertIn('&lt;img', html)
        self.assertNotIn('<img', html)
        self.assertIn('0.0005418', html)
        price['amount_usd'] = .077454915
        rounded_html = renderer(price, 'en', 'rounding-price')
        assert isinstance(rounded_html, str)
        self.assertIn('≈$0.07745492 USD', rounded_html)


class PriceMarkup(HTMLParser):
    """Inspect visible assumption text independently of renderer markup order."""
    def __init__(self, markup):
        super().__init__()
        self.stack = []
        self.assumptions = []
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.stack.append((tag, dict(attrs)))

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()

    def handle_data(self, data):
        if any('price-assumption' in attrs.get('class', '').split() for _, attrs in self.stack):
            self.assumptions.append((data, list(self.stack)))


class PriceAssumptionRenderingTests(unittest.TestCase):
    def setUp(self):
        self.gallery = importlib.import_module('gallery')
        self.price = {
            'amount_usd': .12345678,
            'estimate_kind': 'conditional_assumption',
            'assumption_label': {'en': 'Assumes implicit cache', 'zh': '假定隐式缓存'},
            'historical_cache_mode': None,
            'conditions': [{
                'kind': 'cache_mode_assumption',
                'label': {'en': 'Cache mode assumption', 'zh': '缓存模式假设'},
                'description': {'en': 'Historical cache mode is unknown.', 'zh': '历史缓存模式未知。'},
                'alternatives': [{
                    'label': {'en': 'Assumes explicit cache', 'zh': '假定显式缓存'},
                    'amount_usd': .09876543,
                }],
            }],
        }

    def render_dynamic(self, price, lang, card=False):
        module = (Path(__file__).resolve().parents[1] / 'src/price-hints.js').as_uri()
        result = subprocess.run(['node', '--input-type=module', '-e',
            f'import {{renderPrice, renderPriceAssumption}} from {json.dumps(module)};'
            'const [price, lang, card] = JSON.parse(process.argv[1]);'
            'const amount = renderPrice(price, "≈$0.123", lang, "fixture-price", {showAssumption: !card});'
            'console.log(card ? `<dt>${renderPriceAssumption(price, lang)}</dt><dd>${amount}</dd>` : amount);',
            json.dumps([price, lang, card])], check=True, text=True, capture_output=True)
        return result.stdout.strip()

    def assert_visible_assumption(self, markup, label):
        labels = PriceMarkup(markup).assumptions
        self.assertEqual([text for text, _ in labels], [label])
        for _, ancestors in labels:
            self.assertFalse(any(attrs.get('aria-hidden') == 'true' or 'hidden' in attrs
                                 or attrs.get('role') == 'tooltip' for _, attrs in ancestors))
        self.assertIn('aria-describedby="fixture-price"', markup)

    def test_static_shared_price_discloses_assumption_outside_tooltip(self):
        for lang, label in self.price['assumption_label'].items():
            with self.subTest(lang=lang):
                markup = self.gallery.price_html(self.price, lang, 'fixture-price')
                self.assert_visible_assumption(markup, label)
                self.assertIn(self.price['conditions'][0]['description'][lang], markup)
                self.assertIn('0.09876543', markup)

    def test_dynamic_shared_price_discloses_assumption_outside_tooltip(self):
        for lang, label in self.price['assumption_label'].items():
            with self.subTest(lang=lang):
                markup = self.render_dynamic(self.price, lang)
                self.assert_visible_assumption(markup, label)
                self.assertIn(self.price['conditions'][0]['description'][lang], markup)
                self.assertIn('0.09876543', markup)

    def test_ordinary_and_unavailable_prices_do_not_gain_assumption_labels(self):
        for fields in ({'estimate_kind': 'official'}, {'amount_usd': None}):
            price = {**self.price, **fields}
            for render in (self.gallery.price_html, self.render_dynamic):
                with self.subTest(fields=fields, render=render.__name__):
                    self.assertEqual(PriceMarkup(render(price, 'en')).assumptions, [])

    def test_assumption_labels_are_escaped_in_both_renderers(self):
        self.price['assumption_label'] = {'en': '<img src=x onerror=alert(1)>'}
        for render in (self.gallery.price_html, self.render_dynamic):
            with self.subTest(render=render.__name__):
                markup = render(self.price, 'en')
                self.assertEqual([text for text, _ in PriceMarkup(markup).assumptions],
                                 [self.price['assumption_label']['en']])
                self.assertNotIn('<img', markup)

    def test_static_card_places_assumption_in_metric_label_not_value_row(self):
        run = {'slug': 'fixture', 'name': 'Fixture', 'vendor': 'Test', 'reasoning': ['high'],
               'metrics': {'duration_seconds': 12, 'tokens': {'output': 300}}, 'price': self.price}
        markup = self.gallery.card_html([run])
        label = re.search(r'<dt data-price-label[^>]*>(.*?)</dt>', markup, re.S).group(1)
        value = re.search(r'<dd data-price>(.*?)</dd>', markup, re.S).group(1)
        self.assertEqual([text for text, _ in PriceMarkup(label).assumptions],
                         ['Assumes implicit cache'])
        self.assertEqual(PriceMarkup(value).assumptions, [])
        self.assertIn('data-price-value', value)
        self.assertIn('price-warning', value)

    def test_dynamic_card_components_keep_assumption_out_of_value_row(self):
        for lang, label in self.price['assumption_label'].items():
            with self.subTest(lang=lang):
                markup = self.render_dynamic(self.price, lang, card=True)
                self.assert_visible_assumption(markup, label)
                self.assertEqual(PriceMarkup(markup.split('<dd>', 1)[1]).assumptions, [])

    def test_static_failure_page_includes_both_localized_assumptions(self):
        text = {'en': 'Fixture evidence.', 'zh': '测试证据。'}
        run = {'slug': 'fixture-failure', 'name': 'Fixture', 'vendor': 'Test',
               'reasoning': ['max'], 'date': '2026-11-11', 'outcome': 'no_artwork',
               'price': self.price, 'failure': {'status': 'Output truncated', 'facts': [],
               'references': [], 'summary': text, 'explanation': text, 'limitation': text}}
        markup = self.gallery.failure_html(run, None, reviews={})
        labels = PriceMarkup(markup).assumptions
        self.assertEqual([label for label, _ in labels], list(self.price['assumption_label'].values()))
        for lang, (_, ancestors) in zip(('en', 'zh'), labels):
            self.assertTrue(any(attrs.get('lang') == lang for _, attrs in ancestors))
            self.assertFalse(any(attrs.get('role') == 'tooltip' or attrs.get('aria-hidden') == 'true'
                                 for _, attrs in ancestors))
            self.assertIn(f'aria-describedby="case-fixture-failure-price-{lang}"', markup)


if __name__ == '__main__':
    unittest.main()
