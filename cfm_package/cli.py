#!/usr/bin/env python3
"""
CLI interface for Context File Manager
"""

import sys
import argparse
from .main import ContextFileManager


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