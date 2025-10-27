# Docker Debugging Setup for Barodybroject

## Quick Start
1. **Start containers**: `docker-compose up -d`
2. **Open VS Code**: Launch configuration "🐍 Python/Django Debug (Attach to Docker)"
3. **Set breakpoints** in your Django code
4. **Navigate to http://localhost:8000** to trigger debugging

## Components

### 🐳 Docker Configuration
- **Port 8000**: Django development server
- **Port 5678**: Debugpy debugging port
- **Development entrypoint**: Uses Django runserver with debugpy

### 🔧 VS Code Integration
- **Attach Configuration**: Connects to debugpy running in container
- **Path Mapping**: Maps `/app` (container) to `${workspaceFolder}/src` (local)
- **Pre-launch Task**: Automatically starts Docker containers

### 📁 Files Modified
- `docker-compose.yml`: Development configuration with debug ports
- `src/entrypoint-dev.sh`: Development entrypoint with debugpy
- `src/requirements.txt`: Added debugpy dependency
- `.vscode/launch.json`: Updated with attach configuration
- `.vscode/tasks.json`: Fixed Docker task paths

### 🚀 Available Launch Configurations
1. **🐍 Python/Django Debug (Attach to Docker)** *(Recommended)*
   - Attaches to running Django container with debugpy
   - Full debugging capabilities with breakpoints
   - Automatic Docker container startup

2. **🐍 Python/Django in Docker (Launch)**
   - Alternative direct launch method
   - Runs Django locally (outside container)

### 🛠 Available Tasks
- **Django: Start Debug Server**: Starts Django with debugpy waiting for VS Code
- **Django: Run Development Server (Debug Ready)**: Starts Django ready for debugging
- **Django: Run Migrations**: Database migrations in Docker
- **Django: Create Superuser**: Create admin user in Docker
- **Django: Collect Static Files**: Static file collection in Docker

## Troubleshooting

### Container Won't Start
```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs web

# Rebuild if needed
docker-compose build --no-cache
```

### Debugging Not Working
1. Ensure containers are running: `docker-compose ps`
2. Check debugpy port is exposed: `docker-compose logs web | grep 5678`
3. Verify VS Code is using correct launch configuration
4. Check path mappings in launch.json

### Django Issues
- **Database connection**: Ensure PostgreSQL container is healthy
- **Static files**: Run "Django: Collect Static Files" task
- **Migrations**: Run "Django: Run Migrations" task

## Production vs Development

### Development (docker-compose.yml)
- Uses `entrypoint-dev.sh`
- Django development server on port 8000
- Debugpy enabled on port 5678
- DEBUG=True

### Production (docker-compose.prod.yml)
- Uses `entrypoint.sh`
- Gunicorn server on port 80
- No debug ports
- DEBUG=False

---

**Status**: ✅ Docker debugging fully configured and ready
**Last Updated**: October 26, 2025