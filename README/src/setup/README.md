# Installation Wizard Setup Guide

## Quick Start

The Barodybroject installation wizard provides a comprehensive first-time setup experience for new deployments. Follow these steps to get started:

### 1. Environment Setup

Copy the environment template:
```bash
cp .env.example .env
```

Edit `.env` to configure the installation wizard:
```bash
# Development (skip wizard)
SKIP_INSTALLATION_CHECK=true

# Production (enable wizard)
SKIP_INSTALLATION_CHECK=false
SETUP_TOKEN_EXPIRY_HOURS=1
```

### 2. Start the Application

**Development mode:**
```bash
# Start development containers
docker-compose -f .devcontainer/docker-compose_dev.yml up -d

# Access application at http://localhost:8000
```

**Production mode:**
```bash
# Start production containers
docker-compose up -d

# Access application at http://localhost
```

### 3. Complete Installation

#### Interactive Mode (Recommended for development)
```bash
# Connect to container
docker-compose exec python bash

# Run interactive wizard
python manage.py setup_wizard
```

#### Headless Mode (Recommended for production)
```bash
# Connect to container
docker-compose exec web-prod bash

# Generate setup token
python manage.py setup_wizard --headless
```

This will output:
```
Installation token: abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
Complete setup at: http://localhost/setup/admin/?token=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
Token expires: 2025-01-27 15:30:00 UTC
```

Visit the provided URL to complete admin user creation.

### 4. Verify Installation

Access the setup status page:
- **Status**: http://localhost:8000/setup/status/
- **Health**: http://localhost:8000/setup/health/

## Installation Wizard Features

### 🎯 Interactive Setup
- Step-by-step configuration
- System requirements validation
- Database connection testing
- Admin user creation
- Progress tracking

### 🔒 Headless Mode
- Secure token authentication
- Web-based admin creation
- Automated deployments
- CI/CD integration

### 🎨 Modern UI
- Bootstrap 5.3.3 responsive design
- Real-time form validation
- Progress indicators
- Mobile-friendly interface

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SKIP_INSTALLATION_CHECK` | `false` | Skip wizard in development |
| `SETUP_TOKEN_EXPIRY_HOURS` | `1` | Token expiration time |
| `SETUP_DATA_DIR` | `/app/setup_data` | Data persistence location |

### Docker Volumes

The installation wizard uses persistent volumes:
- `setup-data`: Installation state and configuration
- `app-logs`: Application and setup logs

## Troubleshooting

### Common Issues

**Installation wizard not appearing:**
1. Check `SKIP_INSTALLATION_CHECK` is `false`
2. Verify setup app is in `INSTALLED_APPS`
3. Ensure middleware is configured correctly

**Token validation failures:**
1. Check token hasn't expired
2. Verify token was copied correctly
3. Ensure setup data directory is writable

**Database connection errors:**
1. Verify database container is running
2. Check database credentials in `.env`
3. Test connection with `python manage.py dbshell`

### Debug Mode

Enable debug logging:
```python
# In Django shell
import logging
logging.getLogger('setup').setLevel(logging.DEBUG)
```

### Reset Installation

Remove installation state:
```bash
# Remove configuration file
docker-compose exec web-prod rm -f /app/setup_data/setup_config.json

# Restart containers
docker-compose restart
```

## Development Workflow

### With Installation Wizard (Testing)
1. Set `SKIP_INSTALLATION_CHECK=false` in `.env`
2. Start containers: `docker-compose -f .devcontainer/docker-compose_dev.yml up -d`
3. Visit http://localhost:8000 (redirects to setup wizard)
4. Complete setup process
5. Access main application

### Without Installation Wizard (Normal Development)
1. Set `SKIP_INSTALLATION_CHECK=true` in `.env`
2. Start containers: `docker-compose -f .devcontainer/docker-compose_dev.yml up -d`
3. Create admin manually: `docker-compose exec python python manage.py createsuperuser`
4. Access application directly

## Production Deployment

### Automated Setup
```bash
# Start production containers
docker-compose up -d

# Generate setup token
docker-compose exec web-prod python manage.py setup_wizard --headless

# Complete admin creation via web interface
# Visit: http://yourapp.com/setup/admin/?token=YOUR_TOKEN
```

### Manual Setup
```bash
# Start containers
docker-compose up -d

# Create admin manually
docker-compose exec web-prod python manage.py createsuperuser

# Mark installation complete
docker-compose exec web-prod python manage.py shell -c "
from setup.services import InstallationService
service = InstallationService()
service.mark_installation_complete()
"
```

## Security Considerations

### Token Security
- Tokens use SHA256 hashing
- Automatic expiration (default: 1 hour)
- Single-use for admin creation
- HTTPS required in production

### Production Setup
- Always use HTTPS
- Set strong `SECRET_KEY`
- Configure proper database credentials
- Regular security updates

## Support

For detailed documentation, see: [docs/installation-wizard.md](docs/installation-wizard.md)

For issues and questions:
- Check the troubleshooting section above
- Review application logs in `/app/logs/`
- Open an issue on GitHub

---

**Quick Links:**
- [Full Documentation](docs/installation-wizard.md)
- [Environment Configuration](.env.example)
- [Docker Compose Development](.devcontainer/docker-compose_dev.yml)
- [Docker Compose Production](docker-compose.yml)