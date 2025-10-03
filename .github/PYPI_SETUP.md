# GitHub Actions PyPI Publishing Setup

This document explains how to configure GitHub Actions to automatically publish TPWUtils to PyPI when you create a release.

## Option 1: Using API Tokens (Recommended for Getting Started)

### Step 1: Create PyPI API Tokens

1. **For TestPyPI** (optional, for testing):
   - Go to https://test.pypi.org/manage/account/token/
   - Click "Add API token"
   - Token name: `GitHub Actions - TPWUtils`
   - Scope: Choose "Entire account" (or "Project: TPWUtils" if package already exists)
   - Click "Add token"
   - **COPY THE TOKEN** - you'll only see it once!

2. **For PyPI** (production):
   - Go to https://pypi.org/manage/account/token/
   - Click "Add API token"
   - Token name: `GitHub Actions - TPWUtils`
   - Scope: Choose "Entire account" (or "Project: TPWUtils" after first upload)
   - Click "Add token"
   - **COPY THE TOKEN** - you'll only see it once!

### Step 2: Add Tokens to GitHub Secrets

1. Go to your GitHub repository: https://github.com/mousebrains/TPWUtils
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

   **Secret 1:**
   - Name: `PYPI_API_TOKEN`
   - Value: Paste the PyPI token you copied (starts with `pypi-...`)
   - Click "Add secret"

   **Secret 2** (optional, for testing):
   - Name: `TEST_PYPI_API_TOKEN`
   - Value: Paste the TestPyPI token
   - Click "Add secret"

## Option 2: Trusted Publishing (More Secure, Recommended Long-term)

PyPI supports "Trusted Publishing" which eliminates the need for API tokens.

### Setup Steps:

1. **First, manually upload the package once** using the `publish.sh` script to create the project on PyPI

2. **Configure Trusted Publisher on PyPI**:
   - Go to https://pypi.org/manage/project/TPWUtils/settings/publishing/
   - Scroll to "Trusted Publishers" section
   - Click "Add a new publisher"
   - Fill in:
     - PyPI Project Name: `TPWUtils`
     - Owner: `mousebrains`
     - Repository name: `TPWUtils`
     - Workflow name: `publish.yml`
     - Environment name: (leave blank)
   - Click "Add"

3. **Update the workflow file** to use trusted publishing:
   - In `.github/workflows/publish.yml`, comment out the token-based section
   - Uncomment the "Trusted Publishing" section at the bottom
   - Commit and push the changes

## How to Use the Automated Publishing

### Method 1: GitHub Releases (Automatic)

When you create a GitHub release, it automatically publishes to PyPI:

1. Update version in `pyproject.toml`
2. Commit and push changes
3. Go to https://github.com/mousebrains/TPWUtils/releases/new
4. Tag version: `v0.2.1` (must match pyproject.toml version)
5. Release title: `v0.2.1`
6. Describe changes in release notes
7. Click "Publish release"
8. GitHub Actions will automatically build and publish to PyPI

### Method 2: Manual Trigger (For Testing)

You can manually trigger a publish to TestPyPI or PyPI:

1. Go to https://github.com/mousebrains/TPWUtils/actions/workflows/publish.yml
2. Click "Run workflow"
3. Select branch: `main`
4. Check "Upload to TestPyPI" if you want to test first
5. Click "Run workflow"

## Monitoring the Workflow

1. Go to https://github.com/mousebrains/TPWUtils/actions
2. Click on the running workflow
3. Watch the build, test, and publish steps
4. If it fails, check the logs for errors

## Troubleshooting

### "Invalid credentials" error
- Verify your API token is correct in GitHub Secrets
- Make sure the secret name matches exactly: `PYPI_API_TOKEN`
- Tokens expire - you may need to regenerate them

### "File already exists" error
- You cannot re-upload the same version to PyPI
- Increment the version in `pyproject.toml` first
- Use TestPyPI for testing before production upload

### "Package name already taken"
- Someone else registered `TPWUtils` on PyPI
- You'll need to choose a different name in `pyproject.toml`
- Common solutions: `tpwutils`, `tpw-utils`, `mousebrains-tpwutils`

### Tests fail in workflow
- Tests must pass before publishing
- Run `pytest tests/` locally to debug
- Check workflow logs for specific test failures

## Security Best Practices

1. **Use scoped tokens**: After first upload, create a new token scoped to just "Project: TPWUtils"
2. **Rotate tokens periodically**: Generate new tokens every 6-12 months
3. **Use Trusted Publishing**: Switch to this once you're comfortable with the process
4. **Never commit tokens**: GitHub Secrets are encrypted and safe
5. **Limit workflow permissions**: The workflow only has `id-token: write` and `contents: read`

## Additional Resources

- PyPI Publishing Guide: https://packaging.python.org/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/
- Trusted Publishing: https://docs.pypi.org/trusted-publishers/
- GitHub Actions Docs: https://docs.github.com/en/actions
