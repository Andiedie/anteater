#!/usr/bin/env python3
"""Import Pi shares and build an offline-first static gallery."""

import argparse
import base64
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from html import escape
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import shutil
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

import pricing

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
PRICES = CONTENT / "pricing.json"
PROMPT = "Generate an animated SVG of an anteater riding a unicycle while juggling bottles."
EFFORTS = ("off", "minimal", "low", "medium", "high", "xhigh", "max")
VENDORS = ("OpenAI", "Anthropic", "Google", "DeepSeek", "xAI", "Z.ai", "Tencent", "Xiaomi", "Meta", "Other")
SHARE_PATTERN = re.compile(r"https://pi\.dev/session/#([a-f0-9]{32})")


def digest(data):
    return sha256(data).hexdigest()


def check_svg(data):
    if len(data) > 2_000_000 or re.search(rb"<!\s*(DOCTYPE|ENTITY)|<\?xml-stylesheet", data, re.I):
        raise ValueError("SVG must be under 2 MB and cannot declare entities or a doctype")
    svg = ET.fromstring(data)
    if svg.tag != "{http://www.w3.org/2000/svg}svg" or not svg.get("viewBox"):
        raise ValueError("Expected an SVG document with a viewBox")
    forbidden = {"script", "foreignObject", "iframe", "object", "embed", "audio", "video"}
    for node in svg.iter():
        tag = node.tag.rsplit("}", 1)[-1]
        if tag in forbidden:
            raise ValueError(f"Unsafe SVG element: {tag}")
        for key, value in node.attrib.items():
            attr = key.rsplit("}", 1)[-1].lower()
            if attr.startswith("on") or (attr == "href" and value and not value.startswith("#")):
                raise ValueError(f"Unsafe SVG attribute: {attr}")
            if attr == "attributename" and (value.lower().startswith("on") or "href" in value.lower()):
                raise ValueError("SVG cannot animate links or event handlers")
        css = " ".join(node.attrib.values()) + (node.text or "" if tag == "style" else "")
        if "\\" in css or re.search(r"@import|expression\s*\(", css, re.I):
            raise ValueError("SVG cannot import CSS or execute expressions")
        for url in re.findall(r"url\s*\((.*?)\)", css, re.I | re.S):
            if not url.strip().strip("\"'").startswith("#"):
                raise ValueError("SVG cannot load external resources")
    return svg


def timestamp(value):
    if isinstance(value, (float, int)):
        return value / 1000
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def active_entries(session):
    entries = {entry["id"]: entry for entry in session["entries"]}
    leaf = session.get("leafId")
    path, visited = [], set()
    while leaf:
        if leaf in visited or leaf not in entries:
            raise ValueError("Broken or cyclic session branch")
        visited.add(leaf)
        entry = entries[leaf]
        path.append(entry)
        leaf = entry.get("parentId")
    if not path:
        raise ValueError("Session has no selected branch")
    return list(reversed(path))


def message_text(message):
    content = message.get("content", [])
    if isinstance(content, str):
        return content
    return "\n".join(item.get("text", "") for item in content if item.get("type") == "text")


def summarize(session):
    path = active_entries(session)
    users = [e for e in path if e.get("message", {}).get("role") == "user"]
    if not users or message_text(users[0]["message"]).strip() != PROMPT:
        raise ValueError("First user message does not match the anteater test prompt")
    start = path.index(users[0])
    assistants = [e for e in path[start:] if e.get("message", {}).get("role") == "assistant"]
    if not assistants:
        raise ValueError("Session has no assistant response")
    models, providers, efforts = [], [], []
    effort = None
    for entry in path:
        if entry["type"] == "thinking_level_change":
            effort = entry.get("thinkingLevel")
        msg = entry.get("message", {})
        if msg.get("role") == "assistant":
            for values, value in ((models, msg.get("model")), (providers, msg.get("provider")),
                                  (efforts, msg.get("thinkingLevel") or effort)):
                if value and value not in values:
                    values.append(value)
    numeric_fields = ("input", "output", "cacheRead", "cacheWrite", "reasoning", "totalTokens")
    totals = {key: 0 for key in numeric_fields}
    present = set()
    tools = Counter()
    request_seconds = 0
    timed = True
    costs = []
    errors = 0
    for entry in assistants:
        msg = entry["message"]
        usage = msg.get("usage", {})
        for key in numeric_fields:
            if isinstance(usage.get(key), (float, int)):
                totals[key] += usage[key]
                present.add(key)
        cost = usage.get("cost", {}).get("total")
        if isinstance(cost, (float, int)):
            costs.append(cost)
        for item in msg.get("content", []):
            if item.get("type") == "toolCall":
                tools[item["name"]] += 1
        errors += msg.get("stopReason") in ("error", "aborted")
        if msg.get("timestamp") is None:
            timed = False
        else:
            request_seconds += max(0, timestamp(entry["timestamp"]) - timestamp(msg["timestamp"]))
    # The export's top-level tools may reflect the later sharing session, not this run.
    available_tools = []
    for entry in path:
        msg = entry.get("message", {})
        if msg.get("role") == "system":
            for tool in msg.get("toolsAdded", []):
                if tool["name"] not in available_tools:
                    available_tools.append(tool["name"])
    if not available_tools:
        tool_section = re.search(r"<tools>(.*?)</tools>", session.get("systemPrompt", ""), re.S)
        available_tools = re.findall(r"^- ([\w_]+):", tool_section[1], re.M) if tool_section else []
    recorded_cost = round(sum(costs), 10) if costs else None
    duration = max(0, timestamp(assistants[-1]["timestamp"]) - timestamp(users[0]["timestamp"]))
    return {
        "date": users[0]["timestamp"],
        "model_ids": models,
        "providers": providers,
        "reasoning": efforts or ["unknown"],
        "available_tools": available_tools,
        "follow_up_count": len(users) - 1,
        "metrics": {
            "duration_seconds": round(duration, 3),
            "request_seconds": round(request_seconds, 3) if timed else None,
            "average_tps": round(totals["output"] / request_seconds, 2) if timed and request_seconds and "output" in present else None,
            "tool_calls": sum(tools.values()),
            "tool_breakdown": dict(sorted(tools.items())),
            "assistant_turns": len(assistants),
            "errors": errors,
            "tool_errors": sum(bool(e.get("message", {}).get("isError")) for e in path[start:] if e.get("message", {}).get("role") == "toolResult"),
            "tokens": {key: totals[key] if key in present else None for key in numeric_fields},
            "recorded_cost_usd": recorded_cost,
            "cost_usd": recorded_cost if recorded_cost and recorded_cost > 0 else None,
        },
    }


def model_label(slug):
    effort = slug.rsplit("-", 1)[-1]
    stem = slug[:-(len(effort) + 1)] if effort in EFFORTS else slug
    for prefix, vendor, label in (
        ("gpt-", "OpenAI", "GPT-"), ("claude-", "Anthropic", "Claude "),
        ("gemini-", "Google", "Gemini "), ("deepseek-", "DeepSeek", "DeepSeek "),
        ("grok-", "xAI", "Grok "), ("glm-", "Z.ai", "GLM-"),
        ("hy", "Tencent", "Hunyuan "), ("mimo-", "Xiaomi", "MiMo "),
        ("muse-", "Meta", "Muse "),
    ):
        if stem.startswith(prefix):
            suffix = stem[len(prefix):].replace("-", " ")
            return label + suffix.title(), vendor
    return stem.replace("-", " ").title(), "Other"


def read_url(request):
    for attempt in range(3):
        try:
            with urlopen(request, timeout=45) as response:
                return response.read()
        except HTTPError:
            raise
        except (URLError, OSError):
            if attempt == 2:
                raise


def fetch_session(share_url):
    match = SHARE_PATTERN.fullmatch(share_url)
    if not match:
        raise ValueError("Expected a pi.dev/session/#<gist-id> share URL")
    gist_id = match[1]
    request = Request(f"https://api.github.com/gists/{gist_id}", headers={"User-Agent": "anteater-gallery", "Accept": "application/vnd.github+json"})
    gist = json.loads(read_url(request))
    file = gist["files"].get("session.html")
    if not file:
        raise ValueError("Gist has no session.html")
    html = file.get("content")
    if html is None or file.get("truncated"):
        html = read_url(file["raw_url"]).decode("utf-8")
    embedded = re.search(r'<script\b[^>]*\bid=["\']session-data["\'][^>]*>(.*?)</script>', html, re.S)
    if not embedded:
        raise ValueError("Share has no embedded session data")
    payload = embedded[1].strip()
    session = json.loads(payload if payload.startswith("{") else base64.b64decode(payload))
    return session, gist_id, gist["history"][0]["version"]


def import_run(folder, refresh=False):
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", folder.name):
        raise ValueError(f"Unsafe directory name: {folder.name}")
    svgs = list(folder.glob("*.svg"))
    if not svgs and (folder / "run.json").is_file() and json.loads((folder / "run.json").read_text()).get("outcome") == "no_artwork":
        return f"Kept {folder.name} (no-artwork report)"
    if not svgs and not (folder / "share.txt").exists():
        return f"Skipped {folder.name} (no artwork)"
    if len(svgs) != 1 or not (folder / "share.txt").is_file():
        raise ValueError(f"{folder.name}: needs exactly one SVG and share.txt")
    artwork = svgs[0].read_bytes()
    check_svg(artwork)
    share = (folder / "share.txt").read_text().strip()
    if not SHARE_PATTERN.fullmatch(share):
        raise ValueError(f"{folder.name}: invalid share URL")
    target = CONTENT / folder.name
    previous_path = target / "run.json"
    previous = json.loads(previous_path.read_text()) if previous_path.exists() else None
    if not refresh and previous and previous.get("outcome") != "no_artwork" and previous["source"]["share_url"] == share and previous["source"]["artwork_sha256"] == digest(artwork):
        return f"Unchanged {folder.name}"
    session, gist_id, revision = fetch_session(share)
    name, vendor = model_label(folder.name)
    run = {
        "schema_version": 1, "slug": folder.name,
        "name": previous["name"] if previous else name,
        "vendor": previous["vendor"] if previous else vendor,
        **summarize(session),
        "source": {
            "share_url": share, "gist_id": gist_id, "gist_revision": revision,
            "session_id": session["header"]["id"],
            "imported_at": datetime.now(timezone.utc).isoformat(),
            "artwork_sha256": digest(artwork),
        },
    }
    target.mkdir(parents=True, exist_ok=True)
    (target / "artwork.svg").write_bytes(artwork)
    (target / "share.txt").write_text(share + "\n")
    (target / "run.json").write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n")
    return f"Imported {folder.name}"


def load_catalog():
    runs = []
    for folder in sorted(CONTENT.iterdir()):
        if not folder.is_dir() or not any(item for item in folder.iterdir() if not item.name.startswith(".")):
            continue
        run = json.loads((folder / "run.json").read_text())
        if run["schema_version"] != 1 or run["slug"] != folder.name or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", run["slug"]):
            raise ValueError(f"{folder.name}: invalid run metadata")
        timestamp(run["date"])
        if run.get("outcome") == "no_artwork":
            failure = run["failure"]
            if (folder / "artwork.svg").exists() or "metrics" in run:
                raise ValueError(f"{folder.name}: failure cases cannot claim artwork or imported metrics")
            for field in (failure["summary"], failure["explanation"], failure["limitation"], *(fact["label"] for fact in failure["facts"])):
                if any(not isinstance(field.get(lang), str) or not field[lang].strip() for lang in ("en", "zh")):
                    raise ValueError(f"{folder.name}: failure text needs English and Chinese")
            if "source" in run:
                source = run["source"]
                share = (folder / "share.txt").read_text().strip()
                match = SHARE_PATTERN.fullmatch(share)
                if not match or share != source["share_url"] or match[1] != source["gist_id"] or not re.fullmatch(r"[a-f0-9]{40}", source["gist_revision"]):
                    raise ValueError(f"{folder.name}: invalid failure share snapshot")
            if any(not reference["url"].startswith("https://") for reference in failure["references"]):
                raise ValueError(f"{folder.name}: references must use HTTPS")
            runs.append(run)
            continue
        svg = (folder / "artwork.svg").read_bytes()
        check_svg(svg)
        if digest(svg) != run["source"]["artwork_sha256"]:
            raise ValueError(f"{folder.name}: artwork changed; import it again before building")
        share = (folder / "share.txt").read_text().strip()
        if share != run["source"]["share_url"] or not SHARE_PATTERN.fullmatch(share):
            raise ValueError(f"{folder.name}: share link changed; import it again before building")
        runs.append(run)
    if not runs:
        raise ValueError("No imported artwork")
    by_slug = {run["slug"]: run for run in runs}
    for run in runs:
        if run.get("outcome") == "no_artwork":
            related = by_slug.get(run["failure"]["related_slug"])
            if not related or related.get("outcome") == "no_artwork" or related["name"] != run["name"] or related["vendor"] != run["vendor"]:
                raise ValueError(f"{run['slug']}: related artwork must be the same model")
    return sorted(runs, key=lambda run: run["date"], reverse=True)


def format_time(seconds):
    seconds = round(seconds)
    if seconds < 60:
        return f"{seconds}s"
    return f"{seconds // 60}m {seconds % 60:02d}s"


def card_html(run):
    slug, name = escape(run["slug"], quote=True), escape(run["name"])
    if run.get("outcome") == "no_artwork":
        status = escape(run['failure']['status'])
        return f'''<article class="card failure-card" data-slug="{slug}">
  <a class="preview failure-preview" href="./cases/{slug}/" aria-label="Read failure notes for {name}, max reasoning">
    <span class="failure-symbol" aria-hidden="true">∅</span>
    <span class="failure-title" data-i18n="No SVG delivered">No SVG delivered</span>
    <span class="failure-status" data-i18n="{status}">{status}</span>
  </a>
  <div class="card-info"><div class="card-heading"><span class="vendor-name">{escape(run['vendor'])}</span><span class="effort effort-max" data-level="max">max</span></div>
    <h2><a href="./cases/{slug}/">{name}</a></h2>
    <a class="text-button failure-link" href="./cases/{slug}/"><span data-i18n="Read failure notes">Read failure notes</span><span aria-hidden="true">↗</span></a>
  </div>
</article>'''
    metrics = run["metrics"]
    price_info = run.get("price", {"amount_usd": metrics["cost_usd"], "basis": "recorded"})
    cost = price_info["amount_usd"]
    price = ("≈" if price_info["basis"] == "public" else "") + (f"${cost:.3f}" if cost is not None and cost >= 0.001 else (f"${cost:.4f}" if cost is not None else "Unknown"))
    price_label = {"recorded": "Pi · USD", "public": "Public · USD", "unknown": "Cost · USD"}[price_info["basis"]]
    effort = escape(" → ".join(run["reasoning"]))
    chips = ''.join(f'<span class="effort" data-level="{escape(level, quote=True)}">{escape(level)}</span>' for level in run['reasoning'])
    return f'''<article class="card" data-slug="{slug}">
  <button class="preview" data-open="{slug}" aria-label="View {name}, {effort} reasoning">
    <iframe class="artwork-frame" data-src="./artwork/{slug}.svg" title="{name} animated SVG" sandbox="allow-same-origin" tabindex="-1" aria-hidden="true"></iframe>
    <span class="preview-loading" aria-hidden="true" data-i18n="Loading artwork">Loading artwork</span>
  </button>
  <div class="card-info">
    <div class="card-heading"><span class="vendor-name">{escape(run['vendor'])}</span><span class="effort-chips">{chips}</span></div>
    <h2><a href="?run={slug}" data-open="{slug}">{name}</a></h2>
    <div class="card-bottom"><dl class="card-stats">
      <div><dt data-i18n="Time">Time</dt><dd data-time>{format_time(metrics['duration_seconds'])}</dd></div>
      <div><dt data-i18n="Tools">Tools</dt><dd>{metrics['tool_calls']}</dd></div>
      <div><dt data-i18n="{price_label}">{price_label}</dt><dd data-price>{price}</dd></div>
    </dl><label class="compare-check"><input type="checkbox" data-compare="{slug}" aria-label="Compare {name}, {effort} reasoning"><span data-i18n="Compare">Compare</span></label></div>
  </div>
</article>'''


def failure_html(run, related):
    failure = run["failure"]
    copies = []
    for lang in ("en", "zh"):
        facts = ''.join(f'<div><dt>{escape(fact["label"][lang])}</dt><dd>{escape(str(fact["value"]))}</dd></div>' for fact in failure["facts"])
        copies.append(f'''<div class="case-copy" lang="{lang}">
  <p class="case-summary">{escape(failure['summary'][lang])}</p>
  {f'<dl class="case-facts">{facts}</dl>' if facts else ''}
  <p>{escape(failure['explanation'][lang])}</p>
  <p class="case-limitation">{escape(failure['limitation'][lang])}</p>
</div>''')
    references = ''.join(f'<a href="{escape(reference["url"], quote=True)}" target="_blank" rel="noopener noreferrer">{escape(reference["label"])} ↗</a>' for reference in failure["references"])
    values = {
        "NAME": escape(run["name"]), "SLUG": escape(run["slug"], quote=True), "DATE": escape(run["date"]),
        "VENDOR": escape(run["vendor"]), "STATUS": escape(failure["status"], quote=True), "COPY": '\n'.join(copies),
        "REFERENCES": f'<details class="case-references"><summary data-i18n="References">References</summary><div class="source-links">{references}</div></details>' if references else '',
        "RELATED": escape(related["slug"], quote=True), "LEVEL": escape(' → '.join(related["reasoning"])),
        "SOURCE_LINKS": f'''<div class="source-links case-sources"><a href="{escape(run['source']['share_url'], quote=True)}" target="_blank" rel="noopener noreferrer" data-i18n="Pi conversation ↗">Pi conversation ↗</a><a href="https://gist.github.com/{escape(run['source']['gist_id'])}/{escape(run['source']['gist_revision'])}" target="_blank" rel="noopener noreferrer" data-i18n="Source snapshot ↗">Source snapshot ↗</a></div>''' if 'source' in run else '',
    }
    page = (ROOT / "src/failure.html").read_text()
    for key, value in values.items():
        page = page.replace('{{' + key + '}}', value)
    return page


def build():
    runs = load_catalog()
    snapshot = json.loads(PRICES.read_text()) if PRICES.exists() else {}
    for run in runs:
        if run.get("outcome") != "no_artwork":
            run["price"] = pricing.display_price(run, snapshot)
        run.pop("providers", None)  # Invocation channels are not part of the public gallery.
    counts = Counter(run["vendor"] for run in runs)
    vendors = sorted(counts, key=lambda name: VENDORS.index(name) if name in VENDORS else len(VENDORS))
    tabs = '<button class="vendor-tab active" data-vendor="all" aria-pressed="true"><span class="vendor-label" data-i18n="All models">All models</span><span>' + str(len(runs)) + '</span></button>'
    for vendor in vendors:
        icon_name = re.sub(r"[^a-z0-9]", "", vendor.lower())
        icon_path = ROOT / "src/assets/vendors" / (icon_name + ".svg")
        icon = ""
        if icon_path.is_file():
            check_svg(icon_path.read_bytes())
            icon = icon_path.read_text().replace('<svg ', '<svg class="vendor-logo" aria-hidden="true" focusable="false" ', 1)
        tabs += f'<button class="vendor-tab" data-vendor="{escape(vendor, quote=True)}" aria-pressed="false">{icon}{escape(vendor)}<span>{counts[vendor]}</span></button>'
    template = (ROOT / "src/index.html").read_text()
    values = {
        "CARDS": "\n".join(card_html(run) for run in runs),
        "VENDORS": tabs, "COUNT": str(len(runs)), "FAMILIES": str(len(vendors)),
        "CATALOG": json.dumps(runs, ensure_ascii=False, separators=(",", ":"), allow_nan=False).replace("<", "\\u003c"),
        "UPDATED": datetime.fromisoformat(runs[0]["date"].replace("Z", "+00:00")).strftime("%B %Y"),
    }
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    (dist / "index.html").write_text(template)
    for filename in ("i18n.js", "gallery.js", "failure.js", "styles.css"):
        shutil.copy2(ROOT / "src" / filename, dist / filename)
    shutil.copytree(ROOT / "src/assets", dist / "assets", dirs_exist_ok=True)
    shutil.rmtree(dist / "artwork", ignore_errors=True)
    (dist / "artwork").mkdir()
    shutil.rmtree(dist / "cases", ignore_errors=True)
    by_slug = {run["slug"]: run for run in runs}
    for run in runs:
        if run.get("outcome") == "no_artwork":
            case = dist / "cases" / run["slug"]
            case.mkdir(parents=True)
            (case / "index.html").write_text(failure_html(run, by_slug[run["failure"]["related_slug"]]))
        else:
            shutil.copy2(CONTENT / run["slug"] / "artwork.svg", dist / "artwork" / (run["slug"] + ".svg"))
    (dist / ".nojekyll").touch()
    failures = sum(run.get("outcome") == "no_artwork" for run in runs)
    print(f"Built {len(runs) - failures} artworks + {failures} failure cases → {dist}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    importer = commands.add_parser("import", help="Import folders containing an SVG and share.txt")
    importer.add_argument("source", nargs="?", type=Path, default=CONTENT)
    importer.add_argument("--refresh", action="store_true", help="Re-fetch already imported shares")
    commands.add_parser("prices", help="Refresh public price snapshots for runs without recorded costs")
    commands.add_parser("build", help="Build static dist/ without network access")
    server = commands.add_parser("serve", help="Build and serve a local preview")
    server.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.command == "import":
        folders = sorted(p for p in args.source.expanduser().iterdir() if p.is_dir())
        with ThreadPoolExecutor(max_workers=2) as workers:
            for result in workers.map(lambda folder: import_run(folder, args.refresh), folders):
                print(result)
    elif args.command == "prices":
        pricing.refresh([run for run in load_catalog() if run.get("outcome") != "no_artwork"], PRICES, read_url)
    elif args.command == "build":
        build()
    else:
        build()
        from functools import partial
        handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT / "dist"))
        print(f"Preview → http://localhost:{args.port}", flush=True)
        with ThreadingHTTPServer(("127.0.0.1", args.port), handler) as httpd:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                pass


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, ET.ParseError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
