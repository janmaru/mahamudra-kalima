"""Export functionality for CSV and JSON formats."""

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from .types import Session
from .models import get_model_pricing


def export_csv(
    sessions: list[Session],
    output_path: Path,
    include_periods: bool = True,
) -> None:
    """Export sessions to CSV.

    Args:
        sessions: Sessions to export.
        output_path: Path to write CSV file.
        include_periods: Include today/7d/30d summary rows.
    """
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            "date",
            "project",
            "session_id",
            "model",
            "input_tokens",
            "output_tokens",
            "cache_write_tokens",
            "cache_read_tokens",
            "cost_usd",
            "task_category",
        ])

        # Data rows
        for session in sessions:
            for msg in session.messages:
                writer.writerow([
                    msg.timestamp.strftime("%Y-%m-%d"),
                    session.project_name,
                    session.session_id,
                    msg.model,
                    msg.input_tokens,
                    msg.output_tokens,
                    msg.cache_write_tokens,
                    msg.cache_read_tokens,
                    f"{msg.cost_usd:.6f}",
                    msg.task_category.value,
                ])

        # Summary rows
        if include_periods:
            writer.writerow([])
            writer.writerow(["Summary"])

            today = datetime.now().date()
            today_sessions = [
                s for s in sessions
                if any(m.timestamp.date() == today for m in s.messages)
            ]
            writer.writerow([f"Today ({today})", "", "", "", "", "", "", "", "", ""])
            _write_period_summary(writer, today_sessions)

            # Last 7 days
            cutoff_7d = datetime.now() - timedelta(days=7)
            last_7d = [
                s for s in sessions
                if any(m.timestamp >= cutoff_7d for m in s.messages)
            ]
            writer.writerow([f"Last 7 Days", "", "", "", "", "", "", "", "", ""])
            _write_period_summary(writer, last_7d)

            # Last 30 days
            cutoff_30d = datetime.now() - timedelta(days=30)
            last_30d = [
                s for s in sessions
                if any(m.timestamp >= cutoff_30d for m in s.messages)
            ]
            writer.writerow([f"Last 30 Days", "", "", "", "", "", "", "", "", ""])
            _write_period_summary(writer, last_30d)


def _write_period_summary(writer: csv.writer, sessions: list[Session]) -> None:
    """Write period summary to CSV writer.

    Args:
        writer: CSV writer.
        sessions: Sessions for period.
    """
    total_input = sum(
        m.input_tokens for s in sessions for m in s.messages
    )
    total_output = sum(
        m.output_tokens for s in sessions for m in s.messages
    )
    total_cache_write = sum(
        m.cache_write_tokens for s in sessions for m in s.messages
    )
    total_cache_read = sum(
        m.cache_read_tokens for s in sessions for m in s.messages
    )
    total_cost = sum(m.cost_usd for s in sessions for m in s.messages)

    writer.writerow([
        "Total",
        "",
        "",
        "",
        total_input,
        total_output,
        total_cache_write,
        total_cache_read,
        f"{total_cost:.2f}",
        "",
    ])


def export_json(
    sessions: list[Session],
    output_path: Path,
    include_periods: bool = True,
) -> None:
    """Export sessions to JSON.

    Args:
        sessions: Sessions to export.
        output_path: Path to write JSON file.
        include_periods: Include today/7d/30d summary.
    """
    data = {
        "export_time": datetime.now().isoformat(),
        "sessions": [],
        "summary": {},
    }

    # Sessions
    for session in sessions:
        session_data = {
            "session_id": session.session_id,
            "project": session.project_name,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "messages": [],
        }

        for msg in session.messages:
            msg_data = {
                "timestamp": msg.timestamp.isoformat(),
                "model": msg.model,
                "input_tokens": msg.input_tokens,
                "output_tokens": msg.output_tokens,
                "cache_write_tokens": msg.cache_write_tokens,
                "cache_read_tokens": msg.cache_read_tokens,
                "cost_usd": msg.cost_usd,
                "task_category": msg.task_category.value,
                "tools": msg.tool_uses,
            }
            session_data["messages"].append(msg_data)

        data["sessions"].append(session_data)

    # Summary periods
    if include_periods:
        today = datetime.now().date()
        today_sessions = [
            s for s in sessions
            if any(m.timestamp.date() == today for m in s.messages)
        ]
        data["summary"]["today"] = _calculate_period_summary(today_sessions)

        cutoff_7d = datetime.now() - timedelta(days=7)
        last_7d = [
            s for s in sessions
            if any(m.timestamp >= cutoff_7d for m in s.messages)
        ]
        data["summary"]["last_7_days"] = _calculate_period_summary(last_7d)

        cutoff_30d = datetime.now() - timedelta(days=30)
        last_30d = [
            s for s in sessions
            if any(m.timestamp >= cutoff_30d for m in s.messages)
        ]
        data["summary"]["last_30_days"] = _calculate_period_summary(last_30d)

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)


def _calculate_period_summary(sessions: list[Session]) -> dict:
    """Calculate summary for a period.

    Args:
        sessions: Sessions for period.

    Returns:
        Summary dictionary.
    """
    total_input = sum(
        m.input_tokens for s in sessions for m in s.messages
    )
    total_output = sum(
        m.output_tokens for s in sessions for m in s.messages
    )
    total_cache_write = sum(
        m.cache_write_tokens for s in sessions for m in s.messages
    )
    total_cache_read = sum(
        m.cache_read_tokens for s in sessions for m in s.messages
    )
    total_cost = sum(m.cost_usd for s in sessions for m in s.messages)

    # By model
    by_model = {}
    for s in sessions:
        for m in s.messages:
            if m.model not in by_model:
                by_model[m.model] = {"cost": 0.0, "tokens": 0}
            by_model[m.model]["cost"] += m.cost_usd
            by_model[m.model]["tokens"] += m.input_tokens + m.output_tokens

    # By task
    by_task = {}
    for s in sessions:
        for m in s.messages:
            task = m.task_category.value
            if task not in by_task:
                by_task[task] = {"cost": 0.0, "count": 0}
            by_task[task]["cost"] += m.cost_usd
            by_task[task]["count"] += 1

    return {
        "total_cost_usd": total_cost,
        "input_tokens": total_input,
        "output_tokens": total_output,
        "cache_write_tokens": total_cache_write,
        "cache_read_tokens": total_cache_read,
        "message_count": sum(len(s.messages) for s in sessions),
        "session_count": len(sessions),
        "by_model": by_model,
        "by_task": by_task,
    }
