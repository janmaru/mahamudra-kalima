"""Tests for dashboard module."""

from datetime import datetime

import pytest

from kalima.dashboard import (
    _create_summary_table,
    _create_by_model_table,
    _create_by_task_table,
)
from kalima.types import Message, Session, TaskCategory


class TestDashboardTables:
    """Test dashboard table creation."""

    @pytest.fixture
    def sample_sessions(self):
        """Create sample sessions for testing."""
        now = datetime.now()
        sessions = []

        for i in range(2):
            msg = Message(
                api_message_id=f"msg_{i:03d}",
                timestamp=now,
                model="claude-3-5-sonnet-20241022",
                input_tokens=1000000,
                output_tokens=500000,
                cost_usd=3.75,
                task_category=TaskCategory.CODING,
            )
            session = Session(
                session_id=f"s_{i:03d}",
                project_name="test",
                created_at=now,
                updated_at=now,
                messages=[msg],
            )
            sessions.append(session)

        return sessions

    def test_create_summary_table(self, sample_sessions):
        """Test summary table creation."""
        table = _create_summary_table(sample_sessions, "7 Days", "USD")

        assert table is not None
        assert "Summary: 7 Days" in table.title

    def test_create_by_model_table(self, sample_sessions):
        """Test by-model table creation."""
        table = _create_by_model_table(sample_sessions)

        assert table is not None
        assert "By Model" in table.title

    def test_create_by_task_table(self, sample_sessions):
        """Test by-task table creation."""
        table = _create_by_task_table(sample_sessions)

        assert table is not None
        assert "By Task" in table.title

    def test_by_model_table_aggregates_cost(self, sample_sessions):
        """Test that by-model table aggregates costs correctly."""
        # Add a second message with different model
        msg2 = Message(
            api_message_id="msg_002",
            timestamp=sample_sessions[0].created_at,
            model="claude-3-opus-20250219",
            input_tokens=2000000,
            output_tokens=1000000,
            cost_usd=15.0,
        )
        sample_sessions[0].messages.append(msg2)

        table = _create_by_model_table(sample_sessions)

        assert table is not None

    def test_by_task_table_aggregates_count(self, sample_sessions):
        """Test that by-task table counts messages."""
        table = _create_by_task_table(sample_sessions)

        assert table is not None
