# Architecture & Design

## Overview

Kalima reads Claude Code session transcripts from disk and calculates costs in three stages:
1. **Parse** — Read JSONL session files, deduplicate, filter by date
2. **Classify** — Categorize each turn (13 task types)
3. **Aggregate** — Calculate costs, roll up by period/model/task

No API calls, no proxy. All processing local.

## Data Flow

```
~/.claude/projects/
    ↓
parser.py (read JSONL, dedup, date filter)
    ↓
parser.Session (in-memory representation)
    ↓
classifier.py (analyze tools, keywords → task type)
    ↓
models.py (LiteLLM pricing → cost)
    ↓
report.py / dashboard.py / export.py (format output)
```

## File Organization

```
src/kalima/
├── cli.py           Entry point, Typer commands
├── parser.py        JSONL reader, deduplication, filtering
├── classifier.py    13-category task classifier
├── models.py        Claude model definitions, LiteLLM pricing
├── currency.py      Exchange rates, formatting
├── dashboard.py     Rich TUI (tables, charts, keyboard nav)
├── report.py        Text formatter (ASCII charts, summaries)
├── export.py        CSV/JSON export
├── config.py        Config file and directory management
└── types.py         Pydantic models (TypedDict equivalents)
```

## Core Modules

### `parser.py`

Reads Claude Code JSONL session files:

```python
# ~/.claude/projects/<project>/<session-id>.jsonl
# Each line is a JSON message event

parser.parse_sessions()  # discovers all sessions
parser.get_messages()    # filters by date range
parser.deduplicate()     # removes duplicate entries
```

**Deduplication**: Messages are keyed by `api_message_id` or timestamp to avoid double-counting.

### `classifier.py`

Analyzes each turn and assigns a task category:

```python
def classify(message: Message) -> TaskCategory:
    # Inspect: tools used, keywords in user text
    # Return: one of 13 categories
    pass

# 13 categories: Coding, Debugging, Testing, Refactoring, etc.
```

**Fully deterministic** — no LLM calls, just pattern matching on tool names and keywords.

### `models.py`

Claude model definitions and pricing:

```python
class ModelCost:
    name: str
    input_cost: float   # per 1M input tokens
    output_cost: float  # per 1M output tokens
    cache_write_cost: float
    cache_read_cost: float

MODELS = {
    "claude-opus-4": ModelCost(...),
    "claude-sonnet-4": ModelCost(...),
    ...
}
```

Pricing fetched from LiteLLM and cached 24h at `~/.cache/kalima/litellm_prices.json`.

### `currency.py`

Multi-currency support:

```python
# Auto-detects or reads from config
get_exchange_rate("GBP")  # fetches from Frankfurter
format_cost(2.34, "EUR")  # → "€2.34"
```

Supports all 162 ISO 4217 currencies. Rates cached 24h.

### `dashboard.py`

Interactive Rich TUI:

```python
# Uses Rich tables, panels, sparklines
# Keyboard navigation (arrow keys, number shortcuts)
# Updates on date range change
```

### `report.py`

Terminal text formatter:

```python
format_daily_report()     # today's summary
format_period_report()    # 7d/30d/month with charts
format_ascii_chart()      # bar chart for daily costs
```

### `export.py`

CSV/JSON export:

```python
export_csv(sessions, path)
export_json(sessions, path)

# Outputs multiple periods: today, 7d, 30d, month
```

## Message Structure

Each Claude Code session message:

```python
@dataclass
class Message:
    api_message_id: str
    timestamp: datetime
    model: str
    input_tokens: int
    output_tokens: int
    cache_write_tokens: int
    cache_read_tokens: int
    tool_uses: list[str]  # ["read_file", "write_file", ...]
    user_text: str        # user message content
    task_category: str    # assigned by classifier
    cost: float           # calculated from tokens + model pricing
```

## One-Shot Success Rate

For edit-heavy tasks (Coding, Refactoring, Testing, Debugging):

Detect pattern: `Edit → Bash/Run → Edit` = retry cycle

```
Turn 1: Edit file (Coding)
Turn 2: Bash test (Testing)
Turn 3: Edit again (Coding)  ← Detected as retry

Success rate = (turns without retry) / (total edits)
```

## Configuration

**Config file** at `~/.config/kalima/config.json`:

```json
{
  "currency": "USD",
  "cache_dir": "~/.cache/kalima"
}
```

**Environment overrides**:
- `CLAUDE_CONFIG_DIR` — where to find `~/.claude/projects/`
- `KALIMA_CONFIG_DIR` — config directory
- `KALIMA_CACHE_DIR` — cache directory

## Pricing Logic

**Cost calculation**:
```
input_cost = (input_tokens / 1_000_000) * input_price
output_cost = (output_tokens / 1_000_000) * output_price
cache_write_cost = (cache_write_tokens / 1_000_000) * cache_write_price
cache_read_cost = (cache_read_tokens / 1_000_000) * cache_read_price

total_cost = input_cost + output_cost + cache_write_cost + cache_read_cost

# Convert to requested currency
if currency != "USD":
    total_cost_local = total_cost * exchange_rate
```

## Caching

Two levels of caching:

1. **Pricing Cache** (`~/.cache/kalima/litellm_prices.json`)
   - LiteLLM model prices, updated daily
   - Prevents repeated network requests

2. **Exchange Rate Cache** (`~/.cache/kalima/exchange_rates.json`)
   - Frankfurter rates, updated daily
   - Cached per currency requested

## Performance

- **Parsing**: ~1s for 100 sessions (JSONL streaming)
- **Classification**: ~500ms for 1000 messages (regex matching)
- **Cost calculation**: <100ms
- **Dashboard render**: <200ms (Rich optimizations)

On large datasets (year+ of sessions), expect 5-10s total.

## Testing

Test structure mirrors src:

```
tests/
├── test_parser.py       # JSONL reading, dedup
├── test_classifier.py   # task classification
├── test_models.py       # pricing calculations
├── test_currency.py     # exchange rates, formatting
├── test_cli.py          # command line interface
├── fixtures/
│   └── sample_session.jsonl  # test data
```

## Dependencies

- **typer** — CLI framework (Click-based)
- **rich** — Terminal UI, colors, tables
- **pydantic** — Data validation
- **httpx** — HTTP client (exchange rates, pricing)
- **python-dateutil** — Date/time utilities

Total: ~5 main dependencies, lightweight.

## Future Extensions

Planned (not in v0.1.0):

- Per-project filtering (`--project my_project`)
- Per-task filtering (`--task coding`)
- Watch mode (continuous updates)
- Multi-provider support (Codex, GitHub Copilot)
- SQLite storage for historical tracking
- Web dashboard (optional)

---

See [classifier.md](classifier.md) for detailed task category definitions.
