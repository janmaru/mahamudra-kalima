"""Report formatting for terminal output."""

from datetime import datetime, timedelta
from collections import defaultdict

from .types import Session, TaskCategory
from .models import get_model_pricing
from .currency import CurrencyConverter


def format_daily_summary(
    sessions: list[Session],
    currency: str = "USD",
) -> str:
    """Format a daily cost summary.

    Args:
        sessions: Sessions for the day.
        currency: Currency code for display.

    Returns:
        Formatted string.
    """
    converter = CurrencyConverter()

    total_cost = sum(s.total_cost_usd for s in sessions)
    total_input = sum(s.total_input_tokens for s in sessions)
    total_output = sum(s.total_output_tokens for s in sessions)

    cost_str = converter.format_cost(total_cost, currency)

    lines = [
        f"{'=' * 50}",
        f"Daily Summary",
        f"{'=' * 50}",
        f"Cost:        {cost_str}",
        f"Tokens:      {_format_tokens(total_input)} input, {_format_tokens(total_output)} output",
    ]

    # Top models
    model_costs = defaultdict(float)
    for session in sessions:
        for msg in session.messages:
            model_costs[msg.model] += msg.cost_usd

    if model_costs:
        lines.append(f"\nTop Models:")
        for model, cost in sorted(model_costs.items(), key=lambda x: x[1], reverse=True)[:3]:
            lines.append(f"  {model}: {converter.format_cost(cost, currency)}")

    # Top tasks
    task_costs = defaultdict(float)
    task_counts = defaultdict(int)
    for session in sessions:
        for msg in session.messages:
            task_costs[msg.task_category.value] += msg.cost_usd
            task_counts[msg.task_category.value] += 1

    if task_costs:
        lines.append(f"\nTop Tasks:")
        for task, cost in sorted(task_costs.items(), key=lambda x: x[1], reverse=True)[:5]:
            count = task_counts[task]
            lines.append(f"  {task:20} {str(count):>3} turns  {converter.format_cost(cost, currency)}")

    lines.append("")
    return "\n".join(lines)


def format_period_report(
    sessions: list[Session],
    period_name: str = "7 Days",
    currency: str = "USD",
) -> str:
    """Format a comprehensive period report.

    Args:
        sessions: Sessions for the period.
        period_name: Name of period (e.g., "7 Days").
        currency: Currency code for display.

    Returns:
        Formatted string.
    """
    converter = CurrencyConverter()

    total_cost = sum(s.total_cost_usd for s in sessions)
    total_input = sum(s.total_input_tokens for s in sessions)
    total_output = sum(s.total_output_tokens for s in sessions)
    total_cache_write = sum(s.total_cache_write_tokens for s in sessions)
    total_cache_read = sum(s.total_cache_read_tokens for s in sessions)

    cost_str = converter.format_cost(total_cost, currency)

    lines = [
        f"{'=' * 60}",
        f"Report: {period_name}",
        f"{'=' * 60}",
        f"Total Cost:      {cost_str}",
        f"Input Tokens:    {_format_tokens(total_input)}",
        f"Output Tokens:   {_format_tokens(total_output)}",
    ]

    if total_cache_write > 0 or total_cache_read > 0:
        lines.append(
            f"Cache Tokens:    {_format_tokens(total_cache_write)} write, {_format_tokens(total_cache_read)} read"
        )

    # By model
    lines.append(f"\n{'By Model':}")
    model_data = defaultdict(lambda: {"cost": 0.0, "tokens": 0})
    for session in sessions:
        for msg in session.messages:
            model_data[msg.model]["cost"] += msg.cost_usd
            model_data[msg.model]["tokens"] += msg.input_tokens + msg.output_tokens

    for model in sorted(model_data.keys()):
        cost = model_data[model]["cost"]
        tokens = model_data[model]["tokens"]
        cost_str = converter.format_cost(cost, currency)
        lines.append(f"  {model:40} {str(tokens):>10} tokens  {cost_str:>12}")

    # By task category
    lines.append(f"\n{'By Task Category':}")
    task_data = defaultdict(lambda: {"cost": 0.0, "count": 0})
    for session in sessions:
        for msg in session.messages:
            task = msg.task_category.value
            task_data[task]["cost"] += msg.cost_usd
            task_data[task]["count"] += 1

    for task in sorted(task_data.keys()):
        cost = task_data[task]["cost"]
        count = task_data[task]["count"]
        cost_str = converter.format_cost(cost, currency)
        lines.append(f"  {task:30} {str(count):>4} turns  {cost_str:>12}")

    lines.append(f"\n{'=' * 60}\n")
    return "\n".join(lines)


def format_status_line(
    today_sessions: list[Session],
    month_sessions: list[Session],
    currency: str = "USD",
) -> str:
    """Format a one-liner status.

    Args:
        today_sessions: Today's sessions.
        month_sessions: This month's sessions.
        currency: Currency code for display.

    Returns:
        One-line status string.
    """
    converter = CurrencyConverter()

    today_cost = sum(s.total_cost_usd for s in today_sessions)
    month_cost = sum(s.total_cost_usd for s in month_sessions)

    today_str = converter.format_cost(today_cost, currency)
    month_str = converter.format_cost(month_cost, currency)

    return f"Today: {today_str:>10} | Month: {month_str:>10}"


def _format_tokens(count: int) -> str:
    """Format token count with K/M suffix.

    Args:
        count: Number of tokens.

    Returns:
        Formatted string (e.g., "1.2M").
    """
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    elif count >= 1_000:
        return f"{count / 1_000:.1f}K"
    else:
        return str(count)


def create_ascii_chart(
    values: list[float],
    width: int = 40,
    height: int = 10,
    label: str = "Cost",
) -> str:
    """Create ASCII bar chart.

    Args:
        values: List of values to chart.
        width: Chart width in characters.
        height: Chart height in characters.
        label: Chart label.

    Returns:
        ASCII chart string.
    """
    if not values:
        return ""

    max_val = max(values) if values else 1
    if max_val == 0:
        max_val = 1

    lines = [f"{label} Chart:"]

    # Create rows from top to bottom
    for row in range(height, 0, -1):
        threshold = (row / height) * max_val
        bar = ""
        for val in values:
            if val >= threshold:
                bar += "█"
            else:
                bar += " "
        lines.append(f"│{bar}│")

    lines.append("└" + "─" * len(values) + "┘")

    return "\n".join(lines)
