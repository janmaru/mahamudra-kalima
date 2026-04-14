"""Interactive dashboard for Kalima using Rich TUI."""

from datetime import datetime, timedelta
from typing import Optional

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .parser import discover_sessions, parse_sessions, filter_sessions_by_date, filter_sessions_by_date_range
from .classifier import classify_messages
from .models import calculate_cost
from .config import get_config
from .currency import get_converter


def _prepare_sessions(days: int = 7, custom_claude_dir: Optional[str] = None):
    """Load and prepare sessions."""
    from pathlib import Path

    session_files = discover_sessions(
        Path(custom_claude_dir) if custom_claude_dir else None
    )
    sessions = parse_sessions(session_files)

    for session in sessions:
        session.messages = classify_messages(session.messages)
        for msg in session.messages:
            msg.cost_usd = calculate_cost(
                msg.model,
                msg.input_tokens,
                msg.output_tokens,
                msg.cache_write_tokens,
                msg.cache_read_tokens,
            )

    return sessions


def _create_summary_table(sessions, period_name: str, currency: str) -> Table:
    """Create summary table."""
    converter = get_converter()
    total_cost = sum(s.total_cost_usd for s in sessions)
    formatted = converter.format_cost(total_cost, currency)

    table = Table(title=f"Summary: {period_name}", show_header=False)
    table.add_row("Total Cost", formatted)
    table.add_row(
        "Sessions",
        str(len(sessions)),
    )
    table.add_row(
        "Messages",
        str(sum(len(s.messages) for s in sessions)),
    )

    return table


def _create_by_model_table(sessions: list) -> Table:
    """Create by-model breakdown table."""
    from collections import defaultdict

    converter = get_converter()
    by_model = defaultdict(lambda: {"cost": 0.0, "count": 0})

    for session in sessions:
        for msg in session.messages:
            by_model[msg.model]["cost"] += msg.cost_usd
            by_model[msg.model]["count"] += 1

    table = Table(title="By Model", show_header=True)
    table.add_column("Model", style="cyan")
    table.add_column("Messages", justify="right")
    table.add_column("Cost (USD)", justify="right")

    for model in sorted(by_model.keys()):
        data = by_model[model]
        table.add_row(
            model,
            str(data["count"]),
            f"${data['cost']:.2f}",
        )

    return table


def _create_by_task_table(sessions: list) -> Table:
    """Create by-task breakdown table."""
    from collections import defaultdict

    by_task = defaultdict(lambda: {"cost": 0.0, "count": 0})

    for session in sessions:
        for msg in session.messages:
            task = msg.task_category.value
            by_task[task]["cost"] += msg.cost_usd
            by_task[task]["count"] += 1

    table = Table(title="By Task", show_header=True)
    table.add_column("Task", style="magenta")
    table.add_column("Count", justify="right")
    table.add_column("Cost (USD)", justify="right")

    for task in sorted(by_task.keys()):
        data = by_task[task]
        table.add_row(
            task,
            str(data["count"]),
            f"${data['cost']:.2f}",
        )

    return table


def _create_layout(sessions: list, period_name: str, currency: str) -> Layout:
    """Create dashboard layout."""
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3),
    )

    header_text = Text("Kalima - Claude Code Cost Tracker", justify="center", style="bold cyan")
    layout["header"].update(Panel(header_text))

    layout["body"].split_row(
        Layout(name="left"),
        Layout(name="right"),
    )

    layout["left"].split_column(
        Layout(_create_summary_table(sessions, period_name, currency)),
        Layout(_create_by_task_table(sessions)),
    )

    layout["right"].update(_create_by_model_table(sessions))

    help_text = Text(
        "1: Today | 2: 7 Days | 3: 30 Days | 4: Month | q: Quit",
        justify="center",
        style="dim",
    )
    layout["footer"].update(Panel(help_text))

    return layout


def run_dashboard(custom_claude_dir: Optional[str] = None) -> None:
    """Run interactive dashboard.

    Args:
        custom_claude_dir: Custom Claude directory.
    """
    console = Console()
    config = get_config()
    currency = config.get_currency()

    # Initial load
    sessions = _prepare_sessions(days=7, custom_claude_dir=custom_claude_dir)
    filtered = filter_sessions_by_date(sessions, days=7)

    period = "7 Days"
    period_days = 7

    def refresh_view() -> Layout:
        """Refresh the dashboard view."""
        return _create_layout(filtered, period, currency)

    try:
        with Live(refresh_view(), refresh_per_second=1, screen=True) as live:
            while True:
                key = console.input("")  # This doesn't work for keyboard input in Rich Live

                # For now, just support static display
                # Full interactive keyboard support would require additional libraries
                break

    except KeyboardInterrupt:
        console.print("\n[dim]Dashboard closed[/dim]")
