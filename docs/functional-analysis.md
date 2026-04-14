# Functional Analysis

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Configuration](#configuration)
- [Commands](#commands)
- [Dashboard](#dashboard)
- [Export](#export)
- [Currency Support](#currency-support)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

## Overview

Kalima is a cost tracking CLI for Claude Code. It reads session transcripts directly from disk and provides cost breakdowns by task category, model, and time period.

Key capabilities:

- **Zero config** -- auto-discovers Claude Code sessions from `~/.claude/projects/`
- **No network dependency** -- all processing is local (except optional currency conversion)
- **13 task categories** -- deterministic classification, no LLM calls
- **Multi-period reports** -- Today, 7 days, 30 days, this month
- **162 currencies** -- live exchange rates with 24h cache
- **Interactive dashboard** -- Rich TUI with keyboard navigation
- **CSV/JSON export** -- with breakdowns by period, model, task type

## Installation

### Requirements

- Python 3.11+
- Claude Code installed with session data at `~/.claude/projects/`

### From PyPI

```bash
pip install kalima
```

### From source

```bash
git clone https://github.com/janmaru/mahamudra-kalima.git
cd kalima
pip install -e .
```

### Verify

```bash
kalima version
```

## Configuration

### Config file

Created automatically at `~/.config/kalima/config.json`:

```json
{
  "currency": "USD",
  "cache_dir": "~/.cache/kalima"
}
```

No manual setup needed.

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CLAUDE_CONFIG_DIR` | `~/.claude` | Override Claude Code data directory |
| `KALIMA_CONFIG_DIR` | `~/.config/kalima` | Kalima config directory |
| `KALIMA_CACHE_DIR` | `~/.cache/kalima` | Cache directory (exchange rates, pricing) |

### File locations

| Purpose | Path |
|---------|------|
| Claude sessions | `~/.claude/projects/**/*.jsonl` |
| Kalima config | `~/.config/kalima/config.json` |
| Pricing cache | `~/.cache/kalima/litellm_prices.json` |
| Exchange rate cache | `~/.cache/kalima/exchange_rates.json` |

## Commands

| Command | Description |
|---------|-------------|
| `kalima dashboard` | Interactive Rich TUI dashboard |
| `kalima today` | Today's cost and token breakdown |
| `kalima report [--days N]` | Rolling N-day report (default: 7) |
| `kalima month` | This calendar month |
| `kalima status` | One-line summary (text or JSON) |
| `kalima export [--format json\|csv]` | Export with daily breakdowns |
| `kalima currency [CODE]` | Set or show display currency |
| `kalima currency --reset` | Reset to USD |
| `kalima version` | Show version |

### kalima dashboard

Opens the interactive Rich TUI dashboard showing summary, by-model, and by-task breakdowns.

**Keyboard shortcuts:**

| Key | Action |
|-----|--------|
| `1` | Switch to Today |
| `2` | Switch to 7 Days |
| `3` | Switch to 30 Days |
| `4` | Switch to This Month |
| `q` | Quit |
| `Ctrl+C` | Quit |

### kalima today

Shows today's cost breakdown with token counts and task categories.

```
Kalima - Today

Tokens:  1.2M input, 450K output
Cost:    $3.45 (USD)
Models:  Claude 3.5 Sonnet
Tasks:   Coding (5), Testing (2), Debugging (1)
```

### kalima report

Rolling window report with ASCII bar chart, per-model breakdown, per-task breakdown, and one-shot success rates.

```bash
kalima report              # last 7 days (default)
kalima report --days 30    # last 30 days
kalima report --days 14    # custom period
```

### kalima month

Same as report, but filtered to the current calendar month (1st to today).

### kalima status

Compact one-liner for quick checks or scripting.

```bash
kalima status                # Today: $2.34 | Month: $87.50
kalima status --format json  # {"today_usd": 2.34, "month_usd": 87.50, ...}
```

### kalima export

Exports data with breakdowns for today, 7 days, and 30 days.

```bash
kalima export                        # CSV to auto-named file
kalima export --format json          # JSON to auto-named file
kalima export --output costs.csv     # CSV to specific file
kalima export --format json -o data.json
```

## Dashboard

The interactive dashboard layout:

```
+----------------------------------+
|     Kalima - Cost Tracker        |  header
+----------------+-----------------+
| Summary        | By Model        |
|  Total Cost    |  Model | Cost   |  body
|  Sessions      |  ...   | ...    |
|  Messages      |                 |
+----------------+                 |
| By Task        |                 |
|  Task  | Cost  |                 |
|  ...   | ...   |                 |
+----------------+-----------------+
| 1:Today 2:7d 3:30d 4:Month q:Quit|  footer
+----------------------------------+
```

The dashboard loads all session data on startup and filters client-side when switching periods, so navigation is instant.

## Export

### CSV format

Columns: date, model, task, input_tokens, output_tokens, cache_tokens, cost_usd. Includes summary rows for each period.

### JSON format

```json
{
  "generated_at": "2026-04-15T10:00:00Z",
  "currency": "USD",
  "periods": {
    "today": { "total_cost": 2.34, "sessions": 3, "messages": 45 },
    "7_days": { "total_cost": 18.50, "sessions": 12, "messages": 340 },
    "30_days": { "total_cost": 87.50, "sessions": 48, "messages": 1200 }
  },
  "by_model": [...],
  "by_task": [...],
  "daily": [...]
}
```

## Currency Support

Kalima supports all 162 ISO 4217 currency codes. Exchange rates are fetched from the Frankfurter API (ECB data) and cached for 24 hours.

```bash
kalima currency EUR    # set to Euro
kalima currency GBP    # set to British Pound
kalima currency JPY    # set to Japanese Yen
kalima currency        # show current setting
kalima currency --reset  # reset to USD
```

Common codes: USD, EUR, GBP, JPY, AUD, CAD, CHF, CNY, INR, BRL.

The currency setting is persistent (saved in config) and applies to all commands.

## Troubleshooting

### "No Claude Code sessions found"

Claude Code session files are missing from `~/.claude/projects/`.

- Verify Claude Code is installed and has been used at least once
- Check the directory exists: `ls ~/.claude/projects/`
- Override with: `CLAUDE_CONFIG_DIR=/custom/path kalima today`

### All costs show $0.00

Sessions exist but contain no messages with token usage data. Use Claude Code to generate some conversations, then re-run.

### Pricing looks wrong

Pricing is cached for 24 hours. Force a refresh:

```bash
rm ~/.cache/kalima/litellm_prices.json
kalima report
```

### Dashboard rendering issues

Set explicit terminal dimensions:

```bash
export COLUMNS=180 LINES=40
kalima dashboard
```

### Windows path issues

Kalima uses `pathlib` for cross-platform path handling. Both of these work:

```cmd
set CLAUDE_CONFIG_DIR=C:\Users\YourName\.claude
set CLAUDE_CONFIG_DIR=%USERPROFILE%\.claude
```

## FAQ

**Does Kalima send my data anywhere?**
No. All processing is local. The only network requests are for currency exchange rates (optional) and LiteLLM pricing data.

**Which Claude models are supported?**
All Claude models (Claude 3, 3.5, 4 -- Opus, Sonnet, Haiku). Pricing is automatically fetched from LiteLLM.

**Does it work on Windows, macOS, and Linux?**
Yes. Kalima auto-detects the OS and adjusts paths accordingly.

**What if I have custom session locations?**
Set the `CLAUDE_CONFIG_DIR` environment variable.

**How is task classification done?**
Deterministic pattern matching on tool names and keywords. No LLM calls. See [Technical Analysis](technical-analysis.md#task-classifier) for the full rule set.

**Can I track costs across multiple machines?**
Export on each machine (`kalima export -f json`), then combine the files offline.
