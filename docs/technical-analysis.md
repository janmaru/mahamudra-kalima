# Technical Analysis

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Data Flow](#data-flow)
- [Module Reference](#module-reference)
- [Input Data Format](#input-data-format)
- [Task Classifier](#task-classifier)
- [Pricing Logic](#pricing-logic)
- [Caching](#caching)
- [One-Shot Success Rate](#one-shot-success-rate)
- [Performance](#performance)

## Architecture Overview

Kalima reads Claude Code session transcripts from disk and calculates costs in three stages:

1. **Parse** -- Read JSONL session files, deduplicate, filter by date
2. **Classify** -- Categorize each turn into one of 13 task types
3. **Aggregate** -- Calculate costs, roll up by period/model/task

No API calls, no proxy. All processing is local.

## Data Flow

```
~/.claude/projects/**/*.jsonl
        |
        v
  parser.py        read JSONL, deduplicate by message ID, filter by date
        |
        v
  classifier.py    analyze tools + keywords -> assign task category
        |
        v
  models.py        look up LiteLLM pricing -> compute cost per message
        |
        v
  report.py / dashboard.py / export.py    format and display output
```

## Module Reference

```
src/kalima/
  cli.py           Typer entry point, all CLI commands
  parser.py        JSONL reader, deduplication, date filtering
  classifier.py    13-category deterministic task classifier
  models.py        Claude model definitions, LiteLLM pricing
  currency.py      Exchange rates (Frankfurter API), formatting
  dashboard.py     Rich TUI with interactive keyboard navigation
  report.py        Text formatter (ASCII charts, summaries)
  export.py        CSV/JSON export with period breakdowns
  config.py        Config file and directory management
  types.py         Pydantic data models
```

### parser.py

Discovers and reads Claude Code JSONL session files from `~/.claude/projects/`.

- **Discovery**: Recursively scans for `*.jsonl` files, including `subagents/` directories
- **Deduplication**: Messages are keyed by `api_message_id` or timestamp to avoid double-counting
- **Filtering**: Supports both rolling window (`filter_sessions_by_date`) and absolute range (`filter_sessions_by_date_range`)

### classifier.py

Analyzes each turn and assigns a task category based on tool usage and keywords. Fully deterministic -- no LLM calls, no fuzzy matching. See [Task Classifier](#task-classifier) section for details.

### models.py

Maps Claude model names to pricing. Pricing is fetched from LiteLLM and cached for 24 hours. Supports fuzzy model name matching for flexible lookups.

```python
class ModelCost:
    name: str
    input_cost: float         # per 1M input tokens
    output_cost: float        # per 1M output tokens
    cache_write_cost: float   # per 1M cache write tokens
    cache_read_cost: float    # per 1M cache read tokens
```

### currency.py

Multi-currency support for all 162 ISO 4217 currencies. Exchange rates are fetched from the Frankfurter API (ECB data) and cached for 24 hours.

### dashboard.py

Interactive Rich TUI. Uses `readchar` in a background thread for non-blocking keyboard input. The main thread renders the layout via `Rich Live` at 2 FPS. Period switching (Today / 7d / 30d / Month) is handled by filtering pre-loaded session data.

### report.py / export.py

Text report formatter with ASCII bar charts. Export supports CSV and JSON with breakdowns for multiple periods (today, 7 days, 30 days, month).

## Input Data Format

Kalima reads Claude Code conversation logs stored as JSONL files at:

```
~/.claude/projects/
  C--Project-Name/
    session-uuid-1.jsonl
    session-uuid-2.jsonl
    subagents/
      agent-*.jsonl
```

Each JSONL file contains message events. Kalima supports two formats:

**Claude CLI format (current)**:

```json
{
  "type": "assistant",
  "message": {
    "id": "msg_001",
    "created_at": "2026-04-14T10:00:00Z",
    "model": "claude-opus-4-6",
    "usage": {
      "input_tokens": 1200,
      "output_tokens": 340,
      "cache_creation_input_tokens": 29267,
      "cache_read_input_tokens": 0
    }
  }
}
```

**Claude Code format (older)**:

```json
{
  "type": "assistant",
  "model": "claude-3-5-sonnet",
  "usage": {
    "input_tokens": 500,
    "output_tokens": 200
  }
}
```

Both formats are auto-detected and parsed transparently.

## Task Classifier

Each message is classified into one of 13 categories based on tools used and keywords in user text. Classification is evaluated in priority order:

| # | Category | Triggers |
|---|----------|----------|
| 1 | **Coding** | `write_file` or `edit_file` tool used |
| 2 | **Debugging** | Keywords ("debug", "fix", "error", "bug", "crash") AND tool usage |
| 3 | **Feature Dev** | Keywords ("add", "create", "implement", "build") AND tool usage |
| 4 | **Refactoring** | Keywords ("refactor", "simplify", "rename", "clean") AND `write_file` |
| 5 | **Testing** | `execute_command` containing "pytest", "vitest", "jest", etc. |
| 6 | **Exploration** | `read_file`, `grep_code`, `web_search` WITHOUT any edits |
| 7 | **Planning** | `enter_plan_mode`, `task_create` tools, or plan keywords WITHOUT edits |
| 8 | **Delegation** | `spawn_agent`, `create_agent` tools |
| 9 | **Git Ops** | `execute_command` with "git commit", "git push", "git merge", etc. |
| 10 | **Build/Deploy** | `execute_command` with "npm build", "docker build", "pm2", etc. |
| 11 | **Brainstorming** | Keywords ("brainstorm", "what if") AND no tool usage |
| 12 | **Conversation** | No tools used, pure text exchange |
| 13 | **General** | Fallback for anything that doesn't match above |

### Priority rules

When multiple categories could match a single turn:

- Edit + test = **Coding** (edit takes priority)
- Read + question = **Exploration** (reading is primary)
- Git commit + deploy = **Git Ops** (git takes priority)
- "refactor the debug logic" = **Refactoring** (refactor keyword takes priority)

### Extending the classifier

1. Define triggers (tools + keywords)
2. Add the case in `classifier.py`
3. Add tests in `test_classifier.py`
4. Update this document

## Pricing Logic

Cost is calculated per message:

```
input_cost        = (input_tokens / 1_000_000) * input_price
output_cost       = (output_tokens / 1_000_000) * output_price
cache_write_cost  = (cache_write_tokens / 1_000_000) * cache_write_price
cache_read_cost   = (cache_read_tokens / 1_000_000) * cache_read_price

total_cost_usd = input_cost + output_cost + cache_write_cost + cache_read_cost
```

Currency conversion is applied at display time:

```
if currency != "USD":
    total_cost_local = total_cost_usd * exchange_rate
```

Cache token pricing follows Claude's standard: cache writes cost 25% of input price, cache reads cost 10% of input price.

## Caching

Two levels of caching, both stored at `~/.cache/kalima/`:

| Cache | File | TTL | Purpose |
|-------|------|-----|---------|
| Pricing | `litellm_prices.json` | 24h | LiteLLM model prices |
| Exchange rates | `exchange_rates.json` | 24h | Frankfurter currency rates |

To force a refresh, delete the cache file and re-run any command.

## One-Shot Success Rate

Tracks edit-heavy tasks (Coding, Debugging, Feature Dev, Refactoring) to measure how often the AI gets it right on the first attempt.

**Detection pattern**: `Edit -> Run/Test -> Edit` = retry detected

```
Turn 1: Edit parser.py          (Coding)
Turn 2: Run pytest              (Testing)
Turn 3: Edit parser.py again    (Coding)    <- RETRY
Turn 4: Run pytest              (Testing)
Turn 5: All green               (Conversation)

Edits: 2
Retries: 1
One-shot rate: 50%
```

Formula:

```
one_shot_rate = (edit_turns - retry_turns) / edit_turns * 100
```

## Performance

| Operation | Typical Time |
|-----------|-------------|
| Parsing (100 sessions) | ~1s |
| Classification (1000 messages) | ~500ms |
| Cost calculation | <100ms |
| Dashboard render | <200ms |

On large datasets (1+ year of sessions), expect 5-10s total.

## Message Structure

Internal representation of a parsed message:

```python
class Message:
    api_message_id: str
    timestamp: datetime
    model: str
    input_tokens: int
    output_tokens: int
    cache_write_tokens: int
    cache_read_tokens: int
    tool_uses: list[str]
    user_text: str
    task_category: TaskCategory
    cost_usd: float
```

## Dependencies

| Package | Purpose |
|---------|---------|
| typer | CLI framework (Click-based) |
| rich | Terminal UI, colors, tables |
| pydantic | Data validation and models |
| httpx | HTTP client (exchange rates, pricing) |
| python-dateutil | Date/time utilities |
| readchar | Non-blocking keyboard input for dashboard |
