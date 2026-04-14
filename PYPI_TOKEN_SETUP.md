# PyPI Token Setup Guide

## Problem

You received a `403 Forbidden` error when trying to upload to PyPI. This means authentication is missing.

## Solution

Choose one of two approaches:

### Approach 1: Automated Publishing via GitHub Actions (Recommended)

This is the simplest and most secure method. Once configured, your releases publish automatically.

#### Step 1: Create PyPI API Token

1. Visit: https://pypi.org/manage/account/tokens/
2. Log in with your PyPI account
3. Click "Add API token"
4. Fill in:
   - **Token name**: `kalima-github-actions`
   - **Scope**: "Entire account" (for first-time release)
5. Click "Create token"
6. **Copy the token** - You'll only see it once! (starts with `pypi-`)

#### Step 2: Add Token to GitHub Secrets

1. Go to: https://github.com/janmaru/mahamudra-kalima/settings/secrets/actions
   (Or: Repo → Settings → Secrets and variables → Actions)
2. Click "New repository secret"
3. Fill in:
   - **Name**: `PYPI_API_TOKEN`
   - **Secret**: [Paste the token from Step 1]
4. Click "Add secret"

#### Step 3: Trigger Publishing

The v0.1.0 tag is already pushed. Once you add the secret:

1. GitHub Actions will detect the tag
2. The `publish.yml` workflow will run automatically
3. Package will be built and uploaded to PyPI
4. Check progress: https://github.com/janmaru/mahamudra-kalima/actions

#### Step 4: Verify

- Wait 5-10 minutes after workflow completes
- Visit: https://pypi.org/project/kalima/
- Should see v0.1.0 listed
- Test installation: `pip install kalima==0.1.0`

### Approach 2: Manual Upload (If You Prefer Local Control)

#### Step 1: Create PyPI Token

Same as Approach 1, Step 1 above.

#### Step 2: Create ~/.pypirc

On your machine, create `~/.pypirc`:

**Windows** (save as `C:\Users\YourUsername\.pypirc`):
```
[distutils]
index-servers = pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TOKEN_HERE
```

**macOS/Linux** (save as `~/.pypirc`):
```
[distutils]
index-servers = pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TOKEN_HERE
```

Replace `pypi-YOUR_TOKEN_HERE` with your actual token from Step 1.

#### Step 3: Upload

```bash
cd C:\Coding\kalima
twine upload dist/*
```

#### Step 4: Verify

- Visit: https://pypi.org/project/kalima/
- Should see v0.1.0
- Test: `pip install kalima==0.1.0`

## Important Notes

⚠️ **Never commit your PyPI token to Git!**
- Use GitHub Secrets for Approach 1 (safe)
- Use local `~/.pypirc` for Approach 2 (add to `.gitignore`)

🔐 **Token Security**
- Tokens are like passwords - keep them private
- If token leaks, regenerate it at pypi.org
- Consider using "Scoped" tokens for specific projects in future releases

🚀 **For Future Releases**

Once PYPI_API_TOKEN secret is set up, publishing is automatic:

```bash
# Update version in pyproject.toml and __init__.py
# Update CHANGELOG.md
git commit -am "chore: release v0.2.0"

# Create and push tag
git tag -a v0.2.0 -m "Release notes here..."
git push origin v0.2.0

# GitHub Actions automatically publishes to PyPI!
```

## Troubleshooting

### "403 Forbidden"
- Token not configured in GitHub secrets OR
- Token has expired OR
- Uploading duplicate version

**Solution**: Verify secret is set and token is current

### "PyPI Project Not Found"
- Project may not be created yet on PyPI

**Solution**: Go to https://pypi.org/ and search for "kalima"

### "Invalid Credential"
- Username/password/token incorrect OR
- Token was revoked

**Solution**: Regenerate token at https://pypi.org/manage/account/tokens/

## Reference

- PyPI Token Docs: https://pypi.org/help/#token
- twine Documentation: https://twine.readthedocs.io/
- GitHub Secrets: https://docs.github.com/en/actions/security-guides/encrypted-secrets
