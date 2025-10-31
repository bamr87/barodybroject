# Barodybroject Quick Reference Card

**Version**: 2.0.0 | **Date**: 2025-01-27

---

## 🚀 Quick Start (30 seconds)

```bash
cd /Users/bamr87/github/barodybroject
./init_setup.sh
```

Select your setup mode and follow the prompts!

---

## 📋 Setup Modes

### 1️⃣ Docker Development (Recommended)
**Use when**: Starting development, closest to production
```bash
./init_setup.sh
# Select: 1) Docker Development Setup
```
**Access**: http://localhost:8000  
**Features**: Hot-reload, isolated environment

### 2️⃣ Local Development
**Use when**: No Docker, or prefer virtual environment
```bash
./init_setup.sh
# Select: 2) Local Development Setup
```
**Requires**: Python 3.8+, PostgreSQL or SQLite

### 3️⃣ Azure Deployment
**Use when**: Deploying to cloud production
```bash
./init_setup.sh
# Select: 3) Azure Deployment Setup
```
**Requires**: Azure CLI, azd, active Azure subscription

### 4️⃣ Testing/CI
**Use when**: Running CI/CD tests
```bash
./init_setup.sh
# Select: 4) Testing/CI Setup
```
**Runs**: 56 automated infrastructure checks

---

## 🔧 Common Commands

### Docker Operations
```bash
# Start containers
docker-compose up -d

# View logs
docker-compose logs -f python

# Stop containers
docker-compose stop

# Rebuild containers
docker-compose up --build --force-recreate -d

# Shell access
docker-compose exec python bash
```

### Django Management
```bash
# Migrations
docker-compose exec python python manage.py migrate

# Create superuser
docker-compose exec python python manage.py createsuperuser

# Collect static files
docker-compose exec python python manage.py collectstatic

# Django shell
docker-compose exec python python manage.py shell
```

### Testing
```bash
# Full infrastructure test
./scripts/test-infrastructure.sh

# Django tests
docker-compose exec python python manage.py test

# With coverage
docker-compose exec python pytest --cov=parodynews
```

### Azure Management
```bash
# Login to Azure
az login
azd auth login

# Deploy application
azd up

# Post-deployment config
./scripts/azure-deployment-setup.py

# View logs
az containerapp logs show --name <app> --resource-group <rg>
```

---

## 🐛 Quick Troubleshooting

### Problem: Script won't run
```bash
chmod +x init_setup.sh
```

### Problem: Port already in use
```bash
# Change ports in .env
DJANGO_DEV_PORT=8001
POSTGRES_PORT=5433
```

### Problem: Database connection failed
```bash
# Restart database
docker-compose restart barodydb

# Fresh start (⚠️ deletes data)
docker-compose down -v
docker-compose up -d
```

### Problem: Missing dependencies
```bash
# macOS
brew install python3 git docker

# Linux
sudo apt-get install python3 python3-pip git docker.io
```

### Problem: Environment configuration
```bash
# Copy template
cp .env.example .env

# Generate secret key
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## 📚 Documentation

| Resource | Path | Purpose |
|----------|------|---------|
| **Main README** | [README.md](README.md) | Project overview |
| **Setup Guide** | [scripts/README.md](scripts/README.md) | Complete script documentation |
| **Enhancement Summary** | [docs/SETUP_SYSTEM_ENHANCEMENT_SUMMARY.md](docs/SETUP_SYSTEM_ENHANCEMENT_SUMMARY.md) | Detailed enhancement documentation |
| **Testing Guide** | [docs/INFRASTRUCTURE_TESTING.md](docs/INFRASTRUCTURE_TESTING.md) | Infrastructure testing |
| **Security Docs** | [docs/SECURITY_DOCUMENTATION.md](docs/SECURITY_DOCUMENTATION.md) | Security best practices |

---

## 🎯 Key Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `SECRET_KEY` | Yes | Django secret key |
| `DEBUG` | No | Debug mode (default: False) |
| `DB_PASSWORD` | Yes | Database password |
| `ALLOWED_HOSTS` | Yes | Comma-separated allowed hosts |
| `OPENAI_API_KEY` | No | OpenAI integration (optional) |
| `DJANGO_DEV_PORT` | No | Development server port (default: 8000) |
| `POSTGRES_PORT` | No | PostgreSQL port (default: 5432) |

---

## ✅ Validation Checklist

Before deploying to production:

- [ ] All tests pass (`./scripts/test-infrastructure.sh`)
- [ ] Environment variables configured (`.env`)
- [ ] Database migrations applied
- [ ] Static files collected
- [ ] Superuser created
- [ ] Security settings enabled (HTTPS, headers)
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] Health checks working
- [ ] Documentation updated

---

## 🆘 Get Help

**Issues**: https://github.com/bamr87/barodybroject/issues  
**Email**: bamr87@users.noreply.github.com

**Emergency Commands**:
```bash
# View all logs
docker-compose logs -f

# Check application health
curl -I http://localhost:8000/

# Test database connection
docker-compose exec python python manage.py check --database default
```

---

## 📊 System Status

Check system health:
```bash
# Docker status
docker-compose ps

# Application status
curl http://localhost:8000/health/

# Database status
docker-compose exec barodydb pg_isready

# Azure status (if deployed)
az containerapp show --name <app> --resource-group <rg> --query properties.runningStatus
```

---

**Quick Reference Version**: 1.0  
**Compatible with**: Barodybroject v2.0.0+  
**Last Updated**: 2025-01-27

Print this page or save for offline reference!
