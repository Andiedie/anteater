"""Official API token estimates from one reviewed snapshot; never use Pi costs."""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation


def rate(value):
    try:
        amount = Decimal(str(value))
        return amount if amount.is_finite() and amount >= 0 else None
    except (InvalidOperation, ValueError, TypeError):
        return None


def historical_price(run, profile):
    """Select one official historical quote covering the recorded model run."""
    try:
        stamp = datetime.fromisoformat(run['date'].replace('Z', '+00:00'))
        duration = rate(run['metrics']['duration_seconds'])
        if stamp.tzinfo is None or duration is None:
            return None
        start = stamp.astimezone(timezone.utc)
        end = start + timedelta(seconds=float(duration))
        matches = [quote for quote in profile.get('historical_rates', [])
                   if quote.get('source_kind') == 'official'
                   and date.fromisoformat(quote['valid_from']) <= start.date()
                   and end.date() <= date.fromisoformat(quote['valid_until'])]
    except (KeyError, TypeError, ValueError, OverflowError):
        return None
    if len(matches) != 1:
        return None
    quote = matches[0]
    start, end = quote['valid_from'], quote['valid_until']
    historical = {'kind': 'historical',
                  'label': {'en': 'Historical official rates', 'zh': '历史官方费率'},
                  'description': {'en': f'This retired model uses its historical manufacturer rates. The entire recorded interval must fall within the reviewed UTC dates {start} through {end}. There is no current on-sale quote.',
                                  'zh': f'此已下架型号采用当时的原厂费率；整段运行须位于核验覆盖的 UTC 日期 {start} 至 {end} 内，当前无在售报价。'},
                  'alternatives': []}
    return {**profile, **quote, 'unavailable': False,
            'conditions': [historical, *quote.get('conditions', [])],
            'historical_rate_period': {key: quote[key] for key in ('valid_from', 'valid_until')}}


def find_price(run, snapshot):
    if snapshot.get('schema_version') != 2 or len(run['model_ids']) != 1:
        return None
    for model_id, profile in snapshot.get('models', {}).items():
        if (profile.get('source_kind') == 'official' and profile['vendor'] == run['vendor']
                and run['model_ids'][0] in [model_id, *profile.get('aliases', [])]):
            resolved = (historical_price(run, profile) or profile) if profile.get('unavailable') else profile
            return {**resolved, 'model_id': model_id, 'checked_at': snapshot['as_of']}
    return None


def estimate(tokens, profile, cache_write_ttl_seconds=None):
    if profile.get('unavailable'):
        return None, 'not_found'
    fields = ('input', 'output', 'cacheRead', 'cacheWrite')
    amounts = {key: rate(tokens.get(key)) for key in fields}
    if any(value is None for value in amounts.values()):
        return None, 'missing_usage'
    ttl = profile.get('cache_write_ttl_seconds')
    if amounts['cacheWrite'] and ttl and cache_write_ttl_seconds != ttl:
        return None, 'cache_write_duration'
    input_total = amounts['input'] + amounts['cacheRead'] + amounts['cacheWrite']
    # shortcut: aggregate usage cannot select per-request tiers; retain per-turn usage when needed.
    if profile.get('input_threshold') is not None and input_total > profile['input_threshold']:
        return None, 'per_request_usage'
    rates = profile['rates_per_million']
    if any(amounts[key] and rate(rates.get(key)) is None for key in fields):
        return None, 'missing_cache_price'
    amount = sum(amounts[key] * (rate(rates.get(key)) or Decimal(0)) for key in fields)
    reasoning_rate = rate(rates.get('reasoning'))
    if reasoning_rate is not None and reasoning_rate != rate(rates['output']):
        reasoning = rate(tokens.get('reasoning'))
        if reasoning is None or reasoning > amounts['output']:
            return None, 'missing_usage'
        # Reported output already includes reasoning, so replace its rate rather than adding it.
        amount += reasoning * (reasoning_rate - rate(rates['output']))
    return float((amount / 1000000).quantize(Decimal('0.0000000001'))), None


def off_peak(run, weekdays_only=True):
    """Prove the entire recorded interval is off-peak, without guessing holiday status."""
    try:
        start = datetime.fromisoformat(run['date'].replace('Z', '+00:00'))
        duration = run['metrics']['duration_seconds']
        if start.tzinfo is None or rate(duration) is None or duration > 86400:
            return False
        start = start.astimezone(timezone.utc)
        end = start + timedelta(seconds=duration)
    except (KeyError, TypeError, ValueError):
        return False
    for offset in range((end.date() - start.date()).days + 1):
        day = start.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=offset)
        if not weekdays_only or day.weekday() < 5:
            for begin, finish in ((1, 4), (6, 10)):
                if start < day + timedelta(hours=finish) and end >= day + timedelta(hours=begin):
                    return False
    return True


def reviewed_cache_profile(tokens, profile, reviewed):
    """Keep zero-cache base estimates separate from reviewed cache assumptions."""
    try:
        source = reviewed['source']
        required_pins = ('gist_id', 'gist_revision', 'session_id', 'artwork_sha256')
        if any(not isinstance(source.get(key), str) or not source[key] for key in required_pins):
            return None
        if reviewed['model_id'] != profile['model_id']:
            return None
        fields = ('input', 'output', 'cacheRead', 'cacheWrite')
        if any(type(tokens.get(key)) is not int or tokens[key] < 0
               or type(reviewed['reviewed_tokens'].get(key)) is not int
               or tokens[key] != reviewed['reviewed_tokens'][key] for key in fields):
            return None
        if tokens['cacheWrite'] != 0:
            return None
        if reviewed.get('cache_rates_unused') is True:
            return profile if tokens['cacheRead'] == 0 and 'estimate_assumptions' not in reviewed else None
        if (reviewed['historical_cache_mode'] is not None
                or reviewed['estimate_assumptions'] != {'cache_mode': 'implicit'}):
            return None
        condition = reviewed['condition']
        alternatives = condition['alternatives']
        if condition['kind'] != 'cache_mode_assumption' or len(alternatives) != 1:
            return None
        alternative = alternatives[0]
        if (alternative['cache_mode'] != 'explicit'
                or alternative['id'] != 'explicit_same_recorded_usage'):
            return None
        localized = (reviewed['assumption_label'], condition['label'],
                     condition['description'], alternative['label'])
        if any(not isinstance(text.get(lang), str) or not text[lang].strip()
               for text in localized for lang in ('en', 'zh')):
            return None
        options = profile['cache_rate_options']
        for mode in ('implicit', 'explicit'):
            if any(rate(options[mode].get(key)) is None for key in ('input', 'output', 'cacheRead')):
                return None
        if rate(options['explicit'].get('cacheWrite')) is None:
            return None
    except (KeyError, TypeError, AttributeError, IndexError):
        return None
    return {**profile, 'rates_per_million': options['implicit'],
            'estimate_kind': 'conditional_assumption',
            'assumption_label': reviewed['assumption_label'], 'historical_cache_mode': None,
            'conditions': [*profile.get('conditions', []),
                           {**condition, 'alternatives': [{**alternative, 'rates_per_million': options['explicit']}]}]}


def conditional_estimates(tokens, profile, cache_write_ttl_seconds=None):
    """Reprice the same recorded usage using explicitly reviewed alternative rates."""
    conditions = []
    for condition in profile.get('conditions', []):
        fields = condition.get('applies_to', ('input', 'output', 'cacheRead', 'cacheWrite'))
        if (condition.get('kind') != 'cache_mode_assumption'
                and not any((rate(tokens.get(field)) or Decimal(0)) > 0 for field in fields)):
            continue
        alternatives = []
        for alternative in condition.get('alternatives', []):
            rates = alternative.get('rates_per_million')
            amount, reason = (None, 'not_announced') if rates is None else estimate(
                tokens, {**profile, 'rates_per_million': rates}, cache_write_ttl_seconds)
            alternatives.append({**alternative, 'amount_usd': amount, 'reason': reason})
        conditions.append({**condition, 'alternatives': alternatives})
    return conditions


def display_price(run, snapshot):
    profile = find_price(run, snapshot)
    if not profile:
        return {'amount_usd': None, 'basis': 'unknown', 'reason': 'not_found'}
    reviewed = snapshot.get('runs', {}).get(run['slug'])
    public_fields = ('source', 'source_url', 'rates_per_million', 'rate_note', 'model_id', 'checked_at',
                     'input_threshold', 'cache_write_ttl_seconds', 'historical_rate_period',
                     'region', 'deployment_scope')
    public = {key: profile[key] for key in public_fields if key in profile}
    tokens = run.get('metrics', {}).get('tokens', {})
    reason = None
    if reviewed:
        source = reviewed.get('source', {})
        if not source or any(run.get('source', {}).get(key) != value for key, value in source.items()):
            reason = 'source_changed'
        elif run.get('outcome') == 'no_artwork':
            tokens = reviewed.get('tokens', {})
    assumption = {}
    if not reason and ('cache_rate_options' in profile or (reviewed or {}).get('estimate_assumptions')):
        selected = reviewed_cache_profile(tokens, profile, reviewed)
        if selected is None:
            reason = 'conditional_price'
        else:
            profile = selected
            public['rates_per_million'] = profile['rates_per_million']
            assumption = {key: profile[key] for key in ('estimate_kind', 'assumption_label', 'historical_cache_mode')
                          if key in profile}
    if not reason and profile.get('off_peak_only') and not off_peak(run, profile.get('off_peak_weekdays_only', True)):
        reason = 'conditional_price'
    amount = None
    if not reason:
        amount, reason = estimate(tokens, profile, (reviewed or {}).get('cache_write_ttl_seconds'))
    conditions = conditional_estimates(tokens, profile, (reviewed or {}).get('cache_write_ttl_seconds')) if amount is not None else []
    return {**public, **(assumption if amount is not None else {}), 'amount_usd': amount, 'basis': 'official' if amount is not None else 'unknown', 'reason': reason, 'conditions': conditions}


def report(runs, snapshot):
    """Read-only coverage check; official quotes must be reviewed before editing the snapshot."""
    for run in runs:
        price = display_price(run, snapshot)
        assumption = (f" (conditional assumption: {price['assumption_label']['en']}; historical cache mode unverified)"
                      if price.get('estimate_kind') == 'conditional_assumption' else '')
        print(f"{run['slug']}: {price['amount_usd']} USD{assumption}" if price['amount_usd'] is not None
              else f"{run['slug']}: unavailable ({price['reason']})")
