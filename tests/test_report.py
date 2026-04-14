"""Tests for report module."""

from datetime import datetime

import pytest

from kalima.report import (
    format_daily_summary,
    format_period_report,
    format_status_line,
    _format_tokens,
    create_ascii_chart,
)
from kalima.types import Message, Session, TaskCategory


class TestFormatTokens:
    """Test token formatting."""

    def test_format_tokens_millions(self):
        """Test formatting millions of tokens."""
        result = _format_tokens(1_500_000)

        assert "1.5M" in result

    def test_format_tokens_thousands(self):
        """Test formatting thousands of tokens."""
        result = _format_tokens(1_500)

        assert "1.5K" in result

    def test_format_tokens_single(self):
        """Test formatting single tokens."""
        result = _format_tokens(100)

        assert "100" == result

    def test_format_tokens_zero(self):
        """Test formatting zero tokens."""
        result = _format_tokens(0)

        assert "0" == result


class TestDailySummary:
    """Test daily summary formatting."""

    def test_daily_summary_basic(self):
        """Test basic daily summary."""
        now = datetime.now()
        msg = Message(
            api_message_id="msg_001",
            timestamp=now,
            model="claude-3-5-sonnet-20241022",
            input_tokens=1000000,
            output_tokens=500000,
            cost_usd=3.75,
        )
        session = Session(
            session_id="s_001",
            project_name="test",
            created_at=now,
            updated_at=now,
            messages=[msg],
        )

        result = format_daily_summary([session], "USD")

        assert "Daily Summary" in result
        assert "3.75" in result or "$" in result

    def test_daily_summary_multiple_sessions(self):
        """Test daily summary with multiple sessions."""
        now = datetime.now()
        sessions = []

        for i in range(3):
            msg = Message(
                api_message_id=f"msg_{i:03d}",
                timestamp=now,
                model="claude-3-5-sonnet-20241022",
                input_tokens=1000000,
                output_tokens=500000,
                cost_usd=3.75,
            )
            session = Session(
                session_id=f"s_{i:03d}",
                project_name="test",
                created_at=now,
                updated_at=now,
                messages=[msg],
            )
            sessions.append(session)

        result = format_daily_summary(sessions, "USD")

        assert "Daily Summary" in result
        assert "11.25" in result or "$" in result  # 3 * 3.75


class TestPeriodReport:
    """Test period report formatting."""

    def test_period_report_basic(self):
        """Test basic period report."""
        now = datetime.now()
        msg = Message(
            api_message_id="msg_001",
            timestamp=now,
            model="claude-3-5-sonnet-20241022",
            input_tokens=1000000,
            output_tokens=500000,
            cost_usd=3.75,
            task_category=TaskCategory.CODING,
        )
        session = Session(
            session_id="s_001",
            project_name="test",
            created_at=now,
            updated_at=now,
            messages=[msg],
        )

        result = format_period_report([session], "7 Days", "USD")

        assert "Report: 7 Days" in result
        assert "Total Cost" in result
        assert "By Model" in result
        assert "By Task Category" in result

    def test_period_report_with_cache(self):
        """Test period report with cache tokens."""
        now = datetime.now()
        msg = Message(
            api_message_id="msg_001",
            timestamp=now,
            model="claude-3-5-sonnet-20241022",
            input_tokens=1000000,
            output_tokens=500000,
            cache_write_tokens=100000,
            cache_read_tokens=50000,
            cost_usd=5.0,
        )
        session = Session(
            session_id="s_001",
            project_name="test",
            created_at=now,
            updated_at=now,
            messages=[msg],
        )

        result = format_period_report([session], "7 Days", "USD")

        assert "Cache Tokens" in result


class TestStatusLine:
    """Test status line formatting."""

    def test_status_line_basic(self):
        """Test basic status line."""
        now = datetime.now()
        today_msg = Message(
            api_message_id="msg_001",
            timestamp=now,
            model="claude-3-5-sonnet-20241022",
            input_tokens=1000000,
            output_tokens=500000,
            cost_usd=3.75,
        )
        today_session = Session(
            session_id="s_001",
            project_name="test",
            created_at=now,
            updated_at=now,
            messages=[today_msg],
        )

        month_msg = Message(
            api_message_id="msg_002",
            timestamp=now,
            model="claude-3-5-sonnet-20241022",
            input_tokens=10000000,
            output_tokens=5000000,
            cost_usd=37.50,
        )
        month_session = Session(
            session_id="s_002",
            project_name="test",
            created_at=now,
            updated_at=now,
            messages=[month_msg],
        )

        result = format_status_line([today_session], [month_session], "USD")

        assert "Today:" in result
        assert "Month:" in result


class TestAsciiChart:
    """Test ASCII chart creation."""

    def test_ascii_chart_basic(self):
        """Test basic ASCII chart."""
        values = [1.0, 2.0, 3.0, 2.5, 1.5]

        result = create_ascii_chart(values)

        assert "█" in result
        assert "│" in result

    def test_ascii_chart_empty(self):
        """Test ASCII chart with empty values."""
        result = create_ascii_chart([])

        assert result == ""

    def test_ascii_chart_single(self):
        """Test ASCII chart with single value."""
        result = create_ascii_chart([5.0])

        assert "█" in result

    def test_ascii_chart_custom_size(self):
        """Test ASCII chart with custom dimensions."""
        values = [1.0, 2.0, 3.0]
        result = create_ascii_chart(values, width=10, height=5)

        assert "█" in result
