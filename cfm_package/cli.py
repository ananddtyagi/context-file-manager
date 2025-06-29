#!/usr/bin/env python3
"""
CLI interface for Context File Manager
"""

import sys
import argparse
import json
import subprocess
import shutil
from .main import ContextFileManager


def setup_mcp_config():
    """Generate Claude Desktop MCP configuration for context-file-manager"""
    
    # Check if MCP dependencies are available
    try:
        import mcp
    except ImportError:
        print("❌ MCP dependencies not found!")
        print("📦 Please install with MCP support:")
        print("   pip install 'context-file-manager[mcp]'")
        return
    
    # Find Python executable
    python_path = shutil.which('python')
    if not python_path:
        python_path = shutil.which('python3')
    
    if not python_path:
        print("❌ Python executable not found in PATH")
        return
    
    # Test if the MCP server module is available
    try:
        result = subprocess.run([
            python_path, '-c', 'import cfm_package.cfm_mcp_server'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ cfm_package.cfm_mcp_server module not found")
            print("📦 Please install with MCP support:")
            print("   pip install 'context-file-manager[mcp]'")
            return
    except Exception as e:
        print(f"❌ Error checking MCP server: {e}")
        return
    
    # Generate configuration
    config = {
        "context-file-manager": {
            "command": python_path,
            "args": ["-m", "cfm_package.cfm_mcp_server"]
        }
    }
    
    print("✅ MCP server configuration ready!")
    print("\n📋 Add this to your Claude Desktop config:")
    print("=" * 50)
    print(json.dumps(config, indent=2))
    print("=" * 50)
    print("\n📍 Config file locations:")
    print("   macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("   Windows: %APPDATA%\\Claude\\claude_desktop_config.json")
    print("   Linux: ~/.config/claude/claude_desktop_config.json")


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
  
  # Generate Claude Desktop MCP configuration
  cfm setup-mcp
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
    
    # Setup MCP command
    setup_mcp_parser = subparsers.add_parser('setup-mcp', help='Generate Claude Desktop MCP configuration')

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
        elif args.command == 'setup-mcp':
            setup_mcp_config()
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()