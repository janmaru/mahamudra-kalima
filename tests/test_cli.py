"""Integration tests for CLI commands."""

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from kalima.cli import app
from kalima.types import Message, Session, TaskCategory


runner = CliRunner()


class TestCLIVersion:
    """Test version command."""

    def test_version_command(self):
        """Test version command output."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "Kalima" in result.stdout
        assert "0.1.0" in result.stdout


class TestCLICurrency:
    """Test currency command."""

    def test_currency_show_default(self):
        """Test showing current currency."""
        result = runner.invoke(app, ["currency"])

        assert result.exit_code == 0
        assert "Current currency:" in result.stdout

    def test_currency_set(self):
        """Test setting currency."""
        result = runner.invoke(app, ["currency", "EUR"])

        assert result.exit_code == 0
        assert "EUR" in result.stdout

    def test_currency_reset(self):
        """Test resetting currency to USD."""
        result = runner.invoke(app, ["currency", "--reset"])

        assert result.exit_code == 0
        assert "USD" in result.stdout


class TestCLIExport:
    """Test export command."""

    @patch("kalima.cli.discover_sessions")
    @patch("kalima.cli.parse_sessions")
    def test_export_csv(self, mock_parse, mock_discover):
        """Test CSV export."""
        now = datetime.now()
        msg = Message(
            api_message_id="msg_001",
            timestamp=now,
            model="claude-3-5-sonnet-20241022",
            input_tokens=1000,
            output_tokens=500,
            cost_usd=0.045,
        )
        session = Session(
            session_id="s_001",
            project_name="test",
            created_at=now,
            updated_at=now,
            messages=[msg],
        )

        mock_discover.return_value = [Path("dummy")]
        mock_parse.return_value = [session]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "export.csv"
            result = runner.invoke(
                app,
                ["export", "--output", str(output_path), "--format", "csv"],
            )

            assert result.exit_code == 0
            assert "Exported to" in result.stdout

    @patch("kalima.cli.discover_sessions")
    @patch("kalima.cli.parse_sessions")
    def test_export_json(self, mock_parse, mock_discover):
        """Test JSON export."""
        now = datetime.now()
        msg = Message(
            api_message_id="msg_001",
            timestamp=now,
            model="claude-3-5-sonnet-20241022",
            input_tokens=1000,
            output_tokens=500,
            cost_usd=0.045,
        )
        session = Session(
            session_id="s_001",
            project_name="test",
            created_at=now,
            updated_at=now,
            messages=[msg],
        )

        mock_discover.return_value = [Path("dummy")]
        mock_parse.return_value = [session]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "export.json"
            result = runner.invoke(
                app,
                ["export", "--output", str(output_path), "--format", "json"],
            )

            assert result.exit_code == 0
            assert "Exported to" in result.stdout


class TestCLIStatus:
    """Test status command."""

    @patch("kalima.cli.discover_sessions")
    @patch("kalima.cli.parse_sessions")
    def test_status_text(self, mock_parse, mock_discover):
        """Test status command in text format."""
        now = datetime.now(timezone.utc)
        msg = Message(
            api_message_id="msg_001",
            timestamp=now,
            model="claude-3-5-sonnet-20241022",
            input_tokens=1000,
            output_tokens=500,
            cost_usd=0.045,
        )
        session = Session(
            session_id="s_001",
            project_name="test",
            created_at=now,
            updated_at=now,
            messages=[msg],
        )

        mock_discover.return_value = [Path("dummy")]
        mock_parse.return_value = [session]

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0

    @patch("kalima.cli.discover_sessions")
    @patch("kalima.cli.parse_sessions")
    def test_status_json(self, mock_parse, mock_discover):
        """Test status command in JSON format."""
        now = datetime.now(timezone.utc)
        msg = Message(
            api_message_id="msg_001",
            timestamp=now,
            model="claude-3-5-sonnet-20241022",
            input_tokens=1000,
            output_tokens=500,
            cost_usd=0.045,
        )
        session = Session(
            session_id="s_001",
            project_name="test",
            created_at=now,
            updated_at=now,
            messages=[msg],
        )

        mock_discover.return_value = [Path("dummy")]
        mock_parse.return_value = [session]

        result = runner.invoke(app, ["status", "--format", "json"])

        assert result.exit_code == 0
