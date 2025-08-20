
# .devcontainer Directory

## Purpose
This directory contains Visual Studio Code development container configuration for the barodybroject. It provides a consistent, reproducible development environment using Docker containers that includes all necessary dependencies, tools, and extensions for Django development with OpenAI integration.

## Contents
- `devcontainer.json`: VS Code dev container configuration specifying container image, extensions, and settings
- `Dockerfile_dev`: Development-specific Dockerfile with additional debugging tools and development dependencies
- `docker-compose_dev.yml`: Docker Compose configuration for development environment with volume mounts and debugging ports

## Usage
Development container is automatically used by VS Code:

```bash
# Open in VS Code
code .

# VS Code will prompt to reopen in container
# Or use Command Palette: "Dev Containers: Reopen in Container"

# Development server with hot reload
python manage.py runserver 0.0.0.0:8000

# Debug with VS Code debugger
# Breakpoints and debugging work seamlessly
```

Development environment features:
- **Python 3.11**: Latest Python with Django development tools
- **Pre-installed Extensions**: Python, Django, Docker extensions
- **Debugging Support**: Integrated debugging with breakpoints
- **Hot Reload**: File changes automatically reflected
- **Database Access**: Direct connection to PostgreSQL container
- **Port Forwarding**: Automatic forwarding of development ports

## Container Configuration
Dev container provides complete development environment:
- Based on Python 3.11 with Django and development tools
- Volume mounts for source code with live reload
- PostgreSQL and Redis containers for local development
- Network configuration for inter-container communication
- Debug port exposure for VS Code integration

## Related Paths
- Incoming: Used by VS Code when opening the project
- Outgoing: Provides containerized development environment for Django application
