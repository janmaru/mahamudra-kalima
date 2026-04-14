# Changelog

All notable changes to Kalima will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-04-14

### Added

**Core Modules**
- Parser: JSONL reader with deduplication, date filtering, session discovery
- Classifier: 13-category task classification (Coding, Debugging, Testing, Refactoring, Feature Dev, Exploration, Planning, Delegation, Git Ops, Build/Deploy, Brainstorming, Conversation, General)
- Models: Pricing for Claude 3 and 3.5 models (Opus, Sonnet, Haiku) with cache token support
- Config: Configuration management with persistent JSON storage at `~/.config/kalima/config.json`
- Currency: Multi-currency support (162 currencies) with Frankfurter API integration and 24h caching

**CLI & Reporting**
- CLI with Typer framework:
  - `kalima dashboard` — Interactive Rich TUI
  - `kalima today` — Today's usage
  - `kalima report [--days N]` — Period report (default: 7 days)
  - `kalima month` — This calendar month
  - `kalima status` — One-line status (text or JSON)
  - `kalima export [--format json|csv]` — Export with summaries
  - `kalima currency [CODE|--reset]` — Currency management
  - `kalima version` — Show version
- Report formatting: ASCII charts, tables, token aggregation
- Dashboard: Rich tables showing summary, by-model, and by-task breakdowns
- Export: CSV and JSON export with daily/period summaries

**Testing & CI**
- 112 comprehensive tests across 10 test files
  - Parser (8 tests)
  - Classifier (21 tests)
  - Models (24 tests)
  - Config (9 tests)
  - Currency (12 tests)
  - Report (13 tests)
  - Export (5 tests)
  - Dashboard (5 tests)
  - CLI (8 tests)
  - Types (7 tests)
- GitHub Actions workflows:
  - test.yml: Matrix testing on Windows, macOS, Linux (Python 3.10-3.13)
  - lint.yml: Ruff and mypy checks
  - publish.yml: PyPI publishing on release tags

**Documentation**
- README with quick start and feature overview
- Installation guide (`docs/install.md`)
- Usage guide (`docs/usage.md`)
- Architecture documentation (`docs/architecture.md`)
- Classifier details (`docs/classifier.md`)
- Contributing guide (`docs/contributing.md`)
- MIT License

### Features

- Multi-OS support (Windows, macOS, Linux) with automatic path detection
- Deterministic task classification (no LLM calls, fully reproducible)
- Cache token pricing (25% write, 10% read of input cost)
- One-shot success rate detection (Edit→Test→Edit patterns)
- Configurable currency display with smart decimal formatting
- Zero-config operation (auto-discovers Claude Code sessions)
- Fast JSONL parsing with message deduplication
- Fuzzy model name matching for flexible pricing lookups

### Project Status

- Initial release (alpha)
- All core functionality implemented
- Full test coverage for data processing pipeline
- Ready for PyPI publication
- Production-ready CLI and dashboard

### Known Limitations

- Dashboard keyboard navigation not yet implemented (static display for v0.1.0)
- Single-provider (Claude only, multi-provider planned for v0.2.0)
- No historical trending (in-memory processing only, v0.2.0 will add SQLite)
- No per-project filtering (planned for v0.2.0)

### Next Steps (v0.2.0)

- [ ] SQLite storage for historical trends
- [ ] Interactive keyboard navigation in dashboard
- [ ] Multi-provider support (Codex, GitHub Copilot)
- [ ] Per-project and per-task filtering
- [ ] Watch mode for real-time updates
- [ ] Web dashboard (optional)
- [ ] Cost anomaly detection

---

**Total commits**: 8  
**Total lines of code**: ~2,500 (src + tests)  
**Test coverage**: 112 tests passing  
**Python versions**: 3.11, 3.12, 3.13  
**Dependencies**: typer, rich, pydantic, httpx, python-dateutil (+ dev deps)
