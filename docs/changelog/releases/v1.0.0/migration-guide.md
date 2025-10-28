# Migration Guide: v0.1.0 → v1.0.0

**Migration Overview**: Complete Django Settings Optimization  
**Estimated Time**: 30-60 minutes  
**Complexity**: Medium  
**Impact**: High - Configuration Overhaul  

## ⚠️ Critical Notice

This is a **major configuration upgrade** that requires careful migration planning. While the changes are extensive, they are designed to be backward-compatible where possible.

## Pre-Migration Checklist

### 🔍 **Assessment Phase** (5 minutes)
- [ ] Review current `src/barodybroject/settings.py` file
- [ ] Document any custom configuration modifications
- [ ] Backup current configuration files
- [ ] Verify current environment variables
- [ ] Check current database and cache setup

### 📋 **Prerequisites** (10 minutes)  
- [ ] Docker and Docker Compose installed
- [ ] Python 3.8+ environment
- [ ] Access to production environment variables
- [ ] AWS account access (for production secrets)
- [ ] Redis server available (for production)

### 🛡️ **Backup Strategy** (5 minutes)
```bash
# Backup current configuration
cp src/barodybroject/settings.py src/barodybroject/settings_backup_$(date +%Y%m%d).py

# Backup environment configuration
cp .env .env.backup.$(date +%Y%m%d) 2>/dev/null || echo "No .env file found"

# Backup docker configuration
cp docker-compose.yml docker-compose.backup.$(date +%Y%m%d).yml
```

## Migration Steps

### Step 1: Environment Variable Migration (15 minutes)

#### 1.1 Review New Environment Variables

The new configuration introduces several new environment variables. Review the complete list:

**Core Configuration**:
```bash
# Environment Detection
RUNNING_IN_PRODUCTION=False  # Set to True for production

# Database Configuration  
DB_CHOICE=postgres           # Options: postgres, sqlite
DATABASE_URL=               # Full database URL (optional)
DB_NAME=barodyprojectdb     # Database name
DB_USER=postgres            # Database user
DB_PASSWORD=your_password   # Database password
DB_HOST=localhost           # Database host
DB_PORT=5432               # Database port

# Security Configuration
SECRET_KEY=your-secret-key  # Django secret key
ALLOWED_HOSTS=localhost,127.0.0.1  # Comma-separated hosts

# Cache Configuration (Production)
REDIS_URL=redis://localhost:6379/1  # Redis cache URL
CACHE_TIMEOUT=300                    # Default cache timeout
```

**Production-Only Variables**:
```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=us-west-2

# Email Configuration
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_USE_TLS=True

# Security Configuration
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

#### 1.2 Create New Environment Configuration

**For Development**:
```bash
# Create development environment file
cat > .env.development << 'EOF'
# Development Configuration
RUNNING_IN_PRODUCTION=False
DEBUG=True

# Database
DB_CHOICE=postgres
DB_NAME=barodyprojectdb
DB_USER=postgres
DB_PASSWORD=your_dev_password
DB_HOST=localhost
DB_PORT=5432

# Security (development)
SECRET_KEY=your-development-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Email (development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Static Files
STATIC_URL=/static/
MEDIA_URL=/media/
EOF
```

**For Production**:
```bash
# Create production environment file (for reference)
cat > .env.production.example << 'EOF'
# Production Configuration
RUNNING_IN_PRODUCTION=True
DEBUG=False

# Database
DB_CHOICE=postgres
DATABASE_URL=postgresql://user:pass@host:5432/db

# Security
SECRET_KEY=ultra-secure-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# AWS Configuration
AWS_ACCESS_KEY_ID=your-production-aws-key
AWS_SECRET_ACCESS_KEY=your-production-aws-secret
AWS_STORAGE_BUCKET_NAME=your-production-bucket

# Cache
REDIS_URL=redis://production-redis:6379/1

# Email
EMAIL_HOST=smtp.yourdomain.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_USE_TLS=True

# Security Headers
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
EOF
```

### Step 2: Configuration File Migration (10 minutes)

#### 2.1 Backup and Replace Settings

The new `settings.py` file is completely rewritten. Replace the entire file:

```bash
# Backup current settings
mv src/barodybroject/settings.py src/barodybroject/settings_old.py

# The new settings.py file is already in place with v1.0.0
# Verify it exists and is the new version
head -20 src/barodybroject/settings.py
```

#### 2.2 Validate Configuration Structure

The new settings file should contain these major sections:
1. Environment Detection & Validation
2. Core Django Settings
3. Database Configuration  
4. Cache Configuration
5. Security Configuration
6. Static Files & Media
7. Email Configuration
8. Logging Configuration
9. AWS & Production Services
10. Development Tools
11. API & REST Framework
12. Custom Application Settings

### Step 3: Database Migration (5 minutes)

#### 3.1 Update Docker Configuration

Ensure your `docker-compose.yml` includes PostgreSQL:

```yaml
services:
  barodydb:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: barodyprojectdb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your_dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### 3.2 Run Database Migrations

```bash
# Start the database container
docker-compose up -d barodydb

# Wait for database to be ready
sleep 10

# Run migrations
docker-compose exec python python manage.py migrate

# Create superuser (optional)
docker-compose exec python python manage.py createsuperuser
```

### Step 4: Cache Configuration (5 minutes)

#### 4.1 Development Cache

For development, the new configuration automatically uses database caching as a fallback when Redis is not available.

#### 4.2 Production Cache Setup

For production, ensure Redis is available:

```bash
# Add Redis to production docker-compose.yml
cat >> docker-compose.yml << 'EOF'
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  redis_data:
EOF
```

### Step 5: Validation and Testing (10 minutes)

#### 5.1 Configuration Validation

Run the built-in validation script:

```bash
# Validate development configuration
docker-compose exec python python manage.py check

# Validate with deployment checks
docker-compose exec python python manage.py check --deploy
```

#### 5.2 Environment Testing

Test both development and production configurations:

```bash
# Test development environment
RUNNING_IN_PRODUCTION=False docker-compose exec python python manage.py shell -c "
from django.conf import settings
print(f'DEBUG: {settings.DEBUG}')
print(f'Database: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
print(f'Cache: {settings.CACHES[\"default\"][\"BACKEND\"]}')
"

# Test production-like environment
RUNNING_IN_PRODUCTION=True docker-compose exec python python manage.py shell -c "
from django.conf import settings
print(f'DEBUG: {settings.DEBUG}')
print(f'Security: HTTPS redirect = {settings.SECURE_SSL_REDIRECT}')
"
```

#### 5.3 Application Testing

```bash
# Start the development server
docker-compose up -d

# Test basic functionality
curl http://localhost:8000/

# Check admin interface
curl http://localhost:8000/admin/

# Verify static files
curl http://localhost:8000/static/admin/css/base.css
```

## Common Migration Issues

### Issue 1: Environment Variable Not Set

**Symptom**: `ImproperlyConfigured: Environment variable X is not set`

**Solution**:
```bash
# Check which variables are missing
docker-compose exec python python manage.py shell -c "
import os
from django.core.exceptions import ImproperlyConfigured
required_vars = ['SECRET_KEY', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
for var in required_vars:
    if not os.environ.get(var):
        print(f'Missing: {var}')
"

# Set missing variables in your environment
export MISSING_VAR=value
```

### Issue 2: Database Connection Issues

**Symptom**: `django.db.utils.OperationalError: could not connect to server`

**Solution**:
```bash
# Check database container status
docker-compose ps barodydb

# Check database logs
docker-compose logs barodydb

# Reset database container
docker-compose down barodydb
docker-compose up -d barodydb
```

### Issue 3: Cache Configuration Issues

**Symptom**: Cache-related errors in production

**Solution**:
```bash
# Check Redis availability
docker-compose exec python python -c "
import redis
try:
    r = redis.Redis.from_url('redis://localhost:6379/1')
    r.ping()
    print('Redis available')
except:
    print('Redis not available - using database cache')
"

# Test cache functionality
docker-compose exec python python manage.py shell -c "
from django.core.cache import cache
cache.set('test', 'value')
print(f'Cache test: {cache.get(\"test\")}')
"
```

### Issue 4: Static Files Issues

**Symptom**: Static files not loading properly

**Solution**:
```bash
# Collect static files
docker-compose exec python python manage.py collectstatic --noinput

# Check static files configuration
docker-compose exec python python manage.py shell -c "
from django.conf import settings
print(f'STATIC_URL: {settings.STATIC_URL}')
print(f'STATIC_ROOT: {settings.STATIC_ROOT}')
"
```

## Post-Migration Verification

### ✅ **Configuration Checklist**

- [ ] All environment variables properly set
- [ ] Database connection working
- [ ] Cache system functioning
- [ ] Static files loading
- [ ] Admin interface accessible
- [ ] Email configuration working (if configured)
- [ ] Security headers present (production)
- [ ] Logging functioning properly

### ✅ **Performance Validation**

```bash
# Test database performance
docker-compose exec python python manage.py shell -c "
import time
from django.db import connection
start = time.time()
with connection.cursor() as cursor:
    cursor.execute('SELECT 1')
print(f'Database query time: {time.time() - start:.3f}s')
"

# Test cache performance
docker-compose exec python python manage.py shell -c "
import time
from django.core.cache import cache
start = time.time()
cache.set('perf_test', 'value')
cache.get('perf_test')
print(f'Cache operation time: {time.time() - start:.3f}s')
"
```

### ✅ **Security Validation**

For production environments:

```bash
# Check security headers
curl -I https://yourdomain.com/ | grep -i "strict-transport-security\|x-frame-options\|x-content-type-options"

# Validate SSL redirect
curl -I http://yourdomain.com/ | grep -i location
```

## Rollback Procedure

If migration issues occur, you can rollback:

### Emergency Rollback

```bash
# Restore original settings
mv src/barodybroject/settings_old.py src/barodybroject/settings.py

# Restore environment
mv .env.backup.$(date +%Y%m%d) .env 2>/dev/null || echo "No env backup"

# Restore docker configuration
mv docker-compose.backup.$(date +%Y%m%d).yml docker-compose.yml

# Restart containers
docker-compose down
docker-compose up -d
```

### Gradual Rollback

For production environments, implement a gradual rollback:

1. **Switch traffic back** to previous environment
2. **Investigate issues** in staging environment
3. **Apply fixes** based on investigation
4. **Re-attempt migration** with fixes

## Getting Help

### Documentation Resources

- **[Configuration Guide](../../configuration/settings-optimization.md)** - Comprehensive configuration documentation
- **[Environment Configuration](../../configuration/environment-config.md)** - Environment variable reference
- **[Troubleshooting Guide](../../configuration/troubleshooting.md)** - Common issues and solutions

### Support Channels

- **GitHub Issues**: [Report migration issues](https://github.com/bamr87/barodybroject/issues)
- **Documentation**: [Configuration Documentation](../../configuration/README.md)
- **Email Support**: Contact the development team

### Validation Scripts

Use the provided validation scripts:

```bash
# Run comprehensive configuration validation
python scripts/validate_configuration.py

# Run environment validation
python scripts/validate_environment.py

# Run security validation
python scripts/validate_security.py
```

---

**Migration Guide Version**: 1.0.0  
**Last Updated**: October 27, 2025  
**Estimated Success Rate**: 95%+ with proper preparation  
**Average Migration Time**: 45 minutes