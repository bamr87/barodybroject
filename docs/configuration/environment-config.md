# Environment Configuration Guide

**File**: environment-config.md  
**Description**: Comprehensive environment variable reference and configuration management  
**Author**: Barodybroject Team <team@barodybroject.com>  
**Created**: 2025-10-27  
**Last Modified**: 2025-10-27  
**Version**: 1.0.0  

## Table of Contents

- [Overview](#overview)
- [Environment Variables Reference](#environment-variables-reference)
- [Environment Profiles](#environment-profiles)
- [Variable Validation](#variable-validation)
- [Security Considerations](#security-considerations)
- [Container Configuration](#container-configuration)
- [Troubleshooting](#troubleshooting)

## Overview

This guide provides comprehensive documentation for all environment variables used in the Barodybroject Django application. The configuration follows 12-Factor App principles, using environment variables for all configuration that varies between deployments.

## Environment Variables Reference

### Core Environment Control

| Variable | Type | Default | Description | Required |
|----------|------|---------|-------------|----------|
| `RUNNING_IN_PRODUCTION` | bool | False | Controls production vs development mode | No |
| `DEBUG` | bool | !RUNNING_IN_PRODUCTION | Enables Django debug mode | No |
| `LOG_LEVEL` | string | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) | No |
| `ENVIRONMENT` | string | development | Environment name (development, staging, production) | No |

### Security Configuration

| Variable | Type | Default | Description | Required |
|----------|------|---------|-------------|----------|
| `SECRET_KEY` | string | (generated) | Django secret key for production | Production |
| `USE_HTTPS` | bool | False | Enable HTTPS redirects and secure cookies | No |
| `ALLOWED_HOSTS` | list | localhost,127.0.0.1 | Comma-separated list of allowed hosts | Production |
| `CSRF_TRUSTED_ORIGINS` | list | (auto-generated) | Trusted origins for CSRF protection | No |

### Database Configuration

| Variable | Type | Default | Description | Required |
|----------|------|---------|-------------|----------|
| `DB_CHOICE` | string | postgres | Database backend (postgres, sqlite) | No |
| `DB_HOST` | string | localhost | Database host | No |
| `DB_PORT` | int | 5432 | Database port | No |
| `DB_NAME` | string | barodydb | Database name | No |
| `DB_USER` | string | postgres | Database username | No |
| `DB_PASSWORD` | string | (empty) | Database password | Production |
| `DB_SSL_MODE` | string | prefer | SSL mode for PostgreSQL | No |
| `USE_SQLITE` | bool | False | Force SQLite usage (development) | No |

### AWS Configuration

| Variable | Type | Default | Description | Required |
|----------|------|---------|-------------|----------|
| `AWS_ACCESS_KEY_ID` | string | (empty) | AWS access key for services | Production |
| `AWS_SECRET_ACCESS_KEY` | string | (empty) | AWS secret key | Production |
| `AWS_REGION` | string | us-east-1 | AWS region | No |
| `AWS_SES_REGION_NAME` | string | us-east-1 | SES region for email | No |

### Caching Configuration

| Variable | Type | Default | Description | Required |
|----------|------|---------|-------------|----------|
| `REDIS_URL` | string | redis://127.0.0.1:6379/1 | Redis connection URL | No |
| `CACHE_TIMEOUT` | int | 300 | Default cache timeout in seconds | No |

### Email Configuration

| Variable | Type | Default | Description | Required |
|----------|------|---------|-------------|----------|
| `EMAIL_BACKEND` | string | (auto-detected) | Django email backend | No |
| `EMAIL_HOST` | string | localhost | SMTP host | No |
| `EMAIL_PORT` | int | 587 | SMTP port | No |
| `EMAIL_HOST_USER` | string | (empty) | SMTP username | No |
| `EMAIL_HOST_PASSWORD` | string | (empty) | SMTP password | No |
| `EMAIL_USE_TLS` | bool | True | Use TLS for email | No |

### Social Authentication

| Variable | Type | Default | Description | Required |
|----------|------|---------|-------------|----------|
| `GITHUB_CLIENT_ID` | string | (empty) | GitHub OAuth client ID | No |
| `GITHUB_CLIENT_SECRET` | string | (empty) | GitHub OAuth client secret | No |

### Static Files & Media

| Variable | Type | Default | Description | Required |
|----------|------|---------|-------------|----------|
| `STATIC_URL` | string | /static/ | Static files URL prefix | No |
| `STATIC_ROOT` | path | staticfiles/ | Static files collection directory | No |
| `MEDIA_URL` | string | /media/ | Media files URL prefix | No |
| `MEDIA_ROOT` | path | media/ | Media files storage directory | No |

### Container Configuration

| Variable | Type | Default | Description | Required |
|----------|------|---------|-------------|----------|
| `CONTAINER_APP_NAME` | string | barodybroject | Container app name for Azure | No |
| `PORT` | int | 8000 | Application port | No |

### Development Tools

| Variable | Type | Default | Description | Required |
|----------|------|---------|-------------|----------|
| `ENABLE_DEBUG_TOOLBAR` | bool | False | Enable Django Debug Toolbar | No |
| `DEBUGPY_PORT` | int | 5678 | Debug port for VS Code | No |
| `TESTING` | bool | False | Enable testing mode | No |

## Environment Profiles

### Development Profile (.env.development)

```bash
# Environment Control
RUNNING_IN_PRODUCTION=False
DEBUG=True
LOG_LEVEL=DEBUG
ENVIRONMENT=development

# Database - Local PostgreSQL or SQLite
DB_CHOICE=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=barodydb
DB_USER=postgres
DB_PASSWORD=postgres
# Alternative: Use SQLite for simpler setup
# USE_SQLITE=True

# Email - Console backend for development
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Security - Relaxed for development
SECRET_KEY=dev-secret-key-change-for-production
USE_HTTPS=False

# Debug Tools
ENABLE_DEBUG_TOOLBAR=False
DEBUGPY_PORT=5678

# Social Auth - Development keys
GITHUB_CLIENT_ID=your-dev-github-client-id
GITHUB_CLIENT_SECRET=your-dev-github-client-secret

# Allowed Hosts - Permissive for development
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

### Staging Profile (.env.staging)

```bash
# Environment Control
RUNNING_IN_PRODUCTION=True
DEBUG=False
LOG_LEVEL=INFO
ENVIRONMENT=staging

# Database - Staging PostgreSQL
DB_CHOICE=postgres
DB_HOST=staging-db-host
DB_PORT=5432
DB_NAME=barodydb_staging
DB_USER=postgres
DB_PASSWORD=staging-secure-password
DB_SSL_MODE=require

# Email - SES backend
EMAIL_BACKEND=django_ses.SESBackend
AWS_SES_REGION_NAME=us-east-1

# Security - Production-like security
SECRET_KEY=staging-ultra-secure-secret-key
USE_HTTPS=True

# AWS Services
AWS_ACCESS_KEY_ID=staging-aws-access-key
AWS_SECRET_ACCESS_KEY=staging-aws-secret-key
AWS_REGION=us-east-1

# Cache - Redis
REDIS_URL=redis://staging-redis-host:6379/1

# Social Auth - Staging keys
GITHUB_CLIENT_ID=staging-github-client-id
GITHUB_CLIENT_SECRET=staging-github-client-secret

# Container - Staging configuration
CONTAINER_APP_NAME=barodybroject-staging
ALLOWED_HOSTS=barodybroject-staging.azurecontainerapps.io,staging.barodybroject.com
```

### Production Profile (.env.production)

```bash
# Environment Control
RUNNING_IN_PRODUCTION=True
DEBUG=False
LOG_LEVEL=WARNING
ENVIRONMENT=production

# Database - Production PostgreSQL
DB_CHOICE=postgres
DB_HOST=prod-db-host
DB_PORT=5432
DB_NAME=barodydb_production
DB_USER=postgres
DB_PASSWORD=production-ultra-secure-password
DB_SSL_MODE=require

# Email - SES backend
EMAIL_BACKEND=django_ses.SESBackend
AWS_SES_REGION_NAME=us-east-1

# Security - Maximum security
SECRET_KEY=production-ultra-secure-secret-key-64-chars-minimum
USE_HTTPS=True

# AWS Services
AWS_ACCESS_KEY_ID=production-aws-access-key
AWS_SECRET_ACCESS_KEY=production-aws-secret-key
AWS_REGION=us-east-1

# Cache - Redis with high availability
REDIS_URL=redis://prod-redis-cluster:6379/1

# Social Auth - Production keys
GITHUB_CLIENT_ID=production-github-client-id
GITHUB_CLIENT_SECRET=production-github-client-secret

# Container - Production configuration
CONTAINER_APP_NAME=barodybroject
ALLOWED_HOSTS=barodybroject.azurecontainerapps.io,barodybroject.com,www.barodybroject.com

# Performance
CACHE_TIMEOUT=600
```

## Variable Validation

### Required Variables by Environment

#### Development Requirements
```python
REQUIRED_DEV_VARS = [
    'SECRET_KEY',  # Can use default for development
]

OPTIONAL_DEV_VARS = [
    'DB_PASSWORD',  # Can be empty for local dev
    'GITHUB_CLIENT_ID',  # Only needed for OAuth testing
    'GITHUB_CLIENT_SECRET',
]
```

#### Production Requirements
```python
REQUIRED_PROD_VARS = [
    'SECRET_KEY',
    'DB_PASSWORD',
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'ALLOWED_HOSTS',
]

CRITICAL_PROD_VARS = [
    'SECRET_KEY',  # Must be unique and secure
    'DB_PASSWORD',  # Must be strong
    'AWS_SECRET_ACCESS_KEY',  # Must be protected
]
```

### Validation Scripts

#### Environment Validation Script
```python
#!/usr/bin/env python
"""
Environment validation script for Barodybroject
Usage: python scripts/validate_env.py [environment]
"""
import os
import sys
from pathlib import Path

def validate_environment(env_type='development'):
    required_vars = {
        'development': ['SECRET_KEY'],
        'staging': ['SECRET_KEY', 'DB_PASSWORD', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY'],
        'production': ['SECRET_KEY', 'DB_PASSWORD', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'ALLOWED_HOSTS'],
    }
    
    missing_vars = []
    for var in required_vars.get(env_type, []):
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables for {env_type}:")
        for var in missing_vars:
            print(f"  - {var}")
        return False
    
    print(f"✅ All required environment variables present for {env_type}")
    return True

if __name__ == '__main__':
    env_type = sys.argv[1] if len(sys.argv) > 1 else 'development'
    success = validate_environment(env_type)
    sys.exit(0 if success else 1)
```

## Security Considerations

### Secret Management Best Practices

#### 1. Secret Key Generation
```python
# Generate secure secret key
from django.core.management.utils import get_random_secret_key
secret_key = get_random_secret_key()
print(f"SECRET_KEY={secret_key}")
```

#### 2. Password Security
```bash
# Generate secure database password
openssl rand -base64 32

# Generate secure passwords with special characters
python -c "
import secrets
import string
alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
password = ''.join(secrets.choice(alphabet) for i in range(32))
print(password)
"
```

#### 3. Environment File Security
```bash
# Set proper permissions on .env files
chmod 600 .env*

# Never commit .env files to version control
echo ".env*" >> .gitignore

# Use encrypted environment files for production
# Example with ansible-vault:
ansible-vault encrypt .env.production
```

### Variable Encryption

#### Using AWS Secrets Manager
```python
# Store sensitive variables in AWS Secrets Manager
import boto3
import json

def store_secret(secret_name, secret_dict, region='us-east-1'):
    client = boto3.client('secretsmanager', region_name=region)
    
    try:
        client.create_secret(
            Name=secret_name,
            SecretString=json.dumps(secret_dict),
            Description='Barodybroject environment variables'
        )
        print(f"✅ Secret {secret_name} created successfully")
    except client.exceptions.ResourceExistsException:
        client.update_secret(
            SecretId=secret_name,
            SecretString=json.dumps(secret_dict)
        )
        print(f"✅ Secret {secret_name} updated successfully")

# Usage
secrets_dict = {
    'SECRET_KEY': 'your-secret-key',
    'DB_PASSWORD': 'your-db-password',
    'AWS_SECRET_ACCESS_KEY': 'your-aws-secret',
    'GITHUB_CLIENT_SECRET': 'your-github-secret',
}

store_secret('barodybroject/env', secrets_dict)
```

## Container Configuration

### Docker Environment Configuration

#### Development Docker Compose
```yaml
# docker-compose.override.yml
version: '3.8'
services:
  web:
    environment:
      - RUNNING_IN_PRODUCTION=False
      - DEBUG=True
      - LOG_LEVEL=DEBUG
      - DB_HOST=barodydb
      - DB_PASSWORD=postgres
      - USE_HTTPS=False
    env_file:
      - .env.development
```

#### Production Docker Configuration
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  web:
    environment:
      - RUNNING_IN_PRODUCTION=True
      - DEBUG=False
      - LOG_LEVEL=WARNING
    env_file:
      - .env.production
    secrets:
      - db_password
      - secret_key
      - aws_credentials

secrets:
  db_password:
    external: true
  secret_key:
    external: true
  aws_credentials:
    external: true
```

### Azure Container Apps Environment

#### Container App Configuration
```json
{
  "properties": {
    "configuration": {
      "secrets": [
        {
          "name": "db-password",
          "value": "your-secure-db-password"
        },
        {
          "name": "secret-key", 
          "value": "your-django-secret-key"
        }
      ]
    },
    "template": {
      "containers": [
        {
          "name": "barodybroject",
          "env": [
            {
              "name": "RUNNING_IN_PRODUCTION",
              "value": "True"
            },
            {
              "name": "DB_PASSWORD",
              "secretRef": "db-password"
            },
            {
              "name": "SECRET_KEY",
              "secretRef": "secret-key"
            }
          ]
        }
      ]
    }
  }
}
```

## Troubleshooting

### Common Issues

#### 1. Environment Variables Not Loading
```bash
# Check if .env file exists and is readable
ls -la .env*
cat .env | head -5

# Verify environment loading in Django
python manage.py shell -c "
import os
from django.conf import settings
print('RUNNING_IN_PRODUCTION:', os.environ.get('RUNNING_IN_PRODUCTION'))
print('Settings IS_PRODUCTION:', settings.IS_PRODUCTION)
print('DEBUG:', settings.DEBUG)
"
```

#### 2. Boolean Variables Not Parsing Correctly
```bash
# Django-environ parsing rules:
# True values: True, true, TRUE, 1, yes, YES, on, ON
# False values: False, false, FALSE, 0, no, NO, off, OFF

# Test boolean parsing
python -c "
import environ
env = environ.Env()
print('True values:', ['True', 'true', '1', 'yes', 'on'])
print('False values:', ['False', 'false', '0', 'no', 'off'])
for val in ['True', 'False', '1', '0']:
    os.environ['TEST_BOOL'] = val
    print(f'{val} -> {env.bool(\"TEST_BOOL\")}')
"
```

#### 3. Missing Required Variables
```bash
# Check for missing variables
python scripts/validate_env.py production

# Set temporary environment variables for testing
export SECRET_KEY=temporary-key-for-testing
export DB_PASSWORD=temporary-password
python manage.py check
```

#### 4. AWS Credentials Issues
```bash
# Test AWS credentials
aws sts get-caller-identity

# Test boto3 connection
python -c "
import boto3
try:
    session = boto3.Session()
    sts = session.client('sts')
    identity = sts.get_caller_identity()
    print('✅ AWS credentials valid')
    print(f'Account: {identity[\"Account\"]}')
    print(f'User: {identity[\"Arn\"]}')
except Exception as e:
    print(f'❌ AWS credentials error: {e}')
"
```

### Debug Environment Loading

#### Environment Debug Script
```python
#!/usr/bin/env python
"""Debug environment variable loading"""
import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, 'src')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barodybroject.settings')

print("🔍 Environment Debug Information")
print("=" * 50)

print("\n📁 Environment Files:")
env_files = ['.env', '.env.development', '.env.staging', '.env.production']
for env_file in env_files:
    if Path(env_file).exists():
        print(f"✅ {env_file} (exists)")
    else:
        print(f"❌ {env_file} (missing)")

print("\n🔧 Key Environment Variables:")
key_vars = [
    'RUNNING_IN_PRODUCTION', 'DEBUG', 'SECRET_KEY', 'DB_PASSWORD',
    'AWS_ACCESS_KEY_ID', 'GITHUB_CLIENT_ID'
]

for var in key_vars:
    value = os.environ.get(var)
    if value:
        # Mask sensitive values
        if 'SECRET' in var or 'PASSWORD' in var or 'KEY' in var:
            display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
        else:
            display_value = value
        print(f"✅ {var} = {display_value}")
    else:
        print(f"❌ {var} = (not set)")

print("\n⚙️  Django Settings:")
try:
    from django.conf import settings
    print(f"IS_PRODUCTION: {settings.IS_PRODUCTION}")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"Database: {settings.DATABASES['default']['ENGINE']}")
    print(f"Cache: {settings.CACHES['default']['BACKEND']}")
    print("✅ Django settings loaded successfully")
except Exception as e:
    print(f"❌ Django settings error: {e}")
```

---

## Resources

- **[Settings Optimization Guide](./settings-optimization.md)** - Complete Django settings documentation
- **[Security Configuration](./security-config.md)** - Security-specific environment variables
- **[Deployment Configuration](./deployment-config.md)** - Deployment environment setup

---

**Last Updated**: October 27, 2025  
**Maintainer**: Barodybroject Team  
**Version**: 1.0.0  
**Related**: [Django Settings](./settings-optimization.md) | [Security Guide](./security-config.md)