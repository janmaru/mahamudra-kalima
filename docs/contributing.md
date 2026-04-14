# Contributing to Kalima

Thanks for your interest in Kalima! This guide explains how to set up a development environment and contribute.

## Development Setup

### Clone the Repository

```bash
git clone https://github.com/yourusername/kalima.git
cd kalima
```

### Create a Virtual Environment

```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Install Dependencies (with dev extras)

```bash
pip install -e ".[dev]"
```

This installs:
- Main dependencies: typer, rich, pydantic, httpx
- Dev dependencies: pytest, ruff, mypy, black

### Verify Setup

```bash
kalima --version
pytest tests/
ruff check src/ tests/
mypy src/
```

All should pass.

## Project Structure

```
kalima/
├── src/kalima/          # Main package
│   ├── cli.py           # Typer commands
│   ├── parser.py        # JSONL parsing
│   ├── classifier.py    # Task classification
│   ├── models.py        # Pricing
│   ├── currency.py      # Currency conversion
│   ├── dashboard.py     # Rich TUI
│   ├── report.py        # Formatting
│   ├── export.py        # CSV/JSON export
│   ├── config.py        # Config management
│   └── types.py         # Data models
├── tests/               # Test suite
│   ├── test_*.py
│   └── fixtures/
│       └── sample_session.jsonl
├── docs/                # Documentation
├── pyproject.toml       # Dependencies, build config
└── README.md
```

## Workflow

### 1. Pick an Issue or Feature

Check [GitHub Issues](https://github.com/yourusername/kalima/issues) for open tasks, or open a new one.

### 2. Create a Feature Branch

```bash
git checkout -b feat/my-feature
# or
git checkout -b fix/bug-name
```

Branch naming: `feat/*`, `fix/*`, `docs/*`, `chore/*`

### 3. Make Changes

- Write code in `src/kalima/`
- Write tests in `tests/`
- Run linter/type checker frequently:

```bash
ruff check src/ tests/
mypy src/
black src/ tests/
```

### 4. Write Tests

Every new feature needs tests:

```bash
pytest tests/ -v
pytest tests/test_classifier.py::test_coding_classification -v
```

Use the sample JSONL fixture for testing:

```python
# tests/test_parser.py
from pathlib import Path

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_session.jsonl"

def test_parse_sessions():
    sessions = parser.parse_sessions(FIXTURE_PATH)
    assert len(sessions) > 0
```

### 5. Document Changes

- Update docstrings in functions
- Update [README.md](../README.md) if adding/changing CLI commands
- Update [docs/](../docs) if architectural changes

### 6. Commit

```bash
git add src/ tests/ docs/
git commit -m "feat: add task filtering to reports

- Add --task flag to filter by category
- Update classifier for finer granularity
- Add tests for new filter logic"
```

Good commit messages:
- `feat: add X feature`
- `fix: resolve Y bug`
- `docs: update README`
- `chore: update deps`

### 7. Push and Open PR

```bash
git push origin feat/my-feature
```

On GitHub, open a Pull Request. Include:
- Brief description of changes
- Why the change was needed
- Any testing done

### 8. Code Review

Respond to feedback, make adjustments, push updates. No need to reopen PR — GitHub will notify on new commits.

## Code Standards

### Python Style

- **Format**: Black (100 char line length)
- **Linting**: Ruff (E, F, W, I, N, UP)
- **Types**: mypy strict mode (all functions typed)

Run before committing:
```bash
black src/ tests/
ruff check src/ tests/ --fix
mypy src/
```

### Type Annotations

All functions must have type hints:

```python
# ✅ Good
def classify_task(message: Message, keywords: list[str]) -> str:
    ...

# ❌ Bad
def classify_task(message, keywords):
    ...
```

### Comments

Only comment **why**, not **what**:

```python
# ✅ Good
# Deduplicate by API message ID to handle retransmits
messages = {msg.api_id: msg for msg in raw_messages}.values()

# ❌ Bad
# Loop through messages
for msg in messages:
    ...
```

### Naming

- Classes: `PascalCase` (e.g., `TaskClassifier`)
- Functions: `snake_case` (e.g., `parse_sessions`)
- Constants: `UPPER_CASE` (e.g., `DEFAULT_PERIOD`)
- Private: prefix with `_` (e.g., `_internal_helper`)

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test

```bash
pytest tests/test_classifier.py::test_coding_classification -v
```

### Coverage

```bash
pytest tests/ --cov=src/kalima
```

Aim for >80% coverage on new code.

### Test Fixtures

Sample Claude session JSONL at `tests/fixtures/sample_session.jsonl`:

```python
# tests/test_parser.py
def test_parse_sessions():
    sessions = parser.parse_sessions("tests/fixtures/sample_session.jsonl")
    assert len(sessions) == 1
    assert sessions[0].messages[0].model.startswith("claude-")
```

## Common Tasks

### Add a New CLI Command

1. Add to `cli.py`:
```python
@app.command()
def my_command(option: str = typer.Option(...)) -> None:
    """Description of command."""
    ...
```

2. Test it:
```bash
kalima my-command --option value
```

3. Update [docs/usage.md](../docs/usage.md)

### Add a Task Category

1. Add to `classifier.py`:
```python
CATEGORIES = [..., "New Category"]

def classify(message: Message) -> str:
    if "new_trigger" in message.tools:
        return "New Category"
```

2. Add tests
3. Update [docs/classifier.md](../docs/classifier.md)

### Fix a Bug

1. Write a failing test that reproduces the bug
2. Fix the code
3. Verify test passes
4. Commit with `fix:` prefix

## PR Checklist

Before opening a PR, verify:

- [ ] Tests pass: `pytest tests/`
- [ ] Linter passes: `ruff check src/ tests/`
- [ ] Types pass: `mypy src/`
- [ ] Formatting: `black src/ tests/`
- [ ] Branch name is descriptive (`feat/`, `fix/`, etc.)
- [ ] Commit messages are clear
- [ ] README/docs updated (if applicable)
- [ ] No dead code or debug statements

## Getting Help

- **Question?** Open a [GitHub Discussion](https://github.com/yourusername/kalima/discussions)
- **Bug?** Open an [Issue](https://github.com/yourusername/kalima/issues)
- **Design feedback?** Post in Discussions before coding

## Code of Conduct

This project follows a [Code of Conduct](../CODE_OF_CONDUCT.md) (TBD). Be respectful and inclusive.

---

Thanks for contributing to Kalima! 🎉
