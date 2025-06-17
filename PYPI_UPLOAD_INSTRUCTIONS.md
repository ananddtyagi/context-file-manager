# PyPI Upload Instructions

This guide explains how to build and upload the Context File Manager package to PyPI.

## Prerequisites

1. Create a PyPI account at https://pypi.org/account/register/
2. Install build and upload tools:
   ```bash
   pip install build twine
   ```

## Building the Package

1. Clean any previous builds:
   ```bash
   rm -rf dist/ build/ *.egg-info/
   ```

2. Build the package:
   ```bash
   python -m build
   ```
   
   This creates:
   - `dist/context-file-manager-version.tar.gz` (source distribution)
   - `dist/context_file_manager-version-py3-none-any.whl` (wheel distribution)

## Testing Locally

Before uploading to PyPI, test the package locally:

```bash
pip install dist/context_file_manager-0.1.0-py3-none-any.whl
cfm --help
```

## Uploading to PyPI

1. Upload to PyPI:
   ```bash
   python -m twine upload dist/*
   ```
   
   You'll be prompted for your PyPI username and password.

2. Or use an API token (recommended):
   - Generate a token at https://pypi.org/manage/account/token/
   - Use `__token__` as username and the token as password

## Using .pypirc for Authentication

Create `~/.pypirc` for easier uploads:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
username = __token__
password = pypi-your-testpypi-token-here
```

Then upload without entering credentials:
```bash
python -m twine upload dist/*
```

## Version Updates

When releasing new versions:

1. Update version in:
   - `cfm_package/__init__.py`
   - `setup.py`
   - `pyproject.toml`

2. Rebuild and upload as above

## Verification

After uploading, verify the package:

1. Visit https://pypi.org/project/context-file-manager/
2. Install in a fresh environment:
   ```bash
   pip install context-file-manager
   ```
3. Test the CLI:
   ```bash
   cfm --help
   ```

## Common Issues

- **Name conflicts**: If the package name is taken, update it in `setup.py` and `pyproject.toml`
- **Missing files**: Ensure `MANIFEST.in` includes all necessary files
- **Import errors**: Test the package structure locally before uploading
- **Authentication**: Use API tokens instead of passwords for better security