# Testing Guide for VS Code Launch Configurations

## 🚨 Prerequisites - PostgreSQL Setup

### Issue: Multiple PostgreSQL Instances

You have two PostgreSQL instances running on port 5432:
- **Local PostgreSQL** (homebrew/system) - listening on `localhost:5432`
- **Docker PostgreSQL** - also on `0.0.0.0:5432`

Django connects to the local one by default, which doesn't have the "postgres" role configured.

### Solution Options

#### Option 1: Stop Local PostgreSQL (Recommended for Testing)

```bash
# Check if it's a homebrew service
brew services list | grep postgres

# If found, stop it
brew services stop postgresql@15  # or postgresql@14, @16, etc.

# Or stop manually
pg_ctl -D /opt/homebrew/var/postgres stop
```

#### Option 2: Create postgres Role in Local PostgreSQL

```bash
# Connect to your local PostgreSQL
psql postgres

# Create the postgres role
CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD 'postgres';

# Create the database
CREATE DATABASE barodydb OWNER postgres;

# Exit
\q
```

#### Option 3: Use Docker PostgreSQL with Different Host

Change launch.json configurations to use `127.0.0.1` instead of `localhost`:
```json
"DB_HOST": "127.0.0.1"  // Forces IPv4, may route to Docker
```

## 📋 Test Plan

### Phase 1: Verify PostgreSQL Connection

**Test 1: Docker PostgreSQL**
```bash
# Should work - connects to Docker PostgreSQL
docker exec devcontainer-barodydb-1 psql -U postgres -c "SELECT version();"
```

**Test 2: Local Connection**
```bash
# After fixing PostgreSQL, this should work
cd /Users/bamr87/github/barodybroject/src
source ../.venv/bin/activate
python manage.py check --database default
```

### Phase 2: Test VS Code Tasks

#### 2.1 Docker Tasks

**Test: Start Development Containers**
1. Open Command Palette: `Cmd+Shift+P`
2. Type: `Tasks: Run Task`
3. Select: `🐍 Docker: Development Up`
4. **Expected:** Containers start successfully

**Test: View Development Logs**
1. Run Task: `📋 Docker: View Dev Logs`
2. **Expected:** See logs streaming from Python container

**Test: Check Container Status**
1. Run Task: `🔍 Docker: Container Status (Dev)`
2. **Expected:** See running containers with "Up" status

**Test: Stop Development**
1. Run Task: `⛔ Docker: Stop Development`
2. **Expected:** Containers stop gracefully

#### 2.2 Django Management Tasks

**Test: Run Migrations (Dev)**
1. Ensure dev containers are running
2. Run Task: `📊 Django: Run Migrations (Dev)`
3. **Expected:** Migrations apply successfully

**Test: Django Shell (Dev)**
1. Run Task: `🐚 Django: Shell (Dev)`
2. **Expected:** Interactive Django shell opens
3. Try: `from parodynews.models import *`
4. Exit: `exit()`

### Phase 3: Test Launch Configurations

#### 3.1 Local Development Configurations

**Prerequisites:**
- PostgreSQL accessible (either local or Docker, see above)
- Virtual environment activated
- In correct directory: `/Users/bamr87/github/barodybroject/src`

**Test 1: Django Run Server (Local)**
1. Press `F5` or go to Run & Debug
2. Select: `🐍 Django: Run Server (Local)`
3. **Expected Results:**
   - ✅ Server starts on port 8001
   - ✅ No errors in Debug Console
   - ✅ Can open http://localhost:8001
   - ✅ Console shows: "Starting development server at http://0.0.0.0:8001/"

**Troubleshooting:**
```
Error: "role postgres does not exist"
→ Fix PostgreSQL setup (see above)

Error: "Port 8001 already in use"
→ Run: lsof -ti:8001 | xargs kill -9

Error: "No module named 'barodybroject'"
→ Check PYTHONPATH in launch.json includes src/
```

**Test 2: Set Breakpoint in View**
1. Open: `src/parodynews/views/__init__.py` (or any view file)
2. Set breakpoint (click gutter) on any line inside a view function
3. Start: `🐍 Django: Run Server (Local)`
4. Open browser: http://localhost:8001
5. **Expected:**
   - ✅ Debugger pauses at breakpoint
   - ✅ Variables panel shows local variables
   - ✅ Can step through code (F10, F11)
   - ✅ Can inspect request object

#### 3.2 Testing Configurations

**Test 3: Run All Tests**
1. Stop any running servers
2. Press `F5`
3. Select: `🧪 Django: Run All Tests (Local)`
4. **Expected:**
   - ✅ Tests start running
   - ✅ See test output in Debug Console
   - ✅ Exit code 0 if all pass

**Test 4: Test Current File with Breakpoint**
1. Open: `src/parodynews/tests/test_models.py` (or any test file)
2. Set breakpoint inside a test method
3. Select: `🧪 Django: Test Current File`
4. **Expected:**
   - ✅ Only that file's tests run
   - ✅ Debugger pauses at breakpoint
   - ✅ Can inspect test objects

**Test 5: Pytest Tests**
1. Select: `🧪 Pytest: Run All Tests`
2. **Expected:**
   - ✅ Pytest runs with colored output
   - ✅ Shows test collection
   - ✅ Summary at end

#### 3.3 Management Command Debugging

**Test 6: Debug Make Migrations**
1. Make a small model change (add a comment to a field)
2. Set breakpoint in model's `__str__` or `save` method
3. Select: `🔧 Django: Make Migrations`
4. **Expected:**
   - ✅ Can see migration being created
   - ✅ May hit breakpoint if migration inspects model

**Test 7: Django Shell**
1. Select: `🔧 Django: Shell`
2. In terminal, type Python commands:
```python
from django.contrib.auth.models import User
print(User.objects.count())
```
3. **Expected:**
   - ✅ Interactive shell works
   - ✅ Can import and use models
   - ✅ See output immediately

**Test 8: Check Deployment**
1. Select: `🔧 Django: Check Deployment`
2. **Expected:**
   - ✅ Shows security checklist
   - ✅ May show warnings (expected in dev)
   - ✅ Validates production settings

#### 3.4 Browser Configurations

**Test 9: Open Django App (Dev)**
1. Ensure Docker containers running
2. Select: `🌐 Open Django App (Dev - Port 8000)`
3. **Expected:**
   - ✅ Containers start (if not running)
   - ✅ Browser opens to http://localhost:8000
   - ✅ Application loads

**Test 10: Open Documentation**
1. Ensure docs container running
2. Select: `🌐 Open Documentation (Port 8080)`
3. **Expected:**
   - ✅ Browser opens to http://localhost:8080
   - ✅ Sphinx docs load

#### 3.5 Compound Configurations

**Test 11: Full Stack**
1. Stop all servers
2. Select: `🚀 Full Stack (Local Django + Browser)`
3. **Expected:**
   - ✅ Django server starts on 8001
   - ✅ Browser opens automatically
   - ✅ Both shown in debug panel
   - ✅ Can debug Python while app runs

### Phase 4: Advanced Testing

#### Test Presentation Groups

1. Open Run & Debug panel (`Cmd+Shift+D`)
2. Click configuration dropdown
3. **Expected:** Configurations grouped logically:
   - Compounds at top
   - Web configs together
   - Local Django together
   - Tests together
   - Management together

#### Test Auto-Reload vs No-Reload

**Test 12: Auto-Reload (Default)**
1. Start: `🐍 Django: Run Server (Local)`
2. Edit a Python file (add a comment)
3. Save
4. **Expected:**
   - ✅ See "Reloading..." in console
   - ✅ Server restarts automatically

**Test 13: No-Reload (For Breakpoints)**
1. Start: `🐍 Django: Run Server (Local - No Reload)`
2. Set breakpoint in view
3. Edit a Python file
4. **Expected:**
   - ✅ No auto-reload
   - ✅ Breakpoints work reliably
   - ✅ Must manually restart for code changes

## 🎯 Success Criteria Checklist

### Docker Tasks
- [ ] Can start development containers
- [ ] Can stop development containers
- [ ] Can view logs
- [ ] Can run migrations in container
- [ ] Can access Django shell in container

### Local Development
- [ ] Django server starts on port 8001
- [ ] Can set and hit breakpoints
- [ ] Can inspect variables in debugger
- [ ] Auto-reload works (with reload config)
- [ ] No-reload works (with no-reload config)

### Testing
- [ ] Can run all Django tests
- [ ] Can run single test file
- [ ] Can debug test with breakpoint
- [ ] Can run pytest tests
- [ ] Test output visible in console

### Management Commands
- [ ] Can debug makemigrations
- [ ] Can debug migrate
- [ ] Can use Django shell
- [ ] Can run collectstatic
- [ ] Can run deployment check

### Browser Integration
- [ ] Can open app in browser from debug menu
- [ ] Can open docs in browser
- [ ] Browser opens automatically

### Compound Configurations
- [ ] Full stack starts both services
- [ ] Can debug while browser open

## 🔧 Common Issues and Solutions

### Issue: "Port already in use"
```bash
# Find and kill process
lsof -ti:8001 | xargs kill -9
# Or for Docker
docker-compose down
```

### Issue: "Module not found"
**Check:**
1. Virtual environment activated
2. PYTHONPATH set correctly in launch.json
3. Working directory is `${workspaceFolder}/src`

**Fix:**
```json
"env": {
  "PYTHONPATH": "${workspaceFolder}/src"
},
"cwd": "${workspaceFolder}/src"
```

### Issue: Breakpoints not working
**Causes:**
1. Using auto-reload mode
2. Code in different process/thread
3. `justMyCode` set to true

**Solutions:**
1. Use "No Reload" configuration
2. Set `"justMyCode": false` (already done)
3. Avoid breakpoints in async/threaded code

### Issue: Database connection errors
**Check:**
1. PostgreSQL running: `docker ps | grep postgres`
2. Correct host in environment variables
3. postgres role exists: See PostgreSQL Setup above

### Issue: Docker containers won't start
```bash
# Clean up and restart
docker-compose down
docker system prune -f
docker-compose up -d
```

### Issue: Tests fail with database errors
**Cause:** Test database not created

**Fix:**
```bash
cd src
python manage.py migrate
# Django auto-creates test_barodydb for tests
```

## 📊 Test Results Template

After testing, document results:

```
## Test Results - [Date]

### Environment
- OS: macOS [version]
- Python: [version]
- Django: [version]
- Docker: [version]

### Tests Passed ✅
- [ List successful tests ]

### Tests Failed ❌
- [ List failed tests with error messages ]

### Issues Found
1. [Issue description]
   - Error: [error message]
   - Solution: [what fixed it]

### Performance Notes
- Server startup time: [seconds]
- Test suite duration: [seconds]
- Container startup time: [seconds]
```

## 🚀 Quick Start Testing Sequence

For first-time testing, follow this sequence:

```bash
# 1. Fix PostgreSQL (if needed)
brew services stop postgresql@15

# 2. Verify Docker PostgreSQL
docker ps | grep postgres

# 3. Test connection
docker exec devcontainer-barodydb-1 psql -U postgres -c "SELECT 1;"

# 4. In VS Code:
#    a. Press F5
#    b. Select: 🐍 Django: Run Server (Local)
#    c. Open http://localhost:8001

# 5. Test breakpoint:
#    a. Open any view file
#    b. Click gutter to set breakpoint
#    c. Refresh browser
#    d. Debugger should pause

# 6. Test a task:
#    a. Cmd+Shift+P → Tasks: Run Task
#    b. Select: 🔍 Docker: Container Status (Dev)

# 7. Run tests:
#    a. Press F5
#    b. Select: 🧪 Django: Run All Tests (Local)
```

## 📝 Notes

- All local configurations use port **8001** (Docker uses 8000)
- PostgreSQL must be accessible on **localhost:5432**
- Working directory for Django is always **${workspaceFolder}/src**
- PYTHONPATH must include **${workspaceFolder}/src**

---

**Last Updated:** 2025-12-20
**Status:** Ready for testing

