const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[char]));
let nextHint = 0;
let installed = false;

export function renderPriceAssumption(price, lang = 'en') {
  if (!Number.isFinite(price?.amount_usd) || price?.estimate_kind !== 'conditional_assumption') return '';
  const label = price.assumption_label;
  const text = typeof label === 'string' ? label : label?.[String(lang).toLowerCase().startsWith('zh') ? 'zh' : 'en'] ?? label?.en;
  return text ? `<span class="price-assumption">${escape(text)}</span>` : '';
}

export function renderPrice(price, formattedValue, lang = 'en', id, {showAssumption = true} = {}) {
  const value = `<span data-price-value>${escape(formattedValue)}</span>`;
  const conditions = price?.conditions;
  const assumption = showAssumption ? renderPriceAssumption(price, lang) : '';
  const wrap = markup => assumption ? `<span class="price-with-assumption">${markup}${assumption}</span>` : markup;
  if (!Number.isFinite(price?.amount_usd) || !Array.isArray(conditions) || !conditions.length) return wrap(`<span class="price-estimate">${value}</span>`);
  const zh = String(lang).toLowerCase().startsWith('zh');
  const text = item => typeof item === 'string' ? item : item?.[zh ? 'zh' : 'en'] ?? item?.en ?? '';
  const amount = number => `≈$${new Intl.NumberFormat(zh ? 'zh-CN' : 'en-US', {minimumFractionDigits: 3, maximumFractionDigits: 8}).format(number)} USD`;
  const tooltipId = id ?? `price-hint-dynamic-${++nextHint}`;
  const title = zh ? '条件价格估算' : 'Conditional price estimate';
  const current = zh ? '当前估算' : 'Current estimate';
  const note = zh ? '以下金额均按同一条记录的用量，在对应计价条件下估算，不代表实际扣费。' : 'All amounts estimate the same record’s usage under the stated pricing conditions; they are not actual charges.';
  const details = conditions.map(condition => {
    const alternatives = (condition.alternatives || []).map(alternative => {
      const estimate = Number.isFinite(alternative.amount_usd) ? amount(alternative.amount_usd) : alternative.reason === 'not_announced' ? (zh ? '未公布，无法估算' : 'Not announced; cannot estimate') : (zh ? '未知' : 'Unknown');
      return `<span class="price-tooltip-alternative"><strong>${escape(text(alternative.label))}</strong><span>${escape(estimate)}</span>${alternative.description ? `<span class="price-tooltip-description">${escape(text(alternative.description))}</span>` : ''}</span>`;
    }).join('');
    return `<span class="price-tooltip-condition"><strong>${escape(text(condition.label))}</strong><span class="price-tooltip-description">${escape(text(condition.description))}</span>${alternatives}</span>`;
  }).join('');
  return wrap(`<span class="price-estimate">${value}<button class="price-warning" type="button" data-price-hint="${escape(tooltipId)}" aria-describedby="${escape(tooltipId)}" aria-expanded="false" aria-label="${escape(title)}"><span aria-hidden="true">!</span></button><span class="price-tooltip" id="${escape(tooltipId)}" role="tooltip" popover="manual"><span class="price-tooltip-heading">${escape(title)}</span><span class="price-tooltip-current">${escape(current)}: ${escape(amount(price.amount_usd))}</span><span class="price-tooltip-note">${escape(note)}</span>${details}</span></span>`);
}

export function installPriceHints() {
  if (installed) return;
  installed = true;
  let active = null, closeTimer;
  const warning = target => target.closest?.('.price-warning[data-price-hint]');
  const inside = target => target instanceof Node && active && (active.button.contains(target) || active.tooltip.contains(target));
  const clearClose = () => { clearTimeout(closeTimer); };
  const close = () => {
    clearClose();
    if (!active) return;
    const {button, tooltip} = active;
    active = null;
    button.setAttribute('aria-expanded', 'false');
    if (tooltip.matches(':popover-open')) tooltip.hidePopover();
  };
  const position = () => {
    const {button, tooltip} = active, anchor = button.getBoundingClientRect();
    const viewport = window.visualViewport, margin = 12, gap = 8;
    const left = (viewport?.offsetLeft || 0) + margin, top = (viewport?.offsetTop || 0) + margin;
    const width = Math.max(0, (viewport?.width ?? innerWidth) - margin * 2);
    const height = Math.max(0, (viewport?.height ?? innerHeight) - margin * 2);
    tooltip.style.maxWidth = `${width}px`; tooltip.style.maxHeight = `${height}px`;
    const below = top + height - anchor.bottom - gap, above = anchor.top - top - gap;
    const placeBelow = tooltip.getBoundingClientRect().height <= below || below >= above;
    tooltip.style.maxHeight = `${Math.min(height, Math.max(96, placeBelow ? below : above))}px`;
    const rect = tooltip.getBoundingClientRect();
    tooltip.style.left = `${Math.max(left, Math.min(anchor.left + anchor.width / 2 - rect.width / 2, left + width - rect.width))}px`;
    tooltip.style.top = `${Math.max(top, Math.min(placeBelow ? anchor.bottom + gap : anchor.top - gap - rect.height, top + height - rect.height))}px`;
  };
  const show = (button, keyboard = false) => {
    clearClose();
    if (active?.button === button) { active.keyboard ||= keyboard; return; }
    close();
    const tooltip = document.getElementById(button.dataset.priceHint);
    if (!tooltip?.matches('.price-tooltip[popover]') || !tooltip.showPopover) return;
    active = {button, tooltip, keyboard, pinned: false};
    try {
      tooltip.showPopover(); button.setAttribute('aria-expanded', 'true'); position();
    } catch { close(); }
  };
  const leave = () => {
    clearClose();
    if (active && !active.pinned && !active.keyboard) closeTimer = setTimeout(close, 180);
  };
  document.addEventListener('pointerover', event => {
    if (event.pointerType === 'touch') return;
    const button = warning(event.target);
    if (button) show(button);
    else if (inside(event.target)) clearClose();
  }, true);
  document.addEventListener('pointerout', event => {
    if (event.pointerType !== 'touch' && inside(event.target) && !inside(event.relatedTarget)) leave();
  }, true);
  document.addEventListener('focusin', event => {
    const button = warning(event.target);
    if (button) show(button, true);
    else if (active && !inside(event.target)) close();
  }, true);
  document.addEventListener('focusout', event => {
    if (inside(event.target) && !inside(event.relatedTarget)) close();
  }, true);
  document.addEventListener('pointerdown', event => { if (active && !inside(event.target)) close(); }, true);
  document.addEventListener('click', event => {
    const button = warning(event.target);
    if (!button) { if (active && !inside(event.target)) close(); return; }
    event.preventDefault(); event.stopImmediatePropagation();
    if (active?.button === button && active.pinned) close();
    else { show(button); if (active) active.pinned = true; }
  }, true);
  // Cancel Escape before the enclosing detail/comparison dialog sees it.
  window.addEventListener('keydown', event => {
    if (event.key !== 'Escape' || !active) return;
    event.preventDefault(); event.stopImmediatePropagation(); close();
  }, true);
  document.addEventListener('cancel', event => {
    if (!active) return;
    event.preventDefault(); event.stopImmediatePropagation(); close();
  }, true);
  document.addEventListener('close', close, true);
  document.addEventListener('toggle', event => {
    if (event.target === active?.tooltip && !active.tooltip.matches(':popover-open')) close();
  }, true);
  window.addEventListener('scroll', event => {
    if (active && !(event.target instanceof Node && active.tooltip.contains(event.target))) close();
  }, true);
  window.addEventListener('resize', close);
  window.visualViewport?.addEventListener('resize', close);
  window.visualViewport?.addEventListener('scroll', close);
  window.addEventListener('pagehide', close);
  document.addEventListener('visibilitychange', () => { if (document.hidden) close(); });
  // Replaced level/language markup must not leave an orphan in the top layer.
  new MutationObserver(records => {
    if (active && (!active.button.isConnected || !active.tooltip.isConnected || records.some(record => record.type === 'attributes'))) close();
  }).observe(document.documentElement, {subtree: true, childList: true, attributes: true, attributeFilter: ['lang', 'hidden', 'open', 'data-slug']});
}
