
# .devcontainer Directory

## Purpose
This directory contains Visual Studio Code development container configuration for the barodybroject. It provides a consistent, reproducible development environment using Docker containers with all the dependencies, tools, and extensions needed for Django and React development.

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
- **Port Forwarding**: Automatic forwarding of development ports (8000 Django, 5173 Vite, 5432 PostgreSQL, 5678 debugger)

### Services

| Service | What it runs |
|---|---|
| `python` | Django, under `debugpy --wait-for-client` — port 8000 stays silent until a debugger attaches |
| `frontend` | The Vite dev server for `src/frontend/`, with hot reload |
| `barodydb` | PostgreSQL |

`node_modules` lives in a named volume (`frontend-node-modules`) rather than the bind mount, so a host install and the container install don't fight over native modules.

### AI provider credentials

The compose file passes `AI_DEFAULT_PROVIDER`, `CLAUDE_CODE_OAUTH_TOKEN`, `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` through from your `.env`. The default provider is `claude_code`; mint a token with `claude setup-token`. Set only the variable for the credential you actually have — a stale key in another variable is a common source of confusing auth failures.

## Container Configuration
Development environment uses standard Python 3.11-slim image with:
- **Automated dependency installation**: System packages and Python requirements
- **Volume mounts**: Source code with live reload (`../:/workspace`)
- **PostgreSQL container**: Shared database for development
- **Vite container**: React dev server for the frontend
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
- Parent: [`../docker-compose.yml`](../docker-compose.yml) for the production-like configuration
