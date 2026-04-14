# Installation & Setup

## Requirements

- **Python 3.11 or higher**
- **Claude Code** installed with session data at `~/.claude/projects/`

## Installation

### From PyPI (Recommended)

```bash
pip install kalima
```

### From Source

```bash
git clone https://github.com/yourusername/kalima.git
cd kalima
pip install -e .
```

### From Source with Development Dependencies

```bash
git clone https://github.com/yourusername/kalima.git
cd kalima
pip install -e ".[dev]"
```

## Verify Installation

```bash
kalima --version
kalima --help
```

## Configuration

### Config File

Kalima creates a config file at `~/.config/kalima/config.json`:

```json
{
  "currency": "USD",
  "cache_dir": "~/.cache/kalima"
}
```

No manual setup needed — Kalima creates this automatically on first run.

### Environment Variables

Override default behaviors with environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `CLAUDE_CONFIG_DIR` | `~/.claude` | Location of Claude Code data |
| `KALIMA_CONFIG_DIR` | `~/.config/kalima` | Kalima config directory |
| `KALIMA_CACHE_DIR` | `~/.cache/kalima` | Cache directory (exchange rates, pricing) |

Example:
```bash
export CLAUDE_CONFIG_DIR=/custom/path/to/claude
kalima today
```

## Troubleshooting

### "No Claude sessions found"

Check that Claude Code has created session files:
```bash
ls ~/.claude/projects/
```

If empty, run Claude Code once to generate a session.

### "CLAUDE_CONFIG_DIR not found"

Verify the environment variable points to a valid directory:
```bash
echo $CLAUDE_CONFIG_DIR
ls $CLAUDE_CONFIG_DIR
```

### "Permission denied" on config/cache directories

Kalima will create them automatically. If permission issues persist, ensure your user owns `~/.config` and `~/.cache`:
```bash
chmod u+w ~/.config ~/.cache
```

### On Windows: Path issues

Kalima uses Python's `pathlib`, which auto-converts paths. You can use either:
```bash
set CLAUDE_CONFIG_DIR=C:\Users\YourName\.claude
# or
set CLAUDE_CONFIG_DIR=%USERPROFILE%\.claude
```

## Next Steps

- **Quick Start**: Run `kalima` to open the dashboard
- **Learn Commands**: See [usage.md](usage.md)
- **Understand Costs**: See [architecture.md](architecture.md)
