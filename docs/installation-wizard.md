# Installation Wizard Documentation

## Overview

The Barodybroject Installation Wizard provides a comprehensive first-time setup experience for new Django/OpenAI deployments. It offers both interactive CLI and web-based modes with secure token authentication for headless installations.

## Features

### 🎯 Core Capabilities
- **Interactive Setup Wizard**: Step-by-step configuration with progress tracking
- **Headless Mode**: Automated installation with web-based admin creation
- **Secure Token System**: SHA256-based authentication with expiration
- **Responsive UI**: Bootstrap 5.3.3 interface with modern UX
- **System Health Monitoring**: Real-time validation and status checking
- **Comprehensive Logging**: Detailed tracking for troubleshooting

### 🔒 Security Features
- Token-based authentication with automatic expiration
- Secure password handling with Django validation
- CSRF protection for web forms
- Input sanitization and validation
- Session-based state management

### 🎨 User Experience
- Professional Bootstrap UI with gradient design
- Real-time form validation and feedback
- Progress indicators and status tracking
- Mobile-responsive design
- Accessibility compliance (WCAG guidelines)

## Installation and Setup

### Prerequisites
- Django 4.2+ application
- Python 3.8+
- Docker container environment (recommended)
- PostgreSQL database (production)

### Quick Start

1. **Add to Django settings**:
```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'setup',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'setup.middleware.InstallationMiddleware',  # Add this
    # ... other middleware
]
```

2. **Include URLs**:
```python
# urls.py
urlpatterns = [
    path('setup/', include('setup.urls')),
    # ... other URLs
]
```

3. **Run migrations**:
```bash
python manage.py migrate
```

## Usage Guide

### Interactive Mode (Default)

Start the interactive setup wizard:
```bash
python manage.py setup_wizard
```

The wizard will guide you through:
1. System requirements check
2. Database connection validation
3. Admin user creation
4. Initial configuration setup
5. Completion verification

### Headless Mode

For automated deployments:
```bash
python manage.py setup_wizard --headless
```

This generates a secure token and instructions for web-based admin creation:
```
Installation token: abc123def456ghi789jkl012mno345pqr678stu901vwx234yz

Complete setup at: https://yourapp.com/setup/admin/?token=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
Token expires: 2025-01-27 15:30:00 UTC
```

### Web Interface

Access the setup wizard at `/setup/` when installation is incomplete.

**Available endpoints**:
- `/setup/` - Main wizard overview
- `/setup/admin/` - Admin user creation (requires token in headless mode)
- `/setup/status/` - Installation progress and system health
- `/setup/complete/` - Setup completion page
- `/setup/health/` - System health monitoring

## Configuration Options

### Environment Variables

```bash
# Skip installation checks in development
SKIP_INSTALLATION_CHECK=true

# Custom token expiration (default: 1 hour)
SETUP_TOKEN_EXPIRY_HOURS=2

# Setup data storage location
SETUP_DATA_DIR=/app/setup_data
```

### Django Settings

```python
# settings.py

# Installation wizard configuration
SKIP_INSTALLATION_CHECK = env.bool('SKIP_INSTALLATION_CHECK', default=False)

# Setup data persistence
SETUP_CONFIG_FILE = BASE_DIR / 'setup_config.json'

# Token expiration time (in seconds)
SETUP_TOKEN_EXPIRY = 3600  # 1 hour
```

## API Reference

### InstallationService Class

Main service class for managing installation state and operations.

#### Methods

**`is_installation_complete()`**
```python
def is_installation_complete() -> bool:
    """Check if initial installation is complete."""
```

**`generate_setup_token()`**
```python
def generate_setup_token() -> str:
    """Generate secure token for headless setup."""
```

**`validate_token(token: str)`**
```python
def validate_token(token: str) -> bool:
    """Validate setup token and check expiration."""
```

**`create_admin_user(username: str, email: str, password: str)`**
```python
def create_admin_user(username: str, email: str, password: str) -> User:
    """Create admin user with validation."""
```

**`mark_installation_complete()`**
```python
def mark_installation_complete() -> bool:
    """Mark installation as completed."""
```

### Management Command

**setup_wizard** - Interactive and headless setup

```bash
# Interactive mode
python manage.py setup_wizard

# Headless mode
python manage.py setup_wizard --headless

# Force reinstallation
python manage.py setup_wizard --force

# Quiet mode (minimal output)
python manage.py setup_wizard --quiet
```

### Middleware

**InstallationMiddleware** - Automatic redirection to setup wizard

Exempted paths:
- `/setup/` - Setup wizard URLs
- `/admin/` - Django admin
- `/static/` - Static files
- `/media/` - Media files
- `/api/` - API endpoints
- `/health/` - Health checks

## Security Considerations

### Token Security
- Tokens use SHA256 hashing with secure random generation
- Automatic expiration (default: 1 hour)
- Single-use tokens for admin creation
- Secure transmission over HTTPS (production)

### Input Validation
- All form inputs validated server-side
- Django's built-in password validation
- CSRF protection on all forms
- SQL injection protection via Django ORM

### Production Deployment
- Always use HTTPS in production
- Set strong `SECRET_KEY`
- Configure proper database credentials
- Enable Django security middleware
- Regular security updates

## Troubleshooting

### Common Issues

**1. Installation wizard not appearing**
```
Check middleware configuration:
- Ensure 'setup.middleware.InstallationMiddleware' is in MIDDLEWARE
- Verify setup app is in INSTALLED_APPS
- Check URL configuration includes setup.urls
```

**2. Token validation failures**
```
Token issues:
- Check token hasn't expired (default: 1 hour)
- Verify token was copied correctly (no spaces/truncation)
- Ensure setup_config.json is writable
- Check system clock synchronization
```

**3. Database connection errors**
```
Database issues:
- Verify database credentials in environment variables
- Check database server is running and accessible
- Ensure database exists and user has proper permissions
- Test connection with management command
```

**4. Permission denied errors**
```
File system issues:
- Check setup_config.json file permissions
- Verify application has write access to data directory
- Ensure proper Docker volume mounting
- Check container user permissions
```

### Debug Mode

Enable debug logging for troubleshooting:

```python
# settings.py
LOGGING = {
    'loggers': {
        'setup': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

### Recovery Procedures

**Reset installation state**:
```bash
# Remove configuration file
rm setup_config.json

# Clear any cached state
python manage.py shell -c "from django.core.cache import cache; cache.clear()"

# Restart application
docker-compose restart
```

**Manual admin creation**:
```bash
# If setup wizard fails, create admin manually
python manage.py createsuperuser

# Then mark installation complete
python manage.py shell -c "
from setup.services import InstallationService
service = InstallationService()
service.mark_installation_complete()
"
```

## Integration Examples

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    volumes:
      - ./setup_data:/app/setup_data  # Persist setup state
    environment:
      - SKIP_INSTALLATION_CHECK=false
      - SETUP_TOKEN_EXPIRY_HOURS=2
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: barodydb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
```

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
- name: Run setup wizard
  run: |
    docker-compose exec web python manage.py setup_wizard --headless
    echo "Setup token generated, check logs for details"
```

### Health Check Integration

```python
# Custom health check
from django.http import JsonResponse
from setup.services import InstallationService

def health_check(request):
    service = InstallationService()
    return JsonResponse({
        'status': 'healthy',
        'installation_complete': service.is_installation_complete(),
        'setup_required': not service.is_installation_complete()
    })
```

## Advanced Configuration

### Custom Templates

Override default templates by creating:
```
your_app/templates/setup/
├── base.html
├── wizard.html
├── create_admin.html
├── status.html
├── complete.html
└── health.html
```

### Custom Middleware Configuration

```python
# Custom middleware ordering
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'setup.middleware.InstallationMiddleware',  # Early in chain
    # ... other middleware
]

# Skip installation check for specific paths
SETUP_EXEMPTED_PATHS = [
    '/custom-api/',
    '/webhook/',
]
```

### Integration with Monitoring

```python
# settings.py
LOGGING = {
    'handlers': {
        'setup_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/setup.log',
        },
    },
    'loggers': {
        'setup': {
            'handlers': ['setup_file'],
            'level': 'INFO',
        },
    },
}
```

## Best Practices

### Development
- Use `SKIP_INSTALLATION_CHECK=true` for development
- Test both interactive and headless modes
- Validate token expiration behavior
- Test middleware exemption paths

### Production
- Always use HTTPS for token transmission
- Set appropriate token expiration times
- Monitor setup logs for security events
- Regular backup of setup configuration

### Security
- Rotate tokens regularly in production
- Monitor failed setup attempts
- Use strong admin passwords
- Enable Django security features

### Performance
- Cache installation status checks
- Minimize middleware overhead for exempted paths
- Use efficient database queries
- Optimize template rendering

## Support and Contributing

### Getting Help
- Check troubleshooting section above
- Review application logs for error details
- Test with DEBUG=True for detailed error information
- Use management commands for manual operations

### Contributing
- Follow Django coding standards
- Add tests for new features
- Update documentation for changes
- Test across different environments

### Reporting Issues
When reporting issues, include:
- Django and Python versions
- Environment configuration
- Error messages and stack traces
- Steps to reproduce the problem
- Expected vs. actual behavior

---

**Author**: Barodybroject Team  
**Version**: 1.0.0  
**Last Updated**: 2025-01-27  
**License**: MIT