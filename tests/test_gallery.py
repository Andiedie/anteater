"""One offline smoke check for import semantics, SVG safety, and the real catalog."""

from copy import deepcopy
from pathlib import Path
import json
import re
import shutil
import sys
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import gallery


def check():
    with TemporaryDirectory() as temp:
        root = gallery.ROOT
        try:
            gallery.ROOT = Path(temp)
            (gallery.ROOT / 'src').mkdir()
            assets = ('styles.css', 'gallery.js', 'i18n.js', 'failure.js')
            for filename in assets:
                (gallery.ROOT / 'src' / filename).write_text('first version')
            page = ' '.join(f'"./{filename}"' for filename in assets)
            before = gallery.version_assets(page)
            assert gallery.version_assets(page) == before
            (gallery.ROOT / 'src/styles.css').write_text('new theme rules')
            after = gallery.version_assets(page)
            assert after != before and after.split()[1:] == before.split()[1:]
        finally:
            gallery.ROOT = root

    session = {
        "header": {"id": "test"},
        "leafId": "final",
        "systemPrompt": "<tools>\n- read: Read\n- write: Write\n- edit: Edit\n</tools>\n<docs>\n- Examples: Not a tool\n</docs>",
        "tools": [{"name": "bash"}],
        "entries": [
            {"id": "level", "parentId": None, "type": "thinking_level_change", "thinkingLevel": "max"},
            {"id": "user", "parentId": "level", "type": "message", "timestamp": 1000,
             "message": {"role": "user", "content": [{"type": "text", "text": gallery.PROMPT}]}},
            {"id": "first", "parentId": "user", "type": "message", "timestamp": 4000,
             "message": {"role": "assistant", "timestamp": 1000, "model": "gpt-test", "provider": "cliproxyapi", "stopReason": "toolUse",
                         "content": [{"type": "toolCall", "name": "write"}],
                         "usage": {"input": 20, "output": 60, "reasoning": 40, "totalTokens": 80, "cost": {"total": 0}}}},
            {"id": "tool", "parentId": "first", "type": "message", "timestamp": 4100,
             "message": {"role": "toolResult", "isError": False}},
            {"id": "final", "parentId": "tool", "type": "message", "timestamp": 6000,
             "message": {"role": "assistant", "timestamp": 5000, "model": "gpt-test", "provider": "cliproxyapi", "stopReason": "stop", "content": [],
                         "usage": {"input": 60, "output": 20, "cacheRead": 10, "totalTokens": 90, "cost": {"total": 0}}}},
            {"id": "abandoned", "parentId": "user", "type": "message", "timestamp": 9000,
             "message": {"role": "assistant", "timestamp": 1000, "content": [], "usage": {"output": 99999}}},
        ],
    }
    result = gallery.summarize(session)
    m = result["metrics"]
    assert result["reasoning"] == ["max"]
    assert result["available_tools"] == ["read", "write", "edit"]
    assert result["follow_up_count"] == 0
    assert m["duration_seconds"] == 5 and m["request_seconds"] == 4
    assert m["average_tps"] == 20 and m["assistant_turns"] == 2
    assert m["tool_calls"] == 1 and m["tool_breakdown"] == {"write": 1}
    assert m["tokens"]["totalTokens"] == 170 and m["tokens"]["reasoning"] == 40
    assert m["tokens"]["cacheWrite"] is None
    assert m["recorded_cost_usd"] == 0 and m["cost_usd"] is None
    assert "output_budget_per_request" not in result
    budgeted = deepcopy(session)
    budgeted["entries"][0]["parentId"] = "policy"
    budgeted["entries"].insert(0, {"id": "policy", "parentId": None, "type": "custom",
                                  "customType": "anteater-benchmark-policy",
                                  "data": {"model": "gpt-test", "level": "max", "outputLimitPerRequest": 131072}})
    assert gallery.summarize(budgeted)["output_budget_per_request"] == 131072
    for field, value in (("model", "other-model"), ("level", "low"), ("outputLimitPerRequest", 0)):
        invalid_budget = deepcopy(budgeted)
        invalid_budget["entries"][0]["data"][field] = value
        assert "output_budget_per_request" not in gallery.summarize(invalid_budget)
    conflicting = deepcopy(budgeted)
    conflicting["entries"][0]["parentId"] = "previous-policy"
    conflicting["entries"].insert(0, {"id": "previous-policy", "parentId": None, "type": "custom",
                                     "customType": "anteater-benchmark-policy",
                                     "data": {"model": "gpt-test", "level": "max", "outputLimitPerRequest": 64000}})
    assert "output_budget_per_request" not in gallery.summarize(conflicting)

    corrected = deepcopy(session)
    corrected["entries"].insert(4, {"id": "correction", "parentId": "tool", "type": "message", "timestamp": 4900,
                                   "message": {"role": "user", "content": "Fix the XML error"}})
    corrected["entries"][5]["parentId"] = "correction"
    corrected["entries"][5]["message"]["stopReason"] = "error"
    corrected["entries"][5]["message"]["usage"]["cost"]["total"] = .12
    corrected["entries"][5]["message"].pop("timestamp")
    fixed = gallery.summarize(corrected)
    assert fixed["follow_up_count"] == 1
    assert fixed["metrics"]["errors"] == 1 and fixed["metrics"]["cost_usd"] == .12
    assert fixed["metrics"]["request_seconds"] is None and fixed["metrics"]["average_tps"] is None

    for invalid in ("leaf", "prompt"):
        broken = deepcopy(session)
        if invalid == "leaf":
            broken["entries"][4]["parentId"] = "final"
        else:
            broken["entries"][1]["message"]["content"] = "Another task"
        try:
            gallery.summarize(broken)
            raise AssertionError(f"Accepted invalid {invalid}")
        except ValueError:
            pass

    good = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><path id="p"/><use href="#p"/><style>path{fill:red}</style></svg>'
    gallery.check_svg(good)
    for fragment in (
        '<script>alert(1)</script>', '<foreignObject/>', '<path onclick="alert(1)"/>',
        '<image href="https://example.com/a.png"/>', '<style>@import "https://example.com";</style>',
        '<path fill="url(https://example.com/x)"/>', '<animate attributeName="href" values="javascript:x"/>',
    ):
        try:
            gallery.check_svg(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">{fragment}</svg>'.encode())
            raise AssertionError(f"Accepted unsafe SVG: {fragment}")
        except ValueError:
            pass
    assert gallery.model_label("gpt-6.1-sol-max") == ("GPT-6.1 Sol", "OpenAI")
    assert gallery.model_label("hy4-preview-high") == ("Hunyuan 4 Preview", "Tencent")
    assert gallery.model_label("qwen3.8-max-0902-high") == ("Qwen3.8 Max 0902", "Alibaba")
    assert gallery.model_label("qwen3.8-27b-off") == ("Qwen3.8 27B", "Alibaba")
    assert gallery.model_label("kimi-k3-max") == ("Kimi K3", "Moonshot AI")
    assert gallery.model_label("minimax-m3-on") == ("MiniMax M3", "MiniMax")
    switch = deepcopy(session)
    switch['entries'][0]['thinkingLevel'] = 'medium'
    for entry in switch['entries']:
        if entry.get('message', {}).get('role') == 'assistant':
            entry['message'].update(provider='openrouter', model='minimax/minimax-m3')
    assert gallery.summarize(switch)['reasoning'] == ['medium']
    switch['entries'][0]['parentId'] = 'policy'
    switch['entries'].insert(0, {'id': 'policy', 'parentId': None, 'type': 'custom',
                                  'customType': 'anteater-benchmark-policy',
                                  'data': {'model': 'minimax/minimax-m3', 'level': 'on'}})
    assert gallery.summarize(switch)['reasoning'] == ['on']
    switch['entries'][0]['data']['model'] = 'another-model'
    assert gallery.summarize(switch)['reasoning'] == ['medium']

    with TemporaryDirectory() as directory:
        original, fetch = gallery.CONTENT, gallery.read_url
        try:
            gallery.CONTENT = Path(directory) / 'content'
            gallery.CONTENT.mkdir()
            gallery.read_url = lambda request: (_ for _ in ()).throw(AssertionError('Local import accessed the network'))
            folder = Path(directory) / 'claude-test-max'
            folder.mkdir()
            (folder / 'artwork.svg').write_bytes(good)
            local = deepcopy(session)
            local['entries'][1]['timestamp'] = '1970-01-01T00:00:01Z'
            raw = json.dumps(local)
            (folder / 'session.json').write_text(raw)
            (folder / 'session.html').write_text(f'<script id="session-data" type="application/json">{raw}</script>')
            assert gallery.import_run(folder).startswith('Imported ')
            assert gallery.import_run(folder).startswith('Unchanged ')
            imported = gallery.load_catalog()[0]
            assert imported['source']['kind'] == 'local'
            assert imported['source']['share_url'] == './sessions/claude-test-max.html'
            assert imported['source']['snapshot_url'] == './sessions/claude-test-max.json'
            assert imported['source']['session_id'] == 'test'
            imported['response_model_ids'] = ['upstream-alias']
            metadata = gallery.CONTENT / imported['slug'] / 'run.json'
            metadata.write_text(json.dumps(imported))
            assert gallery.import_run(folder, refresh=True).startswith('Imported ')
            assert json.loads(metadata.read_text())['response_model_ids'] == ['upstream-alias']
            mismatched = deepcopy(local)
            mismatched['header']['id'] = 'another-session'
            html = folder / 'session.html'
            html.write_text(f'<script id="session-data" type="application/json">{json.dumps(mismatched)}</script>')
            try:
                gallery.import_run(folder)
                raise AssertionError('Accepted mismatched HTML and JSON sessions')
            except ValueError:
                pass
            html.write_text(f'<script id="session-data" type="application/json">{raw}</script>')
            failed = deepcopy(imported)
            failed.update(slug='gemini-test-low', name='Gemini Test', vendor='Google', date='1970-01-01', reasoning=['low'], outcome='no_artwork')
            failed.pop('metrics')
            failed['source'].pop('artwork_sha256')
            failed['source'].update(share_url='./sessions/gemini-test-low.html', snapshot_url='./sessions/gemini-test-low.json')
            failed['failure'] = {'status': 'Upstream error', 'summary': {'en': 'No accepted artwork.', 'zh': '没有合格产物。'},
                                 'explanation': {'en': 'The upstream failed.', 'zh': '上游失败。'},
                                 'limitation': {'en': 'Not a capability verdict.', 'zh': '不作为能力结论。'},
                                 'facts': [], 'references': [], 'related_slug': None}
            target = gallery.CONTENT / failed['slug']
            target.mkdir()
            for name in ('session.json', 'session.html'):
                shutil.copy2(folder / name, target / name)
            (target / 'run.json').write_text(json.dumps(failed))
            assert len(gallery.load_catalog()) == 2
            case = gallery.failure_html(failed, None)
            assert ' · low — ' in case and 'data-level="low"' in case
            assert 'case-related' not in case and 'undefined' not in case
            assert './sessions/gemini-test-low.json' in case
            pinned = gallery.CONTENT / imported['slug'] / 'session.json'
            pinned.write_text(raw + '\n')
            try:
                gallery.load_catalog()
                raise AssertionError('Accepted modified local session snapshot')
            except ValueError:
                pass
        finally:
            gallery.CONTENT, gallery.read_url = original, fetch

    if gallery.CONTENT.exists():
        catalog = gallery.load_catalog()
        assert len(catalog) > 0
        with TemporaryDirectory() as directory:
            original = gallery.CONTENT
            try:
                gallery.CONTENT = Path(directory)
                shutil.copytree(original / catalog[0]["slug"], gallery.CONTENT / catalog[0]["slug"])
                (gallery.CONTENT / "pending").mkdir()
                (gallery.CONTENT / "pending/.DS_Store").touch()
                assert len(gallery.load_catalog()) == 1
            finally:
                gallery.CONTENT = original
        failures = [run for run in catalog if run.get('outcome') == 'no_artwork']
        legacy_failures = {'claude-opus-5.5-max', 'claude-sonnet-5.5-max'}
        assert legacy_failures <= {run['slug'] for run in failures}
        for run in catalog:
            if run.get('outcome') == 'no_artwork':
                assert 'metrics' not in run and all(level in gallery.EFFORTS for level in run['reasoning'])
                gallery.check_source(gallery.CONTENT / run['slug'], run)
                assert gallery.import_run(gallery.CONTENT / run['slug']).startswith('Kept ')
                assert gallery.import_run(gallery.CONTENT / run['slug'], refresh=True).startswith('Kept ')
                continue
            metrics = run["metrics"]
            assert metrics["duration_seconds"] >= 0
            assert metrics["tool_calls"] == sum(metrics["tool_breakdown"].values())
            assert metrics["cost_usd"] is None or metrics["cost_usd"] > 0
            gallery.check_source(gallery.CONTENT / run['slug'], run)
            assert "<" not in run["slug"]
        icons = gallery.ROOT / "src/assets/vendors"
        for icon in icons.glob("*.svg"):
            gallery.check_svg(icon.read_bytes())
        gallery.build()
        page = (gallery.ROOT / "dist/index.html").read_text()
        makers = {run["vendor"] for run in catalog}
        assert page.count('class="vendor-logo"') == sum((icons / (re.sub(r"[^a-z0-9]", "", name.lower()) + ".svg")).is_file() for name in makers)
        assert page.count('class="vendor-logo" aria-hidden="true" focusable="false"') == page.count('class="vendor-logo"')
        assert 'data-vendor="OpenAI" aria-pressed="false"><svg' in page
        models = gallery.group_models(catalog)
        assert len(models) == len({(run['vendor'], run['name']) for run in catalog})
        assert len(re.findall(r'<article class="card[^\"]*" data-model=', page)) == len(models)
        assert all(len({(run['vendor'], run['name']) for run in group}) == 1 for group in models)
        deepseek = {group[0]['name']: {run['slug'] for run in group}
                    for group in models if group[0]['vendor'] == 'DeepSeek'}
        assert deepseek == {
            'DeepSeek V4 Flash 0731': {'deepseek-v4-flash-0731-max'},
            'DeepSeek V4.1 Flash 0910': {f'deepseek-v4.1-flash-{level}' for level in ('off', 'low', 'high', 'max')},
            'DeepSeek V4.1 Flash 1017': {f'deepseek-v4.1-flash-1017-{level}' for level in ('off', 'low', 'high', 'max')},
        }
        assert 'DeepSeek V4.1 Flash 0910</a>' in page
        aliases = [dict(catalog[0], name='Same model', model_ids=['native/id']),
                   dict(catalog[0], name='Same model', model_ids=['gateway/id']),
                   dict(catalog[0], name='Other variant')]
        assert [len(group) for group in gallery.group_models(aliases)] == [2, 1]
        failure = next(run for run in failures if run['slug'] in legacy_failures)
        artwork = next(run for run in catalog if run['slug'] == failure['failure']['related_slug'])
        assert f'data-slug="{artwork["slug"]}"' in gallery.card_html([failure, artwork])
        failure_only = gallery.card_html([failure])
        assert 'class="card failure-card"' in failure_only and '<iframe' not in failure_only
        assert 'No SVG delivered' in failure_only and failure['failure']['status'] in failure_only and 'disabled hidden' in failure_only
        assert 'level-status' not in failure_only
        escaped = gallery.card_html([dict(artwork, name='<script>unsafe</script>')])
        assert '<script>unsafe</script>' not in escaped and '&lt;script&gt;unsafe&lt;/script&gt;' in escaped
        for group in models:
            html = gallery.card_html(group)
            assert all(f'data-card-run="{run["slug"]}"' in html for run in group)
            assert html.count('aria-pressed="true"') == 1 and 'aria-current=' not in html
            assert 'type="button" class="level-link"' in html
            if any(run.get('outcome') != 'no_artwork' for run in group):
                assert 'class="card failure-card"' not in html
            assert all('No SVG delivered' not in button for button in re.findall(r'<button[^>]*data-card-run=.*?</button>', html))
            assert 'Read failure notes' not in html and 'level-status' not in html
        assert 'https://unpkg.com' not in page
        assert not re.search(r'CPA|cliproxyapi|opencode-go', page)
        public = json.loads(re.search(r'<script type="application/json" id="catalog-data">(.*?)</script>', page, re.S)[1])
        local_runs = [run for run in public if run['source'].get('kind') == 'local']
        for run in local_runs:
            for extension in ('json', 'html'):
                exported = gallery.ROOT / 'dist/sessions' / (run['slug'] + '.' + extension)
                assert exported.read_bytes() == (gallery.CONTENT / run['slug'] / ('session.' + extension)).read_bytes()
            assert not run['source']['share_url'].startswith('https://')
            if run.get('response_model_ids'):
                assert run['response_model_ids'] == ['deepseek-v4-flash']
        for run in public:
            assert 'providers' not in run
            if run.get('outcome') == 'no_artwork':
                assert 'metrics' not in run and run['price']['basis'] in ('official', 'unknown')
                gallery.check_source(gallery.CONTENT / run['slug'], run)
                case = gallery.ROOT / 'dist/cases' / run['slug'] / 'index.html'
                assert case.is_file()
                case_html = case.read_text()
                assert '<iframe' not in case_html and 'download=' not in case_html
                assert 'Cost estimate · USD' in case_html and '价格估算 · USD' in case_html
                assert gallery.format_price(run['price']['amount_usd']) in case_html
                assert 'Official estimate' not in case_html and 'Actual cost' not in case_html
                related = next((item for item in catalog if item['slug'] == run['failure'].get('related_slug')), None)
                assert (related['slug'] in case_html) if related else 'case-related' not in case_html
                assert f'data-level="{run["reasoning"][0]}"' in case_html
                assert 'lang="zh"' in case_html and 'lang="en"' in case_html
                assert not re.search(r'CPA|cliproxyapi|gpt\.ge|/Users/|session_id|file://', case_html)
                assert not (gallery.ROOT / 'dist/artwork' / (run['slug'] + '.svg')).exists()
                unsafe = deepcopy(run)
                unsafe['failure']['summary']['en'] = '<script>alert(1)</script>'
                assert '&lt;script&gt;' in gallery.failure_html(unsafe, related)
                unsafe['price']['rates_per_million']['input'] = '<script>bad quote</script>'
                assert '$&lt;script&gt;bad quote&lt;/script&gt;' in gallery.failure_html(unsafe, related)
                assert run['source']['share_url'] in case_html and gallery.snapshot_url(run['source']) in case_html
                if run['slug'] in legacy_failures:
                    assert run['source']['gist_revision'] in case_html
                    assert 'incomplete.max_output_tokens' in case_html and '思考阶段耗尽输出预算' in case_html
                    assert 'Response was truncated before completion' in case_html
                    if run['slug'].startswith('claude-sonnet'):
                        assert '64,000' in case_html and '128,000' not in case_html
                    else:
                        assert '128,000' in case_html
                continue
            original_run = next(item for item in catalog if item['slug'] == run['slug'])
            assert run['metrics'] == original_run['metrics']
            assert run['price']['basis'] in ('official', 'unknown')
            assert run['price']['amount_usd'] is None or run['price']['amount_usd'] >= 0
            if run['price']['amount_usd'] is not None:
                assert run['price']['basis'] == 'official' and run['price']['checked_at'] == '2026-10-24'
        assert 'i18n.js' in page and 'id="language"' in page
        assert 'motion-toggle' not in page and 'Play all animations' not in page
        assert all(control not in page for control in ('data-motion', 'data-restart', 'preview-controls'))
        assert 'preview-action' not in page and 'View performance' not in page
        assert 'id="follow-up"' not in page and 'name="followup"' not in page
        for filename in ('styles.css', 'i18n.js', 'gallery.js'):
            assert f'./{filename}?v={gallery.digest((gallery.ROOT / "src" / filename).read_bytes())[:12]}"' in page
        for failure in failures:
            case_page = (gallery.ROOT / 'dist/cases' / failure['slug'] / 'index.html').read_text()
            for filename in ('styles.css', 'i18n.js', 'failure.js'):
                assert f'./{filename}?v={gallery.digest((gallery.ROOT / "src" / filename).read_bytes())[:12]}"' in case_page
        assert 'value="relevance"' in page
        fuse = gallery.ROOT / 'src/assets/fuse/fuse.min.mjs'
        assert gallery.digest(fuse.read_bytes()) == '5ab524d12492bb233568e9600046e1aaa9623d36ebe689589144f7dc9b1da6f7'
        assert (gallery.ROOT / 'dist/assets/fuse/fuse.min.mjs').read_bytes() == fuse.read_bytes()
        assert (gallery.ROOT / 'dist/assets/fuse/LICENSE').is_file()
        for run in public:
            for level in run['reasoning']:
                assert f'class="effort" data-level="{level}">{level}</span>' in page
        with TemporaryDirectory() as directory:
            original = gallery.CONTENT
            try:
                gallery.CONTENT = Path(directory)
                folder = gallery.CONTENT / failures[0]['slug']
                folder.mkdir()
                broken = deepcopy(failures[0]); broken['metrics'] = {'cost_usd': 0}
                (folder / 'run.json').write_text(json.dumps(broken))
                try:
                    gallery.load_catalog()
                    raise AssertionError('Accepted fabricated failure metrics')
                except ValueError:
                    pass
            finally:
                gallery.CONTENT = original
        for slug in ('claude-sonnet-5.5-xhigh', 'claude-opus-5.5-xhigh', 'claude-fable-5.1-xhigh', 'claude-fable-5.1-max'):
            run = next(item for item in catalog if item['slug'] == slug)
            svg = gallery.CONTENT / slug / 'artwork.svg'
            assert gallery.digest(svg.read_bytes()) == run['source']['artwork_sha256']
            assert run['vendor'] == 'Anthropic'
        print(f"PASS · metric semantics, active branches, SVG safety, local logos, {len(catalog) - len(failures)} artworks + {len(failures)} failure cases")
    else:
        print("PASS · metric semantics, active branches, SVG safety")


if __name__ == "__main__":
    check()
