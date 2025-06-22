#!/usr/bin/env python3

from typing import Optional
import sys

from .main import ContextFileManager

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: MCP server dependencies not installed.", file=sys.stderr)
    print("Please install with: pip install context-file-manager[mcp]", file=sys.stderr)
    sys.exit(1)

# Initialize the FastMCP server
mcp = FastMCP("Context File Manager")

@mcp.tool()
async def cfm_add_file(file_path: str, description: str, tags: Optional[list[str]] = None, repo_path: Optional[str] = None) -> str:
    """Add a file to the context repository with description and optional tags.
    
    Args:
        file_path: Path to the file to add
        description: Description of the file
        tags: Optional list of tags for the file
        repo_path: Optional custom repository path
    """
    try:
        cfm = ContextFileManager(repo_path)
        result = cfm.add_file(file_path, description, tags or [])
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def cfm_add_folder(folder_path: str, description: str, tags: Optional[list[str]] = None, repo_path: Optional[str] = None) -> str:
    """Add a folder to the context repository with description and optional tags.
    
    Args:
        folder_path: Path to the folder to add
        description: Description of the folder
        tags: Optional list of tags for the folder
        repo_path: Optional custom repository path
    """
    try:
        cfm = ContextFileManager(repo_path)
        result = cfm.add_folder(folder_path, description, tags or [])
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def cfm_list(tag: Optional[str] = None, format: str = "table", repo_path: Optional[str] = None) -> str:
    """List all files and folders in the repository.
    
    Args:
        tag: Optional tag filter
        format: Output format (table, json, simple)
        repo_path: Optional custom repository path
    """
    try:
        cfm = ContextFileManager(repo_path)
        spec = cfm._load_spec()
        
        if not spec:
            return "The context file repository is currently empty. There are no files or folders added yet."
        
        # Filter by tag if provided
        if tag:
            spec = {k: v for k, v in spec.items() if tag in v.get("tags", [])}
            if not spec:
                return f"No files found with tag: {tag}"
        
        if format == "table":
            return cfm._format_table_output(spec)
        elif format == "json":
            import json
            return json.dumps(spec, indent=2)
        elif format == "simple":
            return "\n".join(spec.keys())
            
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def cfm_search(query: str, repo_path: Optional[str] = None) -> str:
    """Search for files and folders by name, description, or tags.
    
    Args:
        query: Search query
        repo_path: Optional custom repository path
    """
    try:
        cfm = ContextFileManager(repo_path)
        result = cfm.search_files(query)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def cfm_get_file(filename: str, destination: Optional[str] = None, repo_path: Optional[str] = None) -> str:
    """Copy a file from the repository to a destination.
    
    Args:
        filename: Name of the file to retrieve
        destination: Destination path (optional, defaults to current directory)
        repo_path: Optional custom repository path
    """
    try:
        cfm = ContextFileManager(repo_path)
        result = cfm.get_file(filename, destination)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def cfm_get_folder(folder_name: str, destination: Optional[str] = None, repo_path: Optional[str] = None) -> str:
    """Copy a folder from the repository to a destination.
    
    Args:
        folder_name: Name of the folder to retrieve
        destination: Destination path (optional, defaults to current directory)
        repo_path: Optional custom repository path
    """
    try:
        cfm = ContextFileManager(repo_path)
        result = cfm.get_folder(folder_name, destination)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def cfm_remove(name: str, repo_path: Optional[str] = None) -> str:
    """Remove a file from the repository.
    
    Args:
        name: Name of the file to remove
        repo_path: Optional custom repository path
    """
    try:
        cfm = ContextFileManager(repo_path)
        result = cfm.remove_file(name)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def cfm_remove_folder(folder_name: str, repo_path: Optional[str] = None) -> str:
    """Remove a folder from the repository.
    
    Args:
        folder_name: Name of the folder to remove
        repo_path: Optional custom repository path
    """
    try:
        cfm = ContextFileManager(repo_path)
        result = cfm.remove_folder(folder_name)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def cfm_update(filename: str, description: str, repo_path: Optional[str] = None) -> str:
    """Update the description of a file.
    
    Args:
        filename: Name of the file to update
        description: New description for the file
        repo_path: Optional custom repository path
    """
    try:
        cfm = ContextFileManager(repo_path)
        result = cfm.update_description(filename, description)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def cfm_tag(name: str, tags: list[str], repo_path: Optional[str] = None) -> str:
    """Add tags to an existing file or folder.
    
    Args:
        name: Name of the file or folder
        tags: List of tags to add
        repo_path: Optional custom repository path
    """
    try:
        cfm = ContextFileManager(repo_path)
        result = cfm.add_tags(name, tags)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def cfm_status(repo_path: Optional[str] = None) -> str:
    """Get repository status including path and basic info.
    
    Args:
        repo_path: Optional custom repository path
    """
    try:
        cfm = ContextFileManager(repo_path)
        spec = cfm._load_spec()
        
        status_lines = []
        status_lines.append(f"Repository path: {cfm.repo_path}")
        status_lines.append(f"Spec file exists: {cfm.spec_file.exists()}")
        status_lines.append(f"Repository directory exists: {cfm.repo_path.exists()}")
        
        if cfm.spec_file.exists():
            file_count = len(spec)
            folder_count = sum(1 for info in spec.values() if info.get('type') == 'folder')
            regular_file_count = file_count - folder_count
            
            status_lines.append(f"Total items: {file_count}")
            status_lines.append(f"Files: {regular_file_count}")
            status_lines.append(f"Folders: {folder_count}")
        else:
            status_lines.append("No spec file found - repository appears empty")
            
        return "\n".join(status_lines)
        
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def cfm_list_folder(folder_name: str, repo_path: Optional[str] = None) -> str:
    """List contents of a specific folder in the repository.
    
    Args:
        folder_name: Name of the folder to list
        repo_path: Optional custom repository path
    """
    try:
        cfm = ContextFileManager(repo_path)
        result = cfm.list_folder_contents(folder_name)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """Main entry point for the MCP server."""
    mcp.run()

if __name__ == "__main__":
    main()