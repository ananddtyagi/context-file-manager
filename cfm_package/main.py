"""
Context File Manager - A CLI tool for managing shared context files across projects
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class ContextFileManager:
    def __init__(self, repo_path: Optional[str] = None):
        """Initialize the file manager with a repository path."""
        if repo_path:
            self.repo_path = Path(repo_path).expanduser().resolve()
        else:
            # Default to ~/.context-files
            self.repo_path = Path.home() / ".context-files"
        
        self.spec_file = self.repo_path / "spec.json"
        self._ensure_repo_exists()
    
    def _ensure_repo_exists(self):
        """Create the repository directory and spec file if they don't exist."""
        self.repo_path.mkdir(parents=True, exist_ok=True)
        if not self.spec_file.exists():
            self._save_spec({})
    
    def _load_spec(self) -> Dict:
        """Load the spec.json file."""
        try:
            with open(self.spec_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_spec(self, spec: Dict):
        """Save the spec.json file."""
        with open(self.spec_file, 'w') as f:
            json.dump(spec, f, indent=2)
    
    def add_file(self, file_path: str, description: str, tags: Optional[List[str]] = None):
        """Add a file to the repository."""
        source_path = Path(file_path).expanduser().resolve()
        
        if not source_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Generate a unique filename if needed
        dest_filename = source_path.name
        dest_path = self.repo_path / dest_filename
        
        # Handle duplicate filenames
        counter = 1
        while dest_path.exists():
            stem = source_path.stem
            suffix = source_path.suffix
            dest_filename = f"{stem}_{counter}{suffix}"
            dest_path = self.repo_path / dest_filename
            counter += 1
        
        # Copy the file
        shutil.copy2(source_path, dest_path)
        
        # Update spec
        spec = self._load_spec()
        spec[dest_filename] = {
            "description": description,
            "original_path": str(source_path),
            "added_date": datetime.now().isoformat(),
            "size": source_path.stat().st_size,
            "tags": tags or []
        }
        self._save_spec(spec)
        
        print(f"✓ Added: {dest_filename}")
        return dest_filename
    
    def list_files(self, tag: Optional[str] = None, format: str = "table"):
        """List all files in the repository."""
        spec = self._load_spec()
        
        if not spec:
            print("No files in repository.")
            return
        
        # Filter by tag if provided
        if tag:
            spec = {k: v for k, v in spec.items() if tag in v.get("tags", [])}
            if not spec:
                print(f"No files found with tag: {tag}")
                return
        
        if format == "table":
            self._print_table(spec)
        elif format == "json":
            print(json.dumps(spec, indent=2))
        elif format == "simple":
            for filename in spec:
                print(filename)
    
    def _print_table(self, spec: Dict):
        """Print files in a formatted table."""
        # Calculate column widths
        max_filename = max(len(f) for f in spec.keys()) if spec else 8
        max_filename = max(max_filename, 8)  # Minimum width
        
        # Print header
        print(f"\n{'Filename':<{max_filename}} | {'Description':<50} | {'Tags':<20} | Size")
        print("-" * (max_filename + 50 + 20 + 15))
        
        # Print files
        for filename, info in spec.items():
            desc = info['description'][:47] + "..." if len(info['description']) > 50 else info['description']
            tags = ", ".join(info.get('tags', []))[:17] + "..." if len(", ".join(info.get('tags', []))) > 20 else ", ".join(info.get('tags', []))
            size = self._format_size(info.get('size', 0))
            print(f"{filename:<{max_filename}} | {desc:<50} | {tags:<20} | {size}")
    
    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def get_file(self, filename: str, destination: Optional[str] = None):
        """Copy a file from the repository to a destination."""
        source_path = self.repo_path / filename
        
        if not source_path.exists():
            raise FileNotFoundError(f"File not found in repository: {filename}")
        
        if destination:
            dest_path = Path(destination).expanduser().resolve()
        else:
            dest_path = Path.cwd() / filename
        
        shutil.copy2(source_path, dest_path)
        print(f"✓ Copied {filename} to {dest_path}")
        return str(dest_path)
    
    def remove_file(self, filename: str):
        """Remove a file from the repository."""
        file_path = self.repo_path / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found in repository: {filename}")
        
        # Remove from filesystem
        file_path.unlink()
        
        # Update spec
        spec = self._load_spec()
        if filename in spec:
            del spec[filename]
            self._save_spec(spec)
        
        print(f"✓ Removed: {filename}")
    
    def search_files(self, query: str):
        """Search for files by description or filename."""
        spec = self._load_spec()
        query_lower = query.lower()
        
        matches = {}
        for filename, info in spec.items():
            if (query_lower in filename.lower() or 
                query_lower in info['description'].lower() or
                any(query_lower in tag.lower() for tag in info.get('tags', []))):
                matches[filename] = info
        
        if matches:
            self._print_table(matches)
        else:
            print(f"No files found matching: {query}")
    
    def update_description(self, filename: str, description: str):
        """Update the description of a file."""
        spec = self._load_spec()
        
        if filename not in spec:
            raise FileNotFoundError(f"File not found in repository: {filename}")
        
        spec[filename]['description'] = description
        self._save_spec(spec)
        print(f"✓ Updated description for: {filename}")
    
    def add_tags(self, filename: str, tags: List[str]):
        """Add tags to a file."""
        spec = self._load_spec()
        
        if filename not in spec:
            raise FileNotFoundError(f"File not found in repository: {filename}")
        
        current_tags = set(spec[filename].get('tags', []))
        current_tags.update(tags)
        spec[filename]['tags'] = list(current_tags)
        self._save_spec(spec)
        print(f"✓ Added tags to {filename}: {', '.join(tags)}")

def main():
    parser = argparse.ArgumentParser(
        description="Context File Manager - Manage shared context files across projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add a file with description
  cfm add README.md "Main project documentation"
  
  # Add a file with tags
  cfm add config.json "Database configuration" --tags database config
  
  # List all files
  cfm list
  
  # Search for files
  cfm search "config"
  
  # Get a file from the repository
  cfm get README.md ./my-project/
  
  # Remove a file
  cfm remove old-config.json
        """
    )
    
    parser.add_argument('--repo', '-r', help='Repository path (default: ~/.context-files)')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a file to the repository')
    add_parser.add_argument('file', help='Path to the file to add')
    add_parser.add_argument('description', help='Description of the file')
    add_parser.add_argument('--tags', '-t', nargs='+', help='Tags for the file')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all files')
    list_parser.add_argument('--tag', '-t', help='Filter by tag')
    list_parser.add_argument('--format', '-f', choices=['table', 'json', 'simple'], 
                           default='table', help='Output format')
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get a file from the repository')
    get_parser.add_argument('filename', help='Name of the file in the repository')
    get_parser.add_argument('destination', nargs='?', help='Destination path (optional)')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove a file from the repository')
    remove_parser.add_argument('filename', help='Name of the file to remove')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for files')
    search_parser.add_argument('query', help='Search query')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update file description')
    update_parser.add_argument('filename', help='Name of the file')
    update_parser.add_argument('description', help='New description')
    
    # Tag command
    tag_parser = subparsers.add_parser('tag', help='Add tags to a file')
    tag_parser.add_argument('filename', help='Name of the file')
    tag_parser.add_argument('tags', nargs='+', help='Tags to add')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        manager = ContextFileManager(args.repo)
        
        if args.command == 'add':
            manager.add_file(args.file, args.description, args.tags)
        elif args.command == 'list':
            manager.list_files(args.tag, args.format)
        elif args.command == 'get':
            manager.get_file(args.filename, args.destination)
        elif args.command == 'remove':
            manager.remove_file(args.filename)
        elif args.command == 'search':
            manager.search_files(args.query)
        elif args.command == 'update':
            manager.update_description(args.filename, args.description)
        elif args.command == 'tag':
            manager.add_tags(args.filename, args.tags)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()