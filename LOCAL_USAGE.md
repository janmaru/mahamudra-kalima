# Running Kalima Locally

## Installation

### From Source (Development Mode)

```bash
cd C:\Coding\kalima
pip install -e .
```

This installs Kalima in editable mode, so changes to the code are reflected immediately.

### Verify Installation

```bash
python -m kalima.cli version
# Output: Kalima 0.1.0
```

## Commands

### 1. Show Version

```bash
python -m kalima.cli version
```

Output:
```
Kalima 0.1.0
```

### 2. Currency Settings

**Check current currency:**
```bash
python -m kalima.cli currency
```

Output:
```
Current currency: USD
```

**Change currency:**
```bash
python -m kalima.cli currency EUR
# Output: Currency set to EUR

python -m kalima.cli currency GBP
# Output: Currency set to GBP
```

**Reset to USD:**
```bash
python -m kalima.cli currency --reset
# Output: Currency reset to USD
```

### 3. Quick Status

**Show today and month totals:**
```bash
python -m kalima.cli status
```

Output (example):
```
Today: $0.00 | Month: $0.00
```

**As JSON:**
```bash
python -m kalima.cli status --format json
```

Output:
```json
{
  "today_usd": 0.0,
  "month_usd": 0.0,
  "currency": "USD",
  "timestamp": "2026-04-14T19:26:40.938Z"
}
```

### 4. Today's Report

```bash
python -m kalima.cli today
```

Shows today's cost breakdown with token counts and task categories.

### 5. Period Report

**Default (last 7 days):**
```bash
python -m kalima.cli report
```

**Custom period:**
```bash
python -m kalima.cli report --days 30
python -m kalima.cli report --days 15
python -m kalima.cli report --days 1
```

**With currency override:**
```bash
python -m kalima.cli report --days 30 --currency EUR
```

### 6. This Month

```bash
python -m kalima.cli month
```

Shows cost report from the 1st of the current month to today.

### 7. Export Data

**Export as CSV (default):**
```bash
python -m kalima.cli export
# Creates: kalima_export_20260414_192640.csv
```

**Export as JSON:**
```bash
python -m kalima.cli export --format json
# Creates: kalima_export_20260414_192640.json
```

**Specify output file:**
```bash
python -m kalima.cli export --output costs.csv
python -m kalima.cli export --output data.json --format json
```

The exported files include:
- Daily message data with tokens and costs
- Summary sections for today, 7 days, and 30 days
- Breakdown by model and task category

### 8. Interactive Dashboard

```bash
python -m kalima.cli dashboard
```

Shows a Rich TUI dashboard with:
- Summary panel (total cost, session count, message count)
- By-model breakdown table
- By-task category table

## Running Tests

### All Tests

```bash
pytest tests/ -v
```

Expected output:
```
...
================================================= 112 passed in 0.38s =================================================
```

### Specific Test Module

```bash
pytest tests/test_cli.py -v
pytest tests/test_parser.py -v
pytest tests/test_classifier.py -v
```

### Single Test

```bash
pytest tests/test_cli.py::TestCLIVersion::test_version_command -v
```

### With Coverage

```bash
pytest tests/ --cov=src/kalima --cov-report=term-missing
```

## Development Workflow

### Editing Code

After installing with `pip install -e .`, edits are reflected immediately:

```bash
# Edit src/kalima/cli.py
# Run command - changes are active
python -m kalima.cli version
```

### Running Linter

```bash
ruff check src/ tests/
```

### Type Checking

```bash
mypy src/kalima
```

### Building Distribution

```bash
python -m build
# Creates: dist/kalima-0.1.0-py3-none-any.whl
#         dist/kalima-0.1.0.tar.gz
```

## Troubleshooting

### Command Not Found

If you get "command not found" when running `kalima`:

**Option 1: Use full module path**
```bash
python -m kalima.cli version
```

**Option 2: Reinstall editable**
```bash
pip install -e .
```

### No Sessions Found

If you see:
```
[red]No Claude Code sessions found.[/red]
```

This is normal if you don't have Claude Code session data at `~/.claude/projects/`.

The commands still work - they just show $0.00 costs.

### Data Location

Kalima reads from:
```
~/.claude/projects/
```

Configuration saved to:
```
~/.config/kalima/config.json
```

Cache saved to:
```
~/.cache/kalima/
```

## Example Usage Scenarios

### Scenario 1: Check Today's Costs

```bash
python -m kalima.cli today
```

### Scenario 2: Change Currency and Check Status

```bash
python -m kalima.cli currency EUR
python -m kalima.cli status
python -m kalima.cli currency --reset  # Back to USD
```

### Scenario 3: Export Monthly Data

```bash
python -m kalima.cli month
python -m kalima.cli export --format json --output april.json
```

### Scenario 4: Run Full Test Suite

```bash
pytest tests/ -v
# Make sure all 112 tests pass before releasing
```

### Scenario 5: Verify Changes Before Commit

```bash
# After editing code
pytest tests/ -q
python -m kalima.cli version
python -m kalima.cli status
ruff check src/
```

## Next Steps

- Read: [READY_TO_RELEASE.md](READY_TO_RELEASE.md) to publish v0.1.0
- Edit: Any module in `src/kalima/` and test immediately (editable mode)
- Commit: Changes when tests pass and manual testing verifies functionality
