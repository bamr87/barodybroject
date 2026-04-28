# Launch.json Update Summary

## Overview

Comprehensive update to `.vscode/launch.json` to provide better debugging capabilities, organization, and developer experience.

## Key Changes

### 1. ✅ Renamed Browser Configurations

**Before:**
```json
{
  "name": "🐳 Debug Django App (Development)",
  "type": "msedge",
  ...
}
```

**After:**
```json
{
  "name": "🌐 Open Django App (Dev - Port 8000)",
  "type": "msedge",
  ...
}
```

**Reason:** These configurations open a browser, not debug Python code. Clearer naming prevents confusion.

### 2. ✅ Enhanced Local Development Configurations

**Added:**
- `🐍 Django: Run Server (Local)` - With auto-reload
- `🐍 Django: Run Server (Local - No Reload)` - For debugging with breakpoints

**Improvements:**
- Fixed environment variables to include proper database settings
- Added `PYTHONPATH` for module resolution
- Changed working directory to `${workspaceFolder}/src`
- Added proper presentation groups

**Before:**
```json
{
  "env": {
    "DJANGO_SETTINGS_MODULE": "barodybroject.settings.development",
    "DEBUG": "True",
    "RUNNING_IN_PRODUCTION": "False",
    "DB_CHOICE": "sqlite"  // ❌ SQLite not supported
  }
}
```

**After:**
```json
{
  "env": {
    "DJANGO_SETTINGS_MODULE": "barodybroject.settings.development",
    "DEBUG": "True",
    "RUNNING_IN_PRODUCTION": "False",
    "DB_HOST": "localhost",
    "DB_NAME": "barodydb",
    "DB_USERNAME": "postgres",
    "DB_PASSWORD": "postgres",
    "PYTHONPATH": "${workspaceFolder}/src"
  },
  "cwd": "${workspaceFolder}/src"
}
```

### 3. ✅ Comprehensive Testing Configurations

**Added 5 new test configurations:**

1. **Django: Run All Tests (Local)** - Full Django test suite
2. **Django: Test Current File** - Test only the open file
3. **Django: Test Parodynews App** - Test specific app
4. **Pytest: Run All Tests** - Full pytest suite
5. **Pytest: Current File** - Pytest current file

**Benefits:**
- Debug test failures with breakpoints
- Quickly run tests for specific files/apps
- Support both Django and pytest testing frameworks

### 4. ✅ Django Management Command Debugging

**Added 6 management command configurations:**

1. **Django: Make Migrations** - Debug migration creation
2. **Django: Run Migrations** - Debug migration application
3. **Django: Shell** - Interactive debugging
4. **Django: Shell Plus** - Enhanced shell debugging
5. **Django: Collect Static** - Debug static file collection
6. **Django: Check Deployment** - Debug deployment checks

**Use Case:**
```python
# Set breakpoint in your model
class Article(models.Model):
    def save(self, *args, **kwargs):
        # Breakpoint here
        super().save(*args, **kwargs)

# Run "Django: Make Migrations" debug configuration
# Debugger stops at breakpoint during migration creation
```

### 5. ✅ Added Presentation Groups

All configurations now organized into logical groups:

| Group | Purpose | Configurations |
|-------|---------|----------------|
| `0_compounds` | Multi-service debugging | Compound configs |
| `1_docker_web` | Docker browser launches | Web app opens |
| `2_local_django` | Local Django servers | Development servers |
| `3_docs` | Documentation | Sphinx docs |
| `4_testing` | Testing | Django/Pytest tests |
| `5_management` | Management commands | Django commands |
| `6_python` | General Python | Script debugging |

**Visual Benefit:**

```
VS Code Debug Menu:
├── 🚀 Full Stack (Local Django + Browser)    [0_compounds]
├── 🌐 Open Django App (Dev - Port 8000)      [1_docker_web]
├── 🌐 Open Django App (Prod - Port 80)       [1_docker_web]
├── 🐍 Django: Run Server (Local)             [2_local_django]
├── 🧪 Django: Run All Tests (Local)          [4_testing]
├── 🧪 Django: Test Current File              [4_testing]
├── 🔧 Django: Make Migrations                [5_management]
└── 🐍 Python: Current File                   [6_python]
```

### 6. ✅ Added Compound Configuration

**New:**
```json
{
  "name": "🚀 Full Stack (Local Django + Browser)",
  "configurations": [
    "🐍 Django: Run Server (Local)",
    "🌐 Open Django App (Dev - Port 8000)"
  ]
}
```

**Benefit:** Start Django server and browser with one click.

### 7. ✅ Improved Environment Consistency

All local configurations now use consistent environment variables:

```json
{
  "DJANGO_SETTINGS_MODULE": "barodybroject.settings.development",
  "DEBUG": "True",
  "RUNNING_IN_PRODUCTION": "False",
  "DB_HOST": "localhost",
  "DB_NAME": "barodydb",
  "DB_USERNAME": "postgres",
  "DB_PASSWORD": "postgres",
  "PYTHONPATH": "${workspaceFolder}/src"
}
```

### 8. ✅ Better Port Management

Clear port separation:

| Port | Purpose | Config Type |
|------|---------|-------------|
| 8000 | Docker Dev | Docker containers |
| 8001 | Local Dev | Local Python |
| 80 | Docker Prod | Production containers |
| 5432 | PostgreSQL | All environments |
| 8080 | Docs | Documentation |

### 9. ✅ Documentation Improvements

Added comprehensive documentation:

- `README.md` - Full guide with troubleshooting
- `LAUNCH_UPDATES.md` - This file
- Inline comments in `launch.json`

## Removed Configurations

### ❌ Docker Python Attach Configurations

**Removed:**
- `🐍 Python/Django in Docker (Development)`
- `🧪 Python Tests in Docker (Development)`

**Reason:** 
- These configurations attempted to attach to debugpy on port 5678
- The docker-compose configuration doesn't start debugpy server
- Local development provides better debugging experience
- If needed in future, docker-compose needs updating first

**Migration Path:**
Use local development configurations instead:
- `🐍 Django: Run Server (Local)` → Better than Docker attach
- `🧪 Django: Run All Tests (Local)` → Better than Docker tests

## Breaking Changes

### ⚠️ SQLite No Longer Supported

**Old configuration:**
```json
{
  "env": {
    "DB_CHOICE": "sqlite"
  }
}
```

**Issue:** Your `settings.py` explicitly raises an error for SQLite:

```python
if DB_CHOICE == "sqlite":
    raise ImproperlyConfigured(
        "SQLite is not supported in this project. Configure PostgreSQL..."
    )
```

**Solution:** All configurations now use PostgreSQL by default.

### ⚠️ Port Change for Local Development

- **Old:** Port 8001 (but config said sqlite so probably didn't work)
- **New:** Port 8001 with proper PostgreSQL configuration

## Usage Examples

### Example 1: Debug a View

```python
# parodynews/views/article.py
def article_detail(request, pk):
    # Set breakpoint here
    article = Article.objects.get(pk=pk)
    return render(request, 'article.html', {'article': article})
```

**Steps:**
1. Click gutter to set breakpoint
2. Press F5 → Select `🐍 Django: Run Server (Local)`
3. Open http://localhost:8001/articles/1/
4. Debugger pauses at breakpoint
5. Inspect variables, step through code

### Example 2: Debug a Test

```python
# parodynews/tests/test_models.py
class ArticleModelTest(TestCase):
    def test_article_creation(self):
        # Set breakpoint here
        article = Article.objects.create(title="Test")
        self.assertEqual(article.title, "Test")
```

**Steps:**
1. Open test file
2. Set breakpoint in test
3. Press F5 → Select `🧪 Django: Test Current File`
4. Debugger pauses at breakpoint

### Example 3: Debug a Migration

```python
# parodynews/migrations/0001_initial.py
def forwards(apps, schema_editor):
    Article = apps.get_model('parodynews', 'Article')
    # Set breakpoint here
    for article in Article.objects.all():
        article.slug = slugify(article.title)
        article.save()
```

**Steps:**
1. Set breakpoint in migration
2. Press F5 → Select `🔧 Django: Run Migrations`
3. Debugger pauses at breakpoint

## Configuration Philosophy

### Why Local Development First?

1. **Faster Iteration:**
   - No container rebuild/restart
   - Immediate code changes
   - Quick debugging cycles

2. **Better Debugging:**
   - Direct debugger attachment
   - Breakpoints work reliably
   - Full variable inspection

3. **Easier Troubleshooting:**
   - See all logs in real-time
   - No Docker layer complexity
   - Direct file access

4. **Resource Efficient:**
   - Less memory usage
   - Faster startup
   - No Docker overhead

### When to Use Docker?

- **Integration Testing:** Test multi-service interactions
- **Production Verification:** Verify containerized setup
- **Environment Parity:** Match production closely
- **Team Consistency:** Ensure same environment

## Recommendations

### For Daily Development

```
1. Start PostgreSQL in Docker:
   docker-compose up barodydb -d

2. Use local Django:
   F5 → 🐍 Django: Run Server (Local)

3. Debug with breakpoints
4. Run tests locally
```

### For Production Testing

```
1. Start full Docker stack:
   F5 → 🌐 Open Django App (Prod - Port 80)

2. Verify production settings
3. Test deployment configuration
```

### For Testing

```
Single test:
F5 → 🧪 Django: Test Current File

Full suite:
F5 → 🧪 Django: Run All Tests (Local)
```

## Migration Guide

### If you were using:

**"🐳 Debug Django App (Development)"**
→ Use: `🌐 Open Django App (Dev - Port 8000)` (same functionality, clearer name)

**"🐍 Python/Django in Docker (Development)"**
→ Use: `🐍 Django: Run Server (Local)` (better debugging, same functionality)

**"🧪 Python Tests in Docker (Development)"**
→ Use: `🧪 Django: Run All Tests (Local)` (faster, better debugging)

**Local SQLite setup**
→ Start PostgreSQL: `docker-compose up barodydb -d`
→ Then use any local configuration

## Future Enhancements

Potential additions for future updates:

1. **Docker Debugpy Support:**
   - Update docker-compose to start debugpy
   - Add attach configurations back

2. **More Compound Configs:**
   - Django + Docs + Jekyll
   - Full production stack

3. **Remote Debugging:**
   - SSH debugging configurations
   - Remote container attach

4. **Coverage Integration:**
   - Debug with coverage
   - Visual coverage reports

5. **Profile Debugging:**
   - Performance profiling configs
   - Memory profiling configs

## Validation

All configurations have been validated for:

- ✅ Correct JSON syntax (no linter errors)
- ✅ Valid debugpy configuration
- ✅ Proper environment variables
- ✅ Correct working directories
- ✅ Appropriate port assignments
- ✅ Task dependencies exist in tasks.json
- ✅ Consistent naming conventions
- ✅ Proper presentation grouping

## Questions?

If you have questions about:

- **How to use a configuration:** Check `.vscode/README.md`
- **Why something changed:** Check this document
- **Troubleshooting:** Check `.vscode/README.md` → Troubleshooting section
- **Adding new configs:** Follow the patterns established here

---

**Updated:** 2025-12-20
**Author:** AI Assistant via Cursor
**Review Status:** ✅ Complete


