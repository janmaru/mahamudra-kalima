# Usage Guide

## Commands

### Interactive Dashboard

```bash
kalima
```

Opens a rich, interactive dashboard showing your Claude Code costs over the last 7 days. Navigate with arrow keys or number keys.

**Keyboard shortcuts:**
- `1` / `2` / `3` / `4` — Jump to Today / 7 Days / 30 Days / Month
- `←` / `→` or arrow keys — Navigate between periods
- `q` — Quit

### Daily Report

```bash
kalima today
```

Shows today's cost and token breakdown in the terminal. Quick overview without opening the dashboard.

Example output:
```
Kalima - Today

Tokens:  1.2M input, 450K output
Cost:    $3.45 (USD)
Models:  Claude 3.5 Sonnet
Tasks:   Coding (5), Testing (2), Debugging (1)
```

### Rolling Window Reports

```bash
# Last 7 days (default)
kalima report

# Last 30 days
kalima report --days 30

# Custom: last 14 days
kalima report --days 14

# This calendar month
kalima month
```

Output includes:
- Daily cost chart (ASCII bar chart)
- Per-model breakdown
- Per-task breakdown
- One-shot success rates (for edit-heavy tasks)
- Total tokens and cost

### Status One-Liner

```bash
kalima status
```

Compact summary: today's cost + this month's cost.

Example:
```
Today: $2.34 | Month: $87.50
```

### Export Data

```bash
# CSV format (default)
kalima export

# JSON format
kalima export -f json

# Output to file
kalima export -o my_costs.csv
kalima export -f json -o costs.json
```

Exports include breakdowns for:
- Today
- Last 7 days
- Last 30 days
- This month

### Currency Management

```bash
# Set currency to British Pounds
kalima currency GBP

# Set to Australian Dollars
kalima currency AUD

# Show current currency
kalima currency

# Reset to USD
kalima currency --reset
```

Supports all 162 ISO 4217 currency codes. Exchange rates fetched from Frankfurter (ECB data), cached for 24 hours.

Common currencies:
```bash
kalima currency USD  # US Dollar
kalima currency EUR  # Euro
kalima currency GBP  # British Pound
kalima currency JPY  # Japanese Yen
kalima currency AUD  # Australian Dollar
kalima currency CAD  # Canadian Dollar
```

## Examples

### Check today's spending and open dashboard

```bash
kalima today
kalima  # opens dashboard
```

### Weekly cost report

```bash
kalima report --days 7
```

### Export monthly data as JSON for analysis

```bash
kalima export -f json -o march_costs.json
```

### Monitor costs in a specific currency

```bash
kalima currency EUR
kalima report  # now shown in EUR
```

### Quick status check in scripts

```bash
kalima status --format json
# Output: {"today": 2.34, "month": 87.50, "currency": "USD"}
```

## Dashboard Details

The interactive dashboard shows:

1. **Top Panel** — Summary stats (total cost, tokens, one-shot rate)
2. **Chart** — Daily cost trend (ASCII bar chart)
3. **Models** — Per-model cost and token breakdown
4. **Tasks** — 13-category task breakdown with one-shot rates
5. **Tools** — Most-used tools (Read, Edit, Execute, etc.)

Press number keys (`1`/`2`/`3`/`4`) or use arrow keys to switch between:
- **Today** — Current day
- **7 Days** — Last 7 days rolling window
- **30 Days** — Last 30 days rolling window
- **Month** — Current calendar month

## Tips & Tricks

### Quick daily standup

```bash
kalima status
# Get one-liner: "Today: $2.34 | Month: $87.50"
```

### Audit a specific task type

```bash
kalima report --task coding  # (planned feature)
```

### Track costs across machines

Export on each machine, combine offline:
```bash
kalima export -f json -o machine1_costs.json
# copy to other machines, combine in spreadsheet
```

### Watch mode (continuous monitoring)

```bash
kalima --watch  # updates dashboard every 5 minutes (planned)
```

## Troubleshooting

### "No data found"

Ensure Claude Code has run and created sessions:
```bash
ls ~/.claude/projects/
```

### Dashboard rendering issues

Try setting explicit terminal size:
```bash
export COLUMNS=180 LINES=40
kalima
```

### Pricing looks wrong

Kalima caches pricing for 24h. Force refresh:
```bash
rm ~/.cache/kalima/litellm_prices.json
kalima report
```

## Next Steps

- **Deep Dive**: See [architecture.md](architecture.md) for how costs are calculated
- **Classifier**: Learn about the [13 task categories](classifier.md)
- **Contribute**: Help improve Kalima — see [contributing.md](contributing.md)
