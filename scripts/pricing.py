"""Official API token estimates from one reviewed snapshot; never use Pi costs."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation


def rate(value):
    try:
        amount = Decimal(str(value))
        return amount if amount.is_finite() and amount >= 0 else None
    except (InvalidOperation, ValueError, TypeError):
        return None


def find_price(run, snapshot):
    if snapshot.get('schema_version') != 2 or len(run['model_ids']) != 1:
        return None
    for model_id, profile in snapshot.get('models', {}).items():
        if (profile.get('source_kind') == 'official' and profile['vendor'] == run['vendor']
                and run['model_ids'][0] in [model_id, *profile.get('aliases', [])]):
            return {**profile, 'model_id': model_id, 'checked_at': snapshot['as_of']}
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


def off_peak(run):
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
        if day.weekday() < 5:
            for begin, finish in ((1, 4), (6, 10)):
                if start < day + timedelta(hours=finish) and end >= day + timedelta(hours=begin):
                    return False
    return True


def display_price(run, snapshot):
    profile = find_price(run, snapshot)
    if not profile:
        return {'amount_usd': None, 'basis': 'unknown', 'reason': 'not_found'}
    reviewed = snapshot.get('runs', {}).get(run['slug'])
    public = {key: value for key, value in profile.items() if key not in ('vendor', 'aliases', 'source_kind', 'unavailable', 'off_peak_only')}
    tokens = run.get('metrics', {}).get('tokens', {})
    reason = None
    if reviewed:
        source = reviewed.get('source', {})
        if not source or any(run.get('source', {}).get(key) != value for key, value in source.items()):
            reason = 'source_changed'
        elif run.get('outcome') == 'no_artwork':
            tokens = reviewed.get('tokens', {})
    if not reason and profile.get('off_peak_only') and not off_peak(run):
        reason = 'conditional_price'
    amount = None
    if not reason:
        amount, reason = estimate(tokens, profile, (reviewed or {}).get('cache_write_ttl_seconds'))
    return {**public, 'amount_usd': amount, 'basis': 'official' if amount is not None else 'unknown', 'reason': reason}


def report(runs, snapshot):
    """Read-only coverage check; official quotes must be reviewed before editing the snapshot."""
    for run in runs:
        price = display_price(run, snapshot)
        print(f"{run['slug']}: {price['amount_usd']} USD" if price['amount_usd'] is not None
              else f"{run['slug']}: unavailable ({price['reason']})")
