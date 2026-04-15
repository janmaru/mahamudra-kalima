"""Claude model pricing and cost calculations.

Pricing is loaded from ~/.config/kalima/pricing.json if it exists,
otherwise falls back to the bundled pricing_default.json.
To customize prices, copy pricing_default.json to ~/.config/kalima/pricing.json
and edit the values. All costs are USD per 1M tokens.
"""

import json
from importlib import resources
from pathlib import Path

from .types import ModelPricing

_pricing_cache: dict[str, ModelPricing] | None = None


def _load_pricing() -> dict[str, ModelPricing]:
    """Load pricing from user config or bundled default."""
    user_file = Path.home() / ".config" / "kalima" / "pricing.json"

    if user_file.exists():
        with open(user_file, "r") as f:
            raw = json.load(f)
    else:
        ref = resources.files("kalima").joinpath("pricing_default.json")
        raw = json.loads(ref.read_text(encoding="utf-8"))

    models: dict[str, ModelPricing] = {}
    for model_id, data in raw.items():
        models[model_id] = ModelPricing(
            name=data["name"],
            input_cost_per_mtok=data["input"],
            output_cost_per_mtok=data["output"],
            cache_write_cost_per_mtok=data.get("cache_write", 0.0),
            cache_read_cost_per_mtok=data.get("cache_read", 0.0),
        )
    return models


def _get_pricing() -> dict[str, ModelPricing]:
    """Get cached pricing data."""
    global _pricing_cache
    if _pricing_cache is None:
        _pricing_cache = _load_pricing()
    return _pricing_cache


def get_model_pricing(model_name: str) -> ModelPricing:
    """Get pricing for a Claude model.

    Tries exact match first, then fuzzy match by model family keyword.
    Falls back to Sonnet 4.6 if unknown.
    """
    models = _get_pricing()

    if model_name in models:
        return models[model_name]

    model_lower = model_name.lower()

    # Match by family keyword, preferring newer versions
    families = [
        ("opus-4-6", "claude-opus-4-6"),
        ("opus-4-1", "claude-opus-4-1-20250805"),
        ("opus", "claude-opus-4-6"),
        ("sonnet-4-6", "claude-sonnet-4-6"),
        ("sonnet-4-5", "claude-sonnet-4-5-20250929"),
        ("sonnet-3-5", "claude-3-5-sonnet-20241022"),
        ("sonnet", "claude-sonnet-4-6"),
        ("haiku-4-5", "claude-haiku-4-5-20251001"),
        ("haiku-3-5", "claude-3-5-haiku-20241022"),
        ("haiku", "claude-haiku-4-5-20251001"),
    ]

    for keyword, fallback_id in families:
        if keyword in model_lower and fallback_id in models:
            return models[fallback_id]

    # Default fallback
    return models.get("claude-sonnet-4-6", next(iter(models.values())))


def calculate_cost(
    model_name: str,
    input_tokens: int,
    output_tokens: int,
    cache_write_tokens: int = 0,
    cache_read_tokens: int = 0,
) -> float:
    """Calculate total cost for a model and token usage.

    Returns:
        Total cost in USD.
    """
    pricing = get_model_pricing(model_name)
    return pricing.calculate_cost(
        input_tokens, output_tokens, cache_write_tokens, cache_read_tokens
    )


def get_all_models() -> dict[str, str]:
    """Get mapping of model names to display names."""
    return {model_id: pricing.name for model_id, pricing in _get_pricing().items()}
