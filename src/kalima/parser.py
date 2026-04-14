"""JSONL session parser for Claude Code."""

import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from .types import Message, Session, TaskCategory

logger = logging.getLogger(__name__)


def discover_sessions(claude_dir: Optional[Path] = None) -> list[Path]:
    """Discover all Claude Code sessions on disk.

    Args:
        claude_dir: Path to ~/.claude or override. Auto-detected if None.

    Returns:
        List of paths to .jsonl session files.
    """
    if claude_dir is None:
        claude_dir = Path.home() / ".claude"

    projects_dir = claude_dir / "projects"

    if not projects_dir.exists():
        logger.warning(f"Projects directory not found: {projects_dir}")
        return []

    session_files = list(projects_dir.glob("**/*.jsonl"))
    logger.info(f"Found {len(session_files)} session files in {projects_dir}")
    return session_files


def parse_sessions(session_files: list[Path]) -> list[Session]:
    """Parse JSONL session files into Session objects.

    Args:
        session_files: List of .jsonl file paths to parse.

    Returns:
        List of parsed Session objects.
    """
    sessions = []

    for file_path in session_files:
        try:
            session = _parse_single_session(file_path)
            if session and session.messages:
                sessions.append(session)
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            continue

    return sessions


def _parse_single_session(file_path: Path) -> Optional[Session]:
    """Parse a single JSONL session file.

    Args:
        file_path: Path to .jsonl file.

    Returns:
        Parsed Session or None if invalid.
    """
    messages = []
    seen_ids = set()
    first_timestamp = None
    last_timestamp = None
    model = None

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                logger.debug(f"Skipping invalid JSON line in {file_path}")
                continue

            # Extract message from Claude Code JSONL format
            parsed_msg = _extract_message_from_json(data)
            if not parsed_msg:
                continue

            # Deduplicate by API message ID
            msg_id = parsed_msg.get("api_message_id", "")
            if msg_id and msg_id in seen_ids:
                logger.debug(f"Skipping duplicate message {msg_id}")
                continue

            if msg_id:
                seen_ids.add(msg_id)

            timestamp = parsed_msg.get("timestamp")
            if timestamp:
                if first_timestamp is None:
                    first_timestamp = timestamp
                last_timestamp = timestamp

            if not model and parsed_msg.get("model"):
                model = parsed_msg["model"]

            messages.append(parsed_msg)

    if not messages:
        return None

    # Extract project name and session ID from path
    # Path: ~/.claude/projects/<sanitized-path>/<session-id>.jsonl
    parts = file_path.parts
    try:
        projects_idx = parts.index("projects")
        session_id = file_path.stem
        project_parts = parts[projects_idx + 1 : -1]
        project_name = "/".join(project_parts) or "Unknown"
    except (ValueError, IndexError):
        session_id = file_path.stem
        project_name = "Unknown"

    # Create Session object
    session = Session(
        session_id=session_id,
        project_name=project_name,
        created_at=first_timestamp or datetime.now(),
        updated_at=last_timestamp or datetime.now(),
        messages=[Message(**msg) for msg in messages],
    )

    return session


def _extract_message_from_json(data: dict) -> Optional[dict]:
    """Extract message info from Claude JSONL event.

    Supports both formats:
    1. Claude Code: model and usage at top level
    2. Claude CLI: model and usage nested in data["message"]

    Args:
        data: Parsed JSON object from JSONL line.

    Returns:
        Dict with message fields or None if not an assistant message.
    """
    # Support both Claude Code and Claude CLI formats
    msg_data = data.get("message", data)

    # Check if this is an assistant message (has model)
    if "model" not in msg_data:
        return None

    api_message_id = msg_data.get("id", "")
    timestamp_str = msg_data.get("created_at") or data.get("timestamp") or data.get("created_at")

    if timestamp_str:
        try:
            ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            # Ensure timezone-aware (UTC)
            if ts.tzinfo is None:
                timestamp = ts.replace(tzinfo=timezone.utc)
            else:
                timestamp = ts
        except (ValueError, AttributeError):
            timestamp = datetime.now(timezone.utc)
    else:
        timestamp = datetime.now(timezone.utc)

    model = msg_data.get("model", "unknown")
    usage = msg_data.get("usage", {})
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)
    cache_write_tokens = usage.get("cache_creation_input_tokens", 0)
    cache_read_tokens = usage.get("cache_read_input_tokens", 0)

    # Extract tools from content (if structured)
    tool_uses = []
    if "content" in msg_data and isinstance(msg_data["content"], list):
        for block in msg_data["content"]:
            if isinstance(block, dict):
                if block.get("type") == "tool_use":
                    tool_uses.append(block.get("name", ""))

    # Extract user text from previous user message (context-dependent)
    user_text = data.get("user_message", "") or msg_data.get("user_message", "")

    return {
        "api_message_id": api_message_id,
        "timestamp": timestamp,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_write_tokens": cache_write_tokens,
        "cache_read_tokens": cache_read_tokens,
        "tool_uses": tool_uses,
        "user_text": user_text,
        "task_category": TaskCategory.GENERAL,
        "cost_usd": 0.0,
    }


def filter_sessions_by_date(
    sessions: list[Session], days: int
) -> list[Session]:
    """Filter sessions to include only messages from the last N days.

    Args:
        sessions: List of Session objects.
        days: Number of days to include (e.g., 7, 30).

    Returns:
        Filtered sessions with messages from the date range.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    filtered = []
    for session in sessions:
        filtered_messages = [
            msg for msg in session.messages if msg.timestamp >= cutoff
        ]

        if filtered_messages:
            # Create new session with filtered messages
            filtered_session = Session(
                session_id=session.session_id,
                project_name=session.project_name,
                created_at=session.created_at,
                updated_at=session.updated_at,
                messages=filtered_messages,
            )
            filtered.append(filtered_session)

    return filtered


def filter_sessions_by_date_range(
    sessions: list[Session], start_date: datetime, end_date: datetime
) -> list[Session]:
    """Filter sessions to a specific date range (inclusive).

    Args:
        sessions: List of Session objects.
        start_date: Start of range (datetime).
        end_date: End of range (datetime).

    Returns:
        Filtered sessions with messages in the date range.
    """
    filtered = []
    for session in sessions:
        filtered_messages = [
            msg
            for msg in session.messages
            if start_date <= msg.timestamp <= end_date
        ]

        if filtered_messages:
            filtered_session = Session(
                session_id=session.session_id,
                project_name=session.project_name,
                created_at=session.created_at,
                updated_at=session.updated_at,
                messages=filtered_messages,
            )
            filtered.append(filtered_session)

    return filtered
