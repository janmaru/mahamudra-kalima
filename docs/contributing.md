# Contributing

## Table of Contents

- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Workflow](#workflow)
- [Release Process](#release-process)
- [PyPI Publishing](#pypi-publishing)

## Development Setup

### Clone and install

```bash
git clone https://github.com/janmaru/mahamudra-kalima.git
cd kalima
python -m venv venv

# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install -e ".[dev]"
```

### Verify

```bash
kalima version
pytest tests/ -v
ruff check src/ tests/
mypy src/kalima
```

## Code Standards

### Style

- **Formatter**: Black (100 char line length)
- **Linter**: Ruff (rules: E, F, W, I, N, UP)
- **Type checker**: mypy (strict mode)

Run before committing:

```bash
black src/ tests/
ruff check src/ tests/ --fix
mypy src/
```

### Naming

- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_CASE`
- Private: `_prefix`

### Type annotations

All functions must have type hints:

```python
def classify_task(message: Message, keywords: list[str]) -> str:
    ...
```

### Comments

Comment **why**, not **what**.

## Testing

### Run tests

```bash
pytest tests/ -v                    # all tests
pytest tests/test_classifier.py -v  # single module
pytest tests/test_cli.py::TestCLIVersion::test_version_command -v  # single test
pytest tests/ --cov=src/kalima      # with coverage
```

Aim for >80% coverage on new code.

### Writing tests

- Every new feature needs tests
- Bug fixes start with a failing test that reproduces the issue
- Use fixtures from `tests/conftest.py` and `tests/fixtures.py`

## Workflow

### 1. Branch

```bash
git checkout -b feat/my-feature   # or fix/bug-name, docs/topic, chore/task
```

### 2. Implement

Write code in `src/kalima/`, tests in `tests/`.

### 3. Verify

```bash
pytest tests/ -v
ruff check src/ tests/
mypy src/
```

### 4. Commit

```bash
git commit -m "feat: add task filtering to reports"
```

Prefixes: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`

### 5. Push and open PR

```bash
git push origin feat/my-feature
```

Include in PR description: what changed, why, testing done.

## Release Process

### Version convention

Tags follow `vMAJOR.MINOR.PATCH` (semantic versioning):

- **MAJOR**: Breaking changes to API or CLI
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes and maintenance

The version in `pyproject.toml` must match the tag (without `v` prefix).

### Steps

1. **Update version** in `pyproject.toml`:

   ```toml
   [project]
   version = "0.2.0"
   ```

2. **Update version** in `src/kalima/__init__.py`:

   ```python
   __version__ = "0.2.0"
   ```

3. **Update CHANGELOG.md** with release notes:

   ```markdown
   ## [0.2.0] - YYYY-MM-DD

   ### Added
   - New feature description

   ### Fixed
   - Bug fix description
   ```

4. **Commit**:

   ```bash
   git commit -am "chore: release v0.2.0"
   ```

5. **Create and push annotated tag**:

   ```bash
   git tag -a v0.2.0 -m "Release Kalima v0.2.0: Feature X and Y

   Features:
   - Feature X description
   - Feature Y description

   See CHANGELOG.md for full details."

   git push origin main
   git push origin v0.2.0
   ```

6. GitHub Actions automatically builds and publishes to PyPI.

### Pre-release checklist

- [ ] All tests passing: `pytest tests/`
- [ ] Linting clean: `ruff check src/ tests/`
- [ ] Types clean: `mypy src/kalima`
- [ ] CHANGELOG.md updated
- [ ] Version bumped in `pyproject.toml` and `__init__.py`
- [ ] All changes committed

## PyPI Publishing

### How it works

The `.github/workflows/publish.yml` workflow triggers on `v*` tag pushes. It:

1. Checks out the code
2. Sets up Python
3. Runs `python -m build` (wheel + sdist)
4. Uploads to PyPI using the `PYPI_API_TOKEN` secret

### First-time setup

1. **Create a PyPI API token**:
   - Go to https://pypi.org/manage/account/tokens/
   - Name: `kalima-github-actions`
   - Scope: Entire account
   - Copy the token (starts with `pypi-`)

2. **Add token to GitHub Secrets**:
   - Go to https://github.com/janmaru/mahamudra-kalima/settings/secrets/actions
   - New repository secret
   - Name: `PYPI_API_TOKEN`
   - Value: the token from step 1

Once configured, every tag push triggers automatic publishing.

### Manual upload (alternative)

Create `~/.pypirc`:

```ini
[distutils]
index-servers = pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TOKEN_HERE
```

Then:

```bash
python -m build
twine upload dist/*
```

### Verify publication

```bash
# Wait 5-10 minutes after workflow completes
pip install kalima==0.2.0
kalima version
```

### Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| 403 Forbidden | Token missing or expired | Recreate token, update GitHub secret |
| Invalid credential | Token revoked | Regenerate at pypi.org |
| Duplicate version | Version already on PyPI | Bump version number |

Token security: never commit tokens to git. Use GitHub Secrets (encrypted) or local `~/.pypirc`.
