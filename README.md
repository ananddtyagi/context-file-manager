# Context File Manager (CFM)

A command-line tool for managing shared context files across projects. CFM provides a centralized repository for storing, organizing, and retrieving commonly used files with descriptions and tags.

## Features

- **Centralized Storage**: Store commonly used files and folders in a single repository (~/.context-files by default)
- **File Organization**: Add descriptions and tags to files and folders for easy searching and filtering
- **Folder Support**: Add entire folders with preserved directory structure
- **Quick Retrieval**: Copy files or folders from the repository to any project location
- **Search Capabilities**: Find files and folders by name, description, or tags
- **Multiple Output Formats**: View file listings in table, JSON, or simple format

## Installation

### From PyPI (Recommended)

```bash
pip install context-file-manager
```

### From Source

Clone the repository and install in development mode:

```bash
git clone https://github.com/ananddtyagi/context-file-manager.git
cd context-file-manager
pip install -e .
```

### Manual Installation

Make the script executable and add it to your PATH:

```bash
chmod +x cfm
sudo cp cfm /usr/local/bin/
```

Or create an alias in your shell configuration:

```bash
alias cfm='python3 /path/to/context-file-manager/cfm'
```

## Usage

### Add files and folders to the repository

```bash
# Add a file with description
cfm add README.md "Main project documentation"

# Add a file with description and tags
cfm add config.json "Database configuration" --tags database config production

# Add a folder with all its contents
cfm add-folder ./src "Source code directory" --tags code javascript

# Add a folder with tags
cfm add-folder ./templates "Project templates" --tags templates starter
```

### List files and folders

```bash
# List all files and folders
cfm list

# Filter by tag
cfm list --tag database

# Output as JSON
cfm list --format json

# List contents of a specific folder
cfm list-folder src
```

### Search for files and folders

```bash
# Search by filename, description, or tags
cfm search "config"
cfm search "database"
cfm search "template"
```

### Retrieve files and folders

```bash
# Copy a file to current directory
cfm get README.md

# Copy a file to specific location
cfm get config.json ./my-project/

# Copy a folder to current directory
cfm get-folder src

# Copy a folder to specific location
cfm get-folder templates ./new-project/
```

### Update file metadata

```bash
# Update description
cfm update config.json "Production database configuration"

# Add tags to existing file
cfm tag config.json staging development
```

### Remove files and folders

```bash
# Remove a file
cfm remove old-config.json

# Remove a folder
cfm remove-folder old-src
```

## Custom Repository Location

By default, files are stored in `~/.context-files`. You can use a different location:

```bash
cfm --repo /path/to/my/repo add file.txt "Description"
```

## File Storage

Files are stored with their original names in the repository directory. If a filename already exists, a numbered suffix is added (e.g., `config_1.json`, `config_2.json`).

Metadata is stored in `spec.json` within the repository, containing:
- File descriptions
- Original file paths
- Tags
- File sizes
- Date added

## Examples

### Managing Configuration Files

```bash
# Store various config files
cfm add nginx.conf "Nginx configuration for load balancing" --tags nginx webserver
cfm add docker-compose.yml "Standard Docker setup" --tags docker devops
cfm add .eslintrc.js "JavaScript linting rules" --tags javascript linting

# Store entire configuration directories
cfm add-folder ./configs "All configuration files" --tags config settings
cfm add-folder ./docker-configs "Docker configurations" --tags docker devops

# Find all Docker-related files
cfm list --tag docker

# Get a config for a new project
cfm get docker-compose.yml ./new-project/

# Get entire config folder
cfm get-folder configs ./new-project/
```

### Managing Documentation Templates

```bash
# Store documentation templates
cfm add README-template.md "Standard README template" --tags documentation template
cfm add API-docs-template.md "API documentation template" --tags documentation api

# Store documentation folder
cfm add-folder ./doc-templates "Documentation templates" --tags documentation templates

# Search for documentation
cfm search "template"

# List contents of documentation folder
cfm list-folder doc-templates
```

### Managing Project Templates

```bash
# Store entire project template structures
cfm add-folder ./react-template "React project template" --tags react javascript template
cfm add-folder ./python-template "Python project template" --tags python template

# List all templates
cfm list --tag template

# Create new project from template
cfm get-folder react-template ./my-new-react-app
```

## License

MIT