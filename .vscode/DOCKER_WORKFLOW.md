# Docker-First Development Workflow

## 🐳 Philosophy

This project uses **Docker-first development** for consistency, reliability, and ease of setup.

### Why Docker First?

✅ **Consistent Environment** - Everyone uses the same Python, PostgreSQL, and dependencies
✅ **No Local Setup** - No need to install PostgreSQL, Python packages, etc. locally  
✅ **Production Parity** - Develop in an environment similar to production ✅ **Easy Onboarding** - New developers: install Docker and go ✅ **No Conflicts** - Isolated from your local Python/PostgreSQL installations

## 🚀 Quick Start

### 1. Start Docker Development

**Option A: Use VS Code Debug Menu** (Recommended)
```
1. Press F5 or click Run & Debug
2. Select: 🐳 Django: Docker Debug
3. Wait for containers to start
4. Debugger attaches automatically
5. Open http://localhost:8000
```

**Option B: Use VS Code Task**
```
1. Cmd+Shift+P → Tasks: Run Task
2. Select: 🐍 Docker: Development Up
3. Wait for "Starting Django with debugpy..."
4. Press F5 → 🐳 Django: Docker Debug
```

**Option C: Use Command Line**
```bash
docker-compose -f .devcontainer/docker-compose_dev.yml up -d
# Then in VS Code: F5 → 🐳 Django: Docker Debug
```

### 2. Set Breakpoints & Debug

1. Open any Python file (views, models, etc.)
2. Click in the gutter to set a breakpoint (red dot)
3. Visit http://localhost:8000 in your browser
4. Debugger pauses at your breakpoint!

### 3. View Logs

```
Cmd+Shift+P → Tasks: Run Task → 📋 Docker: View Dev Logs
```

Or in terminal:
```bash
docker-compose -f .devcontainer/docker-compose_dev.yml logs -f python
```

### 4. Run Django Commands in Docker

```bash
# Run migrations
docker-compose -f .devcontainer/docker-compose_dev.yml exec python python manage.py migrate

# Create superuser
docker-compose -f .devcontainer/docker-compose_dev.yml exec python python manage.py createsuperuser

# Django shell
docker-compose -f .devcontainer/docker-compose_dev.yml exec python python manage.py shell

# Or use VS Code tasks (Cmd+Shift+P → Tasks: Run Task)
```

### 5. Stop Everything

```bash
docker-compose -f .devcontainer/docker-compose_dev.yml down
```

Or use VS Code task: `⛔ Docker: Stop Development`

## 📋 Available Debug Configurations

### 🐳 Primary (Docker-Based)

| Configuration | Purpose | When to Use |
|--------------|---------|-------------|
| **🐳 Django: Docker Debug** | Full Python debugging in Docker | Daily development |
| **🐳 Django: Docker + Browser** | Debug + auto-open browser | Starting new session |
| **🧪 Django: Run All Tests (Docker)** | Run tests with debugging | Testing |

### 🌐 Browser Shortcuts

| Configuration | URL | Purpose |
|--------------|-----|---------|
| **🌐 Open Django App** | localhost:8000 | Open app in browser |
| **🌐 Open Django Admin** | localhost:8000/admin | Admin interface |
| **🌐 Open Documentation** | localhost:8080 | Sphinx docs |

### 💻 Local Development (Optional)

Only use these if Docker isn't working or for special cases:
- **💻 Django: Local (No Docker)** - Run Django on host machine
- **💻 Django: Test Current File (Local)** - Test single file locally
- **💻 Django: Shell (Local)** - Local Django shell

## 🔧 How It Works

### Docker Compose Setup

The `.devcontainer/docker-compose_dev.yml` defines:

1. **PostgreSQL** (`barodydb`)
   - Port 5432
   - Database: barodydb
   - User: postgres / Pass: postgres

2. **Python/Django** (`python`)
   - Port 8000 (Django)
   - Port 5678 (debugpy)
   - Volume: Your code mounted at `/workspace`
   - Auto-runs migrations and starts server with debugpy

3. **Documentation** (`docs`)
   - Port 8080
   - Sphinx auto-rebuild

### Debugpy Integration

The Python container starts with:
```bash
python -m debugpy --listen 0.0.0.0:5678 --wait-for-client manage.py runserver 0.0.0.0:8000 --noreload --nothreading
```

This:
- Listens for VS Code debugger on port 5678
- Waits for VS Code to connect before starting
- Runs Django without auto-reload (for stable debugging)
- Single-threaded (for predictable debugging)

### Path Mapping

VS Code maps your local code to the container:
```json
"pathMappings": [
  {
    "localRoot": "${workspaceFolder}/src",
    "remoteRoot": "/workspace/src"
  }
]
```

So breakpoints in your local files work in the container!

## 🎯 Common Workflows

### Daily Development

```bash
# Morning: Start containers
docker-compose -f .devcontainer/docker-compose_dev.yml up -d

# In VS Code: Press F5 → 🐳 Django: Docker Debug

# Make changes, set breakpoints, debug...

# Evening: Stop containers (optional, can leave running)
docker-compose -f .devcontainer/docker-compose_dev.yml down
```

### Making Model Changes

```bash
# 1. Edit your model in VS Code
# 2. Create migrations (in container)
docker-compose -f .devcontainer/docker-compose_dev.yml exec python python manage.py makemigrations

# 3. Run migrations
docker-compose -f .devcontainer/docker-compose_dev.yml exec python python manage.py migrate

# Or use VS Code tasks:
# - 🔧 Django: Make Migrations (Dev)
# - 📊 Django: Run Migrations (Dev)
```

### Running Tests

```bash
# All tests
docker-compose -f .devcontainer/docker-compose_dev.yml exec python python manage.py test

# Specific app
docker-compose -f .devcontainer/docker-compose_dev.yml exec python python manage.py test parodynews

# With coverage
docker-compose -f .devcontainer/docker-compose_dev.yml exec python python -m pytest --cov=parodynews

# Or use VS Code tasks/debug configs
```

### Database Access

```bash
# Django shell
docker-compose -f .devcontainer/docker-compose_dev.yml exec python python manage.py shell

# Direct PostgreSQL access
docker-compose -f .devcontainer/docker-compose_dev.yml exec barodydb psql -U postgres -d barodydb

# Create backup
docker-compose -f .devcontainer/docker-compose_dev.yml exec barodydb pg_dump -U postgres barodydb > backup.sql

# Restore backup
cat backup.sql | docker-compose -f .devcontainer/docker-compose_dev.yml exec -T barodydb psql -U postgres -d barodydb
```

### Installing New Python Packages

```bash
# 1. Add package to requirements.txt
echo "new-package==1.0.0" >> src/requirements.txt

# 2. Rebuild containers
docker-compose -f .devcontainer/docker-compose_dev.yml up --build -d

# Or use VS Code task: 🔧 Docker: Rebuild Development
```

### Viewing Logs

```bash
# All services
docker-compose -f .devcontainer/docker-compose_dev.yml logs -f

# Just Django
docker-compose -f .devcontainer/docker-compose_dev.yml logs -f python

# Just PostgreSQL
docker-compose -f .devcontainer/docker-compose_dev.yml logs -f barodydb

# Last 100 lines
docker-compose -f .devcontainer/docker-compose_dev.yml logs --tail=100 python
```

## 🐛 Debugging Tips

### Setting Breakpoints

1. **In Views:**
   ```python
   def article_detail(request, pk):
       # Click here in gutter → red dot appears
       article = Article.objects.get(pk=pk)
       return render(...)
   ```

2. **In Models:**
   ```python
   class Article(models.Model):
       def save(self, *args, **kwargs):
           # Breakpoint here
           super().save(*args, **kwargs)
   ```

3. **In Tests:**
   ```python
   def test_article_creation(self):
       # Breakpoint here
       article = Article.objects.create(title="Test")
   ```

### Inspecting Variables

When debugger pauses:
- **Variables Panel** - See all local variables
- **Watch** - Add expressions to watch
- **Debug Console** - Type Python expressions
- **Call Stack** - See execution path

### Step Through Code

- **F10** (Step Over) - Execute current line
- **F11** (Step Into) - Go into function calls
- **Shift+F11** (Step Out) - Exit current function
- **F5** (Continue) - Run until next breakpoint

### Conditional Breakpoints

Right-click breakpoint → Edit Breakpoint → Add condition:
```python
pk == 42  # Only pause when pk is 42
```

## 🔍 Troubleshooting

### "Cannot connect to debugpy"

**Cause:** Container not started or debugpy not running

**Solution:**
```bash
# Check container status
docker-compose -f .devcontainer/docker-compose_dev.yml ps

# Check logs
docker-compose -f .devcontainer/docker-compose_dev.yml logs python

# Should see: "Starting Django with debugpy on port 5678..."

# Restart if needed
docker-compose -f .devcontainer/docker-compose_dev.yml restart python
```

### "Port 5678 already in use"

**Cause:** Old debugpy process still running

**Solution:**
```bash
# Stop all containers
docker-compose -f .devcontainer/docker-compose_dev.yml down

# Start fresh
docker-compose -f .devcontainer/docker-compose_dev.yml up -d
```

### Breakpoints Not Working

**Check:**
1. ✅ Debugger attached (see "CALL STACK" panel in VS Code)
2. ✅ Breakpoint is solid red (not hollow)
3. ✅ Code path actually executes (visit URL, run test, etc.)

**Try:**
1. Detach and reattach debugger
2. Restart container
3. Check path mappings in launch.json

### Code Changes Not Reflected

**Cause:** Django is running with `--noreload` for debugging

**Solution:**
```bash
# Restart the container to pick up changes
docker-compose -f .devcontainer/docker-compose_dev.yml restart python

# Or if you don't need debugging, comment out debugpy in docker-compose and use:
# python manage.py runserver 0.0.0.0:8000
# (Then auto-reload works, but no debugging)
```

### Database Connection Errors

**Check:**
```bash
# Is PostgreSQL running?
docker-compose -f .devcontainer/docker-compose_dev.yml ps barodydb

# Can we connect?
docker-compose -f .devcontainer/docker-compose_dev.yml exec barodydb psql -U postgres -d barodydb

# Check logs
docker-compose -f .devcontainer/docker-compose_dev.yml logs barodydb
```

### Container Won't Start

```bash
# Clean everything
docker-compose -f .devcontainer/docker-compose_dev.yml down -v
docker system prune -f

# Rebuild from scratch
docker-compose -f .devcontainer/docker-compose_dev.yml build --no-cache

# Start fresh
docker-compose -f .devcontainer/docker-compose_dev.yml up -d
```

## 📊 Performance

### Typical Startup Times

- **First time:** 2-5 minutes (building images, downloading dependencies)
- **Subsequent starts:** 10-30 seconds (containers already built)
- **Debugger attach:** 1-2 seconds

### Improving Performance

**On macOS:**
```yaml
# In docker-compose_dev.yml, add to volumes:
volumes:
  - ../:/workspace:delegated  # Instead of :rw
```

**RAM Allocation:**
```
Docker Desktop → Settings → Resources
Increase RAM to 4GB+ for better performance
```

## 📚 Additional Resources

- **Docker Compose Docs:** https://docs.docker.com/compose/
- **VS Code Docker:** https://code.visualstudio.com/docs/containers/overview
- **Debugpy Docs:** https://github.com/microsoft/debugpy
- **Django in Docker:** https://docs.docker.com/samples/django/

## 🎓 Learning Resources

### New to Docker?

1. **Basics:** https://docker-curriculum.com/
2. **VS Code + Docker:** https://code.visualstudio.com/docs/remote/containers
3. **Docker Compose:** https://docs.docker.com/compose/gettingstarted/

### New to VS Code Debugging?

1. **Python Debugging:** https://code.visualstudio.com/docs/python/debugging
2. **Debugging Tips:** https://code.visualstudio.com/docs/editor/debugging

---

**Last Updated:** 2025-12-20 **Status:** ✅ Production Ready **Support:** Create an issue if you encounter problems


