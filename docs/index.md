# Kalima Documentation

Welcome to Kalima — cost tracking for Claude Code projects.

## Getting Started

- **[Installation](install.md)** — Setup instructions, requirements, environment variables
- **[Usage Guide](usage.md)** — CLI commands, examples, dashboard navigation
- **[Architecture](architecture.md)** — How Kalima works, data flow, parsing logic

## Deep Dives

- **[Task Classifier](classifier.md)** — 13-category breakdown and how tasks are classified
- **[Contributing](contributing.md)** — Development setup, testing, submitting changes

## Quick Links

| Need | Link |
|------|------|
| How do I install? | [install.md](install.md) |
| What commands are available? | [usage.md](usage.md) |
| How does it track costs? | [architecture.md](architecture.md) |
| What are the 13 task categories? | [classifier.md](classifier.md) |
| I want to contribute | [contributing.md](contributing.md) |

## FAQ

**Does Kalima send my data anywhere?**
No. Kalima reads Claude Code session files directly from your disk (`~/.claude/projects/`). No network requests, no data collection, no API keys.

**Which Claude models does it support?**
All Claude models (Claude 3, Claude 3.5 Opus/Sonnet/Haiku). Pricing automatically fetched from LiteLLM.

**Can I use it on Windows/Mac/Linux?**
Yes. Kalima auto-detects your OS and paths. `~/.claude` works on all platforms.

**What if I have custom session locations?**
Set `CLAUDE_CONFIG_DIR` environment variable to override the default.

**How do I export my data?**
Use `kalima export` for CSV or `kalima export -f json` for JSON. Includes all periods (today, 7d, 30d).

**Can I change the currency?**
Yes, `kalima currency GBP` (or any ISO 4217 code). Exchange rates from Frankfurter, cached 24h.

---

Last updated: 2025
