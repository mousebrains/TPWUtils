# Publishing TPWUtils to PyPI

This document describes how to publish TPWUtils to the Python Package Index (PyPI).

## Prerequisites

1. **PyPI Account**: Create accounts on both:
   - TestPyPI: https://test.pypi.org/account/register/
   - PyPI: https://pypi.org/account/register/

2. **API Tokens**: Create API tokens for authentication:
   - TestPyPI: https://test.pypi.org/manage/account/token/
   - PyPI: https://pypi.org/manage/account/token/
   - Store tokens in `~/.pypirc`:
     ```ini
     [distutils]
     index-servers =
         pypi
         testpypi

     [pypi]
     username = __token__
     password = pypi-...your-token-here...

     [testpypi]
     repository = https://test.pypi.org/legacy/
     username = __token__
     password = pypi-...your-token-here...
     ```

3. **Install Build Tools**:
   ```bash
   pip install build twine
   ```

## Version Bumping

Before publishing, update the version in `pyproject.toml`:

```toml
[project]
name = "TPWUtils"
version = "0.2.1"  # Increment appropriately (major.minor.patch)
```

Follow semantic versioning:
- **Patch** (0.2.1): Bug fixes, no API changes
- **Minor** (0.3.0): New features, backward compatible
- **Major** (1.0.0): Breaking changes

## Building the Package

1. **Clean previous builds**:
   ```bash
   rm -rf dist/ build/ *.egg-info
   ```

2. **Build distribution packages**:
   ```bash
   python -m build
   ```

   This creates:
   - `dist/TPWUtils-0.2.0-py3-none-any.whl` (wheel)
   - `dist/TPWUtils-0.2.0.tar.gz` (source distribution)

3. **Verify the build**:
   ```bash
   tar -tzf dist/TPWUtils-0.2.0.tar.gz
   unzip -l dist/TPWUtils-0.2.0-py3-none-any.whl
   ```

## Testing on TestPyPI

Always test on TestPyPI first:

1. **Upload to TestPyPI**:
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

2. **Install from TestPyPI**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ TPWUtils
   ```

   Note: `--extra-index-url` is needed because dependencies (numpy, pyyaml) aren't on TestPyPI

3. **Test the installation**:
   ```bash
   python -c "from TPWUtils import Logger; print('Success!')"
   pytest tests/
   ```

## Publishing to PyPI

Once TestPyPI installation works:

1. **Upload to PyPI**:
   ```bash
   python -m twine upload dist/*
   ```

2. **Verify on PyPI**:
   - Check the project page: https://pypi.org/project/TPWUtils/
   - Verify README renders correctly
   - Check classifiers and metadata

3. **Install from PyPI**:
   ```bash
   pip install TPWUtils
   ```

4. **Create a Git tag**:
   ```bash
   git tag -a v0.2.0 -m "Release version 0.2.0"
   git push origin v0.2.0
   ```

## Full Release Checklist

- [ ] All tests passing (`pytest tests/`)
- [ ] Version bumped in `pyproject.toml`
- [ ] CHANGELOG.md updated (if it exists)
- [ ] `README.md` accurate and complete
- [ ] Clean build: `rm -rf dist/ build/ *.egg-info`
- [ ] Build packages: `python -m build`
- [ ] Check package contents: `tar -tzf dist/*.tar.gz`
- [ ] Upload to TestPyPI: `twine upload --repository testpypi dist/*`
- [ ] Test install from TestPyPI
- [ ] Upload to PyPI: `twine upload dist/*`
- [ ] Verify on PyPI website
- [ ] Test install from PyPI: `pip install TPWUtils`
- [ ] Create and push git tag: `git tag v0.2.0 && git push origin v0.2.0`
- [ ] Create GitHub release with release notes

## Troubleshooting

**Error: "File already exists"**
- You cannot re-upload the same version to PyPI
- Bump the version number and rebuild

**Error: "Invalid distribution"**
- Run `twine check dist/*` to validate packages
- Check `pyproject.toml` for syntax errors

**Import errors after install**
- Verify package structure: `TPWUtils/` directory must have `__init__.py`
- Check `pyproject.toml` has `packages = ["TPWUtils"]`

**Dependencies not installing**
- Verify `dependencies` list in `pyproject.toml`
- Check platform-specific dependencies use markers correctly

## Automation with GitHub Actions

Consider automating releases with GitHub Actions:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.10'
    - run: pip install build twine
    - run: python -m build
    - run: twine upload dist/*
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
```

Store the PyPI API token in GitHub repository secrets.
