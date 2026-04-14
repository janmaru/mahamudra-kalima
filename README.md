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

### Install from PyPI
```bash
pip install kalima
```

### Or install from source
```bash
git clone https://github.com/yourusername/kalima.git
cd kalima
pip install -e .
```

## Quick Start

```bash
# Interactive dashboard (default: 7 days)
kalima

# Today's usage
kalima today

# Last 30 days
kalima report --days 30

# Export as JSON
kalima export -f json

# Set currency to GBP
kalima currency GBP

# Show current settings
kalima status
```

## Commands

| Command | Description |
|---------|-------------|
| `kalima` | Interactive dashboard (7-day view) |
| `kalima today` | Today's cost and token breakdown |
| `kalima report` | 7-day rolling window (or customize with `--days`) |
| `kalima month` | This calendar month |
| `kalima status` | One-line summary (today + month) |
| `kalima export` | CSV export (today, 7d, 30d) |
| `kalima export -f json` | JSON export |
| `kalima currency GBP` | Set display currency |
| `kalima currency` | Show current currency setting |
| `kalima currency --reset` | Back to USD |

## Dashboard Navigation

Once in the interactive dashboard:
- **Arrow keys** or **1/2/3/4** — Switch between Today / 7 Days / 30 Days / Month views
- **q** — Quit

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
- [Installation & Setup](docs/install.md)
- [Usage Guide](docs/usage.md)
- [Architecture](docs/architecture.md)
- [Task Classifier Details](docs/classifier.md)
- [Contributing](docs/contributing.md)

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

## License

MIT — See [LICENSE](LICENSE) for details.

## Credits

Inspired by [CodeBurn](https://github.com/AgentSeal/codeburn) (Node.js version with multi-provider support). Pricing from [LiteLLM](https://github.com/BerriAI/litellm). Exchange rates from [Frankfurter](https://www.frankfurter.app/).

Built for Claude developers tracking their AI coding costs.
