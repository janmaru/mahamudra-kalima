# Kalima Requirements

## Claude CLI / Claude Code

Kalima works with **Claude CLI** (the latest version you're using).

### Data Format

Claude CLI saves conversation logs as JSONL files in:

```
~/.claude/projects/
├── C--Project-Name/
│   ├── session-uuid-1.jsonl   ← Kalima reads these
│   ├── session-uuid-2.jsonl
│   └── subagents/
│       └── agent-*.jsonl      ← Also reads agent logs
```

Each JSONL file contains messages with token usage:

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

### How Kalima Uses the Data

1. **Discovers** all `.jsonl` files in `~/.claude/projects/**`
2. **Parses** messages with token usage
3. **Extracts** model, timestamp, and token counts
4. **Classifies** by task category (conversation, code, debugging, etc.)
5. **Calculates** costs using Claude pricing
6. **Aggregates** by time period, model, and category
7. **Displays** in CLI commands and dashboard

## Supported Formats

Kalima automatically detects and supports:

**Claude Code Format** (older):
```json
{
  "type": "assistant",
  "model": "claude-3-5-sonnet",
  "usage": { "input_tokens": 500, ... }
}
```

**Claude CLI Format** (current):
```json
{
  "type": "assistant",
  "message": {
    "model": "claude-opus-4-6",
    "usage": { "input_tokens": 500, ... }
  }
}
```

Both formats work seamlessly - Kalima detects which one and parses accordingly.

## Your Installation

Since you're using **Claude CLI**, Kalima will automatically:

✅ Find sessions at `~/.claude/projects/`
✅ Parse message.usage structure
✅ Convert cache pricing correctly
✅ Aggregate costs by model and category

## Python Version Requirements

- Python 3.11 or higher
- Tested on: 3.11, 3.12, 3.13

## Dependencies

Automatically installed with `pip install -e .`:

- `typer` - CLI framework
- `rich` - Terminal UI
- `pydantic` - Data validation
- `httpx` - HTTP client (for currency rates)
- `python-dateutil` - Date utilities

## Troubleshooting

### "No Claude Code sessions found"

**Cause**: No `.jsonl` files found in `~/.claude/projects/`

**Fix**:
1. Make sure you have Claude CLI installed
2. Use Claude at least once (creates sessions)
3. Check `~/.claude/projects/` exists

### All costs show $0.00

**Cause**: Sessions exist but have no messages with token data yet

**Fix**:
1. Use Claude CLI to start new conversations
2. Wait for sessions to be saved
3. Kalima will pick them up automatically

### File encoding errors

**Cause**: Corrupted or incompatible JSONL file

**Fix**: The file will be skipped; try deleting and regenerating the session

## File Structure

```
~/.claude/
├── projects/              ← Kalima reads from here
│   └── C--PROJECT-NAME/
│       └── SESSION-UUID.jsonl
├── config/                ← Kalima saves currency settings
└── cache/                 ← Kalima stores exchange rates
```

Kalima creates `~/.config/kalima/` and `~/.cache/kalima/` automatically.

## Testing Your Installation

```bash
# Check installation
python -m kalima.cli version
# Output: Kalima 0.1.0

# Check data discovery
python -m kalima.cli status
# Output: Today: $X.XX | Month: $Y.YY

# See real cost breakdown
python -m kalima.cli report --days 30
# Shows detailed costs by model and category
```

## Next Steps

1. Run `python -m kalima.cli status` to see your costs
2. Explore other commands in LOCAL_USAGE.md
3. Ready to publish? See READY_TO_RELEASE.md
