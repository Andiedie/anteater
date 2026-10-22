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

The collection has **one card per model**, grouped by its curated maker and full display name, not by provider-specific model IDs. Versions and variants stay separate. Every recorded thinking control remains reachable on the card; controls are not inferred from absent records. Failure reasons appear in the selected preview, never beside level chips in the list, detail navigation, or level overview. Initially, with no level filter, the card previews the latest recorded artwork; a global level filter selects that exact control or hides models without it. Card-level choices persist within the page across search, sorting, and language changes; **Clear filters** resets them. Choosing a level that conflicts with the global level filter clears that filter. Sort operations use the displayed individual record, never a model average or a minimum across levels; switching a card level alone keeps its position until the next filter/sort operation. Maker/result counts refer to models; the summary counts models and all run records, without a separate failure count.

Click a card's level button to switch its preview, metrics, exact-run links, and comparison checkbox **in the list**, without opening details. Click the image or model name to open the currently displayed run. The model detail's level buttons and previous/next controls stay within that model, including failed levels; switching replaces the current run URL so one close returns to the list. Existing `?run=<slug>`, `?compare=<slugs>`, and standalone failure-page links remain valid. **Compare levels** directly compares two artwork records; models with more artwork open an in-model overview and a 2–4-record picker. This picker preserves the cross-model tray until a comparison is committed. **Add to compare** adds only the card's currently previewed record to that tray. Failed levels remain readable but cannot enter artwork comparisons. Budget rows show the recorded per-request output limit (including reasoning), or `—` when unknown.

Artwork is still by default. Mouse hover or keyboard focus plays a preview; leaving pauses it. Hover adds no label or overlay over the SVG. Opening a performance starts playback immediately, including on touch devices. Detail and 2–4-way comparison dialogs have no play, pause, or restart buttons; visible comparison SVGs start together. Reduced-motion preferences disable automatic playback. Offscreen previews and hidden browser tabs pause every nested SVG clock and CSS animation; original artwork files stay unchanged. Thinking chips keep their native values (`max`, `xhigh`, etc.) and use distinct colors.

With the preview running, `node tests/browser-smoke.mjs` checks model aggregation and aliases, in-card switching and selected-state styling, preserved card choices/comparison records, native select spacing and GitHub navigation, exact-level filters, in-model level navigation and keyboard focus, two-level direct comparisons, local 2–4-level selection and its return path, inline/standalone failures and their evidence boundaries, old links/reloads, budget differences, automatic languages, live language switching, logos, comparison-tray row alignment, control-free autoplay and reduced-motion behavior, hover/playback, paused-road pixel stability, raw colored reasoning chips, fuzzy/token search and sorting, preview failures, and both-language gallery/picker/tray/comparison layouts in a temporary headless Chrome profile. This optional check needs Node 22+ and Chrome; use `CHROME_BIN` for another Chrome/Chromium executable or pass a different preview URL as the first argument.

## Add a performance

Before running or selecting a new test, follow the [test execution, acceptance, and intervention protocol](docs/testing-protocol.md). A valid SVG from an interrupted session is not a normally completed test.

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

For a local session that must not be uploaded, replace `share.txt` with the original Pi `session.html` export and its `session.json` snapshot (header, entries, selected leaf, and system prompt). The importer checks that they agree, requires a normally stopped selected branch for artwork imports, and pins both files by SHA-256. No share or network request is made. Details link to the local HTML conversation and JSON snapshot under `sessions/`.

**Local exports are copied into the built site in full.** They may contain local paths and raw invocation metadata even though gallery details omit invocation channels. Review them for secrets and privacy before import; do not commit, push, or deploy local-only material without separate publication approval.

Existing, unchanged runs are not fetched again. Use `--refresh` to deliberately update the snapshots. The `name` and `vendor` fields in an existing `run.json` are preserved so model aliases and new makers can be corrected without changing frontend code. Audited `response_model_ids` are also preserved when the local session snapshot is unchanged.

Maker logos are local SVGs in `src/assets/vendors/`; filenames are lowercase maker names without punctuation, such as `zai.svg`. Logo sources and licenses are recorded in [NOTICE.md](src/assets/vendors/NOTICE.md).

For approved publication, commit each run's source files together. `run.json` pins the Gist revision or local export hashes, plus the artwork hash; builds do not access the network. SVGs must have a viewBox, be under 2 MB, and contain no scripts, event handlers, external resources, or foreign HTML. The importer rejects unsafe SVGs rather than rewriting model output.

## Tests without an SVG

Unsuccessful tests stay searchable and their level buttons remain available. Selecting one in the list shows **No SVG delivered** and its specific reason (such as **Output truncated**) in the preview, without fabricated artwork or success metrics. Level buttons show only the reasoning level, both on cards and inside details. Opening the preview reveals the evidence inline; **Read failure notes** opens the standalone bilingual page at `cases/<slug>/`. Failures cannot enter artwork comparisons, and unavailable comparison actions are hidden on list cards. A standalone page links to another delivered level of the same model when one exists. Placeholder surfaces use theme colors independently of the light artwork stage; authored SVGs are never recolored. Builds add content hashes to CSS/JS URLs on both gallery and case pages, so a refreshed page cannot reuse stale UI assets. Browser checks cover direct failure links and switching from delivered artwork into a failure in both themes.

A failure directory contains `run.json`, with `outcome: "no_artwork"` and a `failure` object: English/Chinese `summary`, `explanation`, and `limitation`, labeled `facts`, HTTPS `references`, and an optional `related_slug` pointing to delivered artwork of the same model. A published session can be attached with `share.txt` and a `source` containing its `share_url`, `gist_id`, and pinned `gist_revision`; the page links to both the conversation and snapshot. Local-only reports instead attach matching `session.html` / `session.json` files with `source.kind: "local"`, canonical local URLs, their SHA-256 hashes, and the session ID. Failure reasons distinguish output exhaustion, invalid XML, upstream errors, and harness failures; a harness fault is not a model-capability verdict. `date` is the **report date**, not an invented request timestamp. The importer leaves these entries intact. Builds never invent success metrics for them. A price estimate can be calculated from separately reviewed, complete token usage pinned to the source snapshot; output-only evidence is insufficient. If the same test later delivers an SVG, add it and `share.txt`, then import to replace the failure entry with a checked session snapshot.

The Claude max pages describe the two sessions supplied by the tester on 2026-09-30, checked against their local records and public Gist snapshots. Both contain only thinking, no text/tool calls, and `length / incomplete.max_output_tokens`: Opus reports **128,000 output tokens**, Sonnet **64,000**. This supports thinking exhausting the output budget before delivering an SVG; it does not establish an internal infinite loop or native reasoning-token breakdown. Do not apply Opus's output figure to Sonnet or treat normalized usage as an actual bill. The earlier handoff discussed additional Opus attempts; they are not folded into these single-session pages. No model requests were rerun.

## Metric conventions

- Only the exported session's selected branch is counted. Follow-up prompts and recorded errors are marked, not hidden.
- Total time spans the first test prompt to the last assistant response; it includes human waiting. Request time sums recorded request intervals.
- Average output TPS is reported output divided by request time, including first-token latency and reasoning. It is not a decode-speed benchmark.
- Token fields follow the provider's reported usage. Reasoning is not added again to the total; missing fields stay unknown.
- A scoped, consistent benchmark policy can record `output_budget_per_request`; it includes reasoning and applies to each request, not the whole session. Missing or conflicting policy evidence is not guessed.
- Binary thinking controls remain `on` / `off`, separate from effort tiers. When the session's benchmark policy explicitly records `on`, the Pi-internal `medium` used to enable that switch is not presented as a provider effort level.
- Raw Pi cost fields remain in source records, but never feed displayed amounts, sorting, or comparisons. All displayed **Cost estimate · USD** values use the same dated official API price snapshot and are marked **≈**. Missing prices or billing conditions show **Estimate unavailable**, not zero or a fallback estimate.
- Model makers and model IDs are shown; separately audited response model IDs can be retained when an upstream returns a legacy alias. An alias does not independently attest the backend version. Invocation channels are omitted from gallery data, details, and comparisons; attached original sessions retain their original evidence.

## Price estimates

```sh
python3 scripts/gallery.py prices   # Read-only, offline coverage report; does not refresh quotes
python3 tests/test_pricing.py
python3 scripts/gallery.py build
```

`content/pricing.json` is the reviewed **official API price snapshot** (schema 2). All models share its `as_of` date, so comparisons do not mix historical SDK estimates with current prices. `models` stores manufacturer links, explicit model-ID aliases, USD token rates and applicable conditions. Matching requires the exact ID and maker; retired versions are not silently priced as their replacements. Builds never fetch prices or modify source metrics. The previous models.dev/OpenRouter/LiteLLM refresh path has been removed.

Use standard global API prices where published, otherwise the documented overseas/Singapore USD tariff. Public introductory rates and permanent reductions valid on the snapshot date apply; Batch, Flex, priority, contributor, subscriptions and private/channel discounts do not. These are token-cost estimates, excluding storage and tool/search surcharges, not actual bills. **Pricing details** is collapsed by default and contains the source, date, rates and conditions; cards, details, comparisons and failure reports all use the same **Cost estimate · USD** label.

Input and cache usage are separate; thinking is already part of output. Cache writes with TTL-dependent pricing require a reviewed TTL. `runs` holds source-pinned TTL reviews and complete usage for the two local truncated attempts, not per-run copies of model prices. A changed source invalidates that review. Aggregate usage beyond a price tier, missing cache prices/types, mixed-model records and incomplete usage remain unpriced. DeepSeek off-peak rates are used only if the entire recorded interval is provably outside weekday peak windows; ambiguous peak/holiday conditions are not guessed.

To update pricing, review manufacturer pages and billing conditions for **all models** at one new date, edit the snapshot, then run the commands above and browser checks. Do not advance `as_of` or copy an aggregator/SDK quote without reviewing its official source. Keep unresolved entries explicit. The [2026-10-22 price audit](docs/research/official-prices-20261022.md) lists primary sources, coverage gaps and update triggers. Publication of local-only sessions still requires separate approval.

## GitHub Pages

`.github/workflows/pages.yml` tests, builds, and publishes on every push to `main`; `workflow_dispatch` also allows a manual redeploy. Import new material and commit its `run.json`, any `artwork.svg`, and either `share.txt` or the explicitly approved `session.html` / `session.json` exports before pushing. Publishing uses the checked-in price snapshot and does not fetch sessions or model prices in CI.

Pages uses **GitHub Actions**, the custom domain `anteater.ssoo.fun`, and HTTPS enforcement. Cloudflare's `anteater` CNAME points to `andiedie.github.io` with **DNS only** (gray cloud). The custom domain belongs in GitHub's Pages settings; an Actions deployment does not need a repository CNAME file. Keep the DNS record and Pages domain in sync to avoid broken TLS or a dangling-domain takeover.

Check deployment with `gh run list --workflow pages.yml`, then `node tests/browser-smoke.mjs https://anteater.ssoo.fun`. To roll back a faulty release, revert its source commit on `main` and push; the same workflow rebuilds and deploys it.

## Files

- `content/`: original SVGs, share URLs, imported run snapshots, and explicit no-artwork reports.
- `scripts/gallery.py`: import, validation, static build, and local server.
- `scripts/pricing.py`: official-only matching, source-pinned usage checks, and conservative estimates.
- `src/i18n.js`: shared Simplified Chinese translations and browser-language selection.
- `src/failure.html` / `src/failure.js`: standalone bilingual no-artwork pages.
- `src/`: page template, interactions, styles, and logo assets.
- `tests/test_gallery.py`: offline import, corpus, and logo smoke check.
- `tests/test_pricing.py`: offline pricing and failure-path checks.
- `tests/browser-smoke.mjs`: optional real-browser language, playback, and interaction check.
- `dist/`: generated site; ignored by Git.
