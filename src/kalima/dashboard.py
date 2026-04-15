"""Interactive dashboard for Kalima using Rich TUI."""

import sys
import threading
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Optional

from rich.columns import Columns
from rich import box
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

SYNTHETIC_MODEL = "<synthetic>"


def _prepare_sessions(custom_claude_dir: Optional[str] = None):
    """Load and prepare all sessions."""
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


def _create_summary_panel(sessions, period_name: str, currency: str) -> Panel:
    """Create summary panel as a horizontal bar."""
    converter = get_converter()
    total_cost = sum(s.total_cost_usd for s in sessions)
    formatted = converter.format_cost(total_cost, currency)
    num_sessions = len(sessions)
    num_messages = sum(len(s.messages) for s in sessions)

    # Synthetic stats
    synthetic_count = 0
    for s in sessions:
        for msg in s.messages:
            if msg.model == SYNTHETIC_MODEL:
                synthetic_count += 1

    parts = Text(justify="center")
    parts.append(f"  {period_name}  ", style="bold cyan")
    parts.append("│ ", style="dim")
    parts.append("Cost ", style="dim")
    parts.append(formatted, style="bold green")
    parts.append(" │ ", style="dim")
    parts.append("Sessions ", style="dim")
    parts.append(str(num_sessions), style="bold yellow")
    parts.append(" │ ", style="dim")
    parts.append("Messages ", style="dim")
    parts.append(str(num_messages), style="bold yellow")
    if synthetic_count > 0:
        parts.append(" │ ", style="dim")
        parts.append("Synthetic ", style="dim")
        parts.append(str(synthetic_count), style="dim italic")

    return Panel(parts, border_style="dim")


def _create_by_model_table(sessions: list) -> Table:
    """Create by-model breakdown table (excludes synthetic)."""
    by_model = defaultdict(lambda: {"cost": 0.0, "count": 0})

    for session in sessions:
        for msg in session.messages:
            if msg.model == SYNTHETIC_MODEL:
                continue
            by_model[msg.model]["cost"] += msg.cost_usd
            by_model[msg.model]["count"] += 1

    table = Table(
        title="By Model",
        show_header=True,
        expand=True,
        title_style="bold cyan",
        border_style="dim",
        box=box.ROUNDED,
    )
    table.add_column("Model", style="cyan", ratio=3)
    table.add_column("Msgs", justify="right", ratio=1)
    table.add_column("Cost (USD)", justify="right", ratio=1)

    sorted_models = sorted(by_model.items(), key=lambda x: x[1]["cost"], reverse=True)
    for model, data in sorted_models:
        table.add_row(
            model,
            str(data["count"]),
            f"${data['cost']:.2f}",
        )

    return table


def _create_by_task_table(sessions: list) -> Table:
    """Create by-task breakdown table."""
    by_task = defaultdict(lambda: {"cost": 0.0, "count": 0})

    for session in sessions:
        for msg in session.messages:
            if msg.model == SYNTHETIC_MODEL:
                continue
            task = msg.task_category.value
            by_task[task]["cost"] += msg.cost_usd
            by_task[task]["count"] += 1

    table = Table(
        title="By Task",
        show_header=True,
        expand=True,
        title_style="bold magenta",
        border_style="dim",
        box=box.ROUNDED,
    )
    table.add_column("Task", style="magenta", ratio=2)
    table.add_column("Count", justify="right", ratio=1)
    table.add_column("Cost (USD)", justify="right", ratio=1)

    sorted_tasks = sorted(by_task.items(), key=lambda x: x[1]["cost"], reverse=True)
    for task, data in sorted_tasks:
        table.add_row(
            task,
            str(data["count"]),
            f"${data['cost']:.2f}",
        )

    return table


def _cost_to_color(ratio: float) -> str:
    """Return a color based on cost ratio (0.0 to 1.0 of max)."""
    if ratio < 0.25:
        return "green"
    elif ratio < 0.50:
        return "yellow"
    elif ratio < 0.75:
        return "dark_orange"
    else:
        return "red"


def _to_local(ts: datetime) -> datetime:
    """Convert a timestamp to local time."""
    if ts.tzinfo is not None:
        return ts.astimezone().replace(tzinfo=None)
    return ts


def _aggregate_buckets(sessions: list, period_name: str) -> list[tuple[str, float]]:
    """Aggregate costs into buckets appropriate for the period.

    Returns sorted list of (label, cost) tuples.
    """
    from datetime import date as date_type

    raw = defaultdict(float)

    for session in sessions:
        for msg in session.messages:
            if msg.model == SYNTHETIC_MODEL:
                continue
            raw[_to_local(msg.timestamp)] += msg.cost_usd

    if not raw:
        return []

    if period_name == "Today":
        # By hour — all 24 hours, zero-filled
        buckets = defaultdict(float)
        for ts, cost in raw.items():
            buckets[ts.hour] += cost
        return [(f"{h:02d}", buckets.get(h, 0.0)) for h in range(24)]

    elif period_name == "7 Days":
        # Exactly 7 calendar days ending today
        today = datetime.now().date()
        buckets = defaultdict(float)
        for ts, cost in raw.items():
            buckets[ts.date()] += cost
        days_list = [today - timedelta(days=6 - i) for i in range(7)]
        return [(d.strftime("%b %d"), buckets.get(d, 0.0)) for d in days_list]

    elif period_name == "30 Days":
        # Last 30 days, only days with activity
        buckets = defaultdict(float)
        for ts, cost in raw.items():
            buckets[ts.date()] += cost
        return [(d.strftime("%d"), c) for d, c in sorted(buckets.items())]

    elif period_name == "60 Days":
        # 60 days grouped by week
        today = datetime.now().date()
        start = today - timedelta(days=59)
        buckets = defaultdict(float)
        for ts, cost in raw.items():
            buckets[ts.date()] += cost
        weeks: list[tuple[str, float]] = []
        week_start = start - timedelta(days=start.weekday())
        while week_start <= today:
            week_end = week_start + timedelta(days=6)
            total = sum(buckets.get(week_start + timedelta(days=d), 0.0) for d in range(7))
            label = f"{week_start.strftime('%b %d')}"
            weeks.append((label, total))
            week_start += timedelta(days=7)
        return weeks

    else:
        # 90 days grouped by month — all months in range, zero-filled
        from dateutil.relativedelta import relativedelta
        today = datetime.now().date()
        start = (today - timedelta(days=89)).replace(day=1)
        end = today.replace(day=1)
        buckets = defaultdict(float)
        for ts, cost in raw.items():
            key = ts.date().replace(day=1)
            buckets[key] += cost
        months: list[tuple[str, float]] = []
        current = start
        while current <= end:
            months.append((current.strftime("%b"), buckets.get(current, 0.0)))
            current += relativedelta(months=1)
        return months


def _create_chart(sessions: list, period_name: str, console_width: int, chart_height: int) -> Panel:
    """Create vertical bar chart that fills all available space."""
    buckets = _aggregate_buckets(sessions, period_name)

    titles = {
        "Today": "Cost by Hour",
        "7 Days": "Cost by Day",
        "30 Days": "Cost by Day",
        "60 Days": "Cost by Month",
        "90 Days": "Cost by Month",
    }
    title = titles.get(period_name, "Cost")

    if not buckets:
        return Panel(Text("No data", justify="center", style="dim"), title=title, border_style="dim")

    max_cost = max(v for _, v in buckets)
    if max_cost == 0:
        max_cost = 1.0

    num_buckets = len(buckets)
    # Available width inside panel = console_width - 4 (panel borders + padding)
    inner_width = console_width - 4
    # Slot = bar + gap. Distribute evenly, gap is always 1 char.
    slot_width = inner_width // num_buckets
    gap = 1
    bar_width = max(slot_width - gap, 1)

    bar_data = []
    for _, cost in buckets:
        ratio = cost / max_cost
        h = max(int(ratio * chart_height), 1) if cost > 0 else 0
        bar_data.append((h, ratio, cost))

    lines = Text()

    # Cost value row on top of each bar
    for col, (_, ratio, cost) in enumerate(bar_data):
        if col > 0:
            lines.append(" " * gap)
        cost_str = f"${cost:.0f}" if cost >= 1 else f"${cost:.2f}"
        color = _cost_to_color(ratio) if cost > 0 else "dim"
        lines.append(f"{cost_str:^{bar_width}}", style="bold " + color)
    lines.append("\n\n")

    # Bars from top to bottom
    for row in range(chart_height, 0, -1):
        for col, (h, ratio, _) in enumerate(bar_data):
            if col > 0:
                lines.append(" " * gap)
            if h >= row:
                color = _cost_to_color(ratio)
                lines.append("█" * bar_width, style=color)
            else:
                lines.append(" " * bar_width)
        lines.append("\n")

    # Separator
    total_width = num_buckets * slot_width - gap
    lines.append("─" * total_width, style="dim")
    lines.append("\n")

    # Labels centered under each bar
    for col, (label, _) in enumerate(buckets):
        if col > 0:
            lines.append(" " * gap)
        truncated = label[:bar_width]
        lines.append(f"{truncated:^{bar_width}}", style="dim")

    return Panel(lines, title=title, title_align="left", border_style="dim")


def _create_footer(period_name: str) -> Panel:
    """Create footer with menu, highlighting active period."""
    menu_items = [
        ("1", "Today"),
        ("2", "7 Days"),
        ("3", "30 Days"),
        ("4", "60 Days"),
        ("5", "90 Days"),
    ]
    help_text = Text(justify="center")
    for i, (key, label) in enumerate(menu_items):
        if i > 0:
            help_text.append(" │ ", style="dim")
        if label == period_name:
            help_text.append(f"{key}: {label}", style="bold cyan")
        else:
            help_text.append(f"{key}: {label}", style="dim")
    help_text.append(" │ ", style="dim")
    help_text.append("q: Quit", style="dim")
    return Panel(help_text, border_style="dim")


def _create_layout(sessions: list, period_name: str, currency: str) -> Layout:
    """Create dashboard layout."""
    console = Console()
    console_width = console.width
    console_height = console.height

    # Table height based on content of the bigger table
    model_rows = len({msg.model for s in sessions for msg in s.messages if msg.model != SYNTHETIC_MODEL})
    task_rows = len({msg.task_category.value for s in sessions for msg in s.messages if msg.model != SYNTHETIC_MODEL})
    max_rows = max(model_rows, task_rows, 1)
    # title(1) + top border(1) + header row(1) + header separator(1) + data rows + bottom border(1)
    table_height = max_rows + 5

    # Fixed: header(3) + summary(3) + tables + footer(3)
    fixed_height = 3 + 3 + table_height + 3
    chart_height = max(console_height - fixed_height, 6)
    # Chart content: panel borders(2) + value row(2) + label row(2) + separator(1)
    bar_height = max(chart_height - 7, 3)

    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="summary", size=3),
        Layout(name="tables", size=table_height),
        Layout(name="chart", ratio=1),
        Layout(name="footer", size=3),
    )

    header_text = Text("Kalima — Claude Code Cost Tracker", justify="center", style="bold cyan")
    layout["header"].update(Panel(header_text, border_style="dim"))

    layout["summary"].update(_create_summary_panel(sessions, period_name, currency))

    layout["tables"].split_row(
        Layout(name="tasks"),
        Layout(name="models"),
    )
    layout["tasks"].update(_create_by_task_table(sessions))
    layout["models"].update(_create_by_model_table(sessions))

    layout["chart"].update(_create_chart(sessions, period_name, console_width, bar_height))

    layout["footer"].update(_create_footer(period_name))

    return layout


def _filter_for_period(
    sessions: list, period_key: str
) -> tuple[list, str]:
    """Filter sessions for a given period key.

    Returns:
        (filtered_sessions, period_label)
    """
    if period_key == "1":
        return filter_sessions_by_date(sessions, days=1), "Today"
    elif period_key == "3":
        return filter_sessions_by_date(sessions, days=30), "30 Days"
    elif period_key == "4":
        return filter_sessions_by_date(sessions, days=60), "60 Days"
    elif period_key == "5":
        return filter_sessions_by_date(sessions, days=90), "90 Days"
    else:
        return filter_sessions_by_date(sessions, days=7), "7 Days"


def run_dashboard(custom_claude_dir: Optional[str] = None) -> None:
    """Run interactive dashboard.

    Args:
        custom_claude_dir: Custom Claude directory.
    """
    console = Console()
    config = get_config()
    currency = config.get_currency()

    sessions = _prepare_sessions(custom_claude_dir=custom_claude_dir)
    filtered, period = _filter_for_period(sessions, "2")

    stop_event = threading.Event()

    def key_listener() -> None:
        """Read keys in a background thread."""
        nonlocal filtered, period
        if sys.platform == "win32":
            import msvcrt
            while not stop_event.is_set():
                if msvcrt.kbhit():
                    key = msvcrt.getwch()
                    if key in ("q", "Q"):
                        stop_event.set()
                        return
                    if key in ("1", "2", "3", "4", "5"):
                        filtered, period = _filter_for_period(sessions, key)
                stop_event.wait(0.1)
        else:
            import readchar
            while not stop_event.is_set():
                try:
                    key = readchar.readkey()
                except KeyboardInterrupt:
                    stop_event.set()
                    return
                if key in ("q", "Q"):
                    stop_event.set()
                    return
                if key in ("1", "2", "3", "4", "5"):
                    filtered, period = _filter_for_period(sessions, key)

    listener = threading.Thread(target=key_listener, daemon=True)
    listener.start()

    try:
        with Live(
            _create_layout(filtered, period, currency),
            refresh_per_second=2,
            screen=True,
            console=console,
        ) as live:
            while not stop_event.is_set():
                live.update(_create_layout(filtered, period, currency))
                stop_event.wait(0.5)
    except KeyboardInterrupt:
        stop_event.set()
    finally:
        console.print("[dim]Dashboard closed[/dim]")
