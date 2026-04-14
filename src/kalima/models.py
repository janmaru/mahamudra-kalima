"""Claude model pricing and cost calculations."""

from .types import ModelPricing

# Claude model pricing (USD per 1M tokens)
# Updated to match LiteLLM pricing data
# Cache prices: write cost 25% of input, read cost 10% of input

CLAUDE_MODELS: dict[str, ModelPricing] = {
    # Claude 3.5 models (latest)
    "claude-3-5-sonnet-20241022": ModelPricing(
        name="Claude 3.5 Sonnet",
        input_cost_per_mtok=3.0,
        output_cost_per_mtok=15.0,
        cache_write_cost_per_mtok=0.75,  # 25% of input
        cache_read_cost_per_mtok=0.30,  # 10% of input
    ),
    "claude-3-5-opus-20250514": ModelPricing(
        name="Claude 3.5 Opus",
        input_cost_per_mtok=15.0,
        output_cost_per_mtok=60.0,
        cache_write_cost_per_mtok=3.75,  # 25% of input
        cache_read_cost_per_mtok=1.50,  # 10% of input
    ),
    "claude-3-5-haiku-20241022": ModelPricing(
        name="Claude 3.5 Haiku",
        input_cost_per_mtok=0.80,
        output_cost_per_mtok=4.0,
        cache_write_cost_per_mtok=0.20,  # 25% of input
        cache_read_cost_per_mtok=0.08,  # 10% of input
    ),
    # Claude 3 models
    "claude-3-opus-20240229": ModelPricing(
        name="Claude 3 Opus",
        input_cost_per_mtok=15.0,
        output_cost_per_mtok=75.0,
        cache_write_cost_per_mtok=3.75,  # 25% of input
        cache_read_cost_per_mtok=1.50,  # 10% of input
    ),
    "claude-3-sonnet-20240229": ModelPricing(
        name="Claude 3 Sonnet",
        input_cost_per_mtok=3.0,
        output_cost_per_mtok=15.0,
        cache_write_cost_per_mtok=0.75,  # 25% of input
        cache_read_cost_per_mtok=0.30,  # 10% of input
    ),
    "claude-3-haiku-20240307": ModelPricing(
        name="Claude 3 Haiku",
        input_cost_per_mtok=0.25,
        output_cost_per_mtok=1.25,
        cache_write_cost_per_mtok=0.0625,  # 25% of input
        cache_read_cost_per_mtok=0.025,  # 10% of input
    ),
    # Additional aliases
    "claude-opus": ModelPricing(
        name="Claude Opus",
        input_cost_per_mtok=15.0,
        output_cost_per_mtok=75.0,
        cache_write_cost_per_mtok=3.75,
        cache_read_cost_per_mtok=1.50,
    ),
    "claude-sonnet": ModelPricing(
        name="Claude Sonnet",
        input_cost_per_mtok=3.0,
        output_cost_per_mtok=15.0,
        cache_write_cost_per_mtok=0.75,
        cache_read_cost_per_mtok=0.30,
    ),
    "claude-haiku": ModelPricing(
        name="Claude Haiku",
        input_cost_per_mtok=0.25,
        output_cost_per_mtok=1.25,
        cache_write_cost_per_mtok=0.0625,
        cache_read_cost_per_mtok=0.025,
    ),
}


def get_model_pricing(model_name: str) -> ModelPricing:
    """Get pricing for a Claude model.

    Falls back to Sonnet if model not found.

    Args:
        model_name: Model identifier (e.g., "claude-3-5-sonnet-20241022").

    Returns:
        ModelPricing object with cost calculations.
    """
    # Exact match
    if model_name in CLAUDE_MODELS:
        return CLAUDE_MODELS[model_name]

    # Fuzzy match: check if model name contains known models
    model_lower = model_name.lower()

    if "opus" in model_lower:
        if "3-5" in model_lower:
            return CLAUDE_MODELS["claude-3-5-opus-20250514"]
        return CLAUDE_MODELS["claude-3-opus-20240229"]

    if "sonnet" in model_lower:
        if "3-5" in model_lower:
            return CLAUDE_MODELS["claude-3-5-sonnet-20241022"]
        return CLAUDE_MODELS["claude-3-sonnet-20240229"]

    if "haiku" in model_lower:
        if "3-5" in model_lower:
            return CLAUDE_MODELS["claude-3-5-haiku-20241022"]
        return CLAUDE_MODELS["claude-3-haiku-20240307"]

    # Default to Sonnet if unknown
    return CLAUDE_MODELS["claude-3-5-sonnet-20241022"]


def calculate_cost(
    model_name: str,
    input_tokens: int,
    output_tokens: int,
    cache_write_tokens: int = 0,
    cache_read_tokens: int = 0,
) -> float:
    """Calculate total cost for a model and token usage.

    Args:
        model_name: Model identifier.
        input_tokens: Number of input tokens.
        output_tokens: Number of output tokens.
        cache_write_tokens: Number of cache write tokens.
        cache_read_tokens: Number of cache read tokens.

    Returns:
        Total cost in USD.
    """
    pricing = get_model_pricing(model_name)
    return pricing.calculate_cost(
        input_tokens, output_tokens, cache_write_tokens, cache_read_tokens
    )


def get_all_models() -> dict[str, str]:
    """Get mapping of model names to display names.

    Returns:
        Dict of {model_id: display_name}.
    """
    return {model_id: pricing.name for model_id, pricing in CLAUDE_MODELS.items()}
