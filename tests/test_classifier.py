"""Tests for classifier module."""

from datetime import datetime

import pytest

from kalima.classifier import (
    TaskClassifier,
    classify_message,
    classify_messages,
    detect_retry_cycles,
    calculate_one_shot_success_rate,
)
from kalima.types import Message, TaskCategory


class TestTaskClassifier:
    """Test TaskClassifier classification logic."""

    def test_classify_coding_with_write(self):
        """Test classification of coding task."""
        msg = Message(
            api_message_id="msg_001",
            timestamp=datetime.now(),
            model="claude-3-5-sonnet-20241022",
            tool_uses=["write_file"],
            user_text="Add type hints to this function",
        )

        category = TaskClassifier.classify(msg)

        assert category == TaskCategory.CODING

    def test_classify_refactoring(self):
        """Test classification of refactoring task."""
        msg = Message(
            api_message_id="msg_002",
            timestamp=datetime.now(),
            model="claude-3-5-sonnet-20241022",
            tool_uses=["write_file"],
            user_text="Refactor this to be more readable",
        )

        category = TaskClassifier.classify(msg)

        assert category == TaskCategory.REFACTORING

    def test_classify_debugging(self):
        """Test classification of debugging task."""
        msg = Message(
            api_message_id="msg_003",
            timestamp=datetime.now(),
            model="claude-3-5-sonnet-20241022",
            tool_uses=["read_file", "execute_command"],
            user_text="Fix the error on line 42",
        )

        category = TaskClassifier.classify(msg)

        assert category == TaskCategory.DEBUGGING

    def test_classify_testing(self):
        """Test classification of testing task."""
        msg = Message(
            api_message_id="msg_004",
            timestamp=datetime.now(),
            model="claude-3-5-sonnet-20241022",
            tool_uses=["execute_command"],
            user_text="Run the pytest command to test",
        )

        category = TaskClassifier.classify(msg)

        assert category == TaskCategory.TESTING

    def test_classify_feature_dev(self):
        """Test classification of feature development."""
        msg = Message(
            api_message_id="msg_005",
            timestamp=datetime.now(),
            model="claude-3-5-sonnet-20241022",
            tool_uses=["read_file"],
            user_text="Create a new caching layer",
        )

        category = TaskClassifier.classify(msg)

        assert category == TaskCategory.FEATURE_DEV

    def test_classify_exploration(self):
        """Test classification of exploration."""
        msg = Message(
            api_message_id="msg_006",
            timestamp=datetime.now(),
            model="claude-3-5-sonnet-20241022",
            tool_uses=["read_file", "grep_code"],
            user_text="What does this module do?",
        )

        category = TaskClassifier.classify(msg)

        assert category == TaskCategory.EXPLORATION

    def test_classify_planning(self):
        """Test classification of planning."""
        msg = Message(
            api_message_id="msg_007",
            timestamp=datetime.now(),
            model="claude-3-5-sonnet-20241022",
            tool_uses=[],
            user_text="Let's design the architecture for this feature",
        )

        category = TaskClassifier.classify(msg)

        assert category == TaskCategory.PLANNING

    def test_classify_git_ops(self):
        """Test classification of git operations."""
        msg = Message(
            api_message_id="msg_008",
            timestamp=datetime.now(),
            model="claude-3-5-sonnet-20241022",
            tool_uses=["execute_command"],
            user_text="Please git push the changes to main",
        )

        category = TaskClassifier.classify(msg)

        assert category == TaskCategory.GIT_OPS

    def test_classify_build_deploy(self):
        """Test classification of build/deploy."""
        msg = Message(
            api_message_id="msg_009",
            timestamp=datetime.now(),
            model="claude-3-5-sonnet-20241022",
            tool_uses=["execute_command"],
            user_text="Run docker build to create image",
        )

        category = TaskClassifier.classify(msg)

        assert category == TaskCategory.BUILD_DEPLOY

    def test_classify_brainstorming(self):
        """Test classification of brainstorming."""
        msg = Message(
            api_message_id="msg_010",
            timestamp=datetime.now(),
            model="claude-3-5-sonnet-20241022",
            tool_uses=[],
            user_text="What if we brainstorm different approaches?",
        )

        category = TaskClassifier.classify(msg)

        assert category == TaskCategory.BRAINSTORMING

    def test_classify_delegation(self):
        """Test classification of delegation."""
        msg = Message(
            api_message_id="msg_011",
            timestamp=datetime.now(),
            model="claude-3-5-sonnet-20241022",
            tool_uses=["spawn_agent"],
            user_text="Delegate analysis to background task",
        )

        category = TaskClassifier.classify(msg)

        assert category == TaskCategory.DELEGATION

    def test_classify_conversation(self):
        """Test classification of conversation."""
        msg = Message(
            api_message_id="msg_012",
            timestamp=datetime.now(),
            model="claude-3-5-sonnet-20241022",
            tool_uses=[],
            user_text="Thanks for the explanation!",
        )

        category = TaskClassifier.classify(msg)

        assert category == TaskCategory.CONVERSATION

    def test_classify_general(self):
        """Test classification of general/uncategorized."""
        msg = Message(
            api_message_id="msg_013",
            timestamp=datetime.now(),
            model="claude-3-5-sonnet-20241022",
            tool_uses=["unknown_tool"],
            user_text="Do something",
        )

        category = TaskClassifier.classify(msg)

        assert category == TaskCategory.GENERAL


class TestClassifyMessage:
    """Test classify_message function."""

    def test_classify_message_sets_category(self):
        """Test that classify_message sets the category."""
        msg = Message(
            api_message_id="msg_001",
            timestamp=datetime.now(),
            model="claude-3-5-sonnet-20241022",
            tool_uses=["write_file"],
            user_text="Write a function",
        )

        classified = classify_message(msg)

        assert classified.task_category == TaskCategory.CODING

    def test_classify_messages_bulk(self):
        """Test classify_messages function."""
        messages = [
            Message(
                api_message_id="msg_001",
                timestamp=datetime.now(),
                model="claude-3-5-sonnet-20241022",
                tool_uses=["write_file"],
                user_text="Write code",
            ),
            Message(
                api_message_id="msg_002",
                timestamp=datetime.now(),
                model="claude-3-5-sonnet-20241022",
                tool_uses=["execute_command"],
                user_text="Run pytest",
            ),
        ]

        classified = classify_messages(messages)

        assert len(classified) == 2
        assert classified[0].task_category == TaskCategory.CODING
        assert classified[1].task_category == TaskCategory.TESTING


class TestRetryDetection:
    """Test retry cycle detection."""

    def test_detect_retry_cycle_edit_test_edit(self):
        """Test detection of Edit → Test → Edit cycle."""
        messages = [
            Message(
                api_message_id="msg_001",
                timestamp=datetime.now(),
                model="claude-3-5-sonnet-20241022",
                tool_uses=["write_file"],
                user_text="Write code",
                task_category=TaskCategory.CODING,
            ),
            Message(
                api_message_id="msg_002",
                timestamp=datetime.now(),
                model="claude-3-5-sonnet-20241022",
                tool_uses=["execute_command"],
                user_text="Run pytest",
                task_category=TaskCategory.TESTING,
            ),
            Message(
                api_message_id="msg_003",
                timestamp=datetime.now(),
                model="claude-3-5-sonnet-20241022",
                tool_uses=["write_file"],
                user_text="Fix the error",
                task_category=TaskCategory.CODING,
            ),
        ]

        retries = detect_retry_cycles(messages)

        assert 2 in retries  # msg_003 is marked as retry

    def test_no_retry_when_single_edit(self):
        """Test no retry when there's only one edit."""
        messages = [
            Message(
                api_message_id="msg_001",
                timestamp=datetime.now(),
                model="claude-3-5-sonnet-20241022",
                tool_uses=["write_file"],
                user_text="Write code",
                task_category=TaskCategory.CODING,
            ),
        ]

        retries = detect_retry_cycles(messages)

        assert len(retries) == 0

    def test_no_retry_when_test_between_edits(self):
        """Test no retry without test/execution between edits."""
        messages = [
            Message(
                api_message_id="msg_001",
                timestamp=datetime.now(),
                model="claude-3-5-sonnet-20241022",
                tool_uses=["write_file"],
                user_text="Write code",
                task_category=TaskCategory.CODING,
            ),
            Message(
                api_message_id="msg_002",
                timestamp=datetime.now(),
                model="claude-3-5-sonnet-20241022",
                tool_uses=["read_file"],
                user_text="Read file",
                task_category=TaskCategory.EXPLORATION,
            ),
            Message(
                api_message_id="msg_003",
                timestamp=datetime.now(),
                model="claude-3-5-sonnet-20241022",
                tool_uses=["write_file"],
                user_text="Write again",
                task_category=TaskCategory.CODING,
            ),
        ]

        retries = detect_retry_cycles(messages)

        assert len(retries) == 0


class TestOneShot:
    """Test one-shot success rate calculation."""

    def test_one_shot_100_percent(self):
        """Test 100% one-shot rate when no retries."""
        messages = [
            Message(
                api_message_id="msg_001",
                timestamp=datetime.now(),
                model="claude-3-5-sonnet-20241022",
                tool_uses=["write_file"],
                user_text="Write code",
                task_category=TaskCategory.CODING,
            ),
            Message(
                api_message_id="msg_002",
                timestamp=datetime.now(),
                model="claude-3-5-sonnet-20241022",
                tool_uses=["write_file"],
                user_text="Write more code",
                task_category=TaskCategory.CODING,
            ),
        ]

        rate = calculate_one_shot_success_rate(messages)

        assert rate == 100.0

    def test_one_shot_50_percent(self):
        """Test 50% one-shot rate with one retry."""
        messages = [
            Message(
                api_message_id="msg_001",
                timestamp=datetime.now(),
                model="claude-3-5-sonnet-20241022",
                tool_uses=["write_file"],
                user_text="Write code",
                task_category=TaskCategory.CODING,
            ),
            Message(
                api_message_id="msg_002",
                timestamp=datetime.now(),
                model="claude-3-5-sonnet-20241022",
                tool_uses=["execute_command"],
                user_text="Run test",
                task_category=TaskCategory.TESTING,
            ),
            Message(
                api_message_id="msg_003",
                timestamp=datetime.now(),
                model="claude-3-5-sonnet-20241022",
                tool_uses=["write_file"],
                user_text="Fix error",
                task_category=TaskCategory.CODING,
            ),
            Message(
                api_message_id="msg_004",
                timestamp=datetime.now(),
                model="claude-3-5-sonnet-20241022",
                tool_uses=["write_file"],
                user_text="Write more",
                task_category=TaskCategory.CODING,
            ),
        ]

        rate = calculate_one_shot_success_rate(messages)

        assert rate == 66.66666666666666  # 2 out of 3 edits succeeded

    def test_one_shot_zero_edits(self):
        """Test zero rate when no edit tasks."""
        messages = [
            Message(
                api_message_id="msg_001",
                timestamp=datetime.now(),
                model="claude-3-5-sonnet-20241022",
                tool_uses=["read_file"],
                user_text="Read file",
                task_category=TaskCategory.EXPLORATION,
            ),
        ]

        rate = calculate_one_shot_success_rate(messages)

        assert rate == 0.0
