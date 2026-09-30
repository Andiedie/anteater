<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./src/assets/anteater-logo-dark.svg">
    <img src="./src/assets/anteater-logo.svg" alt="Anteater logo" width="192" height="192">
  </picture>
</p>

<h1 align="center">Anteater</h1>

An animated SVG gallery. One prompt, different models, and the recorded numbers behind each performance.

**Live site: [anteater.ssoo.fun](https://anteater.ssoo.fun)**

## Local preview

Python 3.10+ is the only build dependency. The frontend uses native HTML, CSS, and JavaScript.

```sh
python3 tests/test_gallery.py
python3 scripts/gallery.py serve
```

Open **http://localhost:8765**. After editing source files, restart the server or run `python3 scripts/gallery.py build` and refresh the page. Use `--port 8766` to choose another port.

The interface automatically chooses Simplified Chinese or English from the browser's preferred languages (English fallback). The language selector can override this choice or return to automatic selection; overrides are stored locally when browser storage is available. Model identifiers, the exact English test prompt, and authored SVGs are not translated.

Search uses the full Fuse.js **7.5.0** ESM build, vendored unchanged from the [official npm archive](https://registry.npmjs.org/fuse.js/-/fuse.js-7.5.0.tgz) in `src/assets/fuse/fuse.min.mjs` (about 9 KB gzip), with its [Apache-2.0 license](src/assets/fuse/LICENSE). No CDN or npm build step is needed. Names, makers, slugs, and model IDs are indexed with normalized punctuation, case, and spacing; token search requires all query words and tolerates typos. Queries such as `gpt6`, `g pt6`, `gptt6`, and `luna OpenAI GPT6` work. Search defaults to **Best match**, with fuzzy alternatives after closer matches; manually chosen sorts remain in effect, and clearing search restores newest-first when relevance was selected. The offline build test verifies the pinned bundle checksum; update it deliberately when upgrading Fuse.js.

Artwork is still by default. Mouse hover or keyboard focus plays a preview; leaving pauses it. Hover adds no label or overlay over the SVG. Opening a performance starts playback immediately, including on touch devices. Detail and 2–4-way comparison dialogs have no play, pause, or restart buttons; visible comparison SVGs start together. Reduced-motion preferences disable automatic playback. Offscreen previews and hidden browser tabs pause every nested SVG clock and CSS animation; original artwork files stay unchanged. Thinking chips keep their native values (`max`, `xhigh`, etc.) and use distinct colors.

With the preview running, `node tests/browser-smoke.mjs` checks standalone failure pages, their evidence boundaries and xhigh links, automatic languages, live language switching, logos, comparison-tray row alignment, control-free dialog autoplay and reduced-motion behavior, hover/playback, paused-road pixel stability, raw colored reasoning chips, fuzzy/token search and sorting, filtering, dialogs, 2–4-way comparison URLs/autoplay, preview failures, and both-language gallery/tray/comparison layouts in a temporary headless Chrome profile. This optional check needs Node 22+ and Chrome; use `CHROME_BIN` for another Chrome/Chromium executable or pass a different preview URL as the first argument.

## Add a performance

Create a directory in `content/`, such as `content/gpt-6.1-sol-max/`, containing:

```text
artwork.svg
share.txt       # https://pi.dev/session/#<gist-id>
```

Then run:

```sh
python3 scripts/gallery.py import
python3 tests/test_gallery.py
python3 scripts/gallery.py build
```

The importer generates `run.json` from the public share. It also accepts an external directory containing multiple model folders; each can use any SVG filename:

```sh
python3 scripts/gallery.py import ~/Downloads/personal/anteater
```

Existing, unchanged runs are not fetched again. Use `--refresh` to deliberately update the snapshots. The `name` and `vendor` fields in an existing `run.json` are preserved so model aliases and new makers can be corrected without changing frontend code.

Maker logos are local SVGs in `src/assets/vendors/`; filenames are lowercase maker names without punctuation, such as `zai.svg`. Logo sources and licenses are recorded in [NOTICE.md](src/assets/vendors/NOTICE.md).

Commit each run's three files together. `run.json` pins the Gist revision and the artwork hash; builds do not access the network. SVGs must have a viewBox, be under 2 MB, and contain no scripts, event handlers, external resources, or foreign HTML. The importer rejects unsafe SVGs rather than rewriting model output.

## Tests without an SVG

Unsuccessful tests stay searchable in the gallery, with **No SVG delivered** cards linking to standalone bilingual pages at `cases/<slug>/`. They are counted separately from delivered artwork, have no invented metrics or SVG download, and cannot be selected for artwork comparison. Their pages link to the same model's delivered xhigh result; normal detail navigation skips entries without artwork.

A failure directory contains `run.json`, with `outcome: "no_artwork"` and a `failure` object: English/Chinese `summary`, `explanation`, and `limitation`, labeled `facts`, HTTPS `references`, and a `related_slug` pointing to delivered artwork of the same model. A published session can be attached with `share.txt` and a `source` containing its `share_url`, `gist_id`, and pinned `gist_revision`; the page links to both the conversation and snapshot. `date` is the **report date**, not an invented request timestamp. The importer leaves these entries intact, and builds/pricing refreshes never infer token use, runtime, or cost for them. If the same test later delivers an SVG, add it and `share.txt`, then import to replace the failure entry with a checked session snapshot.

The Claude max pages describe the two sessions supplied by the tester on 2026-09-30, checked against their local records and public Gist snapshots. Both contain only thinking, no text/tool calls, and `length / incomplete.max_output_tokens`: Opus reports **128,000 output tokens**, Sonnet **64,000**. This supports thinking exhausting the output budget before delivering an SVG; it does not establish an internal infinite loop or native reasoning-token breakdown. Do not apply Opus's output figure to Sonnet or treat normalized usage as an actual bill. The earlier handoff discussed additional Opus attempts; they are not folded into these single-session pages. No model requests were rerun.

## Metric conventions

- Only the exported session's selected branch is counted. Follow-up prompts and recorded errors are marked, not hidden.
- Total time spans the first test prompt to the last assistant response; it includes human waiting. Request time sums recorded request intervals.
- Average output TPS is reported output divided by request time, including first-token latency and reasoning. It is not a decode-speed benchmark.
- Token fields follow the provider's reported usage. Reasoning is not added again to the total; missing fields stay unknown.
- Recorded nonzero Pi cost estimates are preserved. Missing/unverified zero costs can be supplemented using public text-token rates, marked **≈** and **Public · USD**. Neither is an actual billing receipt; unresolved prices stay **Unknown**, not free.
- Model makers and model IDs are shown; invocation channels are omitted from page data, details, and comparisons.

## Public prices

```sh
python3 scripts/gallery.py prices
python3 tests/test_pricing.py
python3 scripts/gallery.py build
```

`prices` queries models.dev, OpenRouter, and LiteLLM without API keys and saves a compact snapshot in `content/pricing.json`. Builds use that snapshot offline; original `run.json` metrics are not overwritten. The detail panel shows the reference source, exact catalog model, query date, and input/output/cache rates in USD per million tokens. A price source is a quotation reference, not the model's invocation channel.

Matching uses exact model IDs and maker namespaces, not fuzzy or neighboring model matches. The configured Gemini thinking suffix has an explicit alias in `scripts/pricing.py`. Pi input/cache fields are priced separately; reasoning is already included in output and is not billed twice. Missing cache rates, unrecorded Anthropic cache-write TTLs, mixed-model usage, conditional prices, or aggregate usage exceeding a context tier remain unresolved rather than guessed. Estimates omit search/tool surcharges, discounts, and subscriptions. Failed refreshes do not discard the last usable snapshot.

After adding an unpriced performance, run `prices` and commit the updated snapshot with its material.

## GitHub Pages

`.github/workflows/pages.yml` tests, builds, and publishes on every push to `main`; `workflow_dispatch` also allows a manual redeploy. Import new material and commit its `run.json`, `artwork.svg`, and `share.txt` before pushing. Publishing uses the checked-in price snapshot and does not fetch sessions or model prices in CI.

Pages uses **GitHub Actions**, the custom domain `anteater.ssoo.fun`, and HTTPS enforcement. Cloudflare's `anteater` CNAME points to `andiedie.github.io` with **DNS only** (gray cloud). The custom domain belongs in GitHub's Pages settings; an Actions deployment does not need a repository CNAME file. Keep the DNS record and Pages domain in sync to avoid broken TLS or a dangling-domain takeover.

Check deployment with `gh run list --workflow pages.yml`, then `node tests/browser-smoke.mjs https://anteater.ssoo.fun`. To roll back a faulty release, revert its source commit on `main` and push; the same workflow rebuilds and deploys it.

## Files

- `content/`: original SVGs, share URLs, imported run snapshots, and explicit no-artwork reports.
- `scripts/gallery.py`: import, validation, static build, and local server.
- `scripts/pricing.py`: public price matching, snapshots, and conservative estimates.
- `src/i18n.js`: shared Simplified Chinese translations and browser-language selection.
- `src/failure.html` / `src/failure.js`: standalone bilingual no-artwork pages.
- `src/`: page template, interactions, styles, and logo assets.
- `tests/test_gallery.py`: offline import, corpus, and logo smoke check.
- `tests/test_pricing.py`: offline pricing and failure-path checks.
- `tests/browser-smoke.mjs`: optional real-browser language, playback, and interaction check.
- `dist/`: generated site; ignored by Git.
