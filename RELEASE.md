# Release Instructions

This document explains how to release Kalima to PyPI.

## Checklist Before Release

- [ ] All tests passing locally: `pytest tests/`
- [ ] All modules tested across Python 3.11+: `python -m pytest tests/`
- [ ] Code formatted: (ruff handles this automatically)
- [ ] Type checking: `mypy src/kalima`
- [ ] Linting: `ruff check src/ tests/`
- [ ] Documentation updated (README, CHANGELOG, docs/)
- [ ] Version bumped in `pyproject.toml`
- [ ] CHANGELOG entry created
- [ ] Git history clean (all changes committed)

## Release Steps

### 1. Bump Version

Edit `pyproject.toml`:
```toml
[project]
version = "0.2.0"  # Update this
```

Update `src/kalima/__init__.py`:
```python
__version__ = "0.2.0"  # Match above
```

### 2. Update CHANGELOG

Add new section to `CHANGELOG.md`:
```markdown
## [0.2.0] - YYYY-MM-DD

### Added
- New feature 1
- New feature 2

### Fixed
- Bug fix 1
```

### 3. Commit

```bash
git add -A
git commit -m "chore: release v0.2.0

- Bump version to 0.2.0
- Update CHANGELOG
- Update documentation

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### 4. Tag Release

```bash
git tag v0.2.0
git push origin main
git push origin v0.2.0
```

### 5. Build Distribution

```bash
python -m pip install build twine
python -m build
```

This creates `dist/kalima-0.2.0-py3-none-any.whl` and `dist/kalima-0.2.0.tar.gz`.

### 6. Upload to PyPI (via GitHub Actions)

The `publish.yml` workflow will automatically trigger on release tag push. It will:
1. Build the distribution
2. Upload to PyPI using the `PYPI_API_TOKEN` secret

OR manually:
```bash
twine upload dist/*
```

## Verifying Release

After publish, verify on PyPI:
```bash
pip install kalima==0.2.0
kalima version
```

## Rollback

If something goes wrong, you can delete a release:
```bash
git tag -d v0.2.0
git push origin :v0.2.0
```

Then manually delete the package from PyPI (requires maintainer access).

## PyPI Setup

Ensure your PyPI token is set up as `PYPI_API_TOKEN` in GitHub repository secrets.

**See PYPI_TOKEN_SETUP.md for detailed instructions** on:
- Creating a PyPI API token
- Adding it to GitHub Secrets
- Testing the setup
- Troubleshooting authentication errors

## Testing Locally Before Release

```bash
# Install in editable mode
pip install -e ".[dev]"

# Run full test suite
pytest tests/ -v

# Test all CLI commands
kalima version
kalima currency
kalima status
```

## Build Format

Kalima uses `hatchling` as the build backend. To build manually:

```bash
python -m build --wheel  # Just wheel
python -m build --sdist  # Just source distribution
python -m build          # Both
```

## Python Version Support

Kalima supports Python 3.11+. Releases are tested on:
- Python 3.11
- Python 3.12
- Python 3.13

GitHub Actions tests all versions automatically on each push.
