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
            "tags": tags or [],
            "type": "file"
        }
        self._save_spec(spec)
        
        print(f"✓ Added: {dest_filename}")
        return dest_filename
    
    def add_folder(self, folder_path: str, description: str, tags: Optional[List[str]] = None):
        """Add a folder and all its contents to the repository."""
        source_path = Path(folder_path).expanduser().resolve()
        
        if not source_path.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        
        if not source_path.is_dir():
            raise ValueError(f"Path is not a directory: {folder_path}")
        
        # Generate unique folder name
        folder_name = source_path.name
        dest_folder_path = self.repo_path / folder_name
        
        # Handle duplicate folder names
        counter = 1
        while dest_folder_path.exists():
            folder_name = f"{source_path.name}_{counter}"
            dest_folder_path = self.repo_path / folder_name
            counter += 1
        
        # Create the folder
        dest_folder_path.mkdir(parents=True, exist_ok=True)
        
        # Copy all contents recursively
        files_added = []
        total_size = 0
        
        for item in source_path.rglob("*"):
            if item.is_file():
                # Calculate relative path
                rel_path = item.relative_to(source_path)
                dest_item_path = dest_folder_path / rel_path
                
                # Create parent directories if needed
                dest_item_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy the file
                shutil.copy2(item, dest_item_path)
                files_added.append(str(rel_path))
                total_size += item.stat().st_size
        
        # Update spec
        spec = self._load_spec()
        spec[folder_name] = {
            "description": description,
            "original_path": str(source_path),
            "added_date": datetime.now().isoformat(),
            "size": total_size,
            "tags": tags or [],
            "type": "folder",
            "file_count": len(files_added),
            "files": files_added
        }
        self._save_spec(spec)
        
        print(f"✓ Added folder: {folder_name} ({len(files_added)} files)")
        return folder_name
    
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
        print(self._format_table_output(spec))
    
    def _format_table_output(self, spec: Dict) -> str:
        """Format files in a table and return as string."""
        # Calculate column widths
        max_filename = max(len(f) for f in spec.keys()) if spec else 8
        max_filename = max(max_filename, 8)  # Minimum width
        
        lines = []
        # Header
        lines.append(f"{'Name':<{max_filename}} | {'Type':<6} | {'Description':<40} | {'Tags':<20} | Size")
        lines.append("-" * (max_filename + 6 + 40 + 20 + 20))
        
        # Files and folders
        for filename, info in spec.items():
            item_type = info.get('type', 'file')
            if item_type == 'folder':
                type_str = "folder"
                size_str = f"{self._format_size(info.get('size', 0))} ({info.get('file_count', 0)} files)"
            else:
                type_str = "file"
                size_str = self._format_size(info.get('size', 0))
            
            desc = info['description'][:37] + "..." if len(info['description']) > 40 else info['description']
            tags = ", ".join(info.get('tags', []))[:17] + "..." if len(", ".join(info.get('tags', []))) > 20 else ", ".join(info.get('tags', []))
            
            lines.append(f"{filename:<{max_filename}} | {type_str:<6} | {desc:<40} | {tags:<20} | {size_str}")
        
        return "\n".join(lines)
    
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
    
    def get_folder(self, folder_name: str, destination: Optional[str] = None):
        """Copy a folder from the repository to a destination."""
        source_path = self.repo_path / folder_name
        
        if not source_path.exists():
            raise FileNotFoundError(f"Folder not found in repository: {folder_name}")
        
        if not source_path.is_dir():
            raise ValueError(f"Not a folder: {folder_name}")
        
        if destination:
            dest_base = Path(destination).expanduser().resolve()
        else:
            dest_base = Path.cwd()
        
        dest_path = dest_base / folder_name
        
        # Check if destination already exists
        if dest_path.exists():
            raise FileExistsError(f"Destination already exists: {dest_path}")
        
        # Copy the entire folder
        shutil.copytree(source_path, dest_path)
        
        # Count files
        file_count = sum(1 for _ in dest_path.rglob("*") if _.is_file())
        
        print(f"✓ Copied folder {folder_name} to {dest_path} ({file_count} files)")
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
    
    def remove_folder(self, folder_name: str):
        """Remove a folder from the repository."""
        folder_path = self.repo_path / folder_name
        
        if not folder_path.exists():
            raise FileNotFoundError(f"Folder not found in repository: {folder_name}")
        
        if not folder_path.is_dir():
            raise ValueError(f"Not a folder: {folder_name}")
        
        # Remove from filesystem
        shutil.rmtree(folder_path)
        
        # Update spec
        spec = self._load_spec()
        if folder_name in spec:
            del spec[folder_name]
            self._save_spec(spec)
        
        print(f"✓ Removed folder: {folder_name}")
    
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
    
    def list_folder_contents(self, folder_name: str):
        """List the contents of a folder in the repository."""
        spec = self._load_spec()
        
        if folder_name not in spec:
            raise FileNotFoundError(f"Folder not found in repository: {folder_name}")
        
        folder_info = spec[folder_name]
        if folder_info.get('type') != 'folder':
            raise ValueError(f"Not a folder: {folder_name}")
        
        print(f"\nContents of folder: {folder_name}")
        print(f"Description: {folder_info['description']}")
        print(f"Total size: {self._format_size(folder_info.get('size', 0))}")
        print(f"File count: {folder_info.get('file_count', 0)}")
        
        if folder_info.get('tags'):
            print(f"Tags: {', '.join(folder_info['tags'])}")
        
        files = folder_info.get('files', [])
        if files:
            print(f"\nFiles:")
            for file_path in sorted(files):
                print(f"  - {file_path}")
        else:
            print("\nNo files in folder.")

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
  
  # Add a folder with all its contents
  cfm add-folder ./src "Source code directory" --tags code javascript
  
  # List all files and folders
  cfm list
  
  # List contents of a specific folder
  cfm list-folder src
  
  # Search for files and folders
  cfm search "config"
  
  # Get a file from the repository
  cfm get README.md ./my-project/
  
  # Get a folder from the repository
  cfm get-folder src ./my-project/
  
  # Remove a file
  cfm remove old-config.json
  
  # Remove a folder
  cfm remove-folder old-src
        """
    )
    
    parser.add_argument('--repo', '-r', help='Repository path (default: ~/.context-files)')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a file to the repository')
    add_parser.add_argument('file', help='Path to the file to add')
    add_parser.add_argument('description', help='Description of the file')
    add_parser.add_argument('--tags', '-t', nargs='+', help='Tags for the file')
    
    # Add folder command
    add_folder_parser = subparsers.add_parser('add-folder', help='Add a folder to the repository')
    add_folder_parser.add_argument('folder', help='Path to the folder to add')
    add_folder_parser.add_argument('description', help='Description of the folder')
    add_folder_parser.add_argument('--tags', '-t', nargs='+', help='Tags for the folder')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all files and folders')
    list_parser.add_argument('--tag', '-t', help='Filter by tag')
    list_parser.add_argument('--format', '-f', choices=['table', 'json', 'simple'], 
                           default='table', help='Output format')
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get a file from the repository')
    get_parser.add_argument('filename', help='Name of the file in the repository')
    get_parser.add_argument('destination', nargs='?', help='Destination path (optional)')
    
    # Get folder command
    get_folder_parser = subparsers.add_parser('get-folder', help='Get a folder from the repository')
    get_folder_parser.add_argument('folder', help='Name of the folder in the repository')
    get_folder_parser.add_argument('destination', nargs='?', help='Destination path (optional)')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove a file from the repository')
    remove_parser.add_argument('filename', help='Name of the file to remove')
    
    # Remove folder command
    remove_folder_parser = subparsers.add_parser('remove-folder', help='Remove a folder from the repository')
    remove_folder_parser.add_argument('folder', help='Name of the folder to remove')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for files and folders')
    search_parser.add_argument('query', help='Search query')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update file description')
    update_parser.add_argument('filename', help='Name of the file')
    update_parser.add_argument('description', help='New description')
    
    # Tag command
    tag_parser = subparsers.add_parser('tag', help='Add tags to a file or folder')
    tag_parser.add_argument('filename', help='Name of the file or folder')
    tag_parser.add_argument('tags', nargs='+', help='Tags to add')
    
    # List folder contents command
    list_folder_parser = subparsers.add_parser('list-folder', help='List contents of a folder')
    list_folder_parser.add_argument('folder', help='Name of the folder to list')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        manager = ContextFileManager(args.repo)
        
        if args.command == 'add':
            manager.add_file(args.file, args.description, args.tags)
        elif args.command == 'add-folder':
            manager.add_folder(args.folder, args.description, args.tags)
        elif args.command == 'list':
            manager.list_files(args.tag, args.format)
        elif args.command == 'get':
            manager.get_file(args.filename, args.destination)
        elif args.command == 'get-folder':
            manager.get_folder(args.folder, args.destination)
        elif args.command == 'remove':
            manager.remove_file(args.filename)
        elif args.command == 'remove-folder':
            manager.remove_folder(args.folder)
        elif args.command == 'search':
            manager.search_files(args.query)
        elif args.command == 'update':
            manager.update_description(args.filename, args.description)
        elif args.command == 'tag':
            manager.add_tags(args.filename, args.tags)
        elif args.command == 'list-folder':
            manager.list_folder_contents(args.folder)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()