# Git Tagging Convention

This document describes the tagging convention used for Kalima releases.

## Convention: `vMAJOR.MINOR.PATCH`

Kalima follows the **Python semantic versioning convention** for release tags.

### Format

```
vMAJOR.MINOR.PATCH
```

Examples:
- `v0.1.0` — Initial release
- `v0.2.0` — Minor feature release
- `v0.2.1` — Patch/hotfix release
- `v1.0.0` — Major version release

### Rules

1. **Prefix `v`** — All release tags start with lowercase `v`
2. **Semantic Versioning** — Use MAJOR.MINOR.PATCH format
   - **MAJOR**: Breaking changes to API or CLI
   - **MINOR**: New features (backwards compatible)
   - **PATCH**: Bug fixes and maintenance
3. **Annotated Tags** — Use `git tag -a` with descriptive messages
4. **Release Notes in Message** — Include features and fixes in tag message
5. **Matches PyPI** — Version in `pyproject.toml` must match tag (without `v`)

### Tagging Process

1. Update version in `pyproject.toml`:
   ```toml
   [project]
   version = "0.2.0"
   ```

2. Update `src/kalima/__init__.py`:
   ```python
   __version__ = "0.2.0"
   ```

3. Create annotated tag:
   ```bash
   git tag -a v0.2.0 -m "Release Kalima v0.2.0: Feature X and Y

Features:
- Feature X description
- Feature Y description

Fixes:
- Bug fix 1
- Bug fix 2

See CHANGELOG.md for full details."
   ```

4. Push tag to GitHub:
   ```bash
   git push origin v0.2.0
   ```

5. GitHub Actions `publish.yml` workflow:
   - Detects tag push (on `v*` pattern)
   - Builds distribution
   - Uploads to PyPI
   - Creates GitHub Release

### Version Examples

#### v0.1.0 (Initial Release)
```
Release Kalima v0.1.0: Claude Code cost tracker

Features:
- 13-task category classifier
- Multi-currency support
- CSV/JSON export
- Rich TUI dashboard
- 112 passing tests

See CHANGELOG.md for full details.
```

#### v0.2.0 (Feature Release)
```
Release Kalima v0.2.0: Historical trends and filtering

Features:
- SQLite storage for cost history
- Per-project filtering
- Interactive dashboard navigation
- Cost anomaly detection

Fixes:
- Fix currency conversion precision

See CHANGELOG.md for full details.
```

#### v0.2.1 (Hotfix)
```
Release Kalima v0.2.1: Bug fixes

Fixes:
- Fix crash on empty session files
- Fix date range filtering for month boundary
- Fix currency formatting for negative amounts
```

### Verifying Tags

List all tags:
```bash
git tag
```

Show tag details:
```bash
git tag -ln 10  # Last 10 tags with messages
git show v0.1.0  # Full tag details
```

### Deleting Tags

If you need to rollback a tag:

```bash
# Delete local tag
git tag -d v0.1.0

# Delete remote tag
git push origin :v0.1.0

# Or:
git push origin --delete v0.1.0
```

### Why This Convention?

1. **Standard in Python** — Matches setuptools/pip expectations
2. **Clear versioning** — Semantic versioning is industry standard
3. **GitHub integration** — Automatic release creation
4. **PyPI alignment** — Package version matches tag version
5. **Human readable** — Easy to scan and understand versions

### Related Files

- `pyproject.toml` — Contains version string (without `v` prefix)
- `src/kalima/__init__.py` — Contains `__version__` constant
- `CHANGELOG.md` — Contains detailed release notes
- `.github/workflows/publish.yml` — Triggered on `v*` tags
- `RELEASE.md` — Complete release checklist
