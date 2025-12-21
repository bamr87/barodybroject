# 🔐 Admin Credentials Quick Start

## TL;DR

**Django admin credentials are now automatically created when you start Docker containers!**

### Default Credentials (Development)

```
URL:      http://localhost:8000/admin/
Username: admin
Password: admin
```

**Credentials saved to:** `setup_data/admin_credentials.txt`

---

## Quick Start

### Option 1: Use Defaults (Fastest)

```bash
# Start containers
docker-compose -f .devcontainer/docker-compose_dev.yml up -d

# Login at http://localhost:8000/admin/
# Username: admin
# Password: admin

# View saved credentials
cat setup_data/admin_credentials.txt
```

### Option 2: Custom Credentials (Recommended)

```bash
# Create .env file
cp .env.example .env

# Edit credentials in .env
nano .env
# Change these lines:
#   DJANGO_SUPERUSER_USERNAME=myadmin
#   DJANGO_SUPERUSER_PASSWORD=MySecurePass123!

# Start containers
docker-compose -f .devcontainer/docker-compose_dev.yml up -d

# Login with your custom credentials
```

---

## Where to Find Credentials

### 1. Environment Variables

Check your `.env` file:

```bash
cat .env | grep DJANGO_SUPERUSER
```

### 2. Saved Credentials File

```bash
cat setup_data/admin_credentials.txt
```

### 3. Container Logs

```bash
docker-compose -f .devcontainer/docker-compose_dev.yml logs python | grep -A 5 "Admin Credentials"
```

---

## Production Setup

**⚠️ IMPORTANT: Never use default credentials in production!**

### Using GitHub Secrets

1. Go to: Repository → Settings → Secrets → Actions
2. Add these secrets:
   - `DJANGO_SUPERUSER_USERNAME`
   - `DJANGO_SUPERUSER_EMAIL`
   - `DJANGO_SUPERUSER_PASSWORD`

3. Deploy - credentials will be used automatically

### Using Azure Key Vault

```bash
# Store in Key Vault
az keyvault secret set --vault-name mykeyvault \
  --name django-admin-password --value "$(openssl rand -base64 32)"

# Reference in Container App
az containerapp update \
  --name barodybroject \
  --set-env-vars "DJANGO_SUPERUSER_PASSWORD=secretref:django-admin-password"
```

---

## Troubleshooting

### Can't login?

```bash
# Check what credentials were created
cat setup_data/admin_credentials.txt

# Or check environment variables
docker-compose exec python env | grep DJANGO_SUPERUSER
```

### Forgot password?

```bash
# Restart containers (recreates admin with env vars)
docker-compose down
docker-compose up -d

# Or manually reset
docker-compose exec python python manage.py changepassword admin
```

### Credentials file missing?

```bash
# Manually run the command
docker-compose exec python python manage.py ensure_admin
```

---

## Full Documentation

- **Configuration Guide:** [docs/configuration/admin-credentials.md](docs/configuration/admin-credentials.md)
- **Implementation Details:** [docs/ADMIN_CREDENTIALS_SETUP.md](docs/ADMIN_CREDENTIALS_SETUP.md)
- **Main README:** [README.md](README.md#docker-admin-credentials)

---

## Security Checklist

### Development ✅
- [x] Default credentials are fine
- [x] `.env` is in `.gitignore`
- [x] Credentials file is in `.gitignore`

### Production ⚠️
- [ ] Changed default password
- [ ] Using secrets management (GitHub/Azure)
- [ ] Deleted credentials file after first login
- [ ] Using HTTPS only
- [ ] Enabled MFA/2FA (if available)

---

**Questions?** Check the [full documentation](docs/configuration/admin-credentials.md) or open an issue.

