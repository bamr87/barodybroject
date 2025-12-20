# VS Code Configuration Guide

This directory contains VS Code workspace configurations for debugging and running the Barodybroject Django application.

## Table of Contents

- [Launch Configurations](#launch-configurations)
- [Task Configurations](#task-configurations)
- [Quick Start](#quick-start)
- [Configuration Details](#configuration-details)

## Launch Configurations

The `launch.json` file provides comprehensive debugging configurations organized into categories:

### 1. 🌐 Web Browser Debugging

Launch configurations that open the application in Microsoft Edge for testing:

| Configuration | Purpose | URL | Prerequisites |
|--------------|---------|-----|---------------|
| **Open Django App (Dev - Port 8000)** | Opens development server in browser | http://localhost:8000 | Docker containers running |
| **Open Django App (Prod - Port 80)** | Opens production server in browser | http://localhost:80 | Production containers running |
| **Open Django Admin (Local)** | Opens Django admin interface | http://localhost:8001/admin | Local Django server running |
| **Open Documentation (Port 8080)** | Opens Sphinx documentation | http://localhost:8080 | Documentation server running |

### 2. 🐍 Local Development (Without Docker)

Debug Django directly on your host machine (recommended for active development):

| Configuration | Purpose | Port | When to Use |
|--------------|---------|------|-------------|
| **Django: Run Server (Local)** | Start Django with auto-reload | 8001 | Active development, debugging views/models |
| **Django: Run Server (Local - No Reload)** | Start Django without auto-reload | 8001 | Debugging multi-threaded issues, breakpoints |

**Benefits of Local Development:**
- Faster startup time
- Better debugging experience with breakpoints
- Easier to see real-time code changes
- Direct access to Python debugger

**Requirements:**
- PostgreSQL running locally or via Docker (localhost:5432)
- Python 3.11+ installed
- Dependencies installed: `pip install -r requirements.txt`

### 3. 🧪 Testing Configurations

Debug your Django and pytest tests:

| Configuration | Purpose | Coverage |
|--------------|---------|----------|
| **Django: Run All Tests (Local)** | Run entire Django test suite | All apps |
| **Django: Test Current File** | Run tests in currently open file | Single file |
| **Django: Test Parodynews App** | Run all parodynews app tests | parodynews app |
| **Pytest: Run All Tests** | Run pytest test suite | All test files |
| **Pytest: Current File** | Run pytest on current file | Single file |

**Testing Tips:**
- Set breakpoints in test files to debug test failures
- Use verbose mode (`--verbosity=2`) to see detailed output
- Tests run against test database (`test_barodydb`)

### 4. 🔧 Django Management Commands

Debug Django management commands with breakpoints:

| Configuration | Command | Purpose |
|--------------|---------|---------|
| **Django: Make Migrations** | `makemigrations` | Create new migrations |
| **Django: Run Migrations** | `migrate` | Apply migrations to database |
| **Django: Shell** | `shell` | Interactive Python shell |
| **Django: Shell Plus** | `shell_plus` | Enhanced shell with models pre-loaded |
| **Django: Collect Static** | `collectstatic` | Collect static files |
| **Django: Check Deployment** | `check --deploy` | Validate production settings |

**Usage Example:**
1. Set breakpoint in your model or migration file
2. Select "Django: Make Migrations" from debug menu
3. Debugger will stop at your breakpoint

### 5. 🐍 Python Script Debugging

| Configuration | Purpose |
|--------------|---------|
| **Python: Current File** | Debug any Python script |

### 6. 🚀 Compound Configurations

Combine multiple debug sessions:

| Configuration | Includes | Purpose |
|--------------|----------|---------|
| **Full Stack (Local Django + Browser)** | Django Server + Browser | Complete development environment |

## Task Configurations

The `tasks.json` file provides Docker and Django management tasks. These are automatically triggered by launch configurations or can be run manually.

### Docker Tasks

**Development Environment:**
- `🐍 Docker: Development Up` - Start dev containers
- `⛔ Docker: Stop Development` - Stop dev containers
- `🔧 Docker: Rebuild Development` - Rebuild dev containers

**Production Environment:**
- `🚀 Docker: Production Up` - Start production containers
- `⛔ Docker: Stop Production` - Stop production containers
- `🏭 Docker: Rebuild Production` - Rebuild production containers

**Viewing Logs:**
- `📋 Docker: View Dev Logs` - Follow development logs
- `📋 Docker: View Production Logs` - Follow production logs
- `📋 Docker: View Database Logs` - Follow PostgreSQL logs

### Django Management Tasks

Tasks for running Django commands in containers:
- `📊 Django: Run Migrations (Dev/Prod)`
- `👤 Django: Create Superuser (Dev/Prod)`
- `📁 Django: Collect Static (Dev)`
- `🐚 Django: Shell (Dev)`

### Testing Tasks

- `🧪 Test: Run Django Tests` - Run Django test suite
- `🔬 Test: Run Pytest` - Run pytest
- `📈 Test: Run with Coverage` - Generate coverage report

## Quick Start

### Option 1: Local Development (Recommended for Active Development)

1. **Start PostgreSQL:**
   ```bash
   docker-compose up barodydb -d
   ```

2. **Run Django Locally:**
   - Press `F5` or go to Run & Debug
   - Select: `🐍 Django: Run Server (Local)`
   - Application starts at http://localhost:8001

3. **Set Breakpoints:**
   - Click in the gutter next to any line of code
   - The debugger will pause execution there

### Option 2: Docker Development

1. **Press `F5` and select:** `🌐 Open Django App (Dev - Port 8000)`
2. This will:
   - Start all development containers
   - Open browser to http://localhost:8000
   - Stop containers when you close the debug session

### Option 3: Full Stack Development

1. **Press `F5` and select:** `🚀 Full Stack (Local Django + Browser)`
2. Starts both Django server and browser simultaneously

## Configuration Details

### Environment Variables

All configurations use these environment variables:

```json
{
  "DJANGO_SETTINGS_MODULE": "barodybroject.settings",
  "DEBUG": "True",
  "RUNNING_IN_PRODUCTION": "False",
  "DB_HOST": "localhost",
  "DB_NAME": "barodydb",
  "DB_USERNAME": "postgres",
  "DB_PASSWORD": "postgres",
  "PYTHONPATH": "${workspaceFolder}/src"
}
```

### Ports Reference

| Port | Service | Environment |
|------|---------|-------------|
| 8000 | Django | Docker Development |
| 8001 | Django | Local Development |
| 80 | Django | Docker Production |
| 5432 | PostgreSQL | All |
| 5678 | Debugpy | Docker (reserved for future use) |
| 8080 | Sphinx Docs | Docker |
| 4002 | Jekyll | Docker |

### Working Directories

- **Django commands:** `${workspaceFolder}/src`
- **Python scripts:** `${fileDirname}` (current file's directory)
- **Root operations:** `${workspaceFolder}`

### Presentation Groups

Configurations are organized into groups for better UI organization:
- `0_compounds` - Compound configurations
- `1_docker_web` - Docker browser configurations
- `2_local_django` - Local Django servers
- `3_docs` - Documentation
- `4_testing` - Test configurations
- `5_management` - Management commands
- `6_python` - General Python scripts

## Troubleshooting

### "Cannot connect to debugpy" Error

**Issue:** Docker configurations for Python debugging don't work.

**Reason:** The docker-compose configuration doesn't start debugpy server.

**Solution:** Use local development configurations instead, or update docker-compose to include debugpy:

```yaml
# In .devcontainer/docker-compose_dev.yml
command:
  - /bin/bash
  - -c
  - |
    # ... other setup ...
    pip install debugpy
    python -m debugpy --listen 0.0.0.0:5678 manage.py runserver 0.0.0.0:8000
```

### Database Connection Refused

**Issue:** Django can't connect to PostgreSQL.

**Check:**
1. PostgreSQL is running: `docker-compose ps barodydb`
2. Port is accessible: `psql -h localhost -U postgres -d barodydb`
3. Environment variables are correct in launch configuration

**Solution:**
```bash
# Start PostgreSQL
docker-compose up barodydb -d

# Wait for health check
docker-compose ps barodydb
```

### "Module not found" Errors

**Issue:** Python can't find Django modules.

**Solution:** Check that `PYTHONPATH` includes `${workspaceFolder}/src`:

```json
"env": {
  "PYTHONPATH": "${workspaceFolder}/src"
}
```

### Breakpoints Not Working

**Issue:** Debugger doesn't stop at breakpoints.

**Possible Causes:**
1. Using Docker configuration (debugpy not configured)
2. Auto-reload is enabled (use "No Reload" configuration)
3. Code is in a different process/thread

**Solution:**
- Use local development configurations
- Try "Django: Run Server (Local - No Reload)"
- Set `"justMyCode": false` in configuration

### Port Already in Use

**Issue:** Port 8000 or 8001 is already in use.

**Solution:**
```bash
# Find process using port
lsof -ti:8000 | xargs kill -9

# Or stop all containers
docker-compose down
```

## Best Practices

1. **Use Local Development for Active Coding:**
   - Faster iteration
   - Better debugging experience
   - Easier to test changes

2. **Use Docker for Integration Testing:**
   - Test production-like environment
   - Verify container configurations
   - Test service interactions

3. **Set Breakpoints Strategically:**
   - In views for request/response debugging
   - In models for data validation
   - In management commands for batch operations

4. **Use Compound Configurations:**
   - Start multiple services at once
   - Consistent development environment

5. **Leverage Presentation Groups:**
   - Keep debug menu organized
   - Quickly find relevant configurations

## Additional Resources

- [VS Code Python Debugging](https://code.visualstudio.com/docs/python/debugging)
- [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)

## Updates

- **2025-12-20:** Complete overhaul of launch configurations
  - Added organized presentation groups
  - Added comprehensive testing configurations
  - Added management command debugging
  - Added compound configurations
  - Fixed environment variables and paths
  - Improved documentation

---

*For questions or issues, refer to the project's main README.md or create an issue.*
