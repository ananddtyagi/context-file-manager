"""
Setup configuration for Context File Manager
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="context-file-manager",
    version="0.1.1",
    author="Anand Tyagi",
    author_email="anand.deep.tyagi@gmail.com",
    description="A CLI tool for managing shared context files across projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ananddtyagi/context-file-manager",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Filesystems",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "cfm=cfm_package.main:main",
        ],
    },
    keywords="file management, context files, cli tool, project management",
    project_urls={
        "Bug Reports": "https://github.com/ananddtyagi/context-file-manager/issues",
        "Source": "https://github.com/ananddtyagi/context-file-manager",
    },
)