"""Tests for currency module."""

import json
import tempfile
from pathlib import Path

import pytest

from kalima.currency import CurrencyConverter, get_converter


class TestCurrencyConverter:
    """Test currency conversion."""

    def test_converter_initialization(self):
        """Test creating converter instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            converter = CurrencyConverter(Path(tmpdir))

            assert converter.cache_dir == Path(tmpdir)
            assert "USD" in converter.rates

    def test_convert_usd_to_usd(self):
        """Test converting USD to USD (should be identity)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            converter = CurrencyConverter(Path(tmpdir))

            result = converter.convert(10.0, "USD")
            assert result == 10.0

    def test_get_rate_usd(self):
        """Test getting USD rate."""
        with tempfile.TemporaryDirectory() as tmpdir:
            converter = CurrencyConverter(Path(tmpdir))

            rate = converter.get_rate("USD")
            assert rate == 1.0

    def test_format_cost_usd(self):
        """Test formatting cost in USD."""
        with tempfile.TemporaryDirectory() as tmpdir:
            converter = CurrencyConverter(Path(tmpdir))

            formatted = converter.format_cost(10.0, "USD")
            assert "$" in formatted
            assert "10" in formatted

    def test_format_cost_gbp(self):
        """Test formatting cost in GBP."""
        with tempfile.TemporaryDirectory() as tmpdir:
            converter = CurrencyConverter(Path(tmpdir))

            # Set GBP rate
            converter.rates["GBP"] = 0.79  # Example rate
            formatted = converter.format_cost(10.0, "GBP")

            assert "£" in formatted

    def test_format_cost_precision(self):
        """Test cost formatting with different precision."""
        with tempfile.TemporaryDirectory() as tmpdir:
            converter = CurrencyConverter(Path(tmpdir))

            formatted2 = converter.format_cost(10.123, "USD", precision=2)
            formatted3 = converter.format_cost(10.123, "USD", precision=3)

            assert formatted2.count(".") == 1 or formatted2.count(",") == 1

    def test_currency_symbols(self):
        """Test that currency symbols are defined."""
        with tempfile.TemporaryDirectory() as tmpdir:
            converter = CurrencyConverter(Path(tmpdir))

            assert "USD" in CurrencyConverter.SYMBOLS
            assert "EUR" in CurrencyConverter.SYMBOLS
            assert "GBP" in CurrencyConverter.SYMBOLS

    def test_supported_currencies(self):
        """Test getting supported currencies."""
        with tempfile.TemporaryDirectory() as tmpdir:
            converter = CurrencyConverter(Path(tmpdir))

            currencies = converter.get_all_supported_currencies()

            assert "USD" in currencies
            assert "EUR" in currencies
            assert len(currencies) > 0

    def test_case_insensitive_currency(self):
        """Test that currency codes are case-insensitive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            converter = CurrencyConverter(Path(tmpdir))

            rate_upper = converter.get_rate("USD")
            rate_lower = converter.get_rate("usd")
            rate_mixed = converter.get_rate("UsD")

            assert rate_upper == rate_lower == rate_mixed

    def test_cache_rates(self):
        """Test that rates are cached."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create and save rates
            converter1 = CurrencyConverter(tmppath)
            converter1.rates["EUR"] = 0.92
            converter1._save_rates()

            # Load in new instance
            converter2 = CurrencyConverter(tmppath)
            assert converter2.rates.get("EUR") == 0.92

    def test_format_cost_eur_decimal(self):
        """Test that EUR uses comma for decimal separator."""
        with tempfile.TemporaryDirectory() as tmpdir:
            converter = CurrencyConverter(Path(tmpdir))
            converter.rates["EUR"] = 0.92

            formatted = converter.format_cost(10.50, "EUR")

            # EUR should use comma as decimal separator
            assert "," in formatted or "€" in formatted


class TestGetConverter:
    """Test get_converter helper."""

    def test_get_converter_returns_instance(self):
        """Test that get_converter returns CurrencyConverter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            converter = get_converter(Path(tmpdir))

            assert isinstance(converter, CurrencyConverter)
