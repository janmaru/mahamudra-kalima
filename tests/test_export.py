"""Tests for export module."""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from kalima.export import export_csv, export_json
from kalima.types import Message, Session, TaskCategory


class TestExportCSV:
    """Test CSV export."""

    def test_export_csv_basic(self):
        """Test basic CSV export."""
        now = datetime.now()
        msg = Message(
            api_message_id="msg_001",
            timestamp=now,
            model="claude-3-5-sonnet-20241022",
            input_tokens=1000,
            output_tokens=500,
            cost_usd=0.045,
            task_category=TaskCategory.CODING,
        )
        session = Session(
            session_id="s_001",
            project_name="test",
            created_at=now,
            updated_at=now,
            messages=[msg],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "export.csv"
            export_csv([session], output_path)

            assert output_path.exists()
            content = output_path.read_text()
            assert "date" in content
            assert "model" in content
            assert "claude-3-5-sonnet-20241022" in content

    def test_export_csv_with_summary(self):
        """Test CSV export with summary."""
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

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "export.csv"
            export_csv([session], output_path, include_periods=True)

            content = output_path.read_text()
            assert "Summary" in content
            assert "Today" in content


class TestExportJSON:
    """Test JSON export."""

    def test_export_json_basic(self):
        """Test basic JSON export."""
        now = datetime.now()
        msg = Message(
            api_message_id="msg_001",
            timestamp=now,
            model="claude-3-5-sonnet-20241022",
            input_tokens=1000,
            output_tokens=500,
            cost_usd=0.045,
            task_category=TaskCategory.CODING,
        )
        session = Session(
            session_id="s_001",
            project_name="test",
            created_at=now,
            updated_at=now,
            messages=[msg],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "export.json"
            export_json([session], output_path)

            assert output_path.exists()
            data = json.loads(output_path.read_text())
            assert "sessions" in data
            assert "summary" in data
            assert len(data["sessions"]) == 1
            assert data["sessions"][0]["project"] == "test"

    def test_export_json_structure(self):
        """Test JSON export structure."""
        now = datetime.now()
        msg = Message(
            api_message_id="msg_001",
            timestamp=now,
            model="claude-3-5-sonnet-20241022",
            input_tokens=1000,
            output_tokens=500,
            cost_usd=0.045,
            tool_uses=["read_file"],
        )
        session = Session(
            session_id="s_001",
            project_name="test",
            created_at=now,
            updated_at=now,
            messages=[msg],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "export.json"
            export_json([session], output_path, include_periods=False)

            data = json.loads(output_path.read_text())
            msg_data = data["sessions"][0]["messages"][0]
            assert msg_data["model"] == "claude-3-5-sonnet-20241022"
            assert msg_data["input_tokens"] == 1000
            assert "read_file" in msg_data["tools"]

    def test_export_json_with_summary(self):
        """Test JSON export with summary."""
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

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "export.json"
            export_json([session], output_path, include_periods=True)

            data = json.loads(output_path.read_text())
            assert "today" in data["summary"]
            assert "last_7_days" in data["summary"]
            assert "last_30_days" in data["summary"]
