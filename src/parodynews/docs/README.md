# Parodynews Documentation

Comprehensive Sphinx documentation for the Parodynews Django application.

## Quick Start

### 🐳 Docker Deployment (Recommended)

**Development Mode** (with live reload):
```bash
# Start documentation server with auto-rebuild
docker-compose -f .devcontainer/docker-compose_dev.yml up docs

# Access at http://localhost:8080
# Changes auto-rebuild and reload in browser
```

**Production Mode** (static build):
```bash
# Build and serve static documentation with nginx
docker-compose up -d docs

# Access at http://localhost:8080
```

📖 **See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive container deployment guide**

### 📦 Manual Build (Without Docker)

Build documentation locally in development container:

```bash
# In development container
docker-compose -f .devcontainer/docker-compose_dev.yml exec python bash
cd /workspace/src/parodynews/docs
pip install -r requirements.txt
make clean && make html
```

Documentation will be in `build/html/index.html`

## Documentation Structure

- **getting-started/** - Installation and quickstart guides
- **user-guide/** - User documentation
- **developer-guide/** - Developer documentation  
- **api-reference/** - Auto-generated API docs
- **integrations/** - External service integration guides
- **tutorials/** - Step-by-step tutorials
- **how-to/** - Task-oriented guides
- **reference/** - Technical reference

## Implementation Status

✅ **Phase 1 Complete**: Foundation and structure implemented
- 60+ documentation files created
- Enhanced Sphinx configuration
- Auto-documentation working
- Successfully builds

See `IMPLEMENTATION_SUMMARY.md` for details.

## Building

```bash
make html       # Build HTML
make clean      # Clean build
make linkcheck  # Check links
make doctest    # Test examples
```

## Resources

- [SPHINX_REDESIGN_PLAN.md](SPHINX_REDESIGN_PLAN.md) - Complete redesign plan
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Implementation status
- [Sphinx Documentation](https://www.sphinx-doc.org/)
