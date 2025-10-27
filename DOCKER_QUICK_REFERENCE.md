# Docker Quick Reference Card

## 🚀 Essential Commands

### Start Services
```bash
# Development (default)
docker-compose up -d

# Production
docker-compose --profile production up -d

# Development + Jekyll
docker-compose --profile jekyll up -d
```

### Stop Services
```bash
# Stop all
docker-compose down

# Stop and remove volumes (⚠️ deletes database!)
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web-dev
docker-compose logs -f barodydb
```

### Rebuild
```bash
# Rebuild and restart
docker-compose up --build

# Force rebuild
docker-compose build --no-cache web-dev
```

## 🐍 Django Commands

### Database Migrations
```bash
# Create migrations
docker-compose exec web-dev python manage.py makemigrations

# Apply migrations
docker-compose exec web-dev python manage.py migrate
```

### User Management
```bash
# Create superuser
docker-compose exec web-dev python manage.py createsuperuser
```

### Static Files
```bash
# Collect static files
docker-compose exec web-dev python manage.py collectstatic --noinput
```

### Django Shell
```bash
# Open Python shell
docker-compose exec web-dev python manage.py shell
```

### Run Tests
```bash
# All tests
docker-compose exec web-dev python -m pytest

# With coverage
docker-compose exec web-dev python -m pytest --cov=parodynews

# Specific test
docker-compose exec web-dev python -m pytest tests/test_models.py
```

## 💾 Database Operations

### Access PostgreSQL
```bash
# Connect to database
docker-compose exec barodydb psql -U postgres -d barodydb

# Check connection
docker-compose exec barodydb pg_isready -U postgres
```

### Backup & Restore
```bash
# Create backup
docker-compose exec barodydb pg_dump -U postgres barodydb > backup.sql

# Restore backup
cat backup.sql | docker-compose exec -T barodydb psql -U postgres -d barodydb
```

## 🔍 Troubleshooting

### Check Status
```bash
# Service status
docker-compose ps

# Container details
docker-compose ps -a

# Resource usage
docker stats
```

### Inspect Services
```bash
# View configuration
docker-compose config

# Validate configuration
docker-compose config -q
```

### Clean Up
```bash
# Remove stopped containers
docker-compose rm

# System cleanup
docker system prune -f

# Remove all (⚠️ nuclear option)
docker system prune -a --volumes
```

## 🌐 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Django Dev | http://localhost:8000 | Development server |
| Django Admin | http://localhost:8000/admin | Admin interface |
| Django API | http://localhost:8000/api | REST API |
| Jekyll | http://localhost:4002 | Static site |
| PostgreSQL | localhost:5432 | Database |

## 📝 Environment Variables

Edit `.env` to customize:

```bash
# Ports
DJANGO_DEV_PORT=8000
DJANGO_PROD_PORT=80
POSTGRES_PORT=5432

# Database
DB_PASSWORD=postgres

# Application
DEBUG=True
SECRET_KEY=your-secret-key
OPENAI_API_KEY=sk-...
```

## 🎯 Common Workflows

### New Feature Development
```bash
1. docker-compose up -d
2. docker-compose exec web-dev python manage.py makemigrations
3. docker-compose exec web-dev python manage.py migrate
4. # Make your code changes
5. docker-compose exec web-dev python -m pytest
6. docker-compose down
```

### Production Testing
```bash
1. docker-compose --profile production up --build
2. # Test your application
3. docker-compose --profile production down
```

### Fresh Start
```bash
1. docker-compose down -v
2. docker-compose up --build
3. docker-compose exec web-dev python manage.py migrate
4. docker-compose exec web-dev python manage.py createsuperuser
```

## 🆘 Quick Fixes

### Port Already in Use
```bash
# Change port in .env
DJANGO_DEV_PORT=8001

# Restart
docker-compose down
docker-compose up -d
```

### Database Won't Start
```bash
# Check logs
docker-compose logs barodydb

# Restart database
docker-compose restart barodydb

# Nuclear option: reset database (⚠️ data loss)
docker-compose down -v
docker-compose up -d
```

### Code Changes Not Reflecting
```bash
# Django should auto-reload, but if not:
docker-compose restart web-dev

# Or rebuild
docker-compose up --build
```

---

**📖 Full Documentation**: See `DOCKER_GUIDE.md`  
**🔄 Migration Guide**: See `DOCKER_CONSOLIDATION_SUMMARY.md`  
**📊 Before/After**: See `DOCKER_BEFORE_AFTER.md`
