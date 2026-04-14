#!/usr/bin/env python
"""Kalima CLI for tracking Claude Code costs."""

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from . import __version__
from .parser import discover_sessions, parse_sessions, filter_sessions_by_date, filter_sessions_by_date_range
from .classifier import classify_messages
from .models import calculate_cost
from .config import get_config
from .currency import get_converter
from .report import format_daily_summary, format_period_report, format_status_line
from .export import export_csv, export_json
from .dashboard import run_dashboard

app = typer.Typer(
    help="Track where your Claude Code tokens go.",
    no_args_is_help=True,
)

console = Console()


def _load_and_prepare_sessions(
    days: int = 7,
    custom_claude_dir: Optional[Path] = None,
) -> list:
    """Load, parse, and prepare sessions.

    Args:
        days: Number of days to include.
        custom_claude_dir: Custom Claude directory.

    Returns:
        List of prepared sessions.
    """
    # Discover and parse
    session_files = discover_sessions(custom_claude_dir)
    if not session_files:
        console.print("[red]No Claude Code sessions found.[/red]")
        raise typer.Exit(1)

    sessions = parse_sessions(session_files)
    if not sessions:
        console.print("[red]No valid sessions to process.[/red]")
        raise typer.Exit(1)

    # Filter by date and classify
    filtered = filter_sessions_by_date(sessions, days)
    for session in filtered:
        session.messages = classify_messages(session.messages)

        # Calculate costs
        for msg in session.messages:
            msg.cost_usd = calculate_cost(
                msg.model,
                msg.input_tokens,
                msg.output_tokens,
                msg.cache_write_tokens,
                msg.cache_read_tokens,
            )

    return filtered


@app.command()
def today(
    currency: Optional[str] = typer.Option(
        None,
        "--currency",
        "-c",
        help="Override currency setting",
    ),
) -> None:
    """Show today's usage."""
    config = get_config()
    curr = currency or config.get_currency()

    sessions = _load_and_prepare_sessions(days=0)
    filtered = filter_sessions_by_date(sessions, days=0)

    console.print(format_daily_summary(filtered, curr))


@app.command()
def report(
    days: int = typer.Option(
        7,
        "--days",
        "-d",
        help="Number of days to report",
    ),
    currency: Optional[str] = typer.Option(
        None,
        "--currency",
        "-c",
        help="Override currency setting",
    ),
) -> None:
    """Show cost report for period."""
    config = get_config()
    curr = currency or config.get_currency()

    sessions = _load_and_prepare_sessions(days=days)

    period_name = f"Last {days} days" if days > 1 else "Today"
    console.print(format_period_report(sessions, period_name, curr))


@app.command()
def month(
    currency: Optional[str] = typer.Option(
        None,
        "--currency",
        "-c",
        help="Override currency setting",
    ),
) -> None:
    """Show this month's usage."""
    config = get_config()
    curr = currency or config.get_currency()

    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    session_files = discover_sessions()
    sessions = parse_sessions(session_files)

    filtered = filter_sessions_by_date_range(sessions, month_start, now)
    for session in filtered:
        session.messages = classify_messages(session.messages)
        for msg in session.messages:
            msg.cost_usd = calculate_cost(
                msg.model,
                msg.input_tokens,
                msg.output_tokens,
                msg.cache_write_tokens,
                msg.cache_read_tokens,
            )

    console.print(format_period_report(filtered, "This Month", curr))


@app.command()
def status(
    format: str = typer.Option(
        "text",
        "--format",
        "-f",
        help="Output format (text or json)",
    ),
    currency: Optional[str] = typer.Option(
        None,
        "--currency",
        "-c",
        help="Override currency setting",
    ),
) -> None:
    """Quick status line."""
    import json as json_lib

    config = get_config()
    curr = currency or config.get_currency()

    session_files = discover_sessions()
    sessions = parse_sessions(session_files)

    # Today
    today_sessions = filter_sessions_by_date(sessions, days=0)
    for session in today_sessions:
        session.messages = classify_messages(session.messages)
        for msg in session.messages:
            msg.cost_usd = calculate_cost(
                msg.model,
                msg.input_tokens,
                msg.output_tokens,
                msg.cache_write_tokens,
                msg.cache_read_tokens,
            )

    # This month
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_sessions = filter_sessions_by_date_range(sessions, month_start, now)
    for session in month_sessions:
        session.messages = classify_messages(session.messages)
        for msg in session.messages:
            msg.cost_usd = calculate_cost(
                msg.model,
                msg.input_tokens,
                msg.output_tokens,
                msg.cache_write_tokens,
                msg.cache_read_tokens,
            )

    if format == "json":
        converter = get_converter()
        today_cost = sum(s.total_cost_usd for s in today_sessions)
        month_cost = sum(s.total_cost_usd for s in month_sessions)

        output = {
            "today_usd": today_cost,
            "month_usd": month_cost,
            "currency": curr,
            "timestamp": datetime.now().isoformat(),
        }
        console.print_json(data=output)
    else:
        status = format_status_line(today_sessions, month_sessions, curr)
        console.print(status)


@app.command()
def export(
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path",
    ),
    format: str = typer.Option(
        "csv",
        "--format",
        "-f",
        help="Export format (csv or json)",
    ),
) -> None:
    """Export data to CSV or JSON."""
    session_files = discover_sessions()
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

    # Default output path
    if output is None:
        now = datetime.now()
        if format == "json":
            output = Path(f"kalima_export_{now:%Y%m%d_%H%M%S}.json")
        else:
            output = Path(f"kalima_export_{now:%Y%m%d_%H%M%S}.csv")

    output = Path(output)

    try:
        if format == "json":
            export_json(sessions, output)
            console.print(f"[green]✓[/green] Exported to {output}")
        else:
            export_csv(sessions, output)
            console.print(f"[green]✓[/green] Exported to {output}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def currency(
    code: Optional[str] = typer.Argument(
        None,
        help="ISO 4217 currency code (e.g., EUR, GBP, JPY)",
    ),
    reset: bool = typer.Option(
        False,
        "--reset",
        help="Reset to USD",
    ),
) -> None:
    """Manage currency settings."""
    config = get_config()

    if reset:
        config.set_currency("USD")
        console.print("[green]✓[/green] Currency reset to USD")
        return

    if code is None:
        # Show current
        current = config.get_currency()
        console.print(f"Current currency: {current}")
        return

    # Set currency
    config.set_currency(code.upper())
    console.print(f"[green]✓[/green] Currency set to {code.upper()}")


@app.command()
def dashboard(
    currency: Optional[str] = typer.Option(
        None,
        "--currency",
        "-c",
        help="Override currency setting",
    ),
) -> None:
    """Launch interactive dashboard."""
    config = get_config()
    curr = currency or config.get_currency()

    # Set currency in config if provided
    if currency:
        config.set_currency(currency)

    run_dashboard()


@app.command()
def version() -> None:
    """Show version."""
    console.print(f"Kalima {__version__}")


def main() -> None:
    """Main entry point."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[red]Interrupted[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    main()
