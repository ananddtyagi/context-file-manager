#!/usr/bin/env python3
"""
Auto-version script that updates version based on git commit messages.
Uses conventional commit format: feat:, fix:, docs:, style:, refactor:, test:, chore:

Version bump rules:
- feat: minor version bump (0.x.0)
- fix: patch version bump (0.0.x)
- BREAKING CHANGE in commit body: major version bump (x.0.0)
- Others: no version bump
"""

import re
import subprocess
import sys
from pathlib import Path


def get_current_version():
    """Get current version from setup.py"""
    setup_path = Path(__file__).parent / 'setup.py'
    with open(setup_path, 'r') as f:
        content = f.read()
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    return "0.0.0"


def parse_version(version_str):
    """Parse version string into major, minor, patch"""
    parts = version_str.split('.')
    return int(parts[0]), int(parts[1]), int(parts[2])


def bump_version(version_str, bump_type):
    """Bump version based on bump type"""
    major, minor, patch = parse_version(version_str)
    
    if bump_type == 'major':
        return f"{major + 1}.0.0"
    elif bump_type == 'minor':
        return f"{major}.{minor + 1}.0"
    elif bump_type == 'patch':
        return f"{major}.{minor}.{patch + 1}"
    else:
        return version_str


def get_latest_tag():
    """Get the latest git tag"""
    try:
        result = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], 
                                capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return None


def get_commits_since_tag(tag=None):
    """Get all commits since the last tag"""
    if tag:
        cmd = ['git', 'log', f'{tag}..HEAD', '--pretty=format:%s%n%b%n---']
    else:
        cmd = ['git', 'log', '--pretty=format:%s%n%b%n---']
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []
    
    commits = result.stdout.strip().split('\n---\n')
    return [c.strip() for c in commits if c.strip()]


def determine_bump_type(commits):
    """Determine version bump type based on commits"""
    has_feat = False
    has_fix = False
    has_breaking = False
    
    for commit in commits:
        lines = commit.split('\n')
        subject = lines[0] if lines else ''
        body = '\n'.join(lines[1:]) if len(lines) > 1 else ''
        
        # Check for breaking change
        if 'BREAKING CHANGE' in body or 'BREAKING-CHANGE' in body:
            has_breaking = True
        
        # Check commit type
        if subject.startswith('feat:') or subject.startswith('feat('):
            has_feat = True
        elif subject.startswith('fix:') or subject.startswith('fix('):
            has_fix = True
    
    if has_breaking:
        return 'major'
    elif has_feat:
        return 'minor'
    elif has_fix:
        return 'patch'
    else:
        return None


def update_version_files(new_version):
    """Update version in all relevant files"""
    files_to_update = [
        ('setup.py', r'version\s*=\s*["\'][^"\']+["\']', f'version="{new_version}"'),
        ('pyproject.toml', r'version\s*=\s*["\'][^"\']+["\']', f'version = "{new_version}"'),
        ('cfm_package/__init__.py', r'__version__\s*=\s*["\'][^"\']+["\']', f'__version__ = "{new_version}"'),
    ]
    
    for file_path, pattern, replacement in files_to_update:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            with open(full_path, 'r') as f:
                content = f.read()
            
            updated_content = re.sub(pattern, replacement, content)
            
            with open(full_path, 'w') as f:
                f.write(updated_content)
            print(f"Updated {file_path} with version {new_version}")
        else:
            print(f"Warning: {file_path} not found")


def main():
    """Main function"""
    # Get current version
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    
    # Get latest tag
    latest_tag = get_latest_tag()
    print(f"Latest tag: {latest_tag or 'None'}")
    
    # Get commits since last tag
    commits = get_commits_since_tag(latest_tag)
    if not commits:
        print("No commits found since last tag")
        return
    
    print(f"Found {len(commits)} commits since last tag")
    
    # Determine bump type
    bump_type = determine_bump_type(commits)
    if not bump_type:
        print("No version bump needed (no feat: or fix: commits)")
        return
    
    print(f"Bump type: {bump_type}")
    
    # Calculate new version
    new_version = bump_version(current_version, bump_type)
    print(f"New version: {new_version}")
    
    # Update all version files
    update_version_files(new_version)
    
    # Optionally create git tag
    if '--tag' in sys.argv:
        subprocess.run(['git', 'add', 'setup.py', 'pyproject.toml', 'cfm_package/__init__.py'])
        subprocess.run(['git', 'commit', '-m', f'chore: bump version to {new_version}'])
        subprocess.run(['git', 'tag', f'v{new_version}'])
        print(f"Created git tag v{new_version}")


if __name__ == '__main__':
    main()