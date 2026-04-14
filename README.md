# Kalima

See where your Claude Code tokens go. Cost tracking for Claude AI projects by task, tool, and model.

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python 3.11+" />
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License" />
</p>

## Features

- **Interactive Dashboard** — Rich TUI with gradient bars, responsive tables, keyboard navigation
- **Task Classifier** — 13-category breakdown (Coding, Debugging, Testing, Refactoring, etc.)
- **Multi-Period Reports** — Today, 7 days, 30 days, this month
- **Multi-OS Support** — Works on Windows, macOS, Linux (auto-detects paths)
- **Currency Support** — 162 currencies with live exchange rates (cached 24h)
- **One-Shot Success Rate** — See which tasks the AI nails first-try vs. retry cycles
- **Export** — CSV and JSON with breakdowns by period, model, task type
- **Zero Config** — Auto-detects Claude Code sessions from disk

## Installation

### Requirements
- Python 3.11+
- Claude Code installed with session data at `~/.claude/projects/`

### Install from PyPI (recommended)
```bash
pip install kalima
```

### Or install from source
```bash
git clone https://github.com/janmaru/mahamudra-kalima.git
cd kalima
pip install -e .
```

## Quick Start

```bash
# Interactive dashboard (7-day view with tables)
kalima dashboard

# Today's usage
kalima today

# Last 30 days report
kalima report --days 30

# This month
kalima month

# Export as JSON (includes today/7d/30d summaries)
kalima export --format json

# Export as CSV
kalima export --format csv --output costs.csv

# Set currency to GBP
kalima currency GBP

# Show current settings
kalima status

# Quick status (today + month in one line)
kalima status --format text

# Show version
kalima version
```

## Commands

| Command | Description |
|---------|-------------|
| `kalima dashboard` | Interactive dashboard with Rich tables |
| `kalima today` | Today's cost and token breakdown |
| `kalima report [--days N]` | Rolling N-day report (default: 7) |
| `kalima month` | This calendar month |
| `kalima status` | One-line summary (text or JSON) |
| `kalima export [--format json\|csv]` | Export with daily breakdowns |
| `kalima currency [CODE]` | Set/show display currency |
| `kalima currency --reset` | Reset to USD |
| `kalima version` | Show version |

## Dashboard Navigation

The interactive dashboard shows:
- **Summary panel** — Total cost, session count, message count
- **By Task table** — Cost and count per task category
- **By Model table** — Cost and token count per Claude model

The dashboard refreshes automatically and works on Windows, macOS, and Linux.

## What It Tracks

**13 Task Categories** (no LLM calls, fully deterministic):

| Category | What triggers it |
|----------|------------------|
| Coding | Edit, Write tools |
| Debugging | Error/fix keywords + tool usage |
| Feature Dev | "add", "create", "implement" keywords |
| Refactoring | "refactor", "rename", "simplify" |
| Testing | pytest, vitest, jest in commands |
| Exploration | Read, Grep, WebSearch without edits |
| Planning | EnterPlanMode, TaskCreate tools |
| Delegation | Agent tool spawns |
| Git Ops | git push/commit/merge commands |
| Build/Deploy | npm/docker/pm2 build commands |
| Brainstorming | "brainstorm", "what if", "design" |
| Conversation | No tools, pure text exchange |
| General | Uncategorized |

**Metrics**: Per-task one-shot success rate, daily cost chart, token breakdown, model costs, MCP servers used, core tools breakdown.

## Configuration

Config stored at `~/.config/kalima/config.json`:
```json
{
  "currency": "USD",
  "cache_dir": "~/.cache/kalima"
}
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `CLAUDE_CONFIG_DIR` | Override Claude data directory (default: `~/.claude`) |

## How It Works

Kalima reads Claude Code session transcripts directly from disk (no proxy, no API key). Each session is stored as JSONL at `~/.claude/projects/<project>/<session-id>.jsonl`.

For each turn:
1. Extract model, tokens (input/output/cache), and tool usage
2. Classify by task category (deterministic, keyword + tool-based)
3. Calculate cost via LiteLLM pricing (auto-cached)
4. Aggregate by period, model, task, project

## Docs

Full documentation in [`docs/`](docs/):
- [Technical Analysis](docs/technical-analysis.md) -- Architecture, data flow, classifier, pricing
- [Functional Analysis](docs/functional-analysis.md) -- Commands, features, configuration, FAQ
- [Contributing](docs/contributing.md) -- Development setup, release process, PyPI publishing

## Project Structure

```
src/kalima/
  cli.py            # Typer entry point
  parser.py         # JSONL reader, dedup, filtering
  classifier.py     # 13-category task classifier
  models.py         # LiteLLM pricing for Claude
  currency.py       # Exchange rates, formatting
  dashboard.py      # Rich TUI
  report.py         # Text report formatter
  export.py         # CSV/JSON export
  config.py         # Config file management
  types.py          # Pydantic models
```

## Development

```bash
# Install in dev mode with test deps
pip install -e ".[dev]"

# Run tests
pytest

# Run linter/type checker
ruff check .
mypy src/

# Build distribution
python -m build
```

## Publishing to PyPI

### Prerequisites

1. Create PyPI API token at https://pypi.org/manage/account/tokens/
   - Name: `kalima-github-actions`
   - Scope: Entire account

2. Add token to GitHub Secrets:
   - Go to: https://github.com/janmaru/mahamudra-kalima/settings/secrets/actions
   - Add secret: `PYPI_API_TOKEN` = (your token from step 1)

### Publishing a Release

```bash
# 1. Update version in pyproject.toml and src/kalima/__init__.py
# 2. Update CHANGELOG.md with release notes
git commit -am "chore: release v0.2.0"

# 3. Create and push annotated tag (triggers publish workflow)
git tag -a v0.2.0 -m "Release Kalima v0.2.0: Feature X and Y

Features:
- Feature X description
- Feature Y description

Fixes:
- Bug fix description

See CHANGELOG.md for full details."

git push origin v0.2.0

# 4. GitHub Actions automatically:
#    - Detects v0.2.0 tag
#    - Builds distribution (wheel + sdist)
#    - Uploads to PyPI
#    - Package available in 5-10 minutes
```

### Verify Publication

```bash
# Wait 5-10 minutes after workflow completes
pip install kalima==0.2.0
kalima version
```

See [Contributing](docs/contributing.md#pypi-publishing) for detailed guide.


## License

MIT — See [LICENSE](LICENSE) for details.

## Credits

Inspired by [CodeBurn](https://github.com/AgentSeal/codeburn) (Node.js version with multi-provider support). Pricing from [LiteLLM](https://github.com/BerriAI/litellm). Exchange rates from [Frankfurter](https://www.frankfurter.app/).

Built for Claude developers tracking their AI coding costs.
