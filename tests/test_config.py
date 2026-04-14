"""Tests for config module."""

import json
import tempfile
from pathlib import Path

import pytest

from kalima.config import KalimaConfig, get_config


class TestKalimaConfig:
    """Test configuration management."""

    def test_config_creation(self):
        """Test creating a config instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = KalimaConfig(Path(tmpdir))

            assert config.config_dir == Path(tmpdir)
            assert config.config_file == Path(tmpdir) / "config.json"

    def test_config_default_values(self):
        """Test default configuration values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = KalimaConfig(Path(tmpdir))

            assert config.get_currency() == "USD"
            assert config.get("currency") == "USD"

    def test_config_persistence(self):
        """Test that config is saved and loaded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)

            # Create and save config
            config1 = KalimaConfig(config_dir)
            config1.set_currency("EUR")

            # Load same config
            config2 = KalimaConfig(config_dir)
            assert config2.get_currency() == "EUR"

    def test_config_set_currency(self):
        """Test setting currency."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = KalimaConfig(Path(tmpdir))

            config.set_currency("gbp")
            assert config.get_currency() == "GBP"

    def test_config_custom_values(self):
        """Test setting custom config values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = KalimaConfig(Path(tmpdir))

            config.set("custom_key", "custom_value")
            assert config.get("custom_key") == "custom_value"

    def test_config_default_fallback(self):
        """Test fallback for missing values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = KalimaConfig(Path(tmpdir))

            result = config.get("nonexistent", "default_value")
            assert result == "default_value"

    def test_cache_dir_creation(self):
        """Test that cache directory is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = KalimaConfig(Path(tmpdir))

            cache_dir = config.get_cache_dir()
            assert cache_dir.exists()

    def test_clear_cache(self):
        """Test clearing cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = KalimaConfig(Path(tmpdir))
            cache_dir = config.get_cache_dir()

            # Create test files
            (cache_dir / "test1.json").touch()
            (cache_dir / "test2.json").touch()
            (cache_dir / "test.txt").touch()

            # Clear JSON files
            deleted = config.clear_cache("*.json")
            assert deleted == 2
            assert (cache_dir / "test.txt").exists()


class TestGetConfig:
    """Test get_config helper."""

    def test_get_config_returns_instance(self):
        """Test that get_config returns KalimaConfig."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = get_config(Path(tmpdir))

            assert isinstance(config, KalimaConfig)
