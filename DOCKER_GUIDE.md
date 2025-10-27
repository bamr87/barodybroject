# Docker Setup Guide for Barodybroject

## Overview

This project uses a **unified Docker Compose configuration** that supports both development and production environments through Docker Compose profiles.

## Quick Start

### Development Mode (Default)

```bash
# Start development environment
docker-compose up

# Or in detached mode
docker-compose up -d

# View logs
docker-compose logs -f web-dev
```

Access the application at:
- **Django App**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **API**: http://localhost:8000/api

### Production Mode

```bash
# Start production environment
docker-compose --profile production up -d

# View logs
docker-compose logs -f web-prod
```

Access the application at:
- **Django App**: http://localhost:80

### With Jekyll Static Site

```bash
# Start development with Jekyll
docker-compose --profile jekyll up -d

# Or explicitly activate multiple profiles
docker-compose --profile dev --profile jekyll up -d
```

Access Jekyll at:
- **Jekyll Site**: http://localhost:4002

## Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Services                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │
│  │  web-dev     │   │  web-prod    │   │   jekyll     │   │
│  │  (default)   │   │ (production) │   │  (optional)  │   │
│  │ Port: 8000   │   │  Port: 80    │   │  Port: 4002  │   │
│  └──────┬───────┘   └──────┬───────┘   └──────────────┘   │
│         │                   │                               │
│         └───────────────────┴──────────────┐               │
│                                              │               │
│                                     ┌────────▼─────────┐    │
│                                     │    barodydb      │    │
│                                     │  PostgreSQL 15   │    │
│                                     │   Port: 5432     │    │
│                                     └──────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Available Services

| Service | Profile | Description | Ports |
|---------|---------|-------------|-------|
| `barodydb` | (always) | PostgreSQL database | 5432 |
| `web-dev` | `dev` (default) | Django development server | 8000, 5678 |
| `web-prod` | `production` | Django production (Gunicorn) | 80 |
| `jekyll` | `jekyll` | Static site generator | 4002 |

## Common Commands

### Starting Services

```bash
# Development (default)
docker-compose up

# Production
docker-compose --profile production up

# Development with Jekyll
docker-compose --profile jekyll up

# All services
docker-compose --profile production --profile jekyll up
```

### Stopping Services

```bash
# Stop all running services
docker-compose down

# Stop and remove volumes (⚠️ deletes database data)
docker-compose down -v

# Stop specific profile
docker-compose --profile production down
```

### Rebuilding

```bash
# Rebuild development image
docker-compose build web-dev

# Rebuild production image
docker-compose --profile production build web-prod

# Force rebuild and recreate
docker-compose up --build --force-recreate
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web-dev
docker-compose logs -f barodydb

# Last 100 lines
docker-compose logs --tail=100 web-dev
```

## Django Management Commands

### Running Migrations

```bash
# Development
docker-compose exec web-dev python manage.py migrate

# Production
docker-compose --profile production exec web-prod python manage.py migrate
```

### Creating a Superuser

```bash
# Development
docker-compose exec web-dev python manage.py createsuperuser

# Production
docker-compose --profile production exec web-prod python manage.py createsuperuser
```

### Collecting Static Files

```bash
# Development
docker-compose exec web-dev python manage.py collectstatic --noinput

# Production
docker-compose --profile production exec web-prod python manage.py collectstatic --noinput
```

### Running Tests

```bash
# Development
docker-compose exec web-dev python -m pytest

# With coverage
docker-compose exec web-dev python -m pytest --cov=parodynews
```

### Django Shell

```bash
# Development
docker-compose exec web-dev python manage.py shell

# Production
docker-compose --profile production exec web-prod python manage.py shell
```

### Custom Management Commands

```bash
# Example: Run a custom management command
docker-compose exec web-dev python manage.py your_custom_command
```

## Database Operations

### Accessing PostgreSQL

```bash
# Connect to PostgreSQL
docker-compose exec barodydb psql -U postgres -d barodydb

# Dump database
docker-compose exec barodydb pg_dump -U postgres barodydb > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T barodydb psql -U postgres -d barodydb
```

### Database Backups

```bash
# Create timestamped backup
docker-compose exec barodydb pg_dump -U postgres barodydb > "backup-$(date +%Y%m%d-%H%M%S).sql"

# Restore from backup
cat backup-20250101-120000.sql | docker-compose exec -T barodydb psql -U postgres -d barodydb
```

## Environment Configuration

### Using .env File

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your configuration:
```bash
nano .env
```

3. Environment variables are automatically loaded by Docker Compose

### Environment Variables

Key variables you may want to customize:

```bash
# Application
DEBUG=True
SECRET_KEY=your-secret-key

# Database
DB_PASSWORD=postgres
POSTGRES_PASSWORD=postgres

# Ports
DJANGO_DEV_PORT=8000
DJANGO_PROD_PORT=80
JEKYLL_PORT=4002

# OpenAI
OPENAI_API_KEY=sk-...
```

## Troubleshooting

### Container Won't Start

```bash
# Check container status
docker-compose ps

# View detailed logs
docker-compose logs web-dev

# Check database health
docker-compose exec barodydb pg_isready -U postgres
```

### Port Conflicts

If ports are already in use, update `.env`:

```bash
DJANGO_DEV_PORT=8001  # Change from 8000
POSTGRES_PORT=5433     # Change from 5432
JEKYLL_PORT=4003       # Change from 4002
```

### Database Connection Issues

```bash
# Restart database
docker-compose restart barodydb

# Check database logs
docker-compose logs barodydb

# Verify connection from web container
docker-compose exec web-dev pg_isready -h barodydb -U postgres
```

### Clean Slate Restart

```bash
# Stop everything
docker-compose down

# Remove volumes (⚠️ deletes data)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Start fresh
docker-compose up --build
```

### Permission Issues

```bash
# If you encounter permission errors with volumes
sudo chown -R $USER:$USER ./src

# On Linux, you may need to set the user in docker-compose.yml
# Add under web-dev service:
user: "${UID}:${GID}"
```

## VS Code Integration

### Recommended Tasks

The project includes pre-configured VS Code tasks:

- **Docker: Compose Up (Detached)**
- **Docker: Compose Stop**
- **Docker: Compose Down**
- **Docker: Rebuild (Force)**
- **Test: Run Django Tests**

Access via: `Cmd+Shift+P` → "Tasks: Run Task"

### Debugging

The development container exposes port 5678 for debugpy. Add this to `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Django Docker",
      "type": "python",
      "request": "attach",
      "connect": {
        "host": "localhost",
        "port": 5678
      },
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}/src",
          "remoteRoot": "/app"
        }
      ]
    }
  ]
}
```

## Development Workflow

### Typical Development Session

```bash
# 1. Start services
docker-compose up -d

# 2. Check logs
docker-compose logs -f web-dev

# 3. Apply migrations if needed
docker-compose exec web-dev python manage.py migrate

# 4. Make code changes (auto-reloads)

# 5. Run tests
docker-compose exec web-dev python -m pytest

# 6. Commit changes
git add .
git commit -m "Your changes"

# 7. Stop services when done
docker-compose down
```

### Hot Reload

The development setup uses volume mounts, so code changes are immediately reflected without rebuilding:

```bash
# Just edit files in ./src/
# Django auto-reloads on file changes
```

## Production Deployment

### Building for Production

```bash
# Build production image
docker-compose --profile production build web-prod

# Test production build locally
docker-compose --profile production up

# Push to registry (if using Azure/AWS)
docker tag barodybroject-web-prod:latest yourregistry/barodybroject:latest
docker push yourregistry/barodybroject:latest
```

### Azure Container Apps Deployment

```bash
# Deploy using Azure Developer CLI
azd up

# Or deploy only the app
azd deploy
```

## Performance Optimization

### Development

- Use `.dockerignore` to exclude unnecessary files
- Volume mounts for fast iteration
- Multi-stage builds for smaller images

### Production

- Gunicorn for production server
- Static file serving optimization
- Database connection pooling
- Proper SECRET_KEY and DEBUG settings

## Security Best Practices

- ✅ Never commit `.env` file
- ✅ Use strong SECRET_KEY in production
- ✅ Set DEBUG=False in production
- ✅ Use environment variables for secrets
- ✅ Regularly update base images
- ✅ Run containers as non-root user (production)
- ✅ Use Docker secrets for sensitive data

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)

---

**Need Help?** Open an issue on [GitHub](https://github.com/bamr87/barodybroject/issues)
