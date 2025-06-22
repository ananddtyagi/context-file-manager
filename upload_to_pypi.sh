#!/bin/bash

# Upload Context File Manager to PyPI
# Usage: ./upload_to_pypi.sh [test|prod]

set -e

# Change to the directory containing this script
cd "$(dirname "$0")"

# Parse arguments
ENVIRONMENT=${1:-test}

if [[ "$ENVIRONMENT" != "test" && "$ENVIRONMENT" != "prod" ]]; then
    echo "Usage: $0 [test|prod]"
    echo "  test: Upload to TestPyPI"
    echo "  prod: Upload to PyPI"
    exit 1
fi

echo "📦 Building package..."

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Install build dependencies
pip install --upgrade build twine

# Build the package
python -m build

echo "✅ Package built successfully"

if [[ "$ENVIRONMENT" == "test" ]]; then
    echo "🚀 Uploading to TestPyPI..."
    twine upload --repository testpypi dist/*
    echo "✅ Uploaded to TestPyPI"
    echo "📥 Test installation with:"
    echo "pip install --index-url https://test.pypi.org/simple/ context-file-manager"
    echo "pip install --index-url https://test.pypi.org/simple/ context-file-manager[mcp]"
else
    echo "🚀 Uploading to PyPI..."
    read -p "Are you sure you want to upload to production PyPI? (y/N): " confirm
    if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
        twine upload dist/*
        echo "✅ Uploaded to PyPI"
        echo "📥 Install with:"
        echo "pip install context-file-manager              # CLI only"
        echo "pip install context-file-manager[mcp]         # With MCP server"
        echo "pip install context-file-manager[all]         # Everything"
    else
        echo "❌ Upload cancelled"
        exit 1
    fi
fi