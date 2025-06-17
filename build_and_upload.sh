#!/bin/bash

# Build and Upload Script for Context File Manager
# This script builds the package and uploads it to PyPI

echo "Building Context File Manager for PyPI..."

# Clean up old builds
echo "Cleaning up old builds..."
rm -rf build/ dist/ *.egg-info

# Build the package
echo "Building package..."
python -m build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "Build successful!"
    echo ""
    echo "Files created:"
    ls -la dist/
    echo ""
    echo "To upload to Test PyPI (recommended for first time):"
    echo "  python -m twine upload --repository testpypi dist/*"
    echo ""
    echo "To upload to PyPI:"
    echo "  python -m twine upload dist/*"
else
    echo "Build failed!"
    exit 1
fi