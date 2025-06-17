# Context File Manager (CFM)

A command-line tool for managing shared context files across projects. CFM provides a centralized repository for storing, organizing, and retrieving commonly used files with descriptions and tags.

## Features

- **Centralized Storage**: Store commonly used files in a single repository (~/.context-files by default)
- **File Organization**: Add descriptions and tags to files for easy searching and filtering
- **Quick Retrieval**: Copy files from the repository to any project location
- **Search Capabilities**: Find files by name, description, or tags
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

### Add a file to the repository

```bash
# Add with description
cfm add README.md "Main project documentation"

# Add with description and tags
cfm add config.json "Database configuration" --tags database config production
```

### List files

```bash
# List all files
cfm list

# Filter by tag
cfm list --tag database

# Output as JSON
cfm list --format json
```

### Search for files

```bash
# Search by filename, description, or tags
cfm search "config"
cfm search "database"
```

### Retrieve a file

```bash
# Copy to current directory
cfm get README.md

# Copy to specific location
cfm get config.json ./my-project/
```

### Update file metadata

```bash
# Update description
cfm update config.json "Production database configuration"

# Add tags to existing file
cfm tag config.json staging development
```

### Remove a file

```bash
cfm remove old-config.json
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

# Find all Docker-related files
cfm list --tag docker

# Get a config for a new project
cfm get docker-compose.yml ./new-project/
```

### Managing Documentation Templates

```bash
# Store documentation templates
cfm add README-template.md "Standard README template" --tags documentation template
cfm add API-docs-template.md "API documentation template" --tags documentation api

# Search for documentation
cfm search "template"
```

## License

MIT