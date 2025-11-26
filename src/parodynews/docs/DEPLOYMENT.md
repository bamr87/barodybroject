# Sphinx Documentation Deployment

This directory contains the infrastructure for building and deploying the parodynews Sphinx documentation as a containerized service.

## 🚀 Quick Start

### Development Mode (Live Reload)

Start the documentation server with auto-rebuild on changes:

```bash
# Start the docs service (development mode)
docker-compose -f .devcontainer/docker-compose_dev.yml up docs

# Access documentation at http://localhost:8080
```

The development docs service uses `sphinx-autobuild` which automatically:
- Watches for file changes in the `source/` directory
- Rebuilds documentation when changes are detected
- Live-reloads the browser automatically

### Production Mode (Static Build)

Build and deploy the documentation as a static site with nginx:

```bash
# Build and start the docs service (production mode)
docker-compose up -d docs

# Access documentation at http://localhost:8080
```

Production docs are:
- Built once during image creation
- Served as static HTML files via nginx
- Optimized with gzip compression and caching
- Includes health checks for monitoring

## 📦 Container Architecture

### Development Container

**Base Image**: `python:3.11-slim`

**Features**:
- Live reload with `sphinx-autobuild`
- Volume-mounted source code for instant updates
- Full Django environment for autodoc
- Exposed on port 8080 (configurable via `DOCS_PORT`)

**Command**:
```bash
sphinx-autobuild --host 0.0.0.0 --port 8000 source build/html
```

### Production Container (Multi-Stage Build)

**Stage 1 - Builder** (`python:3.11-slim`):
- Installs Django and all dependencies
- Installs Sphinx and documentation requirements
- Builds static HTML documentation
- Outputs to `/build/parodynews/docs/build/html`

**Stage 2 - Runtime** (`nginx:alpine`):
- Copies built HTML from builder stage
- Serves static files via nginx
- Optimized for performance and security
- Minimal image size (~20MB final image)

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCS_PORT` | `8080` | Port to expose documentation on host |
| `DJANGO_SETTINGS_MODULE` | `barodybroject.settings` | Django settings for autodoc |

### Nginx Configuration

Custom nginx config at `nginx.conf` provides:
- Gzip compression for faster loading
- Security headers (X-Frame-Options, X-Content-Type-Options, X-XSS-Protection)
- Static asset caching (1 year for images, fonts, etc.)
- Custom error pages
- Access and error logging

### Port Configuration

Change the documentation port by setting the environment variable:

```bash
# Use port 9000 instead of 8080
export DOCS_PORT=9000
docker-compose up -d docs
```

Or add to `.env` file:
```env
DOCS_PORT=9000
```

## 📝 Building Documentation Manually

### Inside Docker Container (Development)

```bash
# Enter the development container
docker-compose -f .devcontainer/docker-compose_dev.yml exec docs bash

# Clean and rebuild
make clean
make html

# Output is in build/html/
```

### Inside Docker Container (Python Service)

```bash
# Enter the python development container
docker-compose -f .devcontainer/docker-compose_dev.yml exec python bash

# Navigate to docs directory
cd parodynews/docs

# Install requirements (if not already installed)
pip install -r requirements.txt

# Build documentation
make clean
make html

# Output is in build/html/
```

### Build Production Image

```bash
# Build the documentation Docker image
docker-compose build docs

# Run the container
docker-compose up -d docs

# View logs
docker-compose logs -f docs
```

## 🔍 Accessing Documentation

Once the container is running:

- **Local URL**: http://localhost:8080
- **Container URL**: http://barody-docs (from within Docker network)
- **Health Check**: http://localhost:8080/ (returns 200 OK)

## 📊 Container Management

### Start/Stop Services

```bash
# Start documentation service only
docker-compose up -d docs

# Stop documentation service
docker-compose stop docs

# Restart after code changes (production)
docker-compose restart docs

# Rebuild from scratch
docker-compose up -d --build docs
```

### View Logs

```bash
# Follow documentation server logs
docker-compose logs -f docs

# View last 50 lines
docker-compose logs --tail=50 docs
```

### Health Checks

Production container includes health checks:

```bash
# Check container health
docker ps --filter name=barody-docs

# Manually test health endpoint
curl http://localhost:8080/
```

Health check configuration:
- **Interval**: 30 seconds
- **Timeout**: 3 seconds
- **Retries**: 3
- **Start Period**: 5 seconds

## 🛠️ Troubleshooting

### Documentation Not Building

**Issue**: Import errors during autodoc

**Solution**: Ensure Django settings are properly configured:
```bash
# Check if Django can be imported
docker-compose exec docs python -c "import django; django.setup()"
```

### Port Already in Use

**Issue**: Port 8080 is already allocated

**Solution**: Change the port:
```bash
DOCS_PORT=9000 docker-compose up -d docs
```

### Changes Not Appearing (Development)

**Issue**: Documentation not updating despite file changes

**Solution**: Check sphinx-autobuild is running:
```bash
docker-compose logs docs | grep "Serving on"
```

Restart the service:
```bash
docker-compose restart docs
```

### Nginx 404 Errors (Production)

**Issue**: Pages not found after building

**Solution**: Verify HTML was built correctly:
```bash
docker-compose exec docs ls -la /usr/share/nginx/html/
```

Rebuild if necessary:
```bash
docker-compose up -d --build docs
```

## 📁 File Structure

```
parodynews/docs/
├── Dockerfile              # Multi-stage build for production
├── nginx.conf              # Nginx configuration for serving docs
├── requirements.txt        # Sphinx and extension dependencies
├── Makefile               # Build automation
├── make.bat               # Windows build script
├── README.md              # Documentation deployment guide (this file)
├── source/                # Documentation source files
│   ├── conf.py           # Sphinx configuration
│   ├── index.rst         # Documentation home page
│   ├── _static/          # Custom CSS, JS, images
│   └── ...               # Content directories
└── build/                 # Generated HTML (gitignored)
    └── html/             # Built documentation
```

## 🔐 Security Considerations

### Production Deployment

- Nginx runs as non-root user
- Security headers enabled (XSS, clickjacking protection)
- No sensitive data in documentation
- Health checks for monitoring
- Minimal attack surface (static files only)

### Development Deployment

- Live reload exposes source directory
- Should only be used in trusted environments
- Not suitable for public internet exposure

## 📚 Related Documentation

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [Sphinx AutoBuild](https://github.com/executablebooks/sphinx-autobuild)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)

## 🎯 Next Steps

1. **Enhance Content**: Complete Phase 2-6 of documentation plan (views, forms, tutorials, etc.)
2. **CI/CD Integration**: Automate documentation builds in GitHub Actions
3. **Versioning**: Add documentation versioning for releases
4. **Search**: Ensure search functionality works correctly
5. **PDF Export**: Add PDF generation capability

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-25  
**Maintainer**: Barodybroject Team
