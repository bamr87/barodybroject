# Django Admin Credentials Configuration

## Overview

Barodybroject automatically creates Django admin superuser credentials when Docker containers start. This document explains how the system works and how to configure it for different environments.

## How It Works

### Automatic Creation Process

1. **Container Startup**: When Docker containers start, the `ensure_admin` management command runs automatically
2. **Credential Resolution**: Credentials are resolved in this order:
   - Command-line arguments (if provided)
   - Environment variables
   - Default fallback values
3. **User Creation**: Admin user is created or updated in the database
4. **Credential Logging**: Credentials are saved to `setup_data/admin_credentials.txt` for reference

### Files Involved

| File | Purpose |
|------|---------|
| `src/parodynews/management/commands/ensure_admin.py` | Management command that creates/updates admin user |
| `.env.example` | Template with credential environment variables |
| `.devcontainer/docker-compose_dev.yml` | Development Docker config with credential env vars |
| `docker-compose.yml` | Production Docker config with credential env vars |
| `src/docker-entrypoint.sh` | Production startup script that runs ensure_admin |
| `setup_data/admin_credentials.txt` | Auto-generated file with credentials (gitignored) |

## Configuration

### Default Credentials

If no configuration is provided, these defaults are used:

```bash
Username: admin
Password: admin
Email: admin@localhost.local
```

**⚠️ Warning:** Default credentials are only suitable for local development!

### Environment Variables

Set these environment variables to customize admin credentials:

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SUPERUSER_USERNAME` | Admin username | `admin` |
| `DJANGO_SUPERUSER_EMAIL` | Admin email address | `admin@localhost.local` |
| `DJANGO_SUPERUSER_PASSWORD` | Admin password | `admin` |
| `ADMIN_CREDENTIALS_FILE` | Path to save credentials | `setup_data/admin_credentials.txt` |

### Configuration Methods

#### Method 1: .env File (Local Development)

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your credentials:
   ```bash
   DJANGO_SUPERUSER_USERNAME=myadmin
   DJANGO_SUPERUSER_EMAIL=admin@example.com
   DJANGO_SUPERUSER_PASSWORD=MySecurePassword123!
   ```

3. Start containers:
   ```bash
   docker-compose -f .devcontainer/docker-compose_dev.yml up -d
   ```

#### Method 2: GitHub Secrets (CI/CD)

For automated deployments and CI/CD pipelines:

1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add these secrets:
   - `DJANGO_SUPERUSER_USERNAME`
   - `DJANGO_SUPERUSER_EMAIL`
   - `DJANGO_SUPERUSER_PASSWORD`

3. Reference in GitHub Actions workflow:
   ```yaml
   env:
     DJANGO_SUPERUSER_USERNAME: ${{ secrets.DJANGO_SUPERUSER_USERNAME }}
     DJANGO_SUPERUSER_EMAIL: ${{ secrets.DJANGO_SUPERUSER_EMAIL }}
     DJANGO_SUPERUSER_PASSWORD: ${{ secrets.DJANGO_SUPERUSER_PASSWORD }}
   ```

#### Method 3: Azure Key Vault (Production)

For production deployments on Azure:

1. Create secrets in Azure Key Vault:
   ```bash
   az keyvault secret set --vault-name <vault-name> \
     --name django-superuser-username --value "admin"
   
   az keyvault secret set --vault-name <vault-name> \
     --name django-superuser-email --value "admin@example.com"
   
   az keyvault secret set --vault-name <vault-name> \
     --name django-superuser-password --value "SecurePassword123!"
   ```

2. Reference in Azure Container App:
   ```bash
   az containerapp update \
     --name <app-name> \
     --resource-group <rg-name> \
     --set-env-vars \
       "DJANGO_SUPERUSER_USERNAME=secretref:django-superuser-username" \
       "DJANGO_SUPERUSER_EMAIL=secretref:django-superuser-email" \
       "DJANGO_SUPERUSER_PASSWORD=secretref:django-superuser-password"
   ```

#### Method 4: Command Line (Manual)

Run the command directly with custom credentials:

```bash
docker-compose exec web-prod python manage.py ensure_admin \
  --username myadmin \
  --email admin@example.com \
  --password MySecurePassword123!
```

## Credential Storage

### Credentials File

Credentials are automatically saved to `setup_data/admin_credentials.txt` with:

- Username, email, and password in plaintext
- Timestamp of creation/update
- Admin URL for your environment
- Security warnings and best practices

**File Permissions:** The file is created with `600` permissions (owner read/write only) on Unix-like systems.

**Git Ignore:** The credentials file is automatically excluded from version control via `.gitignore`.

### Viewing Saved Credentials

```bash
# View credentials file
cat setup_data/admin_credentials.txt

# Or from Docker container
docker-compose exec web-prod cat /app/setup_data/admin_credentials.txt
```

### Disabling Credential Logging

To prevent saving credentials to file:

```bash
python manage.py ensure_admin --no-save-credentials
```

Or set in docker-compose command override.

## Security Considerations

### Development Environment

✅ **Acceptable:**
- Using default credentials (`admin`/`admin`)
- Storing credentials in `.env` file
- Credentials file in `setup_data/`

✅ **Recommended:**
- Keep `.env` in `.gitignore` (already configured)
- Don't share `.env` files
- Use different credentials per developer if needed

### Production Environment

⚠️ **Required:**
- **NEVER** use default credentials
- Use strong, unique passwords (12+ characters, mixed case, numbers, symbols)
- Store credentials in secrets management (Azure Key Vault, AWS Secrets Manager, etc.)
- Rotate credentials regularly
- Delete credentials file after first login
- Enable MFA/2FA when available
- Use HTTPS only
- Restrict admin access by IP if possible

❌ **Never:**
- Commit credentials to version control
- Use same password across environments
- Share admin credentials
- Store production credentials in `.env` files

## Troubleshooting

### Admin User Not Created

**Symptom:** Cannot log in to admin panel

**Solutions:**

1. Check container logs:
   ```bash
   docker-compose logs web-prod | grep ensure_admin
   ```

2. Manually run the command:
   ```bash
   docker-compose exec web-prod python manage.py ensure_admin
   ```

3. Verify environment variables:
   ```bash
   docker-compose exec web-prod env | grep DJANGO_SUPERUSER
   ```

### Credentials File Not Found

**Symptom:** `setup_data/admin_credentials.txt` doesn't exist

**Solutions:**

1. Check if directory exists:
   ```bash
   docker-compose exec web-prod ls -la /app/setup_data/
   ```

2. Manually create directory:
   ```bash
   docker-compose exec web-prod mkdir -p /app/setup_data
   ```

3. Run ensure_admin again:
   ```bash
   docker-compose exec web-prod python manage.py ensure_admin
   ```

### Password Not Working

**Symptom:** Correct username but password rejected

**Solutions:**

1. Check if environment variable is set:
   ```bash
   docker-compose exec web-prod env | grep DJANGO_SUPERUSER_PASSWORD
   ```

2. Reset password:
   ```bash
   docker-compose exec web-prod python manage.py changepassword admin
   ```

3. Recreate user:
   ```bash
   # Delete existing user (careful!)
   docker-compose exec web-prod python manage.py shell -c \
     "from django.contrib.auth import get_user_model; \
      get_user_model().objects.filter(username='admin').delete()"
   
   # Recreate
   docker-compose exec web-prod python manage.py ensure_admin
   ```

### Multiple Admin Users

**Symptom:** Multiple superusers exist

**Solution:**

The `ensure_admin` command only manages the user specified by `DJANGO_SUPERUSER_USERNAME`. Other superusers are not affected. To manage multiple admins:

```bash
# List all superusers
docker-compose exec web-prod python manage.py shell -c \
  "from django.contrib.auth import get_user_model; \
   print(list(get_user_model().objects.filter(is_superuser=True).values_list('username', flat=True)))"
```

## Examples

### Example 1: Development with Custom Credentials

```bash
# .env file
DJANGO_SUPERUSER_USERNAME=devadmin
DJANGO_SUPERUSER_EMAIL=dev@example.com
DJANGO_SUPERUSER_PASSWORD=DevPassword123!

# Start containers
docker-compose -f .devcontainer/docker-compose_dev.yml up -d

# View credentials
cat setup_data/admin_credentials.txt

# Login at http://localhost:8000/admin/
# Username: devadmin
# Password: DevPassword123!
```

### Example 2: Production with Azure Key Vault

```bash
# Create secrets in Azure Key Vault
az keyvault secret set --vault-name mykeyvault \
  --name django-admin-username --value "prodadmin"

az keyvault secret set --vault-name mykeyvault \
  --name django-admin-password --value "$(openssl rand -base64 32)"

# Configure Container App
az containerapp update \
  --name barodybroject \
  --resource-group myresourcegroup \
  --set-env-vars \
    "DJANGO_SUPERUSER_USERNAME=secretref:django-admin-username" \
    "DJANGO_SUPERUSER_PASSWORD=secretref:django-admin-password"

# Deploy
docker-compose up -d
```

### Example 3: CI/CD with GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Azure
        env:
          DJANGO_SUPERUSER_USERNAME: ${{ secrets.DJANGO_SUPERUSER_USERNAME }}
          DJANGO_SUPERUSER_EMAIL: ${{ secrets.DJANGO_SUPERUSER_EMAIL }}
          DJANGO_SUPERUSER_PASSWORD: ${{ secrets.DJANGO_SUPERUSER_PASSWORD }}
        run: |
          # Your deployment commands here
          docker-compose up -d
```

## Related Documentation

- [Installation Guide](../installation-wizard.md)
- [Docker Setup](../../README.md#docker-setup)
- [Security Documentation](../SECURITY_DOCUMENTATION.md)
- [Environment Configuration](../../.env.example)

## Support

If you encounter issues not covered in this documentation:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review container logs: `docker-compose logs`
3. Open an issue on GitHub with:
   - Your environment (dev/prod)
   - Docker compose file used
   - Relevant log output
   - Steps to reproduce

