"""Configuration file management for Kalima."""

import json
import os
from pathlib import Path
from typing import Any, Optional


class KalimaConfig:
    """Manages Kalima configuration."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize config manager.

        Args:
            config_dir: Path to config directory. Defaults to ~/.config/kalima.
        """
        if config_dir is None:
            config_dir = Path.home() / ".config" / "kalima"

        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        self.cache_dir = Path.home() / ".cache" / "kalima"

        # Create directories if they don't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load config from file or create default.

        Returns:
            Config dictionary.
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self._get_default_config()
        else:
            config = self._get_default_config()
            self._save_config(config)
            return config

    @staticmethod
    def _get_default_config() -> dict[str, Any]:
        """Get default configuration.

        Returns:
            Default config dictionary.
        """
        return {
            "currency": "USD",
            "cache_dir": str(Path.home() / ".cache" / "kalima"),
        }

    def _save_config(self, config: dict[str, Any]) -> None:
        """Save config to file.

        Args:
            config: Configuration to save.
        """
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)
            f.write("\n")

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value.

        Args:
            key: Config key.
            default: Default value if key not found.

        Returns:
            Config value or default.
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set config value and save.

        Args:
            key: Config key.
            value: Value to set.
        """
        self._config[key] = value
        self._save_config(self._config)

    def get_currency(self) -> str:
        """Get configured currency.

        Returns:
            ISO 4217 currency code (e.g., "USD").
        """
        return self.get("currency", "USD")

    def set_currency(self, currency: str) -> None:
        """Set currency and save.

        Args:
            currency: ISO 4217 currency code.
        """
        self.set("currency", currency.upper())

    def get_cache_dir(self) -> Path:
        """Get cache directory.

        Returns:
            Path to cache directory.
        """
        cache_dir = self.get("cache_dir", str(self.cache_dir))
        return Path(cache_dir)

    def clear_cache(self, file_pattern: str = "") -> int:
        """Clear cache files.

        Args:
            file_pattern: Only delete files matching pattern (e.g., "*.json").

        Returns:
            Number of files deleted.
        """
        cache_dir = self.get_cache_dir()
        if not cache_dir.exists():
            return 0

        deleted = 0
        if file_pattern:
            for file in cache_dir.glob(file_pattern):
                if file.is_file():
                    file.unlink()
                    deleted += 1
        else:
            for file in cache_dir.glob("*"):
                if file.is_file():
                    file.unlink()
                    deleted += 1

        return deleted


def get_config(config_dir: Optional[Path] = None) -> KalimaConfig:
    """Get or create Kalima config.

    Args:
        config_dir: Optional custom config directory.

    Returns:
        KalimaConfig instance.
    """
    return KalimaConfig(config_dir)
