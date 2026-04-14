"""Task classifier for Claude Code messages."""

import re
from .types import Message, TaskCategory


class TaskClassifier:
    """Classifies messages into 13 task categories."""

    # Keywords for each category
    CODING_KEYWORDS = {"code", "implement", "function", "variable", "class"}
    DEBUGGING_KEYWORDS = {
        "debug",
        "fix",
        "error",
        "bug",
        "crash",
        "wrong",
        "issue",
        "not working",
        "broken",
        "fail",
    }
    FEATURE_DEV_KEYWORDS = {
        "add",
        "create",
        "implement",
        "build",
        "new feature",
        "capability",
        "feature",
    }
    REFACTORING_KEYWORDS = {
        "refactor",
        "simplify",
        "clean",
        "optimize",
        "remove",
        "consolidate",
        "rename",
        "reorganize",
    }
    TESTING_COMMANDS = {
        "pytest",
        "vitest",
        "jest",
        "test",
        "npm test",
        "cargo test",
        "unittest",
        "mocha",
        "rspec",
    }
    PLANNING_KEYWORDS = {
        "plan",
        "design",
        "architecture",
        "approach",
        "strategy",
        "roadmap",
    }
    GIT_COMMANDS = {"git commit", "git push", "git merge", "git pull", "git rebase"}
    BUILD_COMMANDS = {
        "npm build",
        "npm run build",
        "docker build",
        "pm2",
        "docker-compose",
        "kubectl",
        "terraform",
        "npm run deploy",
        "cargo build",
        "make build",
    }
    BRAINSTORMING_KEYWORDS = {
        "brainstorm",
        "what if",
        "how would",
        "think about",
        "consider",
        "explore idea",
        "imagine",
    }

    @staticmethod
    def classify(message: Message) -> TaskCategory:
        """Classify a message into a task category.

        Args:
            message: Message to classify.

        Returns:
            TaskCategory enum value.
        """
        user_text = message.user_text.lower()
        tools = set(message.tool_uses)

        # Priority 1: Tool-based classification (most reliable)
        if "write_file" in tools or "edit_file" in tools:
            # Check for refactoring keywords first
            if TaskClassifier._has_keywords(user_text, TaskClassifier.REFACTORING_KEYWORDS):
                return TaskCategory.REFACTORING
            return TaskCategory.CODING

        # Priority 2: Debugging
        if TaskClassifier._has_keywords(user_text, TaskClassifier.DEBUGGING_KEYWORDS):
            if tools:
                return TaskCategory.DEBUGGING

        # Priority 3: Execution-based commands (check before feature dev)
        if "execute_command" in tools:
            if TaskClassifier._has_command(
                user_text, TaskClassifier.TESTING_COMMANDS
            ):
                return TaskCategory.TESTING
            if TaskClassifier._has_command(user_text, TaskClassifier.GIT_COMMANDS):
                return TaskCategory.GIT_OPS
            if TaskClassifier._has_command(user_text, TaskClassifier.BUILD_COMMANDS):
                return TaskCategory.BUILD_DEPLOY

        # Priority 4: Feature development
        if TaskClassifier._has_keywords(user_text, TaskClassifier.FEATURE_DEV_KEYWORDS):
            if tools:
                return TaskCategory.FEATURE_DEV

        # Priority 5: Planning
        if TaskClassifier._has_keywords(user_text, TaskClassifier.PLANNING_KEYWORDS):
            if "write_file" not in tools:
                return TaskCategory.PLANNING

        # Priority 6: Delegation
        if "spawn_agent" in tools or "create_agent" in tools:
            return TaskCategory.DELEGATION

        # Priority 7: Exploration
        if ("read_file" in tools or "grep_code" in tools or "web_search" in tools) and "write_file" not in tools:
            return TaskCategory.EXPLORATION

        # Priority 8: Brainstorming
        if TaskClassifier._has_keywords(user_text, TaskClassifier.BRAINSTORMING_KEYWORDS):
            if not tools:
                return TaskCategory.BRAINSTORMING

        # Priority 9: Conversation (no tools)
        if not tools:
            return TaskCategory.CONVERSATION

        # Priority 10: General (fallback)
        return TaskCategory.GENERAL

    @staticmethod
    def _has_keywords(text: str, keywords: set[str]) -> bool:
        """Check if text contains any keywords.

        Args:
            text: Text to search.
            keywords: Set of keywords to match.

        Returns:
            True if any keyword found.
        """
        for keyword in keywords:
            if re.search(r"\b" + re.escape(keyword) + r"\b", text):
                return True
        return False

    @staticmethod
    def _has_command(text: str, commands: set[str]) -> bool:
        """Check if text contains any commands.

        Args:
            text: Text to search.
            commands: Set of commands to match.

        Returns:
            True if any command found.
        """
        for command in commands:
            if command in text:
                return True
        return False


def classify_message(message: Message) -> Message:
    """Classify a message and return it with category assigned.

    Args:
        message: Message to classify.

    Returns:
        Message with task_category set.
    """
    category = TaskClassifier.classify(message)
    message.task_category = category
    return message


def classify_messages(messages: list[Message]) -> list[Message]:
    """Classify a list of messages.

    Args:
        messages: Messages to classify.

    Returns:
        Messages with task_category set.
    """
    return [classify_message(msg) for msg in messages]


def detect_retry_cycles(messages: list[Message]) -> set[int]:
    """Detect retry cycles in message sequence.

    A retry is detected when Edit → Bash/Execute → Edit pattern occurs.

    Args:
        messages: Sequence of messages.

    Returns:
        Set of indices that are detected as retries.
    """
    retries = set()

    for i in range(len(messages) - 2):
        current = messages[i]
        next_msg = messages[i + 1]
        after_next = messages[i + 2]

        # Pattern: Edit (Coding/Debugging/etc.) → Execute → Edit
        is_edit_current = current.task_category in (
            TaskCategory.CODING,
            TaskCategory.DEBUGGING,
            TaskCategory.REFACTORING,
        )
        is_execute_next = (
            next_msg.task_category == TaskCategory.TESTING
            or "execute_command" in next_msg.tool_uses
        )
        is_edit_after = after_next.task_category in (
            TaskCategory.CODING,
            TaskCategory.DEBUGGING,
            TaskCategory.REFACTORING,
        )

        if is_edit_current and is_execute_next and is_edit_after:
            retries.add(i + 2)  # Mark the retry (second edit)

    return retries


def calculate_one_shot_success_rate(messages: list[Message]) -> float:
    """Calculate one-shot success rate for edit-heavy tasks.

    One-shot = percentage of edits that didn't trigger a retry cycle.

    Args:
        messages: Sequence of messages.

    Returns:
        Success rate as percentage (0-100).
    """
    edit_tasks = {TaskCategory.CODING, TaskCategory.DEBUGGING, TaskCategory.REFACTORING}

    edit_indices = {
        i for i, msg in enumerate(messages) if msg.task_category in edit_tasks
    }

    if not edit_indices:
        return 0.0

    retry_indices = detect_retry_cycles(messages)

    successful_edits = len(edit_indices - retry_indices)
    total_edits = len(edit_indices)

    return (successful_edits / total_edits * 100) if total_edits > 0 else 0.0
