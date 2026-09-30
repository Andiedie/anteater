"""Public text-token price snapshots; raw Pi costs are never overwritten."""

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import re
import sys
from urllib.request import Request

SOURCES = {
    "models.dev": "https://models.dev/api.json",
    "OpenRouter": "https://openrouter.ai/api/v1/models",
    "LiteLLM": "https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json",
}
MAKERS = {"OpenAI": ("openai", "openai"), "Anthropic": ("anthropic", "anthropic"),
          "Google": ("google", "google"), "DeepSeek": ("deepseek", "deepseek"),
          "xAI": ("xai", "x-ai"), "Z.ai": ("zai", "z-ai"), "Tencent": ("tencent", "tencent"),
          "Xiaomi": ("xiaomi", "xiaomi"), "Meta": ("meta", "meta")}
# This adapter appends configured thinking effort to the Gemini model ID.
ALIASES = {"gemini-3.8-flash-high": "gemini-3.8-flash"}


def rate(value, multiplier=1):
    try:
        amount = Decimal(str(value)) * multiplier
        return float(amount) if amount.is_finite() and amount >= 0 else None
    except (InvalidOperation, ValueError, TypeError):
        return None


def normalize(source, model):
    if source == "models.dev":
        raw = model.get("cost", {})
        fields = {"input": "input", "output": "output", "cacheRead": "cache_read", "cacheWrite": "cache_write", "reasoning": "reasoning"}
        thresholds = [tier["tier"]["size"] for tier in raw.get("tiers", []) if tier.get("tier", {}).get("type") == "context"]
        complex_price = any(tier.get("tier", {}).get("type") != "context" for tier in raw.get("tiers", []))
        if not thresholds and raw.get("context_over_200k"):
            thresholds = [200000]
        multiplier = 1
    elif source == "OpenRouter":
        raw = model.get("pricing", {})
        fields = {"input": "prompt", "output": "completion", "cacheRead": "input_cache_read", "cacheWrite": "input_cache_write", "reasoning": "internal_reasoning"}
        overrides = raw.get("overrides", [])
        thresholds = [tier["min_prompt_tokens"] - 1 for tier in overrides if "min_prompt_tokens" in tier]
        request_fee = rate(raw.get("request", 0))
        complex_price = any("min_prompt_tokens" not in tier for tier in overrides) or request_fee is None or request_fee != 0
        multiplier = 1000000
    else:
        raw = model
        fields = {"input": "input_cost_per_token", "output": "output_cost_per_token", "cacheRead": "cache_read_input_token_cost", "cacheWrite": "cache_creation_input_token_cost", "reasoning": "output_cost_per_reasoning_token"}
        thresholds = [int(n) * (1000 if suffix == "k" else 1000000 if suffix == "m" else 1)
                      for key in raw for n, suffix in re.findall(r"_above_(\d+)([km]?)_tokens", key)]
        complex_price = False
        multiplier = 1000000
    rates = {name: rate(raw.get(key), multiplier) for name, key in fields.items()}
    if rates["input"] is None or rates["output"] is None:
        return None
    return {"rates_per_million": rates, "input_threshold": min(thresholds) if thresholds else None,
            "complex_pricing": complex_price}


def find_price(run, catalogs):
    if len(run["model_ids"]) != 1 or run["vendor"] not in MAKERS:
        return None
    requested = run["model_ids"][0]
    model_id = ALIASES.get(requested, requested)
    maker, namespace = MAKERS[run["vendor"]]
    base = model_id.removeprefix(namespace + "/")
    router_id = namespace + "/" + base
    candidates = []
    if run.get("providers") == ["openrouter"]:
        candidates.append(("OpenRouter", router_id, catalogs.get("OpenRouter", {}).get(router_id)))
    model = catalogs.get("models.dev", {}).get(maker, {}).get("models", {}).get(base)
    candidates.append(("models.dev", maker + "/" + base, model))
    candidates.append(("OpenRouter", router_id, catalogs.get("OpenRouter", {}).get(router_id)))
    lite_prefix = "gemini" if maker == "google" else maker
    for key in (lite_prefix + "/" + base, base):
        model = catalogs.get("LiteLLM", {}).get(key)
        if model and (str(model.get("litellm_provider", "")).startswith(lite_prefix) or maker == "google" and str(model.get("litellm_provider", "")).startswith("vertex_ai")):
            candidates.append(("LiteLLM", key, model))
    for source, exact_id, model in candidates:
        if model and (normalized := normalize(source, model)):
            return {"source": source, "source_url": SOURCES[source], "model_id": exact_id,
                    "requested_model": requested, **normalized,
                    **({"cache_write_ttl_required": True} if run["vendor"] == "Anthropic" else {})}
    return None


def estimate(tokens, profile):
    if profile.get("complex_pricing"):
        return None, "conditional_price"
    fields = ("input", "output", "cacheRead", "cacheWrite")
    amounts = {key: tokens.get(key) for key in fields}
    if any(rate(value) is None for value in amounts.values()):
        return None, "missing_usage"
    # ponytail: combined Anthropic cache writes omit TTL; retain per-TTL usage to price them.
    if profile.get("cache_write_ttl_required") and amounts["cacheWrite"]:
        return None, "cache_write_duration"
    input_total = amounts["input"] + amounts["cacheRead"] + amounts["cacheWrite"]
    # ponytail: aggregate usage cannot select per-request tiers; store per-turn usage if needed.
    if profile.get("input_threshold") is not None and input_total > profile["input_threshold"]:
        return None, "per_request_usage"
    rates = profile["rates_per_million"]
    if any(amounts[key] and rates.get(key) is None for key in fields):
        return None, "missing_cache_price"
    amount = sum(Decimal(str(amounts[key])) * Decimal(str(rates.get(key) or 0)) for key in fields)
    reasoning_rate = rates.get("reasoning")
    if reasoning_rate is not None and reasoning_rate != rates["output"]:
        reasoning = tokens.get("reasoning")
        if rate(reasoning) is None or reasoning > amounts["output"]:
            return None, "missing_usage"
        # Pi output includes reasoning; replace its rate, never add the tokens again.
        amount += Decimal(str(reasoning)) * (Decimal(str(reasoning_rate)) - Decimal(str(rates["output"])))
    return float((amount / 1000000).quantize(Decimal("0.0000000001"))), None


def display_price(run, snapshot):
    recorded = run["metrics"]["cost_usd"]
    if recorded is not None:
        return {"amount_usd": recorded, "basis": "recorded"}
    profile = snapshot.get("runs", {}).get(run["slug"])
    if not profile or run["model_ids"] != [profile.get("requested_model")]:
        return {"amount_usd": None, "basis": "unknown", "reason": "not_found"}
    amount, reason = estimate(run["metrics"]["tokens"], profile)
    public = {key: value for key, value in profile.items() if key != "requested_model"}
    return {**public, "amount_usd": amount, "basis": "public" if amount is not None else "unknown", "reason": reason}


def refresh(runs, destination, fetch):
    now = datetime.now(timezone.utc).isoformat()
    catalogs, sources = {}, []
    for name, url in SOURCES.items():
        try:
            raw = fetch(Request(url, headers={"User-Agent": "anteater-gallery"}))
            data = json.loads(raw)
            catalogs[name] = {model["id"]: model for model in data["data"]} if name == "OpenRouter" else data
            sources.append({"name": name, "url": url, "fetched_at": now, "sha256": sha256(raw).hexdigest()})
        except (OSError, ValueError, KeyError) as error:
            print(f"Warning: {name}: {error}", file=sys.stderr)
    if not catalogs:
        raise ValueError("No public pricing source was reachable; existing snapshot retained")
    previous = json.loads(destination.read_text()) if destination.exists() else {}
    profiles = {}
    for run in runs:
        if run["metrics"]["cost_usd"] is not None:
            continue
        profile = find_price(run, catalogs)
        if profile:
            profiles[run["slug"]] = {**profile, "checked_at": now}
        elif len(catalogs) < len(SOURCES):
            old = previous.get("runs", {}).get(run["slug"])
            if old and run["model_ids"] == [old.get("requested_model")]:
                profiles[run["slug"]] = old
    snapshot = {"schema_version": 1, "refreshed_at": now, "sources": sources, "runs": profiles}
    temporary = destination.with_suffix(".tmp")
    temporary.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    temporary.replace(destination)
    for run in runs:
        price = display_price(run, snapshot)
        print(f"{run['slug']}: {price['basis']} · {price['amount_usd'] if price['amount_usd'] is not None else 'unknown'} USD")
