"""Official release ordering uses separate metadata, never the test/import dates."""

from contextlib import contextmanager
from copy import deepcopy
import json
from pathlib import Path
import re
import shutil
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import gallery


def release(vendor, name, day):
    return {'vendor': vendor, 'name': name, 'release_date': day,
            'source_url': f'https://{ "qwen.ai" if vendor == "Alibaba" else "z.ai" }/fixture-release' if day else None,
            'date_basis': 'official_release' if day else 'unknown',
            'notes': {'en': 'Synthetic release fixture.', 'zh': '合成发布日期夹具。'}}


def fixture(root):
    """Self-contained source-valid records with test order opposed to release order."""
    content = root / 'content'
    content.mkdir()
    shutil.copytree(gallery.ROOT / 'src', root / 'src')
    svg = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><circle cx="5" cy="5" r="4"/></svg>'
    records = [
        ('old-high', 'Alibaba', 'Old 20991231', 'high', '2026-11-17T12:00:00Z'),
        ('new-low', 'Z.ai', 'New', 'low', '2026-01-01T00:00:00Z'),
        ('new-high', 'Z.ai', 'New', 'high', '2026-01-02T00:00:00Z'),
        ('tie-high', 'Alibaba', 'Tie', 'high', '2026-06-01T00:00:00Z'),
        ('tie-b-high', 'Alibaba', 'Tie B', 'high', '2026-07-01T00:00:00Z'),
        ('unknown-high', 'Alibaba', 'Unknown', 'high', '2026-11-17T23:00:00Z'),
        ('missing-high', 'Alibaba', 'Missing', 'high', '2026-11-17T23:30:00Z'),
    ]
    for index, (slug, vendor, name, level, tested) in enumerate(records):
        folder = content / slug
        folder.mkdir()
        share = 'https://pi.dev/session/#' + 'a' * 32
        run = {'schema_version': 1, 'slug': slug, 'vendor': vendor, 'name': name,
               'date': tested, 'reasoning': [level], 'model_ids': ['fixture/20991231'],
               'available_tools': ['read', 'write', 'edit'], 'follow_up_count': 0,
               'metrics': {'duration_seconds': 10 + index, 'request_seconds': 5 + index,
                           'average_tps': 20 - index, 'tool_calls': 0, 'tool_breakdown': {},
                           'assistant_turns': 1, 'errors': 0, 'tool_errors': 0,
                           'tokens': {'input': 10, 'output': 100 + index, 'reasoning': 0,
                                      'cacheRead': 0, 'cacheWrite': 0, 'totalTokens': 110 + index},
                           'cost_usd': None},
               'source': {'share_url': share, 'gist_id': 'a' * 32, 'gist_revision': 'b' * 40,
                          'artwork_sha256': gallery.digest(svg), 'imported_at': '2099-12-31T00:00:00Z'}}
        (folder / 'run.json').write_text(json.dumps(run))
        (folder / 'artwork.svg').write_bytes(svg)
        (folder / 'share.txt').write_text(share)
    metadata = {'schema_version': 1, 'as_of': '2026-11-17', 'models': [
        release('Alibaba', 'Old 20991231', '2025-01-01'),
        release('Z.ai', 'New', '2026-10-01'),
        release('Alibaba', 'Tie', '2026-10-01'),
        release('Alibaba', 'Tie B', '2026-10-01'),
        release('Alibaba', 'Unknown', None),
    ]}
    (content / 'model-releases.json').write_text(json.dumps(metadata))
    return metadata


@contextmanager
def use_fixture(root):
    original = gallery.ROOT, gallery.CONTENT, gallery.PRICES
    gallery.ROOT, gallery.CONTENT, gallery.PRICES = root, root / 'content', root / 'content/pricing.json'
    try:
        yield
    finally:
        gallery.ROOT, gallery.CONTENT, gallery.PRICES = original


class ModelReleases(unittest.TestCase):
    def test_reviewed_manufacturer_authorities_remain_narrow(self):
        accepted = [
            ('Meta', 'https://research.meta.ai/blog/muse-ember'),
            ('Xiaomi', 'https://x.com/XiaomiMiMo/status/2046988157888209365'),
        ]
        rejected = [
            ('Xiaomi', 'https://research.meta.ai/blog/muse-ember'),
            ('Meta', 'https://research.meta.ai.evil.example/blog/muse-ember'),
            ('Meta', 'https://x.com/XiaomiMiMo/status/2046988157888209365'),
            ('Xiaomi', 'https://x.com/OtherAccount/status/2046988157888209365'),
            ('Xiaomi', 'https://x.com/XiaomiMiMo/status/1234567890'),
            ('Xiaomi', 'https://x.com/XiaomiMiMo/status/2046988157888209365/extra'),
            ('Xiaomi', 'https://x.com.evil.example/XiaomiMiMo/status/2046988157888209365'),
            ('Xiaomi', 'http://x.com/XiaomiMiMo/status/2046988157888209365'),
        ]
        for vendor, url in accepted:
            with self.subTest(accepted=url):
                self.assertTrue(gallery.model_releases.official_source(vendor, url))
        for vendor, url in rejected:
            with self.subTest(rejected=url):
                self.assertFalse(gallery.model_releases.official_source(vendor, url))

    def test_real_catalog_has_a_reviewed_entry_for_every_model(self):
        path = gallery.CONTENT / 'model-releases.json'
        self.assertTrue(path.is_file(), 'The real catalog needs its reviewed official-release snapshot; fixtures cannot establish corpus coverage')
        snapshot = json.loads(path.read_text())
        runs = gallery.load_catalog()
        expected = {(run['vendor'], run['name']) for run in runs}
        actual = [(entry['vendor'], entry['name']) for entry in snapshot['models']]
        self.assertEqual(set(actual), expected, 'Every curated model needs its own official-release or explicit unknown review')
        self.assertEqual(len(actual), len(expected), 'Model release reviews cannot duplicate an identity')

    def test_metadata_rejects_invalid_identity_dates_and_sources(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            metadata = fixture(root)
            target = root / 'content/model-releases.json'
            changes = [
                ('schema', lambda data: data.update(schema_version=2)),
                ('snapshot day', lambda data: data.update(as_of='2026-2-01')),
                ('duplicate', lambda data: data['models'].append(deepcopy(data['models'][0]))),
                ('wrong maker', lambda data: data['models'][0].update(vendor='Other')),
                ('wrong name', lambda data: data['models'][0].update(name='old 20991231')),
                ('whitespace identity', lambda data: data['models'][0].update(name='Old 20991231 ')),
                ('invalid calendar day', lambda data: data['models'][0].update(release_date='2026-02-30')),
                ('date with time', lambda data: data['models'][0].update(release_date='2026-01-01T00:00:00Z')),
                ('loose date', lambda data: data['models'][0].update(release_date='2026-1-01')),
                ('future date', lambda data: data['models'][0].update(release_date='2026-11-18')),
                ('missing official date', lambda data: data['models'][0].update(release_date=None)),
                ('unknown with date', lambda data: data['models'][0].update(date_basis='unknown')),
                ('unreviewed basis', lambda data: data['models'][0].update(date_basis='test_date')),
                ('missing source', lambda data: data['models'][0].update(source_url=None)),
                ('non-HTTPS source', lambda data: data['models'][0].update(source_url='http://qwen.ai/release')),
                ('invalid HTTPS source', lambda data: data['models'][0].update(source_url='https:///release')),
                ('credentials in source', lambda data: data['models'][0].update(source_url='https://secret@qwen.ai/release')),
                ('unofficial source', lambda data: data['models'][0].update(source_url='https://example.com/release')),
                ('misleading host', lambda data: data['models'][0].update(source_url='https://qwen.ai.evil.example/release')),
                ('wrong official maker', lambda data: data['models'][0].update(source_url='https://openai.com/release')),
                ('missing organization', lambda data: data['models'][0].update(source_url='https://github.com')),
                ('wrong organization', lambda data: data['models'][0].update(source_url='https://github.com/openai/release')),
                ('malformed source port', lambda data: data['models'][0].update(source_url='https://qwen.ai:bad/release')),
                ('source control character', lambda data: data['models'][0].update(source_url='https://qwen.ai/\nrelease')),
                ('missing translation', lambda data: data['models'][0]['notes'].update(zh='')),
            ]
            with use_fixture(root):
                for name, mutate in changes:
                    with self.subTest(name=name):
                        invalid = deepcopy(metadata)
                        mutate(invalid)
                        target.write_text(json.dumps(invalid))
                        with self.assertRaisesRegex(ValueError, 'release'):
                            gallery.load_catalog()

    def test_unknown_review_keeps_official_context_without_inventing_a_day(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            metadata = fixture(root)
            unknown = metadata['models'][-1]
            unknown['source_url'] = 'https://github.com/QwenLM/Qwen'
            (root / 'content/model-releases.json').write_text(json.dumps(metadata))
            with use_fixture(root):
                run = next(run for run in gallery.load_catalog() if run['name'] == 'Unknown')
            self.assertIsNone(run['model_release_date'])
            self.assertEqual(run['model_release'], {field: unknown[field] for field in ('source_url', 'date_basis', 'notes')})

    def test_missing_metadata_remains_unknown_without_inferred_dates(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            fixture(root)
            (root / 'content/model-releases.json').unlink()
            with use_fixture(root):
                runs = gallery.load_catalog()
            self.assertTrue(all(run['model_release_date'] is None for run in runs))
            self.assertEqual([group[0]['name'] for group in gallery.group_models(runs)],
                             ['Missing', 'Old 20991231', 'Tie', 'Tie B', 'Unknown', 'New'])

    def test_build_orders_models_by_release_and_keeps_latest_artwork(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            fixture(root)
            before = {path: path.read_bytes() for path in (root / 'content').glob('*/*')}
            with use_fixture(root):
                gallery.build()
            page = (root / 'dist/index.html').read_text()
            slugs = re.findall(r'<article class="card[^\"]*" data-model="[^\"]*" data-slug="([^\"]*)"', page)
            self.assertEqual(slugs, ['tie-high', 'tie-b-high', 'new-high', 'old-high', 'missing-high', 'unknown-high'],
                             'Static cards must use release dates, stable maker/name ties and unknown-last, while keeping the latest artwork')
            public = json.loads(re.search(r'id="catalog-data">(.*?)</script>', page, re.S)[1])
            new = [run for run in public if run['name'] == 'New']
            self.assertEqual({run['model_release_date'] for run in new}, {'2026-10-01'})
            self.assertEqual({run['date'] for run in new}, {'2026-01-01T00:00:00Z', '2026-01-02T00:00:00Z'})
            for run in public:
                if run['name'] in ('Unknown', 'Missing'):
                    self.assertIsNone(run['model_release_date'])
                    self.assertEqual(run['model_release']['date_basis'], 'unknown')
            self.assertEqual(before, {path: path.read_bytes() for path in before})


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--build-fixture':
        root = Path(sys.argv[2])
        root.mkdir(parents=True, exist_ok=True)
        fixture(root)
        with use_fixture(root):
            gallery.build()
    else:
        unittest.main()
