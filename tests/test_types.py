"""Tests for types module."""

from datetime import datetime

import pytest

from kalima.types import Message, Session, TaskCategory, ModelPricing


def test_message_creation():
    """Test creating a Message instance."""
    msg = Message(
        api_message_id="msg_001",
        timestamp=datetime.now(),
        model="claude-3-5-sonnet-20241022",
        input_tokens=1000,
        output_tokens=500,
    )
    assert msg.api_message_id == "msg_001"
    assert msg.input_tokens == 1000
    assert msg.output_tokens == 500
    assert msg.task_category == TaskCategory.GENERAL


def test_message_with_tools():
    """Test Message with tool uses."""
    msg = Message(
        api_message_id="msg_002",
        timestamp=datetime.now(),
        model="claude-3-5-sonnet-20241022",
        input_tokens=1200,
        output_tokens=800,
        tool_uses=["read_file", "write_file"],
    )
    assert len(msg.tool_uses) == 2
    assert "read_file" in msg.tool_uses


def test_session_creation():
    """Test creating a Session instance."""
    now = datetime.now()
    session = Session(
        session_id="session_001",
        project_name="test_project",
        created_at=now,
        updated_at=now,
    )
    assert session.session_id == "session_001"
    assert session.project_name == "test_project"
    assert len(session.messages) == 0


def test_session_aggregation():
    """Test Session aggregation methods."""
    now = datetime.now()
    msg1 = Message(
        api_message_id="msg_001",
        timestamp=now,
        model="claude-3-5-sonnet-20241022",
        input_tokens=1000,
        output_tokens=500,
        cache_write_tokens=100,
        cache_read_tokens=200,
    )
    msg2 = Message(
        api_message_id="msg_002",
        timestamp=now,
        model="claude-3-5-sonnet-20241022",
        input_tokens=500,
        output_tokens=300,
    )
    session = Session(
        session_id="session_001",
        project_name="test",
        created_at=now,
        updated_at=now,
        messages=[msg1, msg2],
    )

    assert session.total_input_tokens == 1500
    assert session.total_output_tokens == 800
    assert session.total_cache_write_tokens == 100
    assert session.total_cache_read_tokens == 200
    assert session.total_tokens == 2300


def test_model_pricing():
    """Test ModelPricing calculation."""
    pricing = ModelPricing(
        name="claude-3-5-sonnet-20241022",
        input_cost_per_mtok=3.0,
        output_cost_per_mtok=15.0,
        cache_write_cost_per_mtok=3.75,
        cache_read_cost_per_mtok=0.30,
    )

    cost = pricing.calculate_cost(
        input_tokens=1000000,
        output_tokens=1000000,
        cache_write_tokens=1000000,
        cache_read_tokens=1000000,
    )

    expected = 3.0 + 15.0 + 3.75 + 0.30
    assert cost == expected


def test_model_pricing_partial():
    """Test ModelPricing with partial tokens."""
    pricing = ModelPricing(
        name="claude-3-5-sonnet-20241022",
        input_cost_per_mtok=3.0,
        output_cost_per_mtok=15.0,
    )

    cost = pricing.calculate_cost(input_tokens=500000, output_tokens=500000)

    expected = 1.5 + 7.5
    assert cost == expected


def test_task_category_enum():
    """Test TaskCategory enum values."""
    assert TaskCategory.CODING.value == "Coding"
    assert TaskCategory.DEBUGGING.value == "Debugging"
    assert TaskCategory.TESTING.value == "Testing"
    assert len(TaskCategory) == 13
