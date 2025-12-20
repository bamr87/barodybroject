# 🚀 Quick Start - Docker Debugging

## ✅ Status: Ready to Debug!

Your Docker container is now running with debugpy waiting for VS Code to attach.

```
✅ PostgreSQL: Running on port 5432
✅ Django: Waiting for debugger on port 5678
✅ Web Server: Ready on port 8000
```

## 🎯 Test the Debugger Now

### Step 1: Attach Debugger (30 seconds)

1. Open VS Code
2. Press `F5`
3. Select: **`🐳 Django: Docker Debug`**
4. Wait 2-3 seconds for "Debugger attached" message

✅ **Success:** You'll see "Remote (debugpy)" in the CALL STACK panel

### Step 2: Open Browser (10 seconds)

1. Open browser: http://localhost:8000
2. Django app should load

✅ **Success:** You see the Django application

### Step 3: Set & Test Breakpoint (1 minute)

1. In VS Code, open: `src/parodynews/urls.py`
2. Find any URL pattern function
3. Click in the gutter (left of line numbers) → Red dot appears
4. Refresh browser
5. **Debugger should pause!**

✅ **Success:** VS Code pauses, variables visible in panel

## 🎨 Quick Reference

### Available Debug Configurations

Press `F5` and select:

| Configuration | What It Does |
|--------------|-------------|
| **🐳 Django: Docker Debug** | Attach debugger to Django in Docker |
| **🚀 Full Stack: Docker Django + Browser** | Attach debugger + open browser |
| **🌐 Open Django App** | Just open browser (no debugging) |
| **🌐 Open Django Admin** | Open admin interface |
| **💻 Django: Local** | Run Django locally (fallback) |

### Essential Commands

```bash
# View logs
docker logs -f devcontainer-python-1

# Restart Django (to see code changes)
docker-compose -f .devcontainer/docker-compose_dev.yml restart python

# Run Django command
docker-compose -f .devcontainer/docker-compose_dev.yml exec python python manage.py [command]

# Examples:
docker-compose -f .devcontainer/docker-compose_dev.yml exec python python manage.py createsuperuser
docker-compose -f .devcontainer/docker-compose_dev.yml exec python python manage.py migrate
docker-compose -f .devcontainer/docker-compose_dev.yml exec python python manage.py shell
```

### VS Code Tasks

`Cmd+Shift+P` → `Tasks: Run Task` → Select:

- `📊 Django: Run Migrations (Dev)`
- `👤 Django: Create Superuser (Dev)`
- `🐚 Django: Shell (Dev)`
- `📋 Docker: View Dev Logs`
- `⛔ Docker: Stop Development`

## 🐛 Debugging Tips

### Setting Breakpoints

1. **Click in gutter** (left of line numbers) → Red dot
2. **Conditional:** Right-click dot → "Edit Breakpoint" → Add condition
3. **Logpoint:** Right-click → "Add Logpoint" (doesn't stop, just logs)

### When Debugger Pauses

- **F10** - Step Over (execute line, don't go into functions)
- **F11** - Step Into (go into function calls)
- **Shift+F11** - Step Out (exit current function)
- **F5** - Continue (run until next breakpoint)

### Inspect Variables

- **Variables Panel** - See all local variables
- **Watch** - Add expressions to monitor
- **Debug Console** - Type Python code to execute

### Common Debug Scenarios

**Debug a view:**
```python
# src/parodynews/views/article.py
def article_detail(request, pk):
    # Set breakpoint here ←
    article = Article.objects.get(pk=pk)
    return render(request, 'article.html', {'article': article})
```

**Debug a model method:**
```python
# src/parodynews/models/post.py
class Post(models.Model):
    def save(self, *args, **kwargs):
        # Set breakpoint here ←
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
```

**Debug a test:**
```python
# src/parodynews/tests/test_models.py
def test_post_creation(self):
    # Set breakpoint here ←
    post = Post.objects.create(title="Test")
    self.assertEqual(post.title, "Test")
```

## 📝 Daily Workflow

### Morning

```bash
# Check containers (they might still be running from yesterday)
docker ps

# If not running:
docker-compose -f .devcontainer/docker-compose_dev.yml up -d

# In VS Code: F5 → 🐳 Django: Docker Debug
```

### During Development

1. Edit code
2. Set breakpoints
3. Visit http://localhost:8000
4. Debug!

**Note:** Code changes require container restart:
```bash
docker-compose -f .devcontainer/docker-compose_dev.yml restart python
# Then reattach debugger (F5)
```

### Evening

```bash
# Optional: Stop containers (or leave running for tomorrow)
docker-compose -f .devcontainer/docker-compose_dev.yml down
```

## ❌ Troubleshooting

### "Cannot connect to debugpy"

**Check:**
```bash
docker logs devcontainer-python-1 | tail -20
```

**Should see:**
```
Starting Django with debugpy on port 5678...
Waiting for VS Code debugger to attach...
```

**Fix:**
```bash
docker-compose -f .devcontainer/docker-compose_dev.yml restart python
# Wait 30 seconds
# Try F5 again
```

### Breakpoint Not Working

1. **Is debugger attached?** Check CALL STACK panel in VS Code
2. **Is breakpoint solid red?** Hollow means it's not bound
3. **Did code execute?** Breakpoint only triggers if code runs

### Code Changes Not Showing

**Reason:** Running with `--noreload` for debugging

**Solution:**
```bash
docker-compose -f .devcontainer/docker-compose_dev.yml restart python
# Then F5 to reattach
```

### Port Already in Use

```bash
# Check what's using the port
lsof -i :8000
lsof -i :5678

# Stop containers
docker-compose -f .devcontainer/docker-compose_dev.yml down

# Start fresh
docker-compose -f .devcontainer/docker-compose_dev.yml up -d
```

## 📚 Next Steps

1. **Create a superuser:**
   ```bash
   docker-compose -f .devcontainer/docker-compose_dev.yml exec python python manage.py createsuperuser
   ```

2. **Visit admin:** http://localhost:8000/admin

3. **Read full docs:** `.vscode/DOCKER_WORKFLOW.md`

4. **Explore code:** Start in `src/parodynews/`

5. **Run tests:**
   ```bash
   docker-compose -f .devcontainer/docker-compose_dev.yml exec python python manage.py test
   ```

## 🎓 Learn More

- **Full Docker Workflow:** [DOCKER_WORKFLOW.md](DOCKER_WORKFLOW.md)
- **Complete Setup Guide:** [SETUP_COMPLETE.md](SETUP_COMPLETE.md)
- **All Configurations:** [README.md](README.md)
- **Testing Guide:** [TESTING_GUIDE.md](TESTING_GUIDE.md)

---

## ✨ Summary

✅ Docker containers running  
✅ Debugpy waiting for VS Code  
✅ PostgreSQL accessible  
✅ Ready to debug!  

**Next:** Press `F5` → Select `🐳 Django: Docker Debug` → Start coding! 🚀

---

**Last Updated:** 2025-12-20
**Status:** ✅ Ready for Development

