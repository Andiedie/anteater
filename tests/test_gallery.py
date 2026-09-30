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
        assert {run['slug'] for run in failures} == {'claude-opus-5.5-max', 'claude-sonnet-5.5-max'}
        for run in catalog:
            if run.get('outcome') == 'no_artwork':
                assert 'metrics' not in run and run['reasoning'] == ['max']
                assert gallery.SHARE_PATTERN.fullmatch(run['source']['share_url'])
                assert gallery.import_run(gallery.CONTENT / run['slug']).startswith('Kept ')
                assert gallery.import_run(gallery.CONTENT / run['slug'], refresh=True).startswith('Kept ')
                continue
            metrics = run["metrics"]
            assert metrics["duration_seconds"] >= 0
            assert metrics["tool_calls"] == sum(metrics["tool_breakdown"].values())
            assert metrics["cost_usd"] is None or metrics["cost_usd"] > 0
            assert gallery.SHARE_PATTERN.fullmatch(run["source"]["share_url"])
            assert "<" not in run["slug"]
        icons = gallery.ROOT / "src/assets/vendors"
        for icon in icons.glob("*.svg"):
            gallery.check_svg(icon.read_bytes())
        gallery.build()
        page = (gallery.ROOT / "dist/index.html").read_text()
        makers = {run["vendor"] for run in catalog}
        assert page.count('class="vendor-logo"') == sum((icons / (name.lower().replace(".", "") + ".svg")).is_file() for name in makers)
        assert page.count('class="vendor-logo" aria-hidden="true" focusable="false"') == page.count('class="vendor-logo"')
        assert 'data-vendor="OpenAI" aria-pressed="false"><svg' in page
        assert 'https://unpkg.com' not in page
        assert not re.search(r'CPA|cliproxyapi|opencode-go', page)
        public = json.loads(re.search(r'<script type="application/json" id="catalog-data">(.*?)</script>', page, re.S)[1])
        for run in public:
            assert 'providers' not in run
            if run.get('outcome') == 'no_artwork':
                assert 'price' not in run and 'metrics' not in run
                assert gallery.SHARE_PATTERN.fullmatch(run['source']['share_url'])
                case = gallery.ROOT / 'dist/cases' / run['slug'] / 'index.html'
                assert case.is_file()
                case_html = case.read_text()
                assert '<iframe' not in case_html and 'download=' not in case_html
                assert run['failure']['related_slug'] in case_html
                assert 'lang="zh"' in case_html and 'lang="en"' in case_html
                assert not re.search(r'CPA|cliproxyapi|gpt\.ge|/Users/|session_id|file://', case_html)
                assert not (gallery.ROOT / 'dist/artwork' / (run['slug'] + '.svg')).exists()
                unsafe = deepcopy(run)
                unsafe['failure']['summary']['en'] = '<script>alert(1)</script>'
                assert '&lt;script&gt;' in gallery.failure_html(unsafe, next(item for item in catalog if item['slug'] == run['failure']['related_slug']))
                assert run['source']['share_url'] in case_html and run['source']['gist_revision'] in case_html
                assert 'incomplete.max_output_tokens' in case_html and '思考阶段耗尽输出预算' in case_html
                assert 'Response was truncated before completion' in case_html
                if run['slug'].startswith('claude-sonnet'):
                    assert '64,000' in case_html and '128,000' not in case_html
                else:
                    assert '128,000' in case_html
                continue
            if run['metrics']['cost_usd'] is not None:
                assert run['price']['amount_usd'] == run['metrics']['cost_usd']
            assert run['price']['amount_usd'] is None or run['price']['amount_usd'] >= 0
        assert 'i18n.js' in page and 'id="language"' in page
        assert 'motion-toggle' not in page and 'Play all animations' not in page
        assert all(control not in page for control in ('data-motion', 'data-restart', 'preview-controls'))
        assert 'preview-action' not in page and 'View performance' not in page
        assert 'id="follow-up"' not in page and 'name="followup"' not in page
        assert '<script src="./gallery.js" type="module">' in page
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
