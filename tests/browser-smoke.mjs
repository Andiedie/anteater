// Optional real-browser check: run the preview, then `node tests/browser-smoke.mjs`.
// Node 22+ and an installed Chrome; CHROME_BIN overrides the platform default.
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const profile = await mkdtemp(join(tmpdir(), 'anteater-browser-'));
const binary = process.env.CHROME_BIN || (process.platform === 'darwin'
  ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' : 'google-chrome');
const browser = spawn(binary, ['--headless=new', '--no-first-run', '--disable-background-networking',
  '--remote-debugging-port=0', `--user-data-dir=${profile}`, process.argv[2] || 'http://localhost:8765'], {stdio: 'ignore'});
let launchError, socket, nextId = 0;
const pending = new Map();
browser.on('error', error => { launchError = error; });
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

async function pixelChanges(before, after) {
  const images = await Promise.all([before, after].map(async data => createImageBitmap(await (await fetch('data:image/png;base64,' + data)).blob())));
  const canvas = new OffscreenCanvas(images[0].width, images[0].height), context = canvas.getContext('2d');
  const pixels = images.map(image => { context.clearRect(0,0,canvas.width,canvas.height);context.drawImage(image,0,0);image.close();return context.getImageData(0,0,canvas.width,canvas.height).data; });
  let changed = 0;
  // Ignore tiny antialiasing differences, not displaced ground strokes.
  for (let i=0;i<pixels[0].length;i+=4) if ([0,1,2].some(channel => Math.abs(pixels[0][i+channel]-pixels[1][i+channel])>12)) changed++;
  return changed;
}

async function smoke() {
  const checks = [];
  const assert = (value, name) => { if (!value) throw new Error(name); checks.push(name); };
  const waitFor = async (predicate, name) => {
    const start = performance.now();
    while (!predicate()) {
      if (performance.now() - start > 5000) throw new Error(`Timed out: ${name}`);
      await new Promise(resolve => setTimeout(resolve, 30));
    }
  };
  await waitFor(() => document.querySelector('.card iframe.loaded'), 'initial artwork');
  assert(document.documentElement.lang === 'en-US' && document.querySelector('#language').value === 'auto', 'automatic English language');
  assert(document.querySelector('.card iframe.loaded').contentDocument.documentElement.animationsPaused(), 'artwork is still by default');
  assert(!document.querySelector('.preview-action') && [...document.querySelectorAll('.preview')].every(stage => !/View performance|查看作品/.test(stage.textContent)), 'no hover label obstructs artwork');
  const catalog = JSON.parse(document.querySelector('#catalog-data').textContent);
  const visible = () => [...document.querySelectorAll('.card:not([hidden])')];
  const key = run => JSON.stringify([run.vendor, run.name]);
  const cardFor = name => [...document.querySelectorAll('.card')].find(card => JSON.parse(card.dataset.model)[1] === name);
  const showRun = slug => {
    const card = cardFor(catalog.find(run => run.slug === slug).name);
    card.querySelector('[data-card-run="'+slug+'"]').click(); card.querySelector('.preview').click();
  };
  const defaultRuns = catalog.filter(run => run.outcome !== 'no_artwork').filter((run, index, all) => all.findIndex(item => key(item) === key(run)) === index);
  assert(document.querySelectorAll('.card').length === defaultRuns.length && defaultRuns.length < catalog.length, 'one card per model, not per run');
  assert([...document.querySelectorAll('.card')].every(card => card.querySelectorAll('.level-link').length === catalog.filter(run => key(run) === card.dataset.model).length), 'every recorded level remains reachable on its model card');
  const set = (selector, value, event = 'change') => {
    const node = document.querySelector(selector);
    node.value = value; node.dispatchEvent(new Event(event, {bubbles: true}));
  };
  assert(!document.querySelector('.site-header a[href="#the-prompt"]') && document.querySelector('.github-link svg') && document.querySelector('.github-link').getAttribute('aria-label') === 'GitHub', 'header drops prompt shortcut and exposes an accessible GitHub logo');
  assert([...document.querySelectorAll('.language-control,.filter-selects > label')].every(label => getComputedStyle(label,'::after').right === '14px' && parseFloat(getComputedStyle(label.querySelector('select')).paddingRight) >= 34), 'select arrows have reserved space away from text and border');
  const flash = cardFor('MiMo V2.6 Flash'), flashPosition = [...document.querySelector('#gallery').children].indexOf(flash), pageUrl = location.href;
  flash.querySelector('[data-card-run="mimo-v2.6-flash-off"]').click();
  await waitFor(() => flash.querySelector('iframe.loaded'), 'in-card off artwork');
  assert(!document.querySelector('dialog[open]') && location.href === pageUrl && flash.dataset.slug === 'mimo-v2.6-flash-off' && [...document.querySelector('#gallery').children].indexOf(flash) === flashPosition, 'level button switches artwork in place without opening details or changing URL');
  const off = catalog.find(run => run.slug === flash.dataset.slug), offButton = flash.querySelector('[aria-pressed="true"]');
  assert(flash.querySelector('[data-output]').textContent === new Intl.NumberFormat('en-US').format(off.metrics.tokens.output) && flash.querySelector('[data-compare]').dataset.compare === off.slug && flash.querySelector('h2 a').search === '?run='+off.slug && offButton.getAttribute('aria-label').includes('MiMo V2.6 Flash, off'), 'card metrics, accessible level, exact links and comparison follow selected level');
  assert(getComputedStyle(offButton).borderWidth === '0px' && getComputedStyle(offButton.querySelector('.effort')).textDecorationLine === 'none' && getComputedStyle(offButton.querySelector('.effort')).fontWeight === '600', 'selected level uses one filled label, not double borders and underline');
  const offFrame = flash.querySelector('iframe');
  set('#language','zh');
  assert(flash.dataset.slug === off.slug && flash.querySelector('iframe') === offFrame && [...document.querySelector('#gallery').children].indexOf(flash) === flashPosition, 'language switch preserves selected card level, frame and position'); set('#language','en');
  set('#sort','cost');
  assert(flash.dataset.slug === off.slug && flash.querySelector('iframe') === offFrame, 'sort preserves chosen card record');
  flash.querySelector('[data-compare]').checked = true; flash.querySelector('[data-compare]').dispatchEvent(new Event('change',{bubbles:true}));
  flash.querySelector('[data-card-run="mimo-v2.6-flash-high"]').click();
  assert(!flash.querySelector('[data-compare]').checked && document.querySelector('.tray-item').textContent.includes('off') && flash.querySelector('[data-card-run="mimo-v2.6-flash-off"]').classList.contains('in-comparison'), 'level switch preserves comparison of the previously selected exact run');
  document.querySelector('#clear-selection').click();
  const sonnetCard = cardFor('Claude Sonnet 5.5');
  sonnetCard.querySelector('[data-card-run="claude-sonnet-5.5-max"]').click();
  assert(!document.querySelector('dialog[open]') && !sonnetCard.querySelector('iframe') && sonnetCard.querySelector('.card-stats').hidden && sonnetCard.querySelector('[data-compare]').disabled && sonnetCard.querySelector('.preview').textContent.includes('No SVG delivered') && sonnetCard.querySelector('[aria-pressed="true"]').getAttribute('aria-label').includes('No SVG delivered'), 'failed level switches to an accessible no-artwork card without invented metrics');
  set('#language','zh');assert(sonnetCard.dataset.slug === 'claude-sonnet-5.5-max' && sonnetCard.querySelector('.preview').textContent.includes('未交付 SVG'), 'selected failed card translates without resetting level');set('#language','en');
  sonnetCard.querySelector('[data-card-run="claude-sonnet-5.5-low"]').click();
  assert(sonnetCard.querySelector('iframe') && !sonnetCard.querySelector('.card-stats').hidden && !sonnetCard.querySelector('[data-compare]').disabled, 'card can return from failed level to delivered artwork');
  set('#reasoning','low'); flash.querySelector('[data-card-run="mimo-v2.6-flash-off"]').click();
  assert(document.querySelector('#reasoning').value === 'all' && !new URLSearchParams(location.search).has('reasoning') && flash.dataset.slug === 'mimo-v2.6-flash-off', 'local choice clears conflicting global effort filter instead of lying about active filter');
  document.querySelector('#clear-filters').click();
  assert(flash.dataset.slug === defaultRuns.find(run => run.name === 'MiMo V2.6 Flash').slug, 'clear filters restores default card levels');
  assert(performance.getEntriesByType('resource').some(resource => resource.name.endsWith('/assets/fuse/fuse.min.mjs')), 'local Fuse module loaded');
  const failures = catalog.filter(run => run.outcome === 'no_artwork');
  assert(failures.length === 2 && document.querySelectorAll('.failure-card').length === 0, 'failed levels do not duplicate model cards or replace default artwork');
  assert(failures.every(run => document.querySelector(`[data-card-run="${run.slug}"] .level-status`).textContent === 'No SVG delivered'), 'failed levels are explicit and reachable, not unsupported');
  assert(document.querySelector('#summary-count').textContent === `${defaultRuns.length} models · ${catalog.length} runs · ${failures.length} without SVG`, 'summary distinguishes models, records and failures');
  const select = slug => {
    set('#reasoning', catalog.find(run => run.slug === slug).reasoning[0]);
    const checkbox = document.querySelector(`[data-compare="${slug}"]`);
    checkbox.checked = true; checkbox.dispatchEvent(new Event('change', {bubbles: true}));
  };
  select('gpt-6-astra-max'); select('claude-sonnet-5.5-xhigh');
  const center = node => { const rect=node.getBoundingClientRect();return rect.y+rect.height/2; };
  assert(Math.abs(center(document.querySelector('.tray-items'))-center(document.querySelector('.tray-actions')))<1, 'comparison actions vertically align with selected artwork row');
  document.querySelector('#clear-selection').click(); set('#reasoning', 'all');
  document.querySelector('[data-vendor="Anthropic"]').click();
  assert(visible().length === defaultRuns.filter(run => run.vendor === 'Anthropic').length, 'Anthropic groups all levels including failed tests');
  set('#reasoning', 'max');
  assert(visible().length === catalog.filter(run => run.vendor === 'Anthropic' && run.reasoning.includes('max')).length && visible().filter(card => card.classList.contains('failure-card')).length === failures.length, 'Anthropic max filter keeps successes and failures');
  assert(failures.every(run => { const card=document.querySelector('[data-slug="'+run.slug+'"]'); return !card.querySelector('iframe') && card.querySelector('.card-stats').hidden && card.querySelector('[data-compare]').disabled; }), 'filtered failures have no artwork, invented metrics or active comparison');
  set('#language', 'zh'); assert(visible().filter(card => card.classList.contains('failure-card')).every(card => card.querySelector('.preview').textContent.includes('未交付 SVG')), 'filtered failure states translate'); set('#language', 'en');
  set('#search', 'claude opus', 'input');
  assert(visible().length === 1 && visible()[0].dataset.slug === 'claude-opus-5.5-max', 'failed model remains searchable');
  document.querySelector('#clear-filters').click();
  const gpt6 = defaultRuns.filter(run => run.name.startsWith('GPT-6')).map(run => run.slug);
  for (const query of ['gpt6', 'g pt6', 'g p t 6', 'GPT-6', 'GPT 6', 'gpt_6', 'ＧＰＴ６']) {
    set('#search', query, 'input');
    assert(gpt6.every(slug => visible().some(card => card.dataset.slug === slug)) && visible().slice(0, gpt6.length).every(card => gpt6.includes(card.dataset.slug)), `separator-insensitive search: ${query}`);
  }
  for (const query of ['gptt6', 'gp6']) {
    set('#search', query, 'input');
    assert(gpt6.every(slug => visible().some(card => card.dataset.slug === slug)) && visible().slice(0, gpt6.length).every(card => gpt6.includes(card.dataset.slug)), `typo-tolerant search: ${query}`);
  }
  for (const [query, maker] of [['gemni', 'Google'], ['deepsek', 'DeepSeek'], ['MÍMO', 'Xiaomi']]) {
    set('#search', query, 'input');
    const expected = defaultRuns.filter(run => run.vendor === maker).map(run => run.slug);
    assert(visible().length === expected.length && visible().every(card => expected.includes(card.dataset.slug)), `maker typo or accent: ${query}`);
  }
  set('#search', 'gpt61', 'input');
  assert(visible()[0].dataset.slug.startsWith('gpt-6.1-'), 'exact version ranks before fuzzy alternatives');
  set('#search', '  luna OpenAI  GPT6 ', 'input');
  const luna = defaultRuns.filter(run => run.name === 'GPT-6 Luna');
  assert(visible().slice(0, luna.length).every(card => luna.some(run => run.slug === card.dataset.slug)), 'multiple search keywords in any order');
  set('#search', 'openai sol gp6', 'input');
  const sol = defaultRuns.filter(run => run.name.startsWith('GPT-6') && run.name.endsWith('Sol'));
  assert(sol.every(run => visible().some(card => card.dataset.slug === run.slug)) && visible().slice(0, sol.length).every(card => sol.some(run => run.slug === card.dataset.slug)), 'typos in multi-keyword query');
  set('#search', 'deep seek', 'input');
  assert(visible().length === defaultRuns.filter(run => run.vendor === 'DeepSeek').length && visible().every(card => card.dataset.slug.startsWith('deepseek-')), 'maker search ignores spaces');
  set('#search', 'g pt6', 'input');
  const searchOrder = visible().map(card => card.dataset.slug).join(',');
  set('#language', 'zh');
  assert(visible().map(card => card.dataset.slug).join(',') === searchOrder && document.querySelector('#search').value === 'g pt6' && document.querySelector('#sort [value="relevance"]').textContent === '最相关优先', 'language switch preserves fuzzy search');
  set('#language', 'en');
  set('#search', 'gpt6', 'input');
  assert(document.querySelector('#sort').value === 'relevance', 'search defaults to relevance');
  set('#sort', 'cost');
  set('#search', 'gptt6', 'input');
  const prices = visible().map(card => { const run = catalog.find(run => run.slug === card.dataset.slug); return run.price?.amount_usd ?? run.metrics?.cost_usd; }).filter(value => value != null);
  assert(document.querySelector('#sort').value === 'cost' && prices.every((value, index) => !index || value >= prices[index - 1]), 'explicit cost sort survives fuzzy input');
  set('#sort', 'newest');
  set('#search', 'g pt6', 'input');
  assert(document.querySelector('#sort').value === 'newest' && new URLSearchParams(location.search).get('sort') === 'newest' && visible().every((card, index, list) => !index || catalog.find(run => run.slug === list[index - 1].dataset.slug).date >= catalog.find(run => run.slug === card.dataset.slug).date), 'explicit newest sort survives fuzzy input');
  const url = new URL(location.href);
  url.searchParams.set('q', 'gpt6'); history.replaceState(null, '', url); dispatchEvent(new PopStateEvent('popstate'));
  assert(document.querySelector('#search').value === 'gpt6' && gpt6.every(slug => visible().some(card => card.dataset.slug === slug)), 'compact search restored from URL');
  const searched = new Set(visible().map(card => card.dataset.model));
  set('#reasoning', 'low');
  assert(visible().length === catalog.filter(run => searched.has(key(run)) && run.reasoning.includes('low')).length && visible().every(card => searched.has(card.dataset.model) && card.dataset.slug.endsWith('-low')), 'compact search intersects reasoning, including fuzzy alternatives');
  document.querySelector('#clear-filters').click();
  assert(visible().length === defaultRuns.length && document.querySelector('#sort').value === 'newest' && document.querySelector('#sort [value="relevance"]').disabled, 'clear search restores newest and disables relevance');
  set('#search', '  -- … ', 'input');
  assert(visible().length === defaultRuns.length, 'punctuation-only search is empty');
  set('#search', 'nothing-here', 'input');
  assert(visible().length === 0 && !document.querySelector('#empty-state').hidden, 'unrelated query stays empty');
  document.querySelector('[data-reset]').click();
  assert(document.querySelectorAll('.vendor-logo').length === new Set(catalog.map(run => run.vendor)).size, 'every maker has a logo');
  assert([...document.querySelectorAll('.vendor-logo')].every(icon => icon.getAttribute('aria-hidden') === 'true'), 'logos do not duplicate accessible labels');
  document.querySelector('[data-vendor="DeepSeek"] path').dispatchEvent(new MouseEvent('click', {bubbles: true}));
  assert(visible().length === defaultRuns.filter(run => run.vendor === 'DeepSeek').length && location.search.includes('vendor=DeepSeek'), 'clicking the logo filters + updates URL');
  set('#reasoning', 'low');
  assert(visible().length > 0 && visible().every(card => card.dataset.slug.endsWith('-low')), 'reasoning intersection');
  set('#search', 'nothing-here', 'input');
  assert(visible().length === 0 && !document.querySelector('#empty-state').hidden, 'empty state');
  document.querySelector('[data-reset]').click();
  assert(visible().length === defaultRuns.length && document.querySelector('#empty-state').hidden, 'reset');
  assert(!document.querySelector('#follow-up'), 'no follow-up filter');
  set('#reasoning', 'high');
  document.querySelector('#clear-filters').click();
  assert(visible().length === defaultRuns.length && !new URLSearchParams(location.search).has('reasoning'), 'clear filters restores all models');
  set('#sort', 'cost');
  const missing = defaultRuns.filter(run => (run.price?.amount_usd ?? run.metrics?.cost_usd) == null).map(run => run.slug);
  assert(!missing.length || visible().slice(-missing.length).every(card => missing.includes(card.dataset.slug)), 'unknown prices sorted last');
  const amounts = visible().map(card => { const run = catalog.find(run => run.slug === card.dataset.slug); return run.price?.amount_usd ?? run.metrics?.cost_usd; }).filter(value => value != null);
  assert(amounts.every((value, index) => index === 0 || value >= amounts[index - 1]), 'cost sort includes supplemented estimates');
  set('#sort', 'newest');
  await waitFor(() => document.querySelector('.card iframe.loaded')?.contentDocument?.documentElement.localName === 'svg', 'artwork survives rapid filtering/sorting');
  const container = document.querySelector('#gallery'), move = container.moveBefore;
  container.moveBefore = undefined;
  set('#sort', 'cost'); set('#sort', 'newest');
  await waitFor(() => document.querySelector('.card iframe.loaded')?.contentDocument?.documentElement.localName === 'svg', 'legacy reparenting fallback');
  container.moveBefore = move;
  assert(!document.querySelector('#motion-toggle'), 'no global play-all button');
  const frame = document.querySelector('.card iframe.loaded'), svg = frame.contentDocument.documentElement;
  assert([...frame.contentDocument.querySelectorAll('svg')].every(clock => clock.animationsPaused()) && frame.contentDocument.getAnimations().every(animation => animation.playState === 'paused'), 'all SMIL clocks and CSS pause');
  assert([...document.querySelectorAll('.card .effort')].every(chip => chip.textContent === chip.dataset.level && getComputedStyle(chip).textTransform === 'none'), 'thinking chips use raw vocabulary');
  const colors = new Map([...document.querySelectorAll('.card .effort')].map(chip => [chip.dataset.level,getComputedStyle(chip).backgroundColor]));
  assert(new Set(colors.values()).size === colors.size, 'thinking levels have distinct colors');
  const pausedTime = svg.getCurrentTime();
  await new Promise(resolve => setTimeout(resolve, 180));
  assert(Math.abs(svg.getCurrentTime() - pausedTime) < .04, 'paused animation stays still');
  showRun('claude-fable-5.1-xhigh');
  await waitFor(() => document.querySelector('#detail-preview iframe.loaded'), 'new Claude detail artwork');
  document.querySelector('#next-run').click();
  assert(new URLSearchParams(location.search).get('run') === 'claude-fable-5.1-max', 'detail navigation stays within the model');
  document.querySelector('#previous-run').click();
  assert(new URLSearchParams(location.search).get('run') === 'claude-fable-5.1-xhigh', 'previous level stays within the model');
  document.querySelector('#detail-dialog [data-close]').click();
  await waitFor(() => !document.querySelector('#detail-dialog').open, 'Claude detail closes');
  showRun('gpt-6.1-sol-max');
  await waitFor(() => document.querySelector('#detail-preview iframe.loaded'), 'detail artwork');
  assert(document.querySelector('#detail-dialog').open && location.search.includes('run=gpt-6.1-sol-max'), 'detail + deep link');
  assert(catalog.every(run => !Object.hasOwn(run, 'providers')) && !/CPA|cliproxyapi|opencode-go/.test(JSON.stringify(catalog)), 'private invocation channels omitted');
  assert(document.querySelector('#detail-info').textContent.includes('Public estimate') && document.querySelector('#detail-info').textContent.includes('≈$'), 'missing recorded cost uses marked public estimate');
  const targetIndex = catalog.findIndex(run => run.slug === 'gpt-6.1-sol-max');
  assert(document.querySelector('#detail-info').textContent.includes(new Intl.NumberFormat('en-US').format(catalog[targetIndex].metrics.average_tps)), 'TPS displayed');
  assert(document.activeElement.getAttribute('aria-label') === 'Close performance', 'dialog focus');
  assert(document.querySelector('.card iframe').dataset.playing === 'false', 'gallery pauses behind dialog');
  assert([...document.querySelector('#detail-preview iframe').contentDocument.querySelectorAll('svg')].every(clock=>!clock.animationsPaused()), 'detail opens with every SVG clock playing');
  assert(!document.querySelector('[data-motion],[data-restart],.preview-controls'), 'no playback, pause or restart controls');
  const detailFrame = document.querySelector('#detail-preview iframe');
  set('#language', 'zh');
  assert(document.documentElement.lang === 'zh-CN' && document.querySelector('#detail-info').textContent.includes('公开价格估算'), 'Chinese details and price labels');
  assert(document.querySelector('#detail-preview iframe') === detailFrame && document.querySelector('#detail-dialog').open, 'language switch preserves detail artwork');
  set('#language', 'en');
  document.querySelector('#next-run').click();
  assert(new URLSearchParams(location.search).get('run') === 'gpt-6.1-sol-max' && document.querySelector('#next-run').disabled, 'highest recorded level does not jump to another model');
  document.querySelector('#previous-run').click();
  assert(location.search.includes('run=gpt-6.1-sol-xhigh'), 'previous level follows native order');
  document.querySelector('#next-run').click();
  document.querySelector('#detail-dialog [data-close]').click();
  await waitFor(() => !document.querySelector('#detail-dialog').open, 'detail close');
  assert(!location.search.includes('run='), 'close restores gallery URL');
  select('gpt-6.1-sol-max');
  assert(document.querySelector('#open-compare').disabled, 'comparison requires at least two');
  select('gpt-6.1-sol-xhigh'); select('hy3-high'); select('grok-4.7-xhigh'); select('gemini-3.8-flash-high');
  assert(document.querySelectorAll('.tray-item').length === 4 && !document.querySelector('[data-compare="gemini-3.8-flash-high"]').checked, 'comparison limited to four actual runs, even across levels');
  assert(!document.querySelector('#compare-tray').hidden && !document.querySelector('#open-compare').disabled, 'comparison tray');
  document.querySelector('#open-compare').click();
  await waitFor(() => document.querySelectorAll('#comparison-content iframe.loaded').length === 4, 'comparison artworks');
  assert(document.querySelector('#compare-dialog').open && document.querySelectorAll('.compare-table tbody tr').length === 17, 'comparison metrics');
  assert(document.querySelectorAll('.compare-table thead th').length === 5, 'four comparison value columns');
  assert([...document.querySelectorAll('#comparison-content iframe')].every(frame => [...frame.contentDocument.querySelectorAll('svg')].every(clock => !clock.animationsPaused())), 'comparison autoplays all SVG clocks');
  assert(!document.querySelector('#compare-dialog [data-motion],#compare-dialog [data-restart]'), 'comparison has no playback controls');
  assert(location.search.includes('compare='), 'comparison share URL');
  const comparisonFrames = [...document.querySelectorAll('#comparison-content iframe')];
  set('#language', 'zh');
  assert(document.querySelector('.compare-table').textContent.includes('测试指标') && document.querySelector('#comparison-content iframe') === comparisonFrames[0], 'Chinese comparison preserves artwork');
  assert(document.querySelector('#compare-tray').textContent.includes('比较 4 件'), 'Chinese selection tray');
  set('#language', 'en');
  document.querySelector('#compare-dialog').dispatchEvent(new Event('cancel', {cancelable: true}));
  await waitFor(() => !document.querySelector('#compare-dialog').open, 'comparison cancel');
  document.querySelector('#clear-selection').click();
  assert(document.querySelector('#compare-tray').hidden, 'clear selection');
  const slugs = ['gpt-6.1-sol-max','gpt-6.1-sol-xhigh','hy3-high','grok-4.7-xhigh'];
  const link = pair => { const url=new URL(location.href);url.searchParams.set('compare',pair.join(','));history.replaceState(null,'',url);dispatchEvent(new PopStateEvent('popstate')); };
  for (const count of [2,3,4]) {
    link(slugs.slice(0,count));
    await waitFor(() => document.querySelectorAll('#comparison-content iframe.loaded').length === count, `${count}-way direct link`);
    assert(document.querySelector('#compare-dialog').open && document.querySelectorAll('.compare-table thead th').length === count+1, `${count}-way comparison URL`);
  }
  for (const invalid of [[slugs[0],slugs[0]],[...slugs,'gemini-3.8-flash-high'],[slugs[0],'missing-model'],[slugs[0],'claude-opus-5.5-max']]) {
    link(invalid);assert(!document.querySelector('#compare-dialog').open&&!location.search.includes('compare='), 'invalid comparison URL rejected');
  }
  document.querySelector('#clear-selection').click(); document.querySelector('#clear-filters').click();
  cardFor('MiMo V2.6 Flash').querySelector('[data-compare-model]').click();
  await waitFor(() => document.querySelectorAll('#comparison-content iframe.loaded').length === 2, 'two-level quick comparison');
  assert(new URLSearchParams(location.search).get('compare') === 'mimo-v2.6-flash-off,mimo-v2.6-flash-high', 'two recorded artworks compare directly in level order');
  const budgetRow = [...document.querySelectorAll('.compare-table tr')].find(row => row.querySelector('th')?.textContent === 'Output budget / request (incl. reasoning)');
  assert([...budgetRow.querySelectorAll('td')].map(cell => cell.textContent).join(',') === '64,000,131,072', 'comparison discloses different per-request budgets');
  document.querySelector('#compare-dialog [data-close]').click(); await waitFor(() => !document.querySelector('#compare-dialog').open, 'quick comparison returns to gallery');
  document.querySelector('#clear-selection').click();
  showRun('claude-sonnet-5.5-max');
  const dialog = document.querySelector('#detail-dialog'), historyLength = history.length;
  assert(dialog.open && new URLSearchParams(location.search).get('run') === 'claude-sonnet-5.5-max' && !document.querySelector('#detail-preview iframe,#detail-info [download],#detail-info .metric-highlights'), 'old failed-run link stays in model details without fake artwork or metrics');
  assert(document.querySelector('#detail-info').textContent.includes('64,000') && !document.querySelector('#detail-info').textContent.includes('128,000'), 'inline failure keeps model-specific evidence');
  assert(document.querySelector('#detail-levels [aria-pressed="true"]').dataset.levelRun === 'claude-sonnet-5.5-max' && document.querySelector('#detail-levels [aria-pressed="true"]').getAttribute('aria-label').includes('No SVG delivered'), 'failed level remains selected, navigable and labeled for screen readers');
  document.querySelector('#previous-run').click(); await waitFor(() => document.querySelector('#detail-preview iframe.loaded'), 'failure to delivered sibling');
  assert(document.querySelector('#detail-dialog') === dialog && new URLSearchParams(location.search).get('run') === 'claude-sonnet-5.5-xhigh', 'failure switches back to artwork without leaving the model');
  document.querySelector('#next-run').click();
  assert(dialog.open && !document.querySelector('#detail-preview iframe') && history.length === historyLength, 'level changes replace URL and do not add back-stack entries');
  set('#language', 'zh'); assert(document.querySelector('#detail-info').textContent.includes('思考阶段耗尽输出预算') && document.querySelector('#detail-preview').textContent.includes('未交付 SVG'), 'inline failure and level state translate together'); set('#language', 'en');
  document.querySelector('#detail-dialog [data-close]').click(); await waitFor(() => !dialog.open, 'one close after level changes returns to gallery');
  select('gpt-6.1-sol-max'); select('hy3-high');
  cardFor('Claude Sonnet 5.5').querySelector('[data-compare-model]').click();
  assert(dialog.open && document.querySelector('#level-overview').open && document.querySelectorAll('#level-summary tbody tr').length === 5, 'multi-level model opens an in-model picker with all records');
  assert(document.querySelectorAll('.tray-item').length === 2 && document.querySelector('#compare-level-selection').disabled, 'entering local picker preserves cross-model selection until comparison is committed');
  const failedChoice = document.querySelector('[data-level-compare="claude-sonnet-5.5-max"]');
  assert(failedChoice.disabled && [...failedChoice.closest('tr').querySelectorAll('td')].slice(1).every(cell => cell.textContent === '—'), 'failed level is visible but cannot fabricate comparison values');
  failedChoice.checked = true; failedChoice.dispatchEvent(new Event('change', {bubbles:true}));
  assert(!failedChoice.checked && document.querySelector('#compare-level-selection').disabled, 'failure cannot enter local comparison selection');
  for (const level of ['low','medium','high','xhigh']) {
    const box = document.querySelector('[data-level-compare="claude-sonnet-5.5-'+level+'"]'); box.checked = true; box.dispatchEvent(new Event('change',{bubbles:true}));
  }
  document.querySelector('#detail-levels [data-level-run="claude-sonnet-5.5-xhigh"]').click();
  await waitFor(() => document.querySelector('#detail-preview iframe.loaded'), 'picker level switch');
  const pickerFrame = document.querySelector('#detail-preview iframe');
  assert(document.querySelector('#level-overview').open && document.querySelectorAll('[data-level-compare]:checked').length === 4, 'local selections survive level switching');
  set('#language', 'zh');
  assert(document.querySelector('#detail-preview iframe') === pickerFrame && document.querySelector('#compare-level-selection').textContent.includes('比较 4 件') && document.querySelector('#level-selection-count').textContent.includes('4 / 4'), 'language change preserves picker selection and artwork'); set('#language', 'en');
  document.querySelector('#compare-level-selection').click(); await waitFor(() => document.querySelectorAll('#comparison-content iframe.loaded').length === 4, 'same-model four-level comparison');
  assert([...document.querySelectorAll('.compare-model-header h3')].every(node => node.textContent === 'Claude Sonnet 5.5') && document.querySelectorAll('.tray-item').length === 4, 'same-model comparison commits four exact records');
  document.querySelector('#compare-dialog [data-close]').click(); await waitFor(() => !document.querySelector('#compare-dialog').open, 'comparison returns to model context');
  assert(dialog.open && new URLSearchParams(location.search).get('run') === 'claude-sonnet-5.5-xhigh', 'closing same-model comparison restores chosen level');
  document.querySelector('#detail-dialog [data-close]').click(); await waitFor(() => !dialog.open, 'picker model closes');
  document.querySelector('#clear-selection').click(); document.querySelector('#clear-filters').click();
  cardFor('GPT-6.1 Sol').querySelector('[data-compare-model]').click();
  for (const box of document.querySelectorAll('[data-level-compare]')) { box.checked = true; box.dispatchEvent(new Event('change',{bubbles:true})); }
  assert(document.querySelectorAll('[data-level-compare]:checked').length === 4 && !document.querySelector('[data-level-compare="gpt-6.1-sol-max"]').checked, 'local picker enforces four artworks without losing prior choices');
  document.querySelector('#detail-dialog [data-close]').click(); await waitFor(() => !dialog.open, 'limited picker closes');
  assert(cardFor('DeepSeek V4 Flash 0731').querySelector('[data-compare-model]').disabled, 'one-artwork model does not offer impossible level comparison');
  assert(document.documentElement.scrollWidth <= innerWidth, 'no horizontal overflow');
  showRun('gpt-6.1-sol-max');
  await waitFor(() => document.querySelector('#detail-preview iframe.loaded'), 'failure-path artwork');
  document.querySelector('#detail-preview iframe').src = './missing-test-artwork.svg';
  await waitFor(() => document.querySelector('#detail-preview [role="status"]'), 'failed preview feedback');
  assert(document.querySelector('#detail-preview [role="status"]').textContent.includes('download the SVG') && document.querySelector('#detail-info [download]'), 'failed preview offers original SVG');
  set('#language', 'zh');
  assert(document.querySelector('#detail-preview [role="status"]').textContent.includes('下载 SVG'), 'failure feedback is translated');
  assert(!/CPA|cliproxyapi|opencode-go/.test(document.documentElement.outerHTML), 'no private channels in page');
  return checks;
}

try {
  let port;
  for (let attempt = 0; attempt < 100; attempt++) {
    if (launchError) throw launchError;
    try { port = (await readFile(join(profile, 'DevToolsActivePort'), 'utf8')).split('\n')[0]; break; }
    catch { await delay(100); }
  }
  if (!port) throw new Error('Chrome did not start');
  const targets = await (await fetch(`http://localhost:${port}/json`)).json();
  socket = new WebSocket(targets.find(target => target.type === 'page').webSocketDebuggerUrl);
  await once(socket, 'open');
  socket.addEventListener('message', event => {
    const message = JSON.parse(event.data), callbacks = pending.get(message.id);
    if (!callbacks) return;
    pending.delete(message.id);
    if (message.error) callbacks.reject(new Error(message.error.message));
    else callbacks.resolve(message.result);
  });
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++nextId; pending.set(id, {resolve, reject}); socket.send(JSON.stringify({id, method, params}));
  });
  const evaluate = async expression => {
    const result = await send('Runtime.evaluate', {expression, awaitPromise: true, returnByValue: true});
    if (result.exceptionDetails) throw new Error(result.exceptionDetails.exception?.description || result.exceptionDetails.text);
    return result.result.value;
  };
  await send('Page.enable');
  const reload = async (url) => {
    await send(url ? 'Page.navigate' : 'Page.reload', url ? {url} : {});
    for (let attempt = 0; attempt < 100; attempt++) {
      try { if (await evaluate(`document.readyState!=='loading'&&document.querySelector('#results-status')?.textContent&&document.querySelector('#language')${url ? `&&location.href===${JSON.stringify(new URL(url).href)}&&Boolean(document.querySelector('#detail-dialog').open||document.querySelector('#compare-dialog').open)===${new URL(url).searchParams.has('run') || new URL(url).searchParams.has('compare')}` : ''}`)) return; }
      catch { /* A reload briefly destroys the old execution context. */ }
      await delay(50);
    }
    throw new Error('Reloaded gallery did not initialize');
  };
  const userAgent = await evaluate('navigator.userAgent');
  await send('Emulation.setUserAgentOverride', {userAgent, acceptLanguage: 'en-US,en'});
  await send('Emulation.setDeviceMetricsOverride', {width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false});
  await send('Emulation.setEmulatedMedia', {features: [{name: 'prefers-reduced-motion', value: 'no-preference'}]});
  await reload();
  await evaluate(`document.querySelector('#reasoning').value='xhigh';document.querySelector('#reasoning').dispatchEvent(new Event('change',{bubbles:true}))`);
  const stillRect = await evaluate(`(async()=>{const frame=document.querySelector('[data-slug="gpt-6.1-sol-xhigh"] iframe');frame.scrollIntoView({block:'center',behavior:'instant'});const start=performance.now();while(!frame.classList.contains('loaded')){if(performance.now()-start>5000)throw Error('xhigh artwork not ready');await new Promise(r=>setTimeout(r,30))}await frame.contentDocument.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));const r=frame.getBoundingClientRect();return {x:r.x+scrollX,y:r.y+scrollY+r.height*.75,width:r.width,height:r.height*.25,scale:1}})()`);
  const stillBefore = await send('Page.captureScreenshot', {format:'png',clip:stillRect});
  await delay(240);
  const stillAfter = await send('Page.captureScreenshot', {format:'png',clip:stillRect});
  const changed = await evaluate(`(${pixelChanges.toString()})(${JSON.stringify(stillBefore.data)},${JSON.stringify(stillAfter.data)})`);
  if (changed > 8) {
    await writeFile(join(tmpdir(),'anteater-paused-before.png'),Buffer.from(stillBefore.data,'base64'));
    await writeFile(join(tmpdir(),'anteater-paused-after.png'),Buffer.from(stillAfter.data,'base64'));
    throw Error(`gpt-6.1-sol-xhigh changes visually while paused: ${changed} pixels (including its ground)`);
  }
  await evaluate(`document.querySelector('[data-slug="gpt-6.1-sol-xhigh"] iframe').contentDocument.querySelector('svg svg')?.unpauseAnimations()`);
  const movingBefore = await send('Page.captureScreenshot', {format:'png',clip:stillRect});
  await delay(240);
  const movingAfter = await send('Page.captureScreenshot', {format:'png',clip:stillRect});
  if (await evaluate(`(${pixelChanges.toString()})(${JSON.stringify(movingBefore.data)},${JSON.stringify(movingAfter.data)})`) <= 8) throw Error('Pixel check cannot detect the legacy moving-road bug');
  await evaluate(`(()=>{const s=document.querySelector('[data-slug="gpt-6.1-sol-xhigh"] iframe').contentDocument.querySelector('svg svg');s?.pauseAnimations();s?.setCurrentTime(0)})()`);
  await evaluate(`document.querySelector('#clear-filters').click();scrollTo({top:0,behavior:'instant'})`);
  const point = await evaluate(`(async()=>{const start=performance.now();while(!document.querySelector('.card iframe.loaded')){if(performance.now()-start>5000)throw Error('Artwork not ready');await new Promise(r=>setTimeout(r,30))}const rect=document.querySelector('.preview').getBoundingClientRect();return {x:rect.x+rect.width/2,y:rect.y+rect.height/2}})()`);
  await send('Input.dispatchMouseEvent', {type: 'mouseMoved', ...point});
  if (!await evaluate(`(async()=>{await new Promise(r=>setTimeout(r,180));return !document.querySelector('.card iframe.loaded').contentDocument.documentElement.animationsPaused()})()`)) throw new Error('Mouse hover did not play artwork');
  await send('Input.dispatchMouseEvent', {type: 'mouseMoved', x: 0, y: 0});
  if (!await evaluate(`(async()=>{await new Promise(r=>setTimeout(r,50));return document.querySelector('.card iframe.loaded').contentDocument.documentElement.animationsPaused()})()`)) throw new Error('Mouse leave did not pause artwork');
  const checks = await evaluate(`(${smoke.toString()})()`);
  await evaluate(`document.querySelector('#language').value='auto';document.querySelector('#language').dispatchEvent(new Event('change',{bubbles:true}))`);
  await send('Emulation.setUserAgentOverride', {userAgent, acceptLanguage: 'zh-CN,zh,en'});
  // A forced iframe navigation in the failure fixture creates child history entries.
  // Start a fresh top-level page instead of treating them as gallery navigation.
  await reload(process.argv[2] || 'http://localhost:8765');
  if (!await evaluate(`document.documentElement.lang==='zh-CN'&&document.querySelector('#language').value==='auto'&&document.querySelector('#search').placeholder==='搜索模型…'`)) throw new Error('Browser Chinese was not selected automatically');
  checks.push('paused road pixel stability with moving-road positive control', 'real hover playback', 'mouseleave pause', 'automatic browser Chinese');
  for (const choice of ['zh', 'en']) {
    await evaluate(`document.querySelector('#language').value='${choice}';document.querySelector('#language').dispatchEvent(new Event('change',{bubbles:true}))`);
    for (const width of [320,390,768,1024,1440,1920]) {
      await send('Emulation.setDeviceMetricsOverride', {width, height: 1000, deviceScaleFactor: 1, mobile: width < 600});
      const okay = await evaluate(`document.documentElement.scrollWidth<=innerWidth&&[...document.querySelectorAll('.card')].every(card=>card.scrollWidth<=card.clientWidth)`);
      if (!okay) throw new Error(`${choice} layout overflows at ${width}px`);
    }
  }
  checks.push('Chinese and English layouts at six widths');
  for (const choice of ['zh','en']) for (const width of [320,390,768,1440]) {
    await send('Emulation.setDeviceMetricsOverride', {width,height:1000,deviceScaleFactor:1,mobile:width<600});
    await evaluate(`document.querySelector('#language').value='${choice}';document.querySelector('#language').dispatchEvent(new Event('change',{bubbles:true}));for(const slug of ['gpt-6.1-sol-max','gpt-6.1-sol-xhigh','hy3-high','grok-4.7-xhigh']){const filter=document.querySelector('#reasoning');filter.value=slug.split('-').at(-1);filter.dispatchEvent(new Event('change',{bubbles:true}));const box=document.querySelector('[data-compare="'+slug+'"]');box.checked=true;box.dispatchEvent(new Event('change',{bubbles:true}))}`);
    if (!await evaluate(`document.querySelector('#compare-tray').scrollWidth<=document.querySelector('#compare-tray').clientWidth&&document.documentElement.scrollWidth<=innerWidth`)) throw Error(`${choice} four-item tray overflows at ${width}`);
    if (width>600 && !await evaluate(`(()=>{const a=document.querySelector('.tray-actions').getBoundingClientRect(),i=document.querySelector('.tray-items').getBoundingClientRect();return Math.abs(a.y+a.height/2-i.y-i.height/2)<1})()`)) throw Error(`${choice} four-item tray actions misaligned at ${width}`);
    await evaluate(`document.querySelector('#open-compare').click()`);
    if (!await evaluate(`(async()=>{const start=performance.now();while(document.querySelectorAll('#comparison-content iframe.loaded').length!==4){if(performance.now()-start>5000)throw Error('Four artworks not ready');await new Promise(r=>setTimeout(r,30))}const d=document.querySelector('#compare-dialog');return d.scrollWidth<=d.clientWidth&&[...document.querySelectorAll('.compare-artworks section')].every(s=>s.scrollWidth<=s.clientWidth)})()`)) throw Error(`${choice} four-item comparison overflows at ${width}`);
    await evaluate(`document.querySelector('#compare-dialog [data-close]').click()`);
    await evaluate(`(async()=>{while(document.querySelector('#compare-dialog').open)await new Promise(r=>setTimeout(r,20));document.querySelector('#clear-selection').click()})()`);
  }
  checks.push('four-way tray and comparison bilingual layouts');
  await reload(process.argv[2] || 'http://localhost:8765');
  if (!await evaluate(`document.documentElement.lang==='en-US'&&document.querySelector('#language').value==='en'`)) throw new Error('Manual language preference was not preserved');
  await send('Emulation.setEmulatedMedia', {features:[{name:'prefers-color-scheme',value:'dark'},{name:'prefers-reduced-motion',value:'no-preference'}]});
  if (!await evaluate(`(()=>{const linear=v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4},lum=c=>c.match(/[\\d.]+/g).slice(0,3).map(Number).map(linear).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);return [...document.querySelectorAll('.model-levels [aria-pressed="true"] .effort')].every(chip=>{const s=getComputedStyle(chip),a=lum(s.color),b=lum(s.backgroundColor);return (Math.max(a,b)+.05)/(Math.min(a,b)+.05)>=4.5})})()`)) throw Error('Dark-mode selected level text lacks contrast');
  await send('Emulation.setEmulatedMedia', {features:[{name:'forced-colors',value:'active'},{name:'prefers-reduced-motion',value:'no-preference'}]});
  if (!await evaluate(`[...document.querySelectorAll('.language-control,.filter-selects > label')].every(label=>getComputedStyle(label.querySelector('select')).appearance==='auto'&&getComputedStyle(label,'::after').display==='none')`)) throw Error('High contrast does not restore native select indicators');
  checks.push('dark selected-level contrast', 'high-contrast native select indicators');
  await send('Emulation.setEmulatedMedia', {features:[{name:'prefers-color-scheme',value:'light'},{name:'prefers-reduced-motion',value:'no-preference'}]});
  await send('Emulation.setDeviceMetricsOverride', {width:390,height:1000,deviceScaleFactor:1,mobile:true});
  await send('Emulation.setTouchEmulationEnabled', {enabled:true,maxTouchPoints:1});
  const levelTouch = await evaluate(`(()=>{const b=document.querySelector('[data-card-run="mimo-v2.6-pro-high"]');b.scrollIntoView({block:'center',behavior:'instant'});const r=b.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()`);
  await send('Input.dispatchTouchEvent', {type:'touchStart',touchPoints:[levelTouch]});
  await send('Input.dispatchTouchEvent', {type:'touchEnd',touchPoints:[]});
  if (!await evaluate(`!document.querySelector('dialog[open]')&&!new URLSearchParams(location.search).has('run')&&document.querySelector('[data-card-run="mimo-v2.6-pro-high"]').getAttribute('aria-pressed')==='true'`)) throw Error('Touch level selection opens a dialog instead of switching its card');
  await evaluate(`document.querySelector('[data-card-run="mimo-v2.6-pro-off"]').focus()`);
  await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',text:'\r',windowsVirtualKeyCode:13});
  await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});
  if (!await evaluate(`!document.querySelector('dialog[open]')&&document.activeElement.dataset.cardRun==='mimo-v2.6-pro-off'&&document.activeElement.getAttribute('aria-pressed')==='true'`)) throw Error('Keyboard level selection state: '+JSON.stringify(await evaluate(`({focus:document.activeElement.outerHTML,open:!!document.querySelector('dialog[open]'),slug:document.querySelector('[data-card-run="mimo-v2.6-pro-off"]').closest('.card').dataset.slug})`)));
  checks.push('touch level selection stays in list', 'keyboard Enter switches card and retains focus');
  await evaluate(`document.querySelector('.preview').scrollIntoView({block:'center',behavior:'instant'})`);
  const touch = await evaluate(`const rect=document.querySelector('.preview').getBoundingClientRect();({x:rect.x+rect.width/2,y:rect.y+20})`);
  await send('Input.dispatchTouchEvent', {type:'touchStart',touchPoints:[touch]});
  await send('Input.dispatchTouchEvent', {type:'touchEnd',touchPoints:[]});
  if (!await evaluate(`(async()=>{const start=performance.now();while(!document.querySelector('#detail-preview iframe.loaded')){if(performance.now()-start>5000)throw Error('Touch detail failed');await new Promise(r=>setTimeout(r,30))}return [...document.querySelector('#detail-preview iframe').contentDocument.querySelectorAll('svg')].every(clock=>!clock.animationsPaused())})()`)) throw new Error('Touch detail did not autoplay');
  if (!await evaluate(`!document.querySelector('#detail-dialog [data-motion],#detail-dialog [data-restart]')`)) throw new Error('Touch detail has playback controls');
  checks.push('persisted manual language', 'touch detail autoplay without controls');
  await send('Emulation.setEmulatedMedia', {features:[{name:'prefers-reduced-motion',value:'reduce'}]});
  if (!await evaluate(`(async()=>{await new Promise(r=>setTimeout(r,150));return [...document.querySelector('#detail-preview iframe').contentDocument.querySelectorAll('svg')].every(clock=>clock.animationsPaused())})()`)) throw Error('Reduced-motion preference was ignored');
  await send('Emulation.setEmulatedMedia', {features:[{name:'prefers-reduced-motion',value:'no-preference'}]});
  if (!await evaluate(`(async()=>{await new Promise(r=>setTimeout(r,150));return [...document.querySelector('#detail-preview iframe').contentDocument.querySelectorAll('svg')].every(clock=>!clock.animationsPaused())})()`)) throw Error('Detail did not resume when reduced motion was disabled');
  checks.push('autoplay respects reduced-motion preference changes');
  await reload(process.argv[2] || 'http://localhost:8765');
  await evaluate(`(()=>{const c=[...document.querySelectorAll('.card')].find(c=>JSON.parse(c.dataset.model)[1]==='GPT-6.1 Sol');c.querySelector('[data-compare-model]').click()})()`);
  if (!await evaluate(`(()=>{const d=document.querySelector('#detail-dialog'),top=document.querySelector('.detail-top').getBoundingClientRect(),close=d.querySelector('[data-close]').getBoundingClientRect(),overview=document.querySelector('#level-overview').getBoundingClientRect();return d.open&&d.scrollWidth<=d.clientWidth&&close.top>=0&&close.bottom<=innerHeight&&overview.top>=top.bottom-2})()`)) throw Error('Mobile picker hides its controls or overflows');
  await evaluate(`document.querySelector('.level-summary-wrap').focus()`);
  const pickerRun = await evaluate(`new URLSearchParams(location.search).get('run')`);
  await send('Input.dispatchKeyEvent',{type:'keyDown',key:'ArrowRight',code:'ArrowRight',windowsVirtualKeyCode:39});
  await send('Input.dispatchKeyEvent',{type:'keyUp',key:'ArrowRight',code:'ArrowRight',windowsVirtualKeyCode:39});
  await delay(150);
  if (!await evaluate(`document.querySelector('.level-summary-wrap').scrollLeft>0&&new URLSearchParams(location.search).get('run')===${JSON.stringify(pickerRun)}`)) throw Error('Overview arrow keys change level instead of scrolling its table');
  await evaluate(`document.querySelector('#detail-levels [data-level-run="gpt-6.1-sol-low"]').click();document.querySelector('#detail-levels [aria-pressed="true"]').focus()`);
  await send('Input.dispatchKeyEvent',{type:'keyDown',key:'ArrowRight',code:'ArrowRight',windowsVirtualKeyCode:39});
  await send('Input.dispatchKeyEvent',{type:'keyUp',key:'ArrowRight',code:'ArrowRight',windowsVirtualKeyCode:39});
  if (!await evaluate(`new URLSearchParams(location.search).get('run')==='gpt-6.1-sol-medium'&&document.activeElement.dataset.levelRun==='gpt-6.1-sol-medium'`)) throw Error('Keyboard level navigation loses selected state or focus');
  checks.push('mobile picker keeps close/level controls visible', 'overview keyboard scrolling does not navigate levels', 'keyboard level navigation retains focus');
  const oldFailure = new URL(process.argv[2] || 'http://localhost:8765');oldFailure.searchParams.set('run','claude-opus-5.5-max');
  await reload(oldFailure.href);
  if (!await evaluate(`document.querySelector('#detail-dialog').open&&!document.querySelector('#detail-preview iframe')&&document.querySelector('#detail-info').textContent.includes('128,000')&&document.querySelector('#detail-levels [aria-pressed="true"]').dataset.levelRun==='claude-opus-5.5-max'`)) throw Error('Old failed-run URL is not restored on reload');
  checks.push('old failed-run URL survives full reload');
  const queryUrl = new URL(process.argv[2] || 'http://localhost:8765');
  queryUrl.searchParams.set('q', 'g pt6');
  await reload(queryUrl.href);
  if (!await evaluate(`document.querySelector('#search').value==='g pt6'&&document.querySelector('#sort').value==='relevance'&&document.querySelector('.card:not([hidden])').dataset.slug.startsWith('gpt-6')`)) throw Error('Search URL did not survive a full reload');
  checks.push('fuzzy search survives full reload');
  queryUrl.searchParams.set('sort', 'newest');
  await reload(queryUrl.href);
  if (!await evaluate(`document.querySelector('#sort').value==='newest'&&document.querySelector('#search').value==='g pt6'`)) throw Error('Explicit newest sort did not survive reload');
  checks.push('explicit search sort survives full reload');
  await send('Emulation.setTouchEmulationEnabled', {enabled:false});
  for (const slug of ['claude-opus-5.5-max', 'claude-sonnet-5.5-max']) {
    const caseUrl = new URL('cases/' + slug + '/', process.argv[2] || 'http://localhost:8765/').href;
    await send('Page.navigate', {url:caseUrl});
    let ready = false;
    for (let attempt=0;attempt<100;attempt++) {
      try { if (await evaluate(`location.href===${JSON.stringify(caseUrl)}&&document.readyState==='complete'&&document.querySelector('.case-page')&&document.title.includes('SVG')`)) {ready=true;break;} } catch {}
      await delay(50);
    }
    if (!ready) throw Error('Failure page did not initialize: ' + slug);
    if (!await evaluate(`!document.querySelector('iframe,[download],[data-motion]')&&document.querySelector('.case-related').href.includes('xhigh')&&document.querySelector('.skip-link').href===location.href+'#case'&&document.querySelector('.brand').href===new URL('../../',location.href).href`)) throw Error('Failure page links or state invalid');
    checks.push('standalone failure page links and no false artwork: ' + slug);
    await evaluate(`document.querySelector('#language').value='auto';document.querySelector('#language').dispatchEvent(new Event('change',{bubbles:true}))`);
    await send('Page.reload');
    let autoChinese = false;
    for (let attempt=0;attempt<100;attempt++) {
      try { if (await evaluate(`document.readyState==='complete'&&document.documentElement.lang==='zh-CN'&&document.querySelector('#language').value==='auto'&&document.title.includes('未交付 SVG')`)) {autoChinese=true;break;} } catch {}
      await delay(50);
    }
    if (!autoChinese) throw Error('Failure page did not automatically select browser Chinese');
    checks.push('failure page automatic browser language: ' + slug);
    for (const choice of ['zh','en']) {
      await evaluate(`document.querySelector('#language').value='${choice}';document.querySelector('#language').dispatchEvent(new Event('change',{bubbles:true}))`);
      if (!await evaluate(`document.documentElement.lang.startsWith('${choice}')&&getComputedStyle(document.querySelector('.case-copy[lang="${choice}"]')).display!=='none'&&getComputedStyle(document.querySelector('.case-copy[lang="${choice==='zh'?'en':'zh'}"]')).display==='none'`)) throw Error('Failure page locale incorrect');
      for (const width of [320,390,768,1440]) {
        await send('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:width<600});
        if (!await evaluate(`document.documentElement.scrollWidth<=innerWidth&&document.querySelector('.case-page').scrollWidth<=document.querySelector('.case-page').clientWidth`)) throw Error('Failure page overflow: '+slug+' '+choice+' '+width);
      }
    }
    if (!await evaluate(slug.includes('opus') ? `document.querySelector('.case-page').textContent.includes('128,000')&&document.querySelector('.case-page').textContent.includes('Response was truncated before completion')` : `!document.querySelector('.case-page').textContent.includes('128,000')&&document.querySelector('.case-page').textContent.includes('64,000')`)) throw Error('Failure evidence boundaries incorrect');
    if (!await evaluate(`document.querySelector('.case-sources a').href.startsWith('https://pi.dev/session/#')&&document.querySelector('.case-sources a:nth-child(2)').href.startsWith('https://gist.github.com/')&&document.querySelector('.case-page').textContent.includes('incomplete.max_output_tokens')`)) throw Error('Failure session sources missing');
    checks.push('bilingual failure evidence, public sources and four widths: ' + slug);
    await evaluate(`document.querySelector('.case-related').click()`);
    let artwork = false;
    for (let attempt=0;attempt<100;attempt++) {
      try { if (await evaluate(`document.querySelector('#detail-dialog')?.open&&document.querySelector('#detail-preview iframe.loaded')&&new URLSearchParams(location.search).get('run')===${JSON.stringify(slug.replace('-max','-xhigh'))}`)) {artwork=true;break;} } catch {}
      await delay(50);
    }
    if (!artwork) throw Error('Failure page did not link to xhigh artwork');
    checks.push('failure page to delivered xhigh artwork: ' + slug);
  }
  await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
  await reload(process.argv[2] || 'http://localhost:8765');
  await send('Input.dispatchMouseEvent', {type:'mouseMoved',x:0,y:0});
  for (const slug of ['claude-sonnet-5.5-xhigh','claude-opus-5.5-xhigh','claude-fable-5.1-xhigh','claude-fable-5.1-max']) {
    await evaluate(`document.querySelector('#reasoning').value='${slug.split('-').at(-1)}';document.querySelector('#reasoning').dispatchEvent(new Event('change',{bubbles:true}))`);
    const clip = await evaluate(`(async()=>{const f=document.querySelector('[data-slug="${slug}"] iframe');f.scrollIntoView({block:'center',behavior:'instant'});const start=performance.now();while(!f.classList.contains('loaded')){if(performance.now()-start>5000)throw Error('Claude artwork not ready');await new Promise(r=>setTimeout(r,30))}await f.contentDocument.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));if(![...f.contentDocument.querySelectorAll('svg')].every(s=>s.animationsPaused())||!f.contentDocument.getAnimations().every(a=>a.playState==='paused'))throw Error('New Claude has active animation');const r=f.getBoundingClientRect();return {x:r.x+scrollX,y:r.y+scrollY,width:r.width,height:r.height,scale:1}})()`);
    let before = await send('Page.captureScreenshot',{format:'png',clip});
    await delay(240);
    let after = await send('Page.captureScreenshot',{format:'png',clip});
    let changed = await evaluate(`(${pixelChanges.toString()})(${JSON.stringify(before.data)},${JSON.stringify(after.data)})`);
    if (changed>8) {
      before=after;await delay(400);after=await send('Page.captureScreenshot',{format:'png',clip});
      changed=await evaluate(`(${pixelChanges.toString()})(${JSON.stringify(before.data)},${JSON.stringify(after.data)})`);
    }
    if (changed>8) throw Error('New Claude artwork moves while paused: '+slug+' '+changed+' pixels');
    checks.push('new Claude paused pixels and all clocks: '+slug);
  }
  if (process.env.UI_SCREENSHOT_DIR) {
    await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1200,deviceScaleFactor:1,mobile:false});
    await reload(process.argv[2] || 'http://localhost:8765');
    await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:0,y:0});
    await evaluate(`document.querySelector('#language').value='zh';document.querySelector('#language').dispatchEvent(new Event('change',{bubbles:true}))`);
    await delay(300);
    await writeFile(join(process.env.UI_SCREENSHOT_DIR,'models-desktop.png'),Buffer.from((await send('Page.captureScreenshot',{format:'png'})).data,'base64'));
    await send('Emulation.setDeviceMetricsOverride',{width:390,height:1400,deviceScaleFactor:1,mobile:true});
    await delay(200);
    await writeFile(join(process.env.UI_SCREENSHOT_DIR,'models-mobile.png'),Buffer.from((await send('Page.captureScreenshot',{format:'png'})).data,'base64'));
    await send('Emulation.setDeviceMetricsOverride',{width:390,height:1000,deviceScaleFactor:1,mobile:true});
    await evaluate(`[...document.querySelectorAll('.card')].find(c=>JSON.parse(c.dataset.model)[1]==='Claude Sonnet 5.5').querySelector('[data-compare-model]').click()`);
    await delay(200);
    await writeFile(join(process.env.UI_SCREENSHOT_DIR,'levels-mobile.png'),Buffer.from((await send('Page.captureScreenshot',{format:'png'})).data,'base64'));
  }
  console.log(`PASS · real Chrome · ${checks.length} interaction / locale / hover / layout checks`);
} finally {
  socket?.close();
  if (browser.exitCode === null && !launchError) {
    const exited = once(browser, 'exit'); browser.kill(); await exited;
  }
  await rm(profile, {recursive: true, force: true});
}
