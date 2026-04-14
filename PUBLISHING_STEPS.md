# Kalima v0.1.0 - Publishing Steps

## Current Status

✅ Code complete with 112 passing tests  
✅ GitHub repository configured (janmaru/mahamudra-kalima)  
✅ GitHub Actions workflows ready (test, lint, publish)  
✅ v0.1.0 tag created and pushed  
⚠️ **AWAITING**: PyPI authentication token setup

## What You Need to Do

### Step 1: Create PyPI Account Token (5 minutes)

1. Go to: https://pypi.org/manage/account/tokens/
2. Log in to your PyPI account (create one if needed at https://pypi.org)
3. Click "Add API token"
4. Enter name: `kalima-github-actions`
5. Scope: Select "Entire account"
6. Click "Create token"
7. **COPY the token** (long string starting with `pypi-`)
   - Example: `pypi-AgEIcHlwaS5vcmc...` (NEVER share this!)

### Step 2: Add Token to GitHub Secrets (3 minutes)

1. Go to: https://github.com/janmaru/mahamudra-kalima/settings/secrets/actions
2. Click "New repository secret" (green button)
3. Fill in:
   - **Name**: `PYPI_API_TOKEN` (exactly this)
   - **Secret**: [Paste token from Step 1]
4. Click "Add secret"

### Step 3: Automatic Publishing Begins (2-5 minutes)

Once you add the secret:
1. GitHub Actions automatically detects the v0.1.0 tag
2. The `publish.yml` workflow triggers
3. Workflow steps:
   - ✓ Checks out code
   - ✓ Sets up Python 3.13
   - ✓ Installs build dependencies
   - ✓ Runs: `python -m build`
   - ✓ Runs: `twine upload dist/*`
   - ✓ Uploads to PyPI

### Step 4: Verify Publication (5-10 minutes after workflow completes)

**Option A: Check GitHub Actions Status**
- Go to: https://github.com/janmaru/mahamudra-kalima/actions
- Look for: `Publish` workflow
- Status should be ✅ (green checkmark)

**Option B: Check PyPI.org**
- Go to: https://pypi.org/project/kalima/
- Should show v0.1.0 as latest version
- Click on v0.1.0 to see package details

**Option C: Test Installation**
```bash
# Wait 5-10 minutes after workflow succeeds, then:
pip install kalima==0.1.0

# Should work without errors
kalima version  # Output: Kalima 0.1.0
```

## Timeline

| Step | Action | Duration | Start After |
|------|--------|----------|-------------|
| 1 | Create PyPI token | 5 min | Now |
| 2 | Add GitHub secret | 3 min | Step 1 done |
| 3 | Automation begins | 2-5 min | Step 2 done |
| 4 | Wait for PyPI sync | 5-10 min | Workflow ✅ |
| 5 | Verify & announce | 5 min | PyPI shows v0.1.0 |

**Total time**: ~20-30 minutes

## FAQ

**Q: Do I need to push anything else?**
A: No! The v0.1.0 tag is already pushed. Just add the secret and automation runs.

**Q: What if the workflow fails?**
A: Check the workflow logs at https://github.com/janmaru/mahamudra-kalima/actions
Common issues:
- Token invalid or expired → Create new token
- Token not in GitHub secrets → Add it again
- Typo in secret name (must be `PYPI_API_TOKEN`) → Fix it

**Q: Can I redo the upload if it fails?**
A: Yes, you can re-run the workflow:
1. Go to Actions tab
2. Find the failed workflow
3. Click "Re-run all jobs"
4. It will try again with the same tag

**Q: Is my token visible anywhere?**
A: No! GitHub Secrets are encrypted. You can:
- See the secret exists (name only, not value)
- Update or delete it
- Never see the actual value again (for security)

**Q: What about future releases?**
A: Once the token is set up:
```bash
# For v0.2.0:
git tag -a v0.2.0 -m "Release v0.2.0: ..."
git push origin v0.2.0
# Automatic publishing to PyPI!
```

## Documentation References

- **Full Setup Guide**: See `PYPI_TOKEN_SETUP.md`
- **Release Checklist**: See `RELEASE.md`
- **Git Tagging**: See `TAGGING.md`
- **Workflow Definition**: See `.github/workflows/publish.yml`

## Support

If you encounter issues:

1. **Check the workflow logs**:
   https://github.com/janmaru/mahamudra-kalima/actions

2. **Common fixes**:
   - Secret name must be exactly `PYPI_API_TOKEN`
   - Token should start with `pypi-`
   - Give GitHub a minute to register the secret

3. **Manual upload** (backup option):
   See "Approach 2" in `PYPI_TOKEN_SETUP.md`

---

**Next Action**: Create PyPI token (Step 1 above) → Rest happens automatically! 🚀
