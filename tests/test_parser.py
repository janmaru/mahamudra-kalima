"""Tests for parser module."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from kalima.parser import (
    filter_sessions_by_date,
    filter_sessions_by_date_range,
    _extract_message_from_json,
)
from kalima.types import Message, Session, TaskCategory


class TestExtractMessage:
    """Test message extraction from JSON."""

    def test_extract_basic_message(self):
        """Test extracting a basic message."""
        data = {
            "id": "msg_001",
            "created_at": "2025-04-14T10:00:00Z",
            "model": "claude-3-5-sonnet-20241022",
            "usage": {"input_tokens": 500, "output_tokens": 200},
        }

        result = _extract_message_from_json(data)

        assert result is not None
        assert result["api_message_id"] == "msg_001"
        assert result["model"] == "claude-3-5-sonnet-20241022"
        assert result["input_tokens"] == 500
        assert result["output_tokens"] == 200

    def test_extract_message_with_tools(self):
        """Test extracting message with tool uses."""
        data = {
            "id": "msg_002",
            "created_at": "2025-04-14T10:05:00Z",
            "model": "claude-3-5-sonnet-20241022",
            "usage": {"input_tokens": 1200, "output_tokens": 800},
            "content": [
                {"type": "tool_use", "name": "read_file"},
                {"type": "tool_use", "name": "write_file"},
            ],
        }

        result = _extract_message_from_json(data)

        assert result is not None
        assert len(result["tool_uses"]) == 2
        assert "read_file" in result["tool_uses"]
        assert "write_file" in result["tool_uses"]

    def test_extract_message_with_cache_tokens(self):
        """Test extracting message with cache tokens."""
        data = {
            "id": "msg_003",
            "created_at": "2025-04-14T10:10:00Z",
            "model": "claude-3-5-sonnet-20241022",
            "usage": {
                "input_tokens": 2000,
                "output_tokens": 1500,
                "cache_creation_input_tokens": 500,
                "cache_read_input_tokens": 100,
            },
        }

        result = _extract_message_from_json(data)

        assert result is not None
        assert result["cache_write_tokens"] == 500
        assert result["cache_read_tokens"] == 100

    def test_extract_message_no_model(self):
        """Test extracting message without model (should return None)."""
        data = {"id": "msg_004", "created_at": "2025-04-14T10:15:00Z"}

        result = _extract_message_from_json(data)

        assert result is None

    def test_extract_message_timestamp_format(self):
        """Test extracting message with ISO timestamp."""
        data = {
            "id": "msg_005",
            "created_at": "2025-04-14T10:20:00.123456Z",
            "model": "claude-3-5-sonnet-20241022",
            "usage": {"input_tokens": 100, "output_tokens": 50},
        }

        result = _extract_message_from_json(data)

        assert result is not None
        assert isinstance(result["timestamp"], datetime)


class TestFilterByDate:
    """Test date filtering."""

    def test_filter_last_7_days(self):
        """Test filtering messages from last 7 days."""
        now = datetime.now(timezone.utc)
        old_msg = Message(
            api_message_id="old_001",
            timestamp=now - timedelta(days=10),
            model="claude-3-5-sonnet-20241022",
        )
        recent_msg = Message(
            api_message_id="recent_001",
            timestamp=now - timedelta(days=3),
            model="claude-3-5-sonnet-20241022",
        )

        session = Session(
            session_id="test_001",
            project_name="test",
            created_at=now - timedelta(days=10),
            updated_at=now,
            messages=[old_msg, recent_msg],
        )

        filtered = filter_sessions_by_date([session], days=7)

        assert len(filtered) == 1
        assert len(filtered[0].messages) == 1
        assert filtered[0].messages[0].api_message_id == "recent_001"

    def test_filter_no_messages_in_range(self):
        """Test filtering when no messages are in range."""
        now = datetime.now(timezone.utc)
        old_msg = Message(
            api_message_id="old_001",
            timestamp=now - timedelta(days=100),
            model="claude-3-5-sonnet-20241022",
        )

        session = Session(
            session_id="test_001",
            project_name="test",
            created_at=now - timedelta(days=100),
            updated_at=now - timedelta(days=90),
            messages=[old_msg],
        )

        filtered = filter_sessions_by_date([session], days=7)

        assert len(filtered) == 0

    def test_filter_by_date_range(self):
        """Test filtering by specific date range."""
        start = datetime(2025, 4, 10, tzinfo=timezone.utc)
        end = datetime(2025, 4, 20, tzinfo=timezone.utc)

        msg1 = Message(
            api_message_id="msg_001",
            timestamp=datetime(2025, 4, 15, tzinfo=timezone.utc),
            model="claude-3-5-sonnet-20241022",
        )
        msg2 = Message(
            api_message_id="msg_002",
            timestamp=datetime(2025, 4, 5, tzinfo=timezone.utc),
            model="claude-3-5-sonnet-20241022",
        )
        msg3 = Message(
            api_message_id="msg_003",
            timestamp=datetime(2025, 4, 25, tzinfo=timezone.utc),
            model="claude-3-5-sonnet-20241022",
        )

        session = Session(
            session_id="test_001",
            project_name="test",
            created_at=datetime(2025, 4, 1, tzinfo=timezone.utc),
            updated_at=datetime(2025, 4, 30, tzinfo=timezone.utc),
            messages=[msg1, msg2, msg3],
        )

        filtered = filter_sessions_by_date_range([session], start, end)

        assert len(filtered) == 1
        assert len(filtered[0].messages) == 1
        assert filtered[0].messages[0].api_message_id == "msg_001"
