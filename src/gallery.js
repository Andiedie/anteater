import Fuse from './assets/fuse/fuse.min.mjs';

const runs = JSON.parse(document.querySelector('#catalog-data').textContent);
const artworkRuns = runs.filter(run => run.outcome !== 'no_artwork');
const normalizeSearch = text => text.normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}\s]/gu, '').trim();
const modelSearch = new Fuse(runs.map(run => ({
  slug: run.slug,
  terms: [...new Set([run.name, run.vendor, run.slug, ...run.model_ids].flatMap(value => {
    const text = normalizeSearch(value);
    return [text, text.replace(/\s+/g, '')];
  }))],
})), {keys: ['terms'], threshold: .35, ignoreLocation: true, ignoreDiacritics: true, useTokenSearch: true, tokenMatch: 'all'});
const bySlug = new Map(runs.map(run => [run.slug, run]));
const cards = new Map([...document.querySelectorAll('.card')].map(card => [card.dataset.slug, card]));
const gallery = document.querySelector('#gallery');
const detailDialog = document.querySelector('#detail-dialog');
const compareDialog = document.querySelector('#compare-dialog');
const search = document.querySelector('#search');
const reasoning = document.querySelector('#reasoning');
const sort = document.querySelector('#sort');
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const selected = new Set();
let modalPlaying = false;
let visibleRuns = runs;
let vendor = 'all';
let toastTimer;
let resultsTimer;
let currentDetail = null;
let currentComparison = '';
let previousQuery = '';

const e = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[char]));
const number = value => value == null ? '—' : new Intl.NumberFormat(locale(), {maximumFractionDigits: 8}).format(value);
const time = seconds => {
  if (seconds == null) return '—';
  const total = Math.round(seconds);
  return total < 60 ? t('{seconds}s', {seconds: total}) : t('{minutes}m {seconds}s', {minutes: Math.floor(total / 60), seconds: String(total % 60).padStart(2, '0')});
};
const money = value => value == null ? t('Unknown') : `$${value.toFixed(value < .001 ? 4 : 3)}`;
const date = value => new Intl.DateTimeFormat(locale(), {dateStyle: 'medium', timeZone: 'UTC'}).format(new Date(value));
const levels = run => run.reasoning.join(' → ');
const effortChips = run => run.reasoning.map(level => `<span class="effort" data-level="${e(level)}">${e(level)}</span>`).join('');
const validComparison = slugs => slugs.length >= 2 && slugs.length <= 4 && new Set(slugs).size === slugs.length && slugs.every(slug => bySlug.has(slug) && bySlug.get(slug).outcome !== 'no_artwork');
const cost = run => run.price?.amount_usd ?? run.metrics?.cost_usd;
const costText = run => (run.price?.basis === 'public' ? '≈' : '') + money(cost(run));
const costLabel = run => ({recorded: 'Pi estimate · USD', public: 'Public estimate · USD'}[run.price?.basis] || 'Estimated cost · USD');
const comparisonNote = 'Individual runs, not normalized benchmarks. Run time includes any follow-up waits; average TPS includes request latency and reasoning. Costs are estimates; public-rate estimates are marked ≈.';

function notify(message) {
  const toast = document.querySelector('#toast');
  toast.dataset.i18n = message;
  toast.textContent = t(message);
  toast.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toast.hidden = true; }, 3000);
}

function changeUrl(values, push = false) {
  const url = new URL(location.href);
  for (const [key, value] of Object.entries(values)) {
    if (!value || value === 'all' || (key === 'sort' && value === 'newest' && !normalizeSearch(url.searchParams.get('q') || ''))) url.searchParams.delete(key);
    else url.searchParams.set(key, value);
  }
  if (url.href !== location.href) history[push ? 'pushState' : 'replaceState'](push ? {galleryOverlay: true} : history.state, '', url);
}
function syncFilterUrl() {
  changeUrl({q: search.value.trim(), vendor, reasoning: reasoning.value, sort: sort.value});
}

function applyFilters(sync = true) {
  const query = normalizeSearch(search.value);
  const ranks = new Map(query ? modelSearch.search(query).map((result, index) => [result.item.slug, index]) : []);
  if (!query && sort.value === 'relevance') sort.value = 'newest';
  sort.querySelector('[value="relevance"]').disabled = !query;
  previousQuery = query;
  const orderedRuns = [...runs];
  const metric = {time: 'duration_seconds', cost: 'cost', tokens: 'tokens', tps: 'average_tps'}[sort.value];
  orderedRuns.sort((a, b) => {
    if (sort.value === 'relevance') return ((ranks.get(a.slug) ?? Infinity) - (ranks.get(b.slug) ?? Infinity)) || b.date.localeCompare(a.date);
    if (sort.value === 'name') return a.name.localeCompare(b.name) || a.slug.localeCompare(b.slug);
    if (!metric) return b.date.localeCompare(a.date);
    const value = run => metric === 'cost' ? cost(run) : metric === 'tokens' ? run.metrics?.tokens.totalTokens : run.metrics?.[metric];
    const av = value(a), bv = value(b);
    if (av == null || bv == null) return av == null ? (bv == null ? 0 : 1) : -1;
    return (sort.value === 'tps' ? bv - av : av - bv) || b.date.localeCompare(a.date);
  });
  visibleRuns = orderedRuns.filter(run => (!query || ranks.has(run.slug)) && (vendor === 'all' || run.vendor === vendor)
    && (reasoning.value === 'all' || run.reasoning.includes(reasoning.value)));
  const visible = new Set(visibleRuns.map(run => run.slug));
  for (const [slug, card] of cards) {
    const hidden = !visible.has(slug), frame = card.querySelector('iframe');
    if (card.hidden !== hidden) {
      card.hidden = hidden;
      if (frame) { observer.unobserve(frame); observer.observe(frame); }
    }
    if (hidden && frame) playFrame(frame, false);
  }
  orderedRuns.forEach((run, index) => {
    const card = cards.get(run.slug), before = gallery.children[index];
    if (before === card) return;
    const frame = card.querySelector('iframe');
    if (frame) observer.unobserve(frame);
    // Native state-preserving moves keep iframe documents and animation positions.
    if (gallery.moveBefore) gallery.moveBefore(card, before || null);
    else { frame?.classList.remove('loaded'); gallery.insertBefore(card, before || null); }
    if (frame) observer.observe(frame);
  });
  document.querySelector('#visible-count').textContent = number(visibleRuns.length);
  document.querySelector('#empty-state').hidden = visibleRuns.length !== 0;
  document.querySelector('#filter-feedback').hidden = !(query || vendor !== 'all' || reasoning.value !== 'all');
  document.querySelector('#filter-description').textContent = t('{shown} of {total} performances', {shown: number(visibleRuns.length), total: number(runs.length)});
  for (const tab of document.querySelectorAll('[data-vendor]')) {
    const active = tab.dataset.vendor === vendor;
    tab.classList.toggle('active', active); tab.setAttribute('aria-pressed', String(active));
  }
  clearTimeout(resultsTimer);
  resultsTimer = setTimeout(() => { document.querySelector('#results-status').textContent = t('{count} performances found', {count: number(visibleRuns.length)}); }, 200);
  if (sync) syncFilterUrl();
}
function readFilters() {
  const params = new URLSearchParams(location.search);
  search.value = params.get('q') || '';
  vendor = runs.some(run => run.vendor === params.get('vendor')) ? params.get('vendor') : 'all';
  for (const [select, key] of [[reasoning, 'reasoning'], [sort, 'sort']]) {
    const value = params.get(key);
    const fallback = key === 'sort' && normalizeSearch(search.value) ? 'relevance' : select.options[0].value;
    select.value = [...select.options].some(option => option.value === value) ? value : fallback;
  }
  applyFilters(false);
}
function resetFilters() {
  search.value = ''; vendor = 'all'; reasoning.value = 'all'; sort.value = 'newest'; applyFilters();
}

function playFrame(frame, play) {
  try {
    const doc = frame.contentDocument, svg = doc?.documentElement;
    if (svg?.localName !== 'svg') return;
    // Nested SVGs have independent SMIL clocks (for example, the moving road).
    for (const clock of doc.querySelectorAll('svg')) {
      if (play) clock.unpauseAnimations?.(); else clock.pauseAnimations?.();
    }
    for (const animation of doc.getAnimations()) { if (play) animation.play(); else animation.pause(); }
    frame.dataset.playing = String(play);
  } catch { /* Preview load failures have their own visible feedback. */ }
}
function restartFrame(frame) {
  const doc = frame.contentDocument;
  if (doc?.documentElement.localName !== 'svg') return;
  for (const clock of doc.querySelectorAll('svg')) clock.setCurrentTime?.(0);
  for (const animation of doc.getAnimations()) animation.currentTime = 0;
}
function refreshPlayback() {
  const inModal = detailDialog.open || compareDialog.open;
  for (const frame of document.querySelectorAll('.artwork-frame')) {
    const modal = frame.closest('dialog'), stage = frame.parentElement;
    const interacting = !reducedMotion.matches && ((stage.dataset.hovered === 'true' && stage.matches(':hover')) || stage.matches(':focus-visible'));
    playFrame(frame, !document.hidden && frame.dataset.visible === 'true'
      && (modal ? modal.open && modalPlaying : !inModal && !frame.closest('.card')?.hidden && interacting));
  }
  for (const control of document.querySelectorAll('[data-motion]')) {
    const plural = control.closest('#compare-dialog');
    control.textContent = t(modalPlaying ? (plural ? 'Pause animations' : 'Pause animation') : (plural ? 'Play animations' : 'Play animation'));
    control.setAttribute('aria-pressed', String(modalPlaying));
  }
}
const observer = new IntersectionObserver(entries => {
  for (const entry of entries) {
    const frame = entry.target;
    frame.dataset.visible = String(entry.isIntersecting);
    if (entry.isIntersecting && !frame.getAttribute('src')) frame.src = frame.dataset.src;
  }
  refreshPlayback();
}, {threshold: .01});
function prepareFrame(frame) {
  frame.addEventListener('load', () => {
    if (!frame.getAttribute('src')) return;
    try {
      const doc = frame.contentDocument, svg = doc?.documentElement;
      if (svg?.localName !== 'svg') throw new Error('Invalid SVG document');
      // Only the viewport and playback change; committed model output stays untouched.
      svg.setAttribute('width', '100%'); svg.setAttribute('height', '100%');
      svg.style.display = 'block'; svg.style.backgroundColor = getComputedStyle(frame.parentElement).backgroundColor;
      playFrame(frame, false); restartFrame(frame);
      frame.classList.add('loaded'); refreshPlayback();
    } catch {
      const message = frame.parentElement.querySelector('.preview-loading');
      message.removeAttribute('aria-hidden'); message.setAttribute('role', 'status');
      message.dataset.i18n = frame.closest('dialog') ? 'Preview unavailable · download the SVG below' : 'Preview unavailable · open run details';
      message.textContent = t(message.dataset.i18n); frame.classList.remove('loaded');
    }
  });
  observer.observe(frame);
}
function preview(run) {
  return `<iframe class="artwork-frame" data-src="./artwork/${e(run.slug)}.svg" title="${e(t('{model} animated SVG', {model: run.name}))}" sandbox="allow-same-origin" tabindex="-1"></iframe><span class="preview-loading" aria-hidden="true" data-i18n="Loading artwork">${e(t('Loading artwork'))}</span>`;
}
function removeFrames(container) {
  for (const frame of container.querySelectorAll('iframe')) observer.unobserve(frame);
  container.replaceChildren();
}
function metricRow(label, value, className = '') {
  return `<div class="${className}"><dt>${e(t(label))}</dt><dd>${e(value)}</dd></div>`;
}
function sourceLinks(run) {
  return `<a href="${e(run.source.share_url)}" target="_blank" rel="noopener noreferrer" data-i18n="Pi conversation ↗">${e(t('Pi conversation ↗'))}</a><a href="./artwork/${e(run.slug)}.svg" download="${e(run.slug)}.svg" data-i18n="Download SVG ↓">${e(t('Download SVG ↓'))}</a>`;
}
function priceDetails(run) {
  const price = run.price;
  if (price?.basis === 'recorded') return `<p>${e(t('Pi recorded this estimate in the shared session.'))}</p>`;
  const reasons = {not_found: 'No exact public model price was found.', missing_usage: 'Required usage fields are missing.', missing_cache_price: 'Cache pricing is missing for the recorded cache usage.', cache_write_duration: 'Cache-write duration is not recorded.', per_request_usage: 'Per-request usage is needed to apply context price tiers.', conditional_price: 'Conditional pricing cannot be resolved from this export.'};
  const explanation = price?.basis === 'public' ? 'The share records $0; the displayed estimate uses public text-token rates.' : reasons[price?.reason] || reasons.not_found;
  return `<p>${e(t(explanation))}</p>${price?.source ? `<dl class="metric-list"><div><dt>${e(t('Price source'))}</dt><dd><a href="${e(price.source_url)}" target="_blank" rel="noopener noreferrer">${e(price.source)} ↗</a></dd></div>${metricRow('Catalog model', price.model_id)}${metricRow('Checked', date(price.checked_at))}${['input', 'output', 'cacheRead', 'cacheWrite'].map((key, index) => metricRow(['Input', 'Output', 'Cache read', 'Cache write'][index], price.rates_per_million[key] == null ? '—' : '$' + number(price.rates_per_million[key]))).join('')}</dl><p>${e(t('USD / 1M tokens'))}</p><p>${e(t('Public catalog rates at the checked date, not the actual bill. Excludes search, tool surcharges, discounts, and subscriptions.'))}</p>` : ''}`;
}
function runDetails(run) {
  const m = run.metrics, tokens = m.tokens;
  const badges = effortChips(run)
    + (run.follow_up_count ? `<span class="badge note">${e(t('{count} follow-up corrections', {count: run.follow_up_count}))}</span>` : '')
    + (m.errors || m.tool_errors ? `<span class="badge note">${e(t('Includes errors / retries'))}</span>` : '');
  return `<div class="run-badges">${badges}</div>
    <dl class="metric-highlights">${metricRow('Total run time', time(m.duration_seconds))}${metricRow('Average output TPS', number(m.average_tps))}${metricRow('Tool calls', number(m.tool_calls))}${metricRow(costLabel(run), costText(run))}</dl>
    <section class="metric-section"><h3>${e(t('Tokens'))}</h3><dl class="metric-list">${metricRow('Input', number(tokens.input))}${metricRow('Output', number(tokens.output))}${metricRow('Reasoning', number(tokens.reasoning))}${metricRow('Cache read', number(tokens.cacheRead))}${metricRow('Cache write', number(tokens.cacheWrite))}${metricRow('Recorded total', number(tokens.totalTokens), 'token-total')}</dl></section>
    <section class="metric-section"><h3>${e(t('The run'))}</h3><dl class="metric-list">${metricRow('Tested', date(run.date) + ' · UTC')}${metricRow('Model ID', run.model_ids.join(', '))}${metricRow('Request time', time(m.request_seconds))}${metricRow('Assistant turns', number(m.assistant_turns))}${metricRow('Tool breakdown', Object.entries(m.tool_breakdown).map(([tool, count]) => `${tool} × ${count}`).join(' · ') || t('No tool calls'))}${metricRow('Available tools', run.available_tools.join(' · ') || t('Not recorded'))}${metricRow('Errors recorded', number(m.errors + m.tool_errors))}</dl></section>
    <details class="metric-notes price-notes"><summary>${e(t('Price reference'))}</summary>${priceDetails(run)}</details>
    <details class="metric-notes"><summary>${e(t('How these numbers are measured'))}</summary>${['Total run time includes tool execution, retries, and any wait for a follow-up prompt. Request time is the sum of recorded assistant request intervals.', 'Average output TPS = reported output tokens ÷ request time. It includes first-token latency and reasoning time; it is not a streaming decode benchmark. Output may include reasoning tokens.', 'Token totals follow the exported usage. Reasoning is a breakdown, not an extra amount added to the total. Input and cache usage can recur across turns.', 'Costs are estimates, not billing receipts. Unverified zero costs are not treated as free.'].map(text => `<p>${e(t(text))}</p>`).join('')}</details>
    <div class="source-links">${sourceLinks(run)}<a href="https://gist.github.com/${e(run.source.gist_id)}/${e(run.source.gist_revision)}" target="_blank" rel="noopener noreferrer">${e(t('Source snapshot ↗'))}</a></div>`;
}
function showDetail(slug) {
  const run = bySlug.get(slug);
  if (!run) return;
  if (run.outcome === 'no_artwork') { location.replace(`./cases/${encodeURIComponent(run.slug)}/`); return; }
  if (compareDialog.open) compareDialog.close();
  if (currentDetail !== slug) {
    currentDetail = slug;
    const stage = document.querySelector('#detail-preview');
    removeFrames(stage); stage.innerHTML = preview(run); prepareFrame(stage.querySelector('iframe'));
    document.querySelector('#detail-title').textContent = run.name;
    document.querySelector('#detail-vendor').textContent = `${run.vendor} / ${levels(run)}`;
    document.querySelector('#detail-info').innerHTML = runDetails(run); detailDialog.scrollTop = 0;
  }
  if (!detailDialog.open) { modalPlaying = false; detailDialog.showModal(); }
  document.body.classList.add('modal-open');
  const displayedArtwork = visibleRuns.filter(item => item.outcome !== 'no_artwork');
  const group = displayedArtwork.some(item => item.slug === slug) ? displayedArtwork : artworkRuns;
  const index = group.findIndex(item => item.slug === slug);
  document.querySelector('#previous-run').disabled = index <= 0;
  document.querySelector('#next-run').disabled = index >= group.length - 1;
  refreshPlayback();
}
function openDetail(slug) { changeUrl({run: slug, compare: null}, true); reconcileDialogs(); }
function stepRun(direction) {
  const displayedArtwork = visibleRuns.filter(item => item.outcome !== 'no_artwork');
  const group = displayedArtwork.some(item => item.slug === currentDetail) ? displayedArtwork : artworkRuns;
  const next = group[group.findIndex(run => run.slug === currentDetail) + direction];
  if (next) { changeUrl({run: next.slug}, false); showDetail(next.slug); }
}
function syncSelection() {
  for (const [slug, card] of cards) {
    card.classList.toggle('selected', selected.has(slug));
    const checkbox = card.querySelector('[data-compare]');
    if (checkbox) checkbox.checked = selected.has(slug);
  }
  document.querySelector('#compare-tray').hidden = selected.size === 0;
  document.body.classList.toggle('has-selection', selected.size > 0);
  document.querySelector('#tray-items').innerHTML = [...selected].map(slug => {
    const run = bySlug.get(slug);
    return `<span class="tray-item"><span class="tray-model-name">${e(run.name)}</span><span class="effort-chips">${effortChips(run)}</span><button type="button" data-remove="${e(slug)}" aria-label="${e(t('Remove {model} from comparison', {model: run.name + ' · ' + levels(run)}))}">×</button></span>`;
  }).join('');
  document.querySelector('#selection-count').textContent = t('{count} / 4 selected', {count: selected.size});
  const button = document.querySelector('#open-compare');
  button.disabled = selected.size < 2;
  button.textContent = selected.size >= 2 ? t('Compare {count} ↗', {count: selected.size}) : t('Choose one more');
}
function toggleSelection(slug, checked) {
  if (!bySlug.has(slug) || bySlug.get(slug).outcome === 'no_artwork') return;
  if (checked && selected.size === 4 && !selected.has(slug)) notify('Compare up to four performances. Remove one to change your selection.');
  else if (checked) selected.add(slug); else selected.delete(slug);
  syncSelection();
}
function comparisonTable(pair) {
  const rows = [['Model maker', run => run.vendor], ['Reasoning', levels], ['Total run time', run => time(run.metrics.duration_seconds)], ['Request time', run => time(run.metrics.request_seconds)], ['Avg. output TPS', run => number(run.metrics.average_tps)], ['Estimated cost · USD', costText], ['Tool calls', run => number(run.metrics.tool_calls)], ['Assistant turns', run => number(run.metrics.assistant_turns)], ['Follow-up prompts', run => number(run.follow_up_count)], ['Errors recorded', run => number(run.metrics.errors + run.metrics.tool_errors)], ['Input tokens', run => number(run.metrics.tokens.input)], ['Output tokens', run => number(run.metrics.tokens.output)], ['Reasoning tokens', run => number(run.metrics.tokens.reasoning)], ['Cache read tokens', run => number(run.metrics.tokens.cacheRead)], ['Cache write tokens', run => number(run.metrics.tokens.cacheWrite)], ['Recorded total tokens', run => number(run.metrics.tokens.totalTokens)]];
  return `<table class="compare-table"><caption class="sr-only">${e(t('Performance metrics comparison'))}</caption><thead><tr><th scope="col">${e(t('Run details'))}</th>${pair.map(run => `<th scope="col">${e(run.name)} · ${e(levels(run))}</th>`).join('')}</tr></thead><tbody>${rows.map(([label, value]) => `<tr><th scope="row">${e(t(label))}</th>${pair.map(run => `<td>${e(value(run))}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
}
function showComparison(slugs) {
  if (!validComparison(slugs)) return;
  const pair = slugs.map(slug => bySlug.get(slug));
  compareDialog.style.setProperty('--compare-count', pair.length);
  compareDialog.style.setProperty('--comparison-width', pair.length > 2 ? '1440px' : '1000px');
  if (detailDialog.open) detailDialog.close();
  selected.clear(); slugs.forEach(slug => selected.add(slug)); syncSelection();
  const key = slugs.join(',');
  if (currentComparison !== key) {
    currentComparison = key;
    const content = document.querySelector('#comparison-content');
    removeFrames(content);
    content.innerHTML = `<div class="compare-artworks">${pair.map(run => `<section data-run="${e(run.slug)}"><div class="compare-model-header"><h3>${e(run.name)}</h3><span class="effort-chips">${effortChips(run)}</span></div><div class="large-preview">${preview(run)}</div><div class="compare-model-links">${sourceLinks(run)}</div></section>`).join('')}</div><div class="compare-table-wrap" tabindex="0" role="region" aria-label="${e(t('Performance metrics comparison'))}">${comparisonTable(pair)}</div><p class="compare-notes" data-i18n="${e(comparisonNote)}">${e(t(comparisonNote))}</p>`;
    content.querySelectorAll('iframe').forEach(prepareFrame); compareDialog.scrollTop = 0;
  }
  if (!compareDialog.open) { modalPlaying = true; compareDialog.showModal(); }
  document.body.classList.add('modal-open'); refreshPlayback();
}
function reconcileDialogs() {
  const params = new URLSearchParams(location.search), slug = params.get('run');
  const pair = (params.get('compare') || '').split(',').filter(Boolean);
  if (bySlug.has(slug)) showDetail(slug);
  else if (validComparison(pair)) showComparison(pair);
  else {
    if (detailDialog.open) detailDialog.close(); if (compareDialog.open) compareDialog.close();
    removeFrames(document.querySelector('#detail-preview')); removeFrames(document.querySelector('#comparison-content'));
    currentDetail = null; currentComparison = ''; document.body.classList.remove('modal-open'); refreshPlayback();
    if (slug || params.has('compare')) { changeUrl({run: null, compare: null}); notify('That performance link is unavailable. Browse the collection below.'); }
  }
}
function closeDialog() {
  if (history.state?.galleryOverlay) history.back(); else { changeUrl({run: null, compare: null}); reconcileDialogs(); }
}
async function copyLink(button) {
  try {
    await navigator.clipboard.writeText(location.href);
    const label = button.querySelector('[data-i18n]'), original = label.dataset.i18n;
    label.dataset.i18n = 'Link copied ✓'; label.textContent = t('Link copied ✓');
    setTimeout(() => { label.dataset.i18n = original; label.textContent = t(original); }, 1800);
  } catch { notify('Copy unavailable. Copy this page’s address from your browser.'); }
}

function renderLanguage() {
  const failed = runs.length - artworkRuns.length;
  document.querySelector('#summary-count').textContent = failed ? t('{works} artworks · {failed} without SVG', {works: number(artworkRuns.length), failed: number(failed)}) : t('{count} performances', {count: number(runs.length)});
  document.querySelector('#summary-makers').textContent = t('{count} model makers', {count: number(new Set(runs.map(run => run.vendor)).size)});
  document.querySelector('#updated-date').textContent = new Intl.DateTimeFormat(locale(), {month: 'long', year: 'numeric', timeZone: 'UTC'}).format(new Date(runs[0].date));
  for (const run of runs) {
    const card = cards.get(run.slug), level = levels(run);
    card.querySelector('.preview').setAttribute('aria-label', run.outcome === 'no_artwork' ? t('Read failure notes for {model}, max reasoning', {model: run.name}) : t('View {model}, {level} reasoning', {model: run.name, level}));
    if (run.outcome === 'no_artwork') continue;
    card.querySelector('[data-compare]').setAttribute('aria-label', t('Compare {model}, {level} reasoning', {model: run.name, level}));
    card.querySelector('iframe').title = t('{model} animated SVG', {model: run.name});
    card.querySelector('[data-time]').textContent = time(run.metrics.duration_seconds);
    card.querySelector('[data-price]').textContent = costText(run);
  }
  if (currentDetail) {
    const run = bySlug.get(currentDetail);
    document.querySelector('#detail-vendor').textContent = `${run.vendor} / ${levels(run)}`;
    document.querySelector('#detail-info').innerHTML = runDetails(run);
    document.querySelector('#detail-preview iframe').title = t('{model} animated SVG', {model: run.name});
  }
  if (currentComparison) {
    const pair = currentComparison.split(',').map(slug => bySlug.get(slug));
    document.querySelector('#comparison-content .compare-table-wrap').innerHTML = comparisonTable(pair);
    for (const section of document.querySelectorAll('.compare-artworks section')) {
      const run = bySlug.get(section.dataset.run);
      section.querySelector('iframe').title = t('{model} animated SVG', {model: run.name});
    }
  }
  syncSelection(); applyFilters(false); refreshPlayback();
}
for (const type of ['pointerenter', 'pointerleave']) document.addEventListener(type, event => {
  if (!event.target.matches?.('.preview')) return;
  event.target.dataset.hovered = String(type === 'pointerenter' && event.pointerType !== 'touch'); refreshPlayback();
}, true);
for (const type of ['focusin', 'focusout']) document.addEventListener(type, refreshPlayback);
search.addEventListener('input', () => {
  if (!previousQuery && normalizeSearch(search.value) && sort.value === 'newest') sort.value = 'relevance';
  applyFilters();
});
for (const select of [reasoning, sort]) select.addEventListener('change', () => applyFilters());
document.querySelector('#filters').addEventListener('submit', event => event.preventDefault());
document.querySelector('#clear-filters').addEventListener('click', resetFilters);
document.querySelector('[data-reset]').addEventListener('click', resetFilters);
document.querySelector('#previous-run').addEventListener('click', () => stepRun(-1));
document.querySelector('#next-run').addEventListener('click', () => stepRun(1));
document.querySelector('#clear-selection').addEventListener('click', () => { selected.clear(); syncSelection(); });
document.querySelector('#open-compare').addEventListener('click', () => { if (validComparison([...selected])) { changeUrl({run: null, compare: [...selected].join(',')}, true); reconcileDialogs(); } });
document.addEventListener('click', event => {
  const target = event.target.closest('button, a');
  if (!target) return;
  if (target.hasAttribute('data-open')) { event.preventDefault(); openDetail(target.dataset.open); }
  else if (target.hasAttribute('data-vendor')) { vendor = target.dataset.vendor; applyFilters(); }
  else if (target.hasAttribute('data-remove')) toggleSelection(target.dataset.remove, false);
  else if (target.hasAttribute('data-close')) closeDialog();
  else if (target.hasAttribute('data-motion')) { modalPlaying = !modalPlaying; refreshPlayback(); }
  else if (target.hasAttribute('data-restart')) target.closest('dialog').querySelectorAll('iframe').forEach(restartFrame);
  else if (target.hasAttribute('data-copy')) copyLink(target);
});
document.addEventListener('change', event => { if (event.target.matches('[data-compare]')) toggleSelection(event.target.dataset.compare, event.target.checked); });
for (const dialog of [detailDialog, compareDialog]) {
  dialog.addEventListener('cancel', event => { event.preventDefault(); closeDialog(); });
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const rect = dialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) closeDialog();
  });
}
document.addEventListener('keydown', event => {
  if (!detailDialog.open || /INPUT|SELECT|TEXTAREA/.test(event.target.tagName)) return;
  if (event.key === 'ArrowLeft') { event.preventDefault(); stepRun(-1); }
  if (event.key === 'ArrowRight') { event.preventDefault(); stepRun(1); }
});
document.addEventListener('visibilitychange', refreshPlayback);
reducedMotion.addEventListener('change', () => { modalPlaying = false; refreshPlayback(); });
window.addEventListener('popstate', () => { readFilters(); reconcileDialogs(); });
const knownEfforts = new Set([...reasoning.options].map(option => option.value));
for (const level of new Set(runs.flatMap(run => run.reasoning))) if (!knownEfforts.has(level)) reasoning.add(new Option(level, level));
document.querySelectorAll('.artwork-frame').forEach(prepareFrame);
readFilters(); setupLanguage(renderLanguage); reconcileDialogs();
