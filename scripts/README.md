# Scripts Directory

This directory contains various scripts to help with deployment and management of the BarodyBroject application.

## 🚀 Quick Start

### Universal Setup Initializer

The easiest way to get started is using the **universal setup initializer** located in the project root:

```bash
# From the project root
./init_setup.sh
```

This interactive script will:
- ✅ Check all required dependencies
- 🔧 Configure your environment (.env setup)
- 📦 Set up Docker containers OR local environment
- 🗄️ Initialize the database
- 👤 Optionally create admin users
- ☁️ Deploy to Azure (if selected)
- 🧪 Run infrastructure tests

**Setup Modes Available:**
1. **Docker Development** (Recommended) - Containerized development with hot-reload
2. **Local Development** - Direct installation on your machine
3. **Azure Deployment** - Production deployment to Azure Container Apps
4. **Testing/CI** - Minimal setup for CI/CD pipelines

## Script Categories

### 🏁 Initialization Scripts

#### `../init_setup.sh` (Project Root)
**Purpose**: Main entry point for complete repository setup and initialization

**Features**:
- Multi-mode setup (Docker, Local, Azure, Testing)
- Dependency checking for all platforms (macOS, Linux, Windows)
- Interactive configuration with smart defaults
- Comprehensive error handling and logging
- Post-setup validation and next steps

**Usage**:
```bash
cd /path/to/barodybroject
./init_setup.sh
```

**Supported Platforms**:
- macOS (via Homebrew)
- Linux (Ubuntu/Debian, CentOS/RHEL)
- Windows (WSL2 recommended)

**Requirements**:
- Python 3.8+
- Git
- Docker (for containerized setup)
- Azure CLI (for Azure deployment)

## Azure Deployment Scripts

### `azure-deployment-setup.py`
Interactive Python script for setting up a new Azure deployment after running `azd up`. This comprehensive script handles:

- **Prerequisites Check**: Verifies Azure CLI and azd are installed and configured
- **Environment Discovery**: Automatically detects your Azure resources and configuration
- **Database Migrations**: Runs Django migrations to set up the database schema
- **Static Files**: Collects static files for proper CSS/JS serving
- **Admin User Creation**: Interactive creation of Django superuser accounts
- **CMS Setup**: Configures initial Django CMS pages and site settings
- **Health Checks**: Verifies the application is working correctly

**Usage:**
```bash
# From project root
python3 scripts/azure-deployment-setup.py

# Or use the wrapper script
./scripts/setup-deployment.sh
```

**Features:**
- Interactive prompts with colored output
- Error handling and recovery options
- Automatic resource detection
- Comprehensive health checks
- User-friendly progress indicators

### `setup-deployment.sh`
Simple shell script wrapper for the Python setup script. Provides basic environment checks and runs the main setup script.

**Usage:**
```bash
./scripts/setup-deployment.sh
```

### 🧪 Testing & Validation Scripts

#### `test-init-setup.sh` ⭐ **NEW**
**Purpose**: Automated test suite for the main initialization script

**Features**:
- 14 automated validation checks
- Syntax and structure verification
- Function existence validation
- Error handling verification
- Dependency checking logic validation
- 100% test coverage of init_setup.sh

**Usage**:
```bash
# Run automated tests
./scripts/test-init-setup.sh

# View test results
cat /tmp/init_setup_test_*.log
```

**What It Tests**:
- ✅ Script exists and is executable
- ✅ Bash syntax validation
- ✅ Correct shebang line
- ✅ Error handling (set -euo pipefail)
- ✅ All logging functions present
- ✅ Dependency checking functions
- ✅ Setup mode functions
- ✅ pip/pip3 detection logic
- ✅ OS detection functionality
- ✅ Color code definitions
- ✅ Log directory creation
- ✅ Cleanup handlers
- ✅ Error trap configuration

**Test Results**:
- Latest run: 14/14 tests passed (100%)
- See [Test Summary](../docs/TEST_SUMMARY.md) for detailed results
- See [Full Test Report](../docs/INIT_SETUP_TEST_RESULTS.md) for analysis

#### `test-infrastructure.sh`
**Purpose**: Comprehensive infrastructure testing for CI/CD and local validation

**Features**:
- Complete Docker orchestration testing
- Database connectivity and migration validation  
- Django service layer verification
- Installation wizard component testing
- Security and performance validation
- Web interface and API testing
- Full unit test suite execution (24/24 tests)

**Usage**:
```bash
# Full test suite
./scripts/test-infrastructure.sh

# Verbose output with detailed logging
./scripts/test-infrastructure.sh --verbose

# CI/CD mode (optimized for automation)
./scripts/test-infrastructure.sh --ci-mode

# Skip cleanup (useful for debugging)
./scripts/test-infrastructure.sh --skip-cleanup
```

**What It Tests**:
- ✅ Docker container health and networking
- ✅ PostgreSQL database connectivity
- ✅ Django migrations and ORM functionality
- ✅ Installation wizard services
- ✅ Admin user creation and authentication
- ✅ Token generation and validation
- ✅ Web views and form handling
- ✅ Management commands
- ✅ Security measures (CSRF, password validation)

**CI/CD Integration**:
- GitHub Actions workflow: `.github/workflows/infrastructure-test.yml`
- Automatic execution on push/PR to main/develop
- Daily scheduled testing (2 AM UTC)
- Comprehensive logging and artifact collection

See [Infrastructure Testing Guide](../docs/INFRASTRUCTURE_TESTING.md) for details.

#### `validate-cicd.sh`
**Purpose**: Validate CI/CD pipeline configuration and workflows

**Usage**:
```bash
./scripts/validate-cicd.sh
```

**Validates**:
- GitHub Actions workflow syntax
- Docker build configurations
- Environment variable setup
- Secret management
- Deployment pipelines

### 🛠️ Utility & Management Scripts

#### `version-manager.sh`
**Purpose**: Manage application versions and changelog generation

**Features**:
- Semantic versioning support (MAJOR.MINOR.PATCH)
- Automatic changelog generation from git commits
- Version bumping with git tagging
- Release note generation

**Usage**:
```bash
# Bump patch version (0.1.0 -> 0.1.1)
./scripts/version-manager.sh patch

# Bump minor version (0.1.0 -> 0.2.0)
./scripts/version-manager.sh minor

# Bump major version (0.1.0 -> 1.0.0)
./scripts/version-manager.sh major

# Show current version
./scripts/version-manager.sh current
```

#### `generate-readmes.py`
**Purpose**: Auto-generate README files for project directories

**Usage**:
```bash
python3 scripts/generate-readmes.py [directory]
```

**Features**:
- Scans directory structure
- Generates comprehensive README templates
- Includes file listings and descriptions
- Follows IT-Journey documentation standards

#### `add_current_ip_rule.py`
**Purpose**: Add your current IP address to Azure firewall rules

**Usage**:
```bash
python3 scripts/add_current_ip_rule.py
```

**Use Cases**:
- Troubleshooting Azure connectivity issues
- Temporary access to Azure resources
- Development environment setup

### 📦 Legacy & Specialized Scripts

#### `azure-setup.py`
**Legacy Azure setup script** - Consider using `azure-deployment-setup.py` instead for new deployments.

**Note**: Maintained for backward compatibility with older deployments.

#### `setup-azure.sh`
**Shell wrapper** for Azure resource provisioning. Use `azd up` or `init_setup.sh` for modern deployments.

#### `setup_aurora_serverless.py`
**AWS-specific script** for Aurora Serverless database setup.

**Note**: This project primarily targets Azure, but this script is available for AWS experiments or migrations.

## Prerequisites

Before running the Azure deployment scripts, ensure you have:

1. **Azure CLI** installed and configured
   ```bash
   # Install Azure CLI (macOS)
   brew install azure-cli
   
   # Login to Azure
   az login
   ```

2. **Azure Developer CLI (azd)** installed
   ```bash
   # Install azd (macOS)
   brew install azd
   ```

3. **Successful deployment** with `azd up`
   ```bash
   # Deploy the application first
   azd up
   ```

## Typical Workflow

1. **Initial Deployment**
   ```bash
   # Deploy infrastructure and application
   azd up
   ```

2. **Post-Deployment Setup**
   ```bash
   # Run the interactive setup script
   ./scripts/setup-deployment.sh
   ```

3. **Verification**
   - Visit your application URL
   - Log into the admin panel
   - Verify CMS functionality

## 🔄 Workflow Diagrams

### Complete Setup Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    Start Setup Process                       │
│                   (./init_setup.sh)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ├─→ Check Dependencies
                       │   ├─ Python 3.8+
                       │   ├─ Git
                       │   ├─ Docker (optional)
                       │   └─ Azure CLI (optional)
                       │
                       ├─→ Environment Configuration
                       │   └─ Create/Configure .env
                       │
                       ├─→ Select Setup Mode
                       │   │
┌──────────────────────┼───────────────────────┬──────────────┐
│                      │                       │              │
▼                      ▼                       ▼              ▼
Docker Development     Local Development      Azure Deploy   Testing
│                      │                       │              │
├─ Start containers    ├─ Create venv          ├─ az login   ├─ Install deps
├─ Run migrations      ├─ Install deps         ├─ azd up     ├─ Run tests
├─ Create superuser    ├─ Setup DB             ├─ Configure  └─ Validate
└─ Access at :8000     ├─ Collect static       └─ Post-setup
                       └─ Create superuser
```

### Infrastructure Testing Workflow

```
┌─────────────────────────────────────────────────────────────┐
│              Infrastructure Testing Pipeline                 │
│            (./scripts/test-infrastructure.sh)               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ├─→ Environment Setup
                       │   ├─ Start Docker containers
                       │   └─ Wait for service readiness
                       │
                       ├─→ Docker Infrastructure
                       │   ├─ Container status checks
                       │   ├─ Network connectivity
                       │   └─ Volume mount verification
                       │
                       ├─→ Database Testing
                       │   ├─ Django configuration
                       │   ├─ Database connection
                       │   └─ Run migrations
                       │
                       ├─→ Service Layer Testing
                       │   ├─ InstallationService init
                       │   ├─ Token generation/validation
                       │   └─ Business logic verification
                       │
                       ├─→ Admin User Testing
                       │   ├─ User creation
                       │   ├─ Permission validation
                       │   └─ Installation completion
                       │
                       ├─→ Web Interface Testing
                       │   ├─ View imports
                       │   ├─ Form validation
                       │   └─ Django test client
                       │
                       ├─→ Management Commands
                       │   ├─ Command availability
                       │   └─ Help text validation
                       │
                       ├─→ Unit Test Suite
                       │   └─ 24/24 tests execution
                       │
                       └─→ Security & Performance
                           ├─ Token security
                           └─ Password validation
```

### Azure Deployment Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                  Azure Deployment Process                    │
│                   (azd up + post-setup)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ├─→ Authentication
                       │   └─ az login / azd auth login
                       │
                       ├─→ Resource Provisioning
                       │   ├─ Container Apps Environment
                       │   ├─ PostgreSQL Flexible Server
                       │   ├─ Key Vault (secrets)
                       │   ├─ Container Registry
                       │   └─ Application Insights
                       │
                       ├─→ Application Deployment
                       │   ├─ Build Docker image
                       │   ├─ Push to registry
                       │   └─ Deploy to Container Apps
                       │
                       ├─→ Post-Deployment Setup
                       │   │  (./scripts/azure-deployment-setup.py)
                       │   │
                       │   ├─ Environment Configuration
                       │   │  ├─ Dev/Staging/Production
                       │   │  └─ Custom domain (optional)
                       │   │
                       │   ├─ Database Setup
                       │   │  └─ Run migrations
                       │   │
                       │   ├─ Static Files
                       │   │  └─ Collect static
                       │   │
                       │   ├─ Admin User
                       │   │  └─ Create superuser
                       │   │
                       │   ├─ Production Config (if prod)
                       │   │  ├─ SSL/HTTPS enforcement
                       │   │  ├─ Security headers
                       │   │  ├─ Custom domain setup
                       │   │  └─ Certificate configuration
                       │   │
                       │   └─ Health Checks
                       │       ├─ Application response
                       │       └─ Admin panel access
                       │
                       └─→ Deployment Complete
                           └─ Print access URLs
```

## 🔧 Troubleshooting

### Common Setup Issues

#### **Issue**: Script can't find dependencies

**Symptoms**:
- Error: "python3: command not found"
- Error: "docker: command not found"

**Solutions**:
1. Verify installation: `which python3 docker git`
2. Check PATH environment variable
3. Reinstall missing dependencies using package manager
4. For Docker: Ensure Docker Desktop is running

**macOS**:
```bash
brew install python3 git docker
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip git docker.io
```

#### **Issue**: Environment configuration problems

**Symptoms**:
- Error: ".env file not found"
- Error: "SECRET_KEY is required"
- Database connection errors

**Solutions**:
1. Create .env from template:
   ```bash
   cp .env.example .env
   ```

2. Generate secure SECRET_KEY:
   ```python
   python3 -c "import secrets; print(secrets.token_urlsafe(50))"
   ```

3. Configure required variables:
   - `SECRET_KEY` - Generated secure string
   - `DB_PASSWORD` - Secure database password
   - `OPENAI_API_KEY` - From OpenAI platform
   - `ALLOWED_HOSTS` - Add your domains

4. Verify configuration:
   ```bash
   cd src && python manage.py check
   ```

#### **Issue**: Docker container issues

**Symptoms**:
- Containers won't start
- Port conflicts (address already in use)
- Database connection refused

**Solutions**:

1. **Check Docker daemon**:
   ```bash
   docker info
   ```
   If fails: Start Docker Desktop application

2. **Port conflicts**:
   ```bash
   # Find process using port
   lsof -i :8000
   
   # Change ports in .env
   DJANGO_DEV_PORT=8001
   POSTGRES_PORT=5433
   ```

3. **Database connection**:
   ```bash
   # Check database health
   docker-compose exec barodydb pg_isready -U postgres
   
   # Restart database
   docker-compose restart barodydb
   
   # Fresh start (⚠️ deletes data)
   docker-compose down -v
   docker-compose up -d
   ```

4. **View logs**:
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f python
   docker-compose logs -f barodydb
   ```

#### **Issue**: Azure deployment failures

**Symptoms**:
- `azd up` fails
- Resource provisioning errors
- Authentication problems

**Solutions**:

1. **Check Azure login**:
   ```bash
   az account show
   az login  # If not logged in
   ```

2. **Verify subscription**:
   ```bash
   az account list
   az account set --subscription <subscription-id>
   ```

3. **Check resource availability**:
   ```bash
   # Check region availability
   az account list-locations --output table
   
   # Check resource provider registration
   az provider show --namespace Microsoft.App --query registrationState
   ```

4. **Review deployment logs**:
   ```bash
   # View azd logs
   azd show
   
   # Check Container App logs
   az containerapp logs show --name <app-name> --resource-group <rg-name>
   ```

5. **Clean up and retry**:
   ```bash
   azd down  # Remove all resources
   azd up    # Start fresh deployment
   ```

#### **Issue**: Database migration errors

**Symptoms**:
- Migration conflicts
- "Table already exists" errors
- Unapplied migrations

**Solutions**:

1. **Check migration status**:
   ```bash
   python manage.py showmigrations
   ```

2. **Fake initial migration** (if table exists):
   ```bash
   python manage.py migrate --fake-initial
   ```

3. **Reset migrations** (⚠️ development only):
   ```bash
   # Remove migration files (except __init__.py)
   find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
   find . -path "*/migrations/*.pyc" -delete
   
   # Recreate migrations
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Database reset** (⚠️ deletes all data):
   ```bash
   # For Docker
   docker-compose down -v
   docker-compose up -d
   python manage.py migrate
   
   # For local SQLite
   rm db.sqlite3
   python manage.py migrate
   ```

#### **Issue**: Permission and authentication errors

**Symptoms**:
- "Permission denied" errors
- Azure resource access denied
- Docker socket connection refused

**Solutions**:

1. **Script permissions**:
   ```bash
   chmod +x init_setup.sh
   chmod +x scripts/*.sh
   ```

2. **Docker permissions (Linux)**:
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker  # Or logout/login
   ```

3. **Azure permissions**:
   - Verify subscription access
   - Check resource group permissions
   - Ensure proper RBAC roles

4. **File ownership**:
   ```bash
   # Fix ownership issues
   sudo chown -R $USER:$USER .
   ```

### Infrastructure Testing Issues

#### **Issue**: Tests failing in CI/CD

**Symptoms**:
- Tests pass locally but fail in CI
- Timeout errors in GitHub Actions
- Missing dependencies

**Solutions**:

1. **Check CI environment**:
   ```bash
   # Run in CI mode locally
   ./scripts/test-infrastructure.sh --ci-mode
   ```

2. **Review GitHub Actions logs**:
   - Navigate to Actions tab in GitHub
   - Check workflow run details
   - Review artifact uploads

3. **Verify test configuration**:
   ```bash
   # Ensure test settings exist
   cat src/barodybroject/test_settings.py
   ```

4. **Network issues**:
   - Check Docker network configuration
   - Verify inter-container connectivity
   - Ensure proper service dependencies

### Getting Help

If you encounter issues not covered here:

#### 📚 **Documentation Resources**:
- [Main README](../README.md) - Project overview
- [Infrastructure Testing Guide](../docs/INFRASTRUCTURE_TESTING.md)
- [Configuration Documentation](../docs/configuration/)
- [Changelog](../docs/changelog/CHANGELOG.md)

#### 🔍 **Diagnostic Commands**:
```bash
# System info
./init_setup.sh  # Run dependency check

# Docker diagnostics
docker-compose ps
docker-compose logs -f
docker system df

# Azure diagnostics
az account show
azd env get-values
az containerapp show --name <app> --resource-group <rg>

# Application diagnostics
cd src && python manage.py check --deploy
python manage.py test --settings=barodybroject.test_settings
```

#### 🐛 **Issue Reporting**:
1. Check [existing issues](https://github.com/bamr87/barodybroject/issues)
2. Review logs in `logs/` directory
3. Run diagnostics with `--verbose` flag
4. Create new issue with:
   - Operating system and version
   - Python version
   - Docker version (if applicable)
   - Complete error message
   - Steps to reproduce

#### 💬 **Support Channels**:
- GitHub Issues: [barodybroject/issues](https://github.com/bamr87/barodybroject/issues)
- Email: bamr87@users.noreply.github.com

## 🚀 CI/CD Integration

### GitHub Actions Workflows

The repository includes automated testing and validation workflows:

#### **Infrastructure Testing Workflow**

Location: `.github/workflows/infrastructure-test.yml`

Triggers:
- Push to `main` branch
- Pull requests to `main`
- Manual dispatch (`workflow_dispatch`)

Test Matrix:
- Python versions: 3.8, 3.9, 3.10, 3.11, 3.12
- Operating systems: Ubuntu (Linux), macOS, Windows

**What it tests**:
```yaml
✓ Docker infrastructure setup
✓ PostgreSQL database connectivity
✓ Django migrations
✓ InstallationService functionality
✓ Token generation/validation
✓ Admin user creation
✓ Web interface (views, forms)
✓ Management commands
✓ Full unit test suite (24 tests)
✓ Security validation
```

**Running locally**:
```bash
# Simulate CI environment
./scripts/test-infrastructure.sh --ci-mode

# With coverage
./scripts/test-infrastructure.sh --ci-mode --with-coverage
```

#### **Validation Workflow**

For pre-deployment validation:

```bash
# Run all CI/CD checks
./scripts/validate-cicd.sh

# Validate specific environment
./scripts/validate-cicd.sh --env production
```

### Automated Deployment Pipeline

**Development Workflow**:
```
Developer Push → GitHub Actions → Test Suite → Build → Deploy to Dev
```

**Production Workflow**:
```
Pull Request → Review → Merge → GitHub Actions → Test Suite → Build → Deploy to Production
```

### Setting Up CI/CD

#### **GitHub Actions Secrets**

Configure these secrets in your GitHub repository:

```bash
# Azure Credentials (for deployment)
AZURE_CREDENTIALS        # Service principal JSON
AZURE_SUBSCRIPTION_ID    # Azure subscription ID
AZURE_RESOURCE_GROUP     # Resource group name

# Application Secrets
DJANGO_SECRET_KEY        # Django secret key
DB_PASSWORD              # Database password
OPENAI_API_KEY          # OpenAI API key (if using AI features)

# Azure Container App
AZURE_CONTAINER_APP_NAME # Container app name
AZURE_REGISTRY_USERNAME  # Container registry username
AZURE_REGISTRY_PASSWORD  # Container registry password
```

#### **Setting Secrets via CLI**:

```bash
# Using GitHub CLI
gh secret set AZURE_CREDENTIALS < azure-credentials.json
gh secret set DJANGO_SECRET_KEY --body "your-secret-key"

# List existing secrets
gh secret list
```

#### **Azure Service Principal Setup**:

```bash
# Create service principal for GitHub Actions
az ad sp create-for-rbac \
  --name "github-actions-barodybroject" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} \
  --sdk-auth

# Output will be JSON - save as AZURE_CREDENTIALS secret
```

### Monitoring and Maintenance

#### **Log Monitoring**:
```bash
# View recent workflow runs
gh run list --limit 10

# View specific run logs
gh run view <run-id> --log

# Watch live logs
gh run watch
```

#### **Health Checks**:
```bash
# Application health
curl -I https://your-app.azurecontainerapps.io/health/

# Database health
az containerapp exec --name <app> --resource-group <rg> \
  --command "python manage.py check --database default"

# View application insights
az monitor app-insights component show --app <app-insights-name> --resource-group <rg>
```

## 📋 Best Practices

### Development Workflow

1. **Always use the initialization script** (`./init_setup.sh`) for new setups
   - Ensures consistent environment across team members
   - Automates dependency checking and installation
   - Provides interactive guidance for configuration

2. **Start with Docker Development mode**:
   ```bash
   ./init_setup.sh
   # Select: 1) Docker Development Setup
   ```
   - Closest to production environment
   - Includes hot-reload for rapid development
   - Isolated dependencies prevent conflicts

3. **Test locally before pushing**:
   ```bash
   # Run full test suite
   docker-compose exec python python manage.py test
   
   # Run infrastructure tests
   ./scripts/test-infrastructure.sh
   
   # Run with coverage
   docker-compose exec python pytest --cov=parodynews
   ```

### Security Best Practices

1. **Never commit sensitive data**:
   - `.env` files
   - API keys
   - Passwords
   - Secret keys
   - Azure credentials

2. **Use strong secrets**:
   ```bash
   # Generate secure SECRET_KEY
   python3 -c "import secrets; print(secrets.token_urlsafe(50))"
   
   # Generate secure DB password
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Rotate credentials regularly**:
   - Change `SECRET_KEY` between environments
   - Rotate database passwords quarterly
   - Update API keys when team members change
   - Use Azure Key Vault for production secrets

4. **Enable production security**:
   ```bash
   # Enforce HTTPS
   SECURE_SSL_REDIRECT=True
   
   # Security headers
   SECURE_HSTS_SECONDS=31536000
   SECURE_CONTENT_TYPE_NOSNIFF=True
   SECURE_BROWSER_XSS_FILTER=True
   ```

### Version Control

1. **Use semantic versioning**:
   ```bash
   # Update version for releases
   ./scripts/version-manager.sh patch  # 1.0.0 → 1.0.1
   ./scripts/version-manager.sh minor  # 1.0.1 → 1.1.0
   ./scripts/version-manager.sh major  # 1.1.0 → 2.0.0
   ```

2. **Tag releases**:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

3. **Document changes**:
   - Update `docs/changelog/CHANGELOG.md`
   - Include migration notes for breaking changes
   - Document new environment variables

### Deployment Strategy

1. **Deploy to staging first**:
   ```bash
   # Deploy to staging environment
   azd deploy --environment staging
   
   # Run post-deployment setup
   ./scripts/azure-deployment-setup.py
   # Select: 2) Staging/Preview Environment
   
   # Test thoroughly
   # Promote to production only after validation
   ```

2. **Use database backups**:
   ```bash
   # Azure PostgreSQL backup (automatic)
   az postgres flexible-server backup list \
     --resource-group <rg> \
     --name <server-name>
   
   # Manual backup
   docker-compose exec barodydb pg_dump -U postgres parody > backup.sql
   ```

3. **Monitor post-deployment**:
   ```bash
   # Check application logs
   docker-compose logs -f python
   
   # Azure logs
   az containerapp logs show --name <app> --resource-group <rg>
   
   # Health check
   curl -I https://your-app.azurecontainerapps.io/health/
   ```

### Code Quality

1. **Run linters before committing**:
   ```bash
   # Python code quality
   docker-compose exec python flake8 parodynews/
   docker-compose exec python black parodynews/ --check
   docker-compose exec python mypy parodynews/
   ```

2. **Maintain test coverage**:
   ```bash
   # Aim for >80% coverage
   docker-compose exec python pytest --cov=parodynews --cov-report=html
   open htmlcov/index.html
   ```

3. **Document code changes**:
   - Add docstrings to functions and classes
   - Update README for new features
   - Document configuration changes in `.env.example`

### Performance Optimization

1. **Use database connection pooling**:
   ```python
   # settings.py
   DATABASES = {
       'default': {
           'CONN_MAX_AGE': 600,  # Keep connections alive
       }
   }
   ```

2. **Enable caching**:
   ```bash
   # Redis for production
   CACHE_BACKEND=django_redis.cache.RedisCache
   CACHE_LOCATION=redis://redis:6379/1
   ```

3. **Optimize static files**:
   ```bash
   # Collect and compress static files
   python manage.py collectstatic --no-input
   python manage.py compress
   ```

### Troubleshooting Strategy

1. **Check logs systematically**:
   ```bash
   # Application logs
   tail -f logs/django.log
   
   # Database logs
   docker-compose logs barodydb
   
   # All services
   docker-compose logs -f
   ```

2. **Use Django shell for debugging**:
   ```bash
   docker-compose exec python python manage.py shell
   
   # Test database connection
   from django.db import connection
   connection.ensure_connection()
   print("Connected:", connection.is_usable())
   ```

3. **Enable debug mode temporarily**:
   ```bash
   # .env (development only!)
   DEBUG=True
   DJANGO_LOG_LEVEL=DEBUG
   ```

## 📚 Additional Resources

### Documentation

- [Main README](../README.md) - Project overview and quick start
- [Infrastructure Testing Guide](../docs/INFRASTRUCTURE_TESTING.md) - Comprehensive testing documentation
- [Security Documentation](../docs/SECURITY_DOCUMENTATION.md) - Security best practices
- [Changelog](../docs/changelog/CHANGELOG.md) - Version history and changes

### External Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure Developer CLI](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Support

For issues, questions, or contributions:

- **GitHub Issues**: [barodybroject/issues](https://github.com/bamr87/barodybroject/issues)
- **Discussions**: [barodybroject/discussions](https://github.com/bamr87/barodybroject/discussions)
- **Email**: bamr87@users.noreply.github.com

## Contributing

When adding new scripts:

1. Follow the existing naming conventions
2. Add appropriate error handling
3. Include usage documentation
4. Make scripts executable: `chmod +x script-name.py`
5. Update this README with script descriptions

---

**Last Updated**: 2025-01-27  
**Version**: 2.0.0  
**Maintainer**: barodybroject team
