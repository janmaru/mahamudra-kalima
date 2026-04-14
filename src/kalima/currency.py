"""Multi-currency support with exchange rates."""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

try:
    import httpx

    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

logger = logging.getLogger(__name__)


class CurrencyConverter:
    """Handles currency conversion and formatting."""

    # ISO 4217 currency symbols (common ones)
    SYMBOLS = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CHF": "CHF",
        "CAD": "C$",
        "AUD": "A$",
        "NZD": "NZ$",
        "CNY": "¥",
        "INR": "₹",
        "MXN": "$",
        "BRL": "R$",
        "SEK": "kr",
        "NOK": "kr",
        "DKK": "kr",
        "SGD": "S$",
        "HKD": "HK$",
        "AED": "د.إ",
        "KRW": "₩",
        "THB": "฿",
    }

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize currency converter.

        Args:
            cache_dir: Path to cache directory for exchange rates.
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "kalima"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.rates_file = self.cache_dir / "exchange_rates.json"
        self.rates: dict[str, float] = self._load_rates()

    def _load_rates(self) -> dict[str, float]:
        """Load exchange rates from cache.

        Returns:
            Dict of {currency: rate_to_usd}.
        """
        if self.rates_file.exists():
            try:
                with open(self.rates_file, "r") as f:
                    data = json.load(f)
                    # Check if cache is still valid (24h)
                    timestamp = data.get("timestamp", 0)
                    if datetime.now().timestamp() - timestamp < 86400:
                        return data.get("rates", {"USD": 1.0})
            except json.JSONDecodeError:
                pass

        # Default rates
        return {"USD": 1.0}

    def _save_rates(self) -> None:
        """Save rates to cache."""
        data = {
            "timestamp": datetime.now().timestamp(),
            "rates": self.rates,
        }
        with open(self.rates_file, "w") as f:
            json.dump(data, f)

    def fetch_rates(self) -> bool:
        """Fetch current exchange rates from Frankfurter.

        Returns:
            True if successful, False otherwise.
        """
        if not HAS_HTTPX:
            logger.warning("httpx not available, using cached rates")
            return False

        try:
            response = httpx.get(
                "https://api.frankfurter.app/latest?from=USD",
                timeout=5.0,
            )
            response.raise_for_status()
            data = response.json()

            # Invert rates (we want USD to other currencies)
            rates_to_usd = {"USD": 1.0}
            for currency, rate in data.get("rates", {}).items():
                rates_to_usd[currency] = 1.0 / rate

            self.rates = rates_to_usd
            self._save_rates()
            logger.info(f"Fetched exchange rates for {len(self.rates)} currencies")
            return True

        except Exception as e:
            logger.warning(f"Failed to fetch exchange rates: {e}")
            return False

    def get_rate(self, currency: str) -> float:
        """Get exchange rate for currency.

        Args:
            currency: ISO 4217 currency code.

        Returns:
            Exchange rate (USD to currency).
        """
        currency = currency.upper()

        if currency not in self.rates:
            # Try to fetch if not in cache
            self.fetch_rates()

        return self.rates.get(currency, 1.0)

    def convert(self, amount_usd: float, currency: str) -> float:
        """Convert USD amount to another currency.

        Args:
            amount_usd: Amount in USD.
            currency: Target currency code.

        Returns:
            Converted amount.
        """
        rate = self.get_rate(currency)
        return amount_usd * rate

    def format_cost(
        self, amount_usd: float, currency: str = "USD", precision: int = 2
    ) -> str:
        """Format cost with currency symbol.

        Args:
            amount_usd: Amount in USD.
            currency: Target currency code.
            precision: Decimal places to show.

        Returns:
            Formatted string (e.g., "$2.34" or "€2,10").
        """
        currency = currency.upper()
        converted = self.convert(amount_usd, currency)

        symbol = self.SYMBOLS.get(currency, currency)

        # European format uses comma for decimal
        if currency in ("EUR", "SEK", "NOK", "DKK", "AED"):
            formatted = f"{converted:.{precision}f}".replace(".", ",")
        else:
            formatted = f"{converted:.{precision}f}"

        return f"{symbol}{formatted}"

    def get_all_supported_currencies(self) -> list[str]:
        """Get list of all supported currencies.

        Returns:
            List of ISO 4217 currency codes.
        """
        # Always include USD
        currencies = set(["USD"])

        # Add any cached currencies
        currencies.update(self.rates.keys())

        # Add common currencies with symbols
        currencies.update(self.SYMBOLS.keys())

        return sorted(list(currencies))


def get_converter(cache_dir: Optional[Path] = None) -> CurrencyConverter:
    """Get currency converter instance.

    Args:
        cache_dir: Optional custom cache directory.

    Returns:
        CurrencyConverter instance.
    """
    return CurrencyConverter(cache_dir)
