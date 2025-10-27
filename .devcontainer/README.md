
# .devcontainer Directory

## Purpose
This directory contains Visual Studio Code development container configuration for the barodybroject. It provides a consistent, reproducible development environment using Docker containers that includes all necessary dependencies, tools, and extensions for Django development with OpenAI integration.

## Contents
- `devcontainer.json`: VS Code dev container configuration specifying container services, extensions, and settings
- `docker-compose_dev.yml`: Docker Compose configuration for development environment with automated dependency installation
- ~~`Dockerfile_dev`~~: **REMOVED** - Now using standard Python image with inline commands
- ~~`README.md`~~: This documentation file

## Usage
Development container is automatically used by VS Code:

```bash
# Open in VS Code
code .

# VS Code will prompt to reopen in container
# Or use Command Palette: "Dev Containers: Reopen in Container"

# Development server starts automatically on container creation
# Access at http://localhost:8000

# Debug with VS Code debugger
# Breakpoints and debugging work seamlessly
```

Development environment features:
- **Python 3.11**: Latest Python with Django development tools
- **Automated Setup**: Dependencies installed automatically on container start
- **Pre-installed Extensions**: Python, Django, Docker, Azure tools
- **Debugging Support**: Integrated debugging with breakpoints (port 5678)
- **Hot Reload**: File changes automatically reflected
- **Database Access**: Direct connection to PostgreSQL container
- **Port Forwarding**: Automatic forwarding of development ports (8000, 5432)

## Container Configuration
Development environment uses standard Python 3.11-slim image with:
- **Automated dependency installation**: System packages and Python requirements
- **Volume mounts**: Source code with live reload (`../:/workspace`)
- **PostgreSQL container**: Shared database for development
- **Jekyll container**: Optional static site generation
- **Network configuration**: Isolated network for inter-container communication
- **Debug port exposure**: VS Code debugging integration on port 5678

## Key Changes
- **Eliminated custom Dockerfile**: Now uses standard `python:3.11-slim` image
- **Inline dependency installation**: All setup commands are in docker-compose_dev.yml
- **Simplified maintenance**: No separate Dockerfile_dev to maintain
- **Consistent with production**: Similar approach as production docker-compose.yml

## Related Paths
- Incoming: Used by VS Code when opening the project in dev containers
- Outgoing: Provides containerized development environment for Django application
- Parent: `/Users/bamr87/github/barodybroject/docker-compose.yml` for production configuration
