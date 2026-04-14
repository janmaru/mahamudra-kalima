"""Tests for models module."""

import pytest

from kalima.models import (
    get_model_pricing,
    calculate_cost,
    get_all_models,
    CLAUDE_MODELS,
)


class TestGetModelPricing:
    """Test model pricing retrieval."""

    def test_get_exact_sonnet_pricing(self):
        """Test getting exact Sonnet pricing."""
        pricing = get_model_pricing("claude-3-5-sonnet-20241022")

        assert pricing.name == "Claude 3.5 Sonnet"
        assert pricing.input_cost_per_mtok == 3.0
        assert pricing.output_cost_per_mtok == 15.0

    def test_get_opus_pricing(self):
        """Test getting Opus pricing."""
        pricing = get_model_pricing("claude-3-5-opus-20250514")

        assert pricing.name == "Claude 3.5 Opus"
        assert pricing.input_cost_per_mtok == 15.0
        assert pricing.output_cost_per_mtok == 60.0

    def test_get_haiku_pricing(self):
        """Test getting Haiku pricing."""
        pricing = get_model_pricing("claude-3-5-haiku-20241022")

        assert pricing.name == "Claude 3.5 Haiku"
        assert pricing.input_cost_per_mtok == 0.80
        assert pricing.output_cost_per_mtok == 4.0

    def test_get_model_pricing_fuzzy_match_opus(self):
        """Test fuzzy matching for Opus models."""
        # Should match "opus" and default to latest
        pricing = get_model_pricing("claude-opus")

        assert "Opus" in pricing.name

    def test_get_model_pricing_fuzzy_match_sonnet(self):
        """Test fuzzy matching for Sonnet models."""
        pricing = get_model_pricing("claude-sonnet")

        assert "Sonnet" in pricing.name

    def test_get_model_pricing_fuzzy_match_haiku(self):
        """Test fuzzy matching for Haiku models."""
        pricing = get_model_pricing("claude-haiku")

        assert "Haiku" in pricing.name

    def test_get_model_pricing_defaults_to_sonnet(self):
        """Test that unknown models default to Sonnet."""
        pricing = get_model_pricing("unknown-model-xyz")

        assert "Sonnet" in pricing.name

    def test_model_pricing_has_cache_costs(self):
        """Test that models have cache pricing."""
        pricing = get_model_pricing("claude-3-5-sonnet-20241022")

        assert pricing.cache_write_cost_per_mtok == 0.75  # 25% of input
        assert pricing.cache_read_cost_per_mtok == 0.30  # 10% of input


class TestCalculateCost:
    """Test cost calculation."""

    def test_calculate_cost_sonnet_basic(self):
        """Test basic cost calculation for Sonnet."""
        cost = calculate_cost(
            "claude-3-5-sonnet-20241022",
            input_tokens=1000000,
            output_tokens=1000000,
        )

        expected = 3.0 + 15.0
        assert cost == expected

    def test_calculate_cost_with_cache_tokens(self):
        """Test cost calculation with cache tokens."""
        cost = calculate_cost(
            "claude-3-5-sonnet-20241022",
            input_tokens=1000000,
            output_tokens=1000000,
            cache_write_tokens=1000000,
            cache_read_tokens=1000000,
        )

        expected = 3.0 + 15.0 + 0.75 + 0.30
        assert cost == expected

    def test_calculate_cost_partial_tokens(self):
        """Test cost calculation with partial tokens."""
        cost = calculate_cost(
            "claude-3-5-sonnet-20241022",
            input_tokens=500000,
            output_tokens=500000,
        )

        expected = 1.5 + 7.5
        assert cost == expected

    def test_calculate_cost_haiku_cheap(self):
        """Test that Haiku is cheaper than Sonnet."""
        haiku_cost = calculate_cost(
            "claude-3-5-haiku-20241022",
            input_tokens=1000000,
            output_tokens=1000000,
        )

        sonnet_cost = calculate_cost(
            "claude-3-5-sonnet-20241022",
            input_tokens=1000000,
            output_tokens=1000000,
        )

        assert haiku_cost < sonnet_cost

    def test_calculate_cost_opus_expensive(self):
        """Test that Opus is more expensive than Sonnet."""
        opus_cost = calculate_cost(
            "claude-3-5-opus-20250514",
            input_tokens=1000000,
            output_tokens=1000000,
        )

        sonnet_cost = calculate_cost(
            "claude-3-5-sonnet-20241022",
            input_tokens=1000000,
            output_tokens=1000000,
        )

        assert opus_cost > sonnet_cost

    def test_calculate_cost_zero_tokens(self):
        """Test cost calculation with zero tokens."""
        cost = calculate_cost(
            "claude-3-5-sonnet-20241022",
            input_tokens=0,
            output_tokens=0,
        )

        assert cost == 0.0

    def test_calculate_cost_input_only(self):
        """Test cost calculation with input tokens only."""
        cost = calculate_cost(
            "claude-3-5-sonnet-20241022",
            input_tokens=1000000,
            output_tokens=0,
        )

        assert cost == 3.0

    def test_calculate_cost_output_only(self):
        """Test cost calculation with output tokens only."""
        cost = calculate_cost(
            "claude-3-5-sonnet-20241022",
            input_tokens=0,
            output_tokens=1000000,
        )

        assert cost == 15.0


class TestGetAllModels:
    """Test getting all available models."""

    def test_get_all_models_returns_dict(self):
        """Test that get_all_models returns a dict."""
        models = get_all_models()

        assert isinstance(models, dict)
        assert len(models) > 0

    def test_get_all_models_has_sonnet(self):
        """Test that Sonnet models are in the list."""
        models = get_all_models()

        sonnet_models = [m for m in models.values() if "Sonnet" in m]
        assert len(sonnet_models) > 0

    def test_get_all_models_has_opus(self):
        """Test that Opus models are in the list."""
        models = get_all_models()

        opus_models = [m for m in models.values() if "Opus" in m]
        assert len(opus_models) > 0

    def test_get_all_models_has_haiku(self):
        """Test that Haiku models are in the list."""
        models = get_all_models()

        haiku_models = [m for m in models.values() if "Haiku" in m]
        assert len(haiku_models) > 0


class TestModelPricingData:
    """Test pricing data consistency."""

    def test_all_models_have_pricing(self):
        """Test that all models have valid pricing."""
        for model_id, pricing in CLAUDE_MODELS.items():
            assert pricing.name != ""
            assert pricing.input_cost_per_mtok > 0
            assert pricing.output_cost_per_mtok > 0

    def test_cache_costs_are_fraction_of_input(self):
        """Test that cache costs are fractions of input cost."""
        for pricing in CLAUDE_MODELS.values():
            # Cache write should be ~25% of input
            assert pricing.cache_write_cost_per_mtok <= pricing.input_cost_per_mtok

            # Cache read should be ~10% of input
            assert pricing.cache_read_cost_per_mtok <= pricing.input_cost_per_mtok

    def test_opus_more_expensive_than_sonnet(self):
        """Test Opus is more expensive than Sonnet."""
        opus = CLAUDE_MODELS["claude-3-5-opus-20250514"]
        sonnet = CLAUDE_MODELS["claude-3-5-sonnet-20241022"]

        assert opus.input_cost_per_mtok > sonnet.input_cost_per_mtok
        assert opus.output_cost_per_mtok > sonnet.output_cost_per_mtok

    def test_haiku_cheaper_than_sonnet(self):
        """Test Haiku is cheaper than Sonnet."""
        haiku = CLAUDE_MODELS["claude-3-5-haiku-20241022"]
        sonnet = CLAUDE_MODELS["claude-3-5-sonnet-20241022"]

        assert haiku.input_cost_per_mtok < sonnet.input_cost_per_mtok
        assert haiku.output_cost_per_mtok < sonnet.output_cost_per_mtok
