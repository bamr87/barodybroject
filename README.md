# Parody News Generator

A Django-based web application integrated with OpenAI to generate AI-powered parody news content. This project combines modern web development practices with artificial intelligence to create a platform for generating and managing satirical news articles.

> � **Successfully Deployed on Azure Container Apps!** This application is now live and running in production. See [DEPLOYMENT-SUCCESS.md](DEPLOYMENT-SUCCESS.md) for deployment details and [DEPLOYMENT-GUIDE-MINIMAL.md](DEPLOYMENT-GUIDE-MINIMAL.md) for setup instructions.

> �👨‍💻 **Developers**: Looking for a quick technical setup? See the [Developer Guide](.github/README.md) for concise commands and architecture overview. For critical insights (don't read!), check [DONTREADME.md](DONTREADME.md).

**AI Development Notes**: This README centralizes all repo contents into a comprehensive narrative. Explore the codebase, understand AI integrations, document changes, manage machines (infrastructure), and handle everything else through this hub.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture & Design Patterns](#architecture--design-patterns)
- [Configuration & Environment](#configuration--environment)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [Docker Setup](#docker-setup)
- [Azure Deployment](#azure-deployment)
- [Deployment Success](#deployment-success)
- [Cost Optimization](#cost-optimization)
- [Testing](#testing)
- [Development Container Workflow](#development-container-workflow)
- [Contributing](#contributing)
- [Changelog](#changelog)
- [License](#license)
- [Screenshots](#screenshots)
- [Meta-Notes: AAR Recursion Applied](#meta-notes-aar-recursion-applied)

## Features

## Features

### Core Features

- **AI-Powered Content Generation**: Leverages OpenAI APIs to generate parody news articles with customizable prompts
- **User Authentication**: Complete user management with registration, login, logout, and password management
- **Dynamic Content Management**: Django admin interface for managing content, users, and site settings
- **RESTful API**: Full-featured API for programmatic interaction with application data
- **Responsive Design**: Bootstrap 5.3.3-based responsive UI that adapts to various screen sizes
- **Blog Module**: Integrated blog with categories, tags, and content management
- **Search Functionality**: Built-in search for finding content across the site
- **Security Features**: Django's built-in security protections against XSS, CSRF, SQL Injection, and more

### Advanced Features

- **Dynamic Form Support**: Reusable Django forms with validation and error handling
- **Streamlined Templates**: Clean Django template system with Bootstrap integration
- **Jekyll Static Site Generation**: Integrated Jekyll for static content and blog publishing
- **Enhanced Navigation**: YAML-based navigation and UI text management
- **GitHub Automation**: AI-assisted GitHub issue handling and repository management
- **Email Integration**: Django email support for notifications and user communications
- **Docker-First Development**: Complete containerization for consistent environments
- **Azure Cloud Deployment**: Production-ready deployment on Azure Container Apps

### Recent Updates (v0.2.0)
- **✅ Successful Azure Deployment**: Live production deployment on Azure Container Apps
- **🔧 Streamlined Architecture**: Removed CMS dependencies for simplified deployment and maintenance
- **💰 Cost Optimization**: Minimal cost infrastructure with Bicep templates
- **📚 Comprehensive Documentation**: Complete deployment guides and troubleshooting resources

## Technology Stack

### Backend Framework & Tools

- **Django 4.2.20**: High-level Python web framework for rapid development
- **Django REST Framework**: Powerful toolkit for building Web APIs
- **Python 3.8+**: Primary programming language
- **Gunicorn**: WSGI HTTP server for production deployment

### Frontend & UI

- **Bootstrap 5.3.3**: Responsive front-end toolkit for modern web design
- **jQuery**: JavaScript library for DOM manipulation (optional)
- **Pure Django Templates**: Streamlined template system without CMS dependencies

### Databases

- **PostgreSQL**: Database for development, testing, and production

### Infrastructure & Deployment

- **Docker & Docker Compose**: Containerization for consistent development and deployment
- **Azure Container Apps**: ✅ **Successfully Deployed** - Cloud container hosting service
- **Azure Developer CLI (azd)**: Tool for provisioning and deploying Azure resources
- **Azure Bicep**: Infrastructure as Code (IaC) for Azure resources
- **Azure Application Insights**: Monitoring and diagnostics
- **Jekyll**: Static site generator for blog content

### AI Integration

- **OpenAI API**: Access to GPT models for content generation
- **Custom OpenAI Integration**: Configurable AI services for specialized content creation

### Testing & Quality Assurance

- **Pytest**: Python testing framework
- **Pytest-Django**: Django plugin for pytest
- **Playwright**: End-to-end browser testing
- **Selenium**: Web automation and testing
- **Coverage.py**: Code coverage measurement
- **Ruff**: Fast Python linter

### Development Tools

- **Git & GitHub**: Version control and collaboration
- **VS Code**: Recommended IDE with Dev Container support
- **GitHub Codespaces**: Cloud-based development environments
- **Sphinx**: Documentation generation

## Architecture & Design Patterns

### Core Patterns

**MVC (Model-View-Controller)**
- Clear separation of concerns with Django models, views, and templates
- Models define data structure and business logic
- Views handle request/response logic
- Templates manage presentation layer

**RESTful API Design**
- Django REST Framework for structured API endpoints
- Serializers for data validation and transformation
- ViewSets for consistent CRUD operations
- Token-based authentication support

**Template Management**
- Django templating system with inheritance and includes
- Bootstrap integration for responsive layouts
- Custom template tags and filters
- Context processors for global template variables

### Infrastructure Patterns

**Infrastructure as Code (IaC)**
- Azure Bicep files for cloud resource provisioning
- Declarative infrastructure definitions
- Version-controlled infrastructure changes
- Automated deployment pipelines

**Containerization**
- Multi-stage Dockerfiles for optimized images
- Docker Compose for local development orchestration
- Separate containers for app, database, and Jekyll services
- Volume mounts for hot-reload development

### Security & Best Practices

**Security Features**
- Django built-in protections (XSS, CSRF, SQL Injection)
- Secure password hashing with PBKDF2
- HTTPS enforcement in production
- Content Security Policy headers
- DKIM email authentication

**Middleware & Context Processors**
- Custom middleware for authentication and request processing
- Context processors for CMS integration
- Localization support via Django's i18n framework

**Logging & Monitoring**
- Azure Application Insights integration
- Structured logging throughout the application
- Performance metrics collection
- Error tracking and alerting

## Configuration & Environment

### Enterprise-Grade Configuration Management

Barodybroject features a completely optimized Django configuration system designed for enterprise production deployment while maintaining excellent developer experience.

**Key Configuration Features:**
- **12-Factor App Compliance**: All configuration through environment variables
- **Multi-Environment Support**: Development, staging, and production configurations
- **AWS Secrets Manager Integration**: Secure production secrets management
- **Environment Auto-Detection**: Intelligent environment detection and configuration
- **Security-First Design**: Secure defaults with development overrides
- **Performance Optimization**: Production-tuned caching, database, and static file settings

### Environment Profiles

#### Development Environment
- **Database**: PostgreSQL
- **Caching**: Local memory cache for fast development
- **Security**: Relaxed settings for easy debugging
- **Email**: Console backend for testing
- **Debug Tools**: Optional Django Debug Toolbar support

#### Production Environment  
- **Database**: PostgreSQL with connection pooling and SSL
- **Caching**: Redis with intelligent database fallback
- **Security**: Enterprise-grade security headers and HTTPS enforcement
- **Email**: AWS SES with DKIM authentication
- **Monitoring**: Comprehensive structured logging with JSON formatting
- **Static Files**: Optimized static file serving with manifest storage

### Configuration Documentation

For comprehensive configuration guidance, see our detailed documentation:

- **[Django Settings Optimization Guide](./docs/configuration/settings-optimization.md)** - Complete 100+ page configuration guide
- **[Environment Configuration Reference](./docs/configuration/environment-config.md)** - Environment variable reference and validation
- **[Security Configuration Guide](./docs/configuration/security-config.md)** - Security best practices and implementation
- **[Performance Configuration Guide](./docs/configuration/performance-config.md)** - Performance optimization strategies

### Quick Configuration Setup

#### Development Setup
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables for development
RUNNING_IN_PRODUCTION=False
DEBUG=True
DB_CHOICE=postgres
```

#### Production Deployment
```bash
# Set production environment variables
RUNNING_IN_PRODUCTION=True
DEBUG=False
SECRET_KEY=your-ultra-secure-secret-key
DB_PASSWORD=your-secure-database-password
AWS_ACCESS_KEY_ID=your-aws-access-key
REDIS_URL=redis://your-redis-host:6379/1
```

### Configuration Validation

```bash
# Validate development configuration
python manage.py check

# Validate production deployment configuration  
python manage.py check --deploy

# Test environment variable loading
python scripts/validate_env.py production
```

## Project Structure

```
barodybroject/
├── docs/                       # Comprehensive project documentation
│   ├── configuration/          # Django configuration documentation
│   │   ├── README.md           # Configuration documentation overview
│   │   ├── settings-optimization.md # Complete Django settings guide (100+ pages)
│   │   ├── environment-config.md    # Environment variable reference
│   │   ├── security-config.md       # Security configuration guide
│   │   └── performance-config.md    # Performance optimization guide
│   └── changelog/              # Change documentation and templates
│       ├── README.md           # Documentation system overview
│       ├── CHANGELOG.md        # Main project changelog
│       ├── CONTRIBUTING_CHANGES.md # Change contribution guidelines
│       ├── templates/          # Standardized change templates
│       ├── releases/           # Release-specific documentation
│       ├── summaries/          # Date-organized change summaries
│       └── archive/            # Historical documentation files
├── infra/                      # Azure infrastructure as code (Bicep)
│   ├── main.bicep             # Main infrastructure definition
│   ├── app/                   # Application-specific resources
│   └── shared/                # Shared resources (Key Vault, monitoring, etc.)
├── scripts/                    # Deployment and automation scripts
│   ├── azure-setup.py         # Azure setup automation
│   └── version-manager.sh     # Version management
├── src/                       # Django application source code
│   ├── barodybroject/         # Django project settings
│   │   ├── settings.py        # Enterprise-grade application configuration (950+ lines)
│   │   ├── urls.py            # URL routing
│   │   └── wsgi.py            # WSGI application entry point
│   ├── parodynews/            # Main Django app
│   │   ├── models.py          # Data models
│   │   ├── views.py           # View logic
│   │   ├── urls.py            # App-specific URLs
│   │   ├── forms.py           # Form definitions
│   │   ├── admin.py           # Admin interface customization
│   │   ├── templates/         # HTML templates
│   │   ├── management/        # Custom Django management commands
│   │   ├── tests/             # Unit and integration tests
│   │   └── utils/             # Utility functions
│   ├── pages/                 # Jekyll static site content
│   │   ├── _posts/            # Blog posts (59 articles)
│   │   └── _config.yml        # Jekyll configuration
│   ├── static/                # Static files (CSS, JS, images)
│   ├── requirements.txt       # Python dependencies
│   ├── manage.py              # Django management script
│   └── Dockerfile             # Application container definition
├── docker-compose.yml         # Local development orchestration
├── azure.yaml                 # Azure Developer CLI configuration
├── pyproject.toml             # Python project metadata
├── requirements-dev.txt       # Development dependencies
├── README.md                  # This file
├── CONTRIBUTING.md            # Contribution guidelines
├── LICENSE                    # MIT License
└── VERSION                    # Current version (0.1.0)
```

### Key Directories Explained

- **docs/changelog/**: Comprehensive change documentation system with templates, guidelines, and historical records
- **infra/**: Contains all Azure infrastructure definitions using Bicep templates for repeatable deployments
- **src/parodynews/**: The main Django application with all business logic, models, and views
- **src/pages/**: Jekyll-based static site with blog posts and documentation
- **src/static/**: Collected static files including admin, CMS, and custom assets
- **scripts/**: Automation scripts for deployment, setup, and maintenance

## Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python 3.8+**: Primary development language
- **pip**: Python package manager (usually comes with Python)
- **Git**: Version control system
- **GitHub CLI** (optional): For streamlined GitHub operations
- **virtualenv**: For creating isolated Python environments (recommended)
- **Docker & Docker Compose**: For containerized development (optional but recommended)
- **Azure CLI**: For Azure deployments (if deploying to Azure)
- **Node.js**: For Jekyll static site generation (optional)

## Installation & Setup

### Quick Start

1. **Set Naming Parameters**

```bash
GH_USER=bamr87
GH_REPO=barodybroject
GH_HOME=~/github
GH_REPO_DIR=${GH_HOME}/${GH_REPO}
PY_VENV=.venv
```

2. **Clone the Repository**

```bash
cd $GH_HOME
gh repo clone ${GH_USER}/${GH_REPO} ${GH_REPO_DIR}
cd ${GH_REPO_DIR}
```

Or using git directly:

```bash
cd $GH_HOME
git clone https://github.com/${GH_USER}/${GH_REPO}.git
cd ${GH_REPO_DIR}
```

3. **Create a Virtual Environment**

For Unix/Linux/Mac:
```bash
python3 -m venv $PY_VENV
source $PY_VENV/bin/activate
```

For Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```

4. **Install Dependencies**

```bash
pip install -r requirements-dev.txt
```

5. **Set Up Environment Variables**

Create a `.env` file in the project root:

```bash
cd ${GH_REPO_DIR}
touch .env
```

Add the following environment variables:

```plaintext
# Application Settings
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production

# Database Configuration (local development)
# PostgreSQL
DB_HOST=localhost
DB_NAME=barodydb
DB_USERNAME=postgres
DB_PASSWORD=postgres
POSTGRES_PORT=5432

# Container App Settings (Azure)
CONTAINER_APP_NAME=barodybroject
CONTAINER_APP_ENV_DNS_SUFFIX=localhost

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Email Settings (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Jekyll Settings
JEKYLL_ENV=development
```

6. **Database Migrations**

Navigate to the source directory and run migrations:

```bash
cd src
python manage.py makemigrations
python manage.py migrate
```

7. **Create a Superuser (Optional)**

To access the Django admin interface:

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

**Note:** When using Docker, admin credentials are automatically created. See the [Docker Admin Credentials](#docker-admin-credentials) section below.

8. **Run the Development Server**

```bash
python manage.py runserver
```

Visit [http://localhost:8000](http://localhost:8000) to view the application.

## Running the Application

### Local Development

After completing the installation steps, run the Django development server:

```bash
cd src
python manage.py runserver
```

The application will be available at:
- **Django App**: [http://localhost:8000](http://localhost:8000)
- **Admin Interface**: [http://localhost:8000/admin](http://localhost:8000/admin)
- **API Root**: [http://localhost:8000/api](http://localhost:8000/api)

### With PostgreSQL (Local)

1. Install PostgreSQL:
```bash
# macOS
brew install postgresql
brew services start postgresql@14

# Linux (Debian/Ubuntu)
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

2. Create a database:
```bash
createdb barodydb
```

3. Update your `.env` file with PostgreSQL settings:
```plaintext
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/barodydb
DB_HOST=localhost
DB_NAME=barodydb
DB_USERNAME=postgres
DB_PASSWORD=your_password
```

4. Run migrations and start the server as usual.

## Docker Setup

### Unified Docker Configuration

The project uses a **unified Docker Compose configuration** that supports multiple environments through profiles:

**Available Environments:**
- **Development** (default): Django development server with hot reload
- **Production**: Gunicorn-based production server
- **Jekyll**: Static site generation alongside Django

### Quick Start

#### Development Environment (Default)

```bash
# Start development environment
docker-compose -f .devcontainer/docker-compose_dev.yml up -d

# View the application
open http://localhost:8000
```

**Admin Access:** Default credentials are automatically created:
- **Username:** `admin`
- **Password:** `admin`
- **Admin URL:** http://localhost:8000/admin/

See [Docker Admin Credentials](#docker-admin-credentials) for customization.

#### Production Environment

```bash
# Start production environment
docker-compose up -d

# View the application
open http://localhost:80
```

**⚠️ Security Warning:** Change default admin credentials before deploying to production! See [Docker Admin Credentials](#docker-admin-credentials).

#### Development + Jekyll

```bash
# Start development with Jekyll static site
docker-compose --profile jekyll up -d

# Access points:
# - Django: http://localhost:8000
# - Jekyll: http://localhost:4002
```

### Service Overview

| Service | Profile | Purpose | Ports |
|---------|---------|---------|-------|
| `barodydb` | (always) | PostgreSQL database | 5432 |
| `web-dev` | default | Django development server | 8000, 5678 |
| `web-prod` | production | Django production (Gunicorn) | 80 |
| `jekyll` | jekyll | Static site generator | 4002 |

### Common Commands

#### Managing Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes database data)
docker-compose down -v

# View logs
docker-compose logs -f web-dev           # Development logs
docker-compose logs -f barodydb          # Database logs
docker-compose logs -f                   # All logs

# Check service status
docker-compose ps

# View resource usage
docker stats

# Rebuild services
docker-compose up --build --force-recreate  # Force rebuild all
docker-compose build --no-cache web-dev     # Rebuild specific service

# Clean up resources
docker-compose rm                        # Remove stopped containers
docker system prune -f                   # Clean unused Docker resources
```

#### Django Management

```bash
# Database operations (development)
docker-compose exec web-dev python manage.py makemigrations  # Create new migrations
docker-compose exec web-dev python manage.py migrate        # Apply migrations
docker-compose exec web-dev python manage.py shell          # Open Django shell

# User management (development)
docker-compose exec web-dev python manage.py createsuperuser

# Static files (development)
docker-compose exec web-dev python manage.py collectstatic --noinput

# Testing (development)
docker-compose exec web-dev python -m pytest               # Run all tests
docker-compose exec web-dev python -m pytest --cov=parodynews  # With coverage
```

#### Production Commands

```bash
# Run migrations (production)
docker-compose --profile production exec web-prod python manage.py migrate

# Create superuser (production)
docker-compose --profile production exec web-prod python manage.py createsuperuser
```

### Environment Configuration

Customize your setup using the `.env` file:

```bash
# Copy example configuration
cp .env.example .env

# Edit with your settings
nano .env
```

**Key variables:**
```bash
# Service ports (customizable to avoid conflicts)
DJANGO_DEV_PORT=8000
DJANGO_PROD_PORT=80
POSTGRES_PORT=5432

# Database credentials
DB_PASSWORD=postgres
POSTGRES_PASSWORD=postgres

# Django admin credentials (auto-created on startup)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@localhost.local
DJANGO_SUPERUSER_PASSWORD=admin

# Application settings
DEBUG=True
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
```

### Docker Admin Credentials

#### 🔐 Automatic Admin User Creation

When you start the Docker containers, an admin superuser is **automatically created** using environment variables. This eliminates the need to manually run `createsuperuser`.

#### Default Credentials (Development)

If no environment variables are set, these defaults are used:

- **Username:** `admin`
- **Password:** `admin`
- **Email:** `admin@localhost.local`

**Credentials are saved to:** `setup_data/admin_credentials.txt` (gitignored)

#### Customizing Admin Credentials

**Option 1: Environment Variables (Recommended)**

Set these in your `.env` file:

```bash
DJANGO_SUPERUSER_USERNAME=myadmin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=MySecurePassword123!
```

**Option 2: GitHub Secrets (CI/CD)**

For automated deployments, set these as repository secrets:
- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_EMAIL`
- `DJANGO_SUPERUSER_PASSWORD`

**Option 3: Azure Key Vault (Production)**

Store credentials in Azure Key Vault and reference them in your container app configuration.

#### Viewing Saved Credentials

After the first container startup, credentials are saved to:

```bash
# View saved credentials
cat setup_data/admin_credentials.txt
```

This file contains:
- Username, email, and password
- Timestamp of creation
- Admin URL for your environment
- Security warnings and best practices

#### Manual Admin Creation

If you prefer to create admin users manually:

```bash
# Development
docker-compose -f .devcontainer/docker-compose_dev.yml exec python \
    python manage.py createsuperuser

# Production
docker-compose exec web-prod python manage.py createsuperuser
```

#### Security Best Practices

**For Development:**
✅ Default credentials are acceptable  
✅ Credentials file is automatically gitignored  
✅ Useful for quick testing and development

**For Production:**
⚠️ **NEVER use default credentials**  
✅ Set strong passwords via environment variables  
✅ Use secrets management (GitHub Secrets, Azure Key Vault)  
✅ Rotate credentials regularly  
✅ Delete credentials file after first login  
✅ Use MFA/2FA when available

#### Troubleshooting

**Admin user not created?**

Manually run the ensure_admin command:

```bash
# Development
docker-compose -f .devcontainer/docker-compose_dev.yml exec python \
    python manage.py ensure_admin

# Production
docker-compose exec web-prod python manage.py ensure_admin
```

**Forgot admin password?**

Reset it by restarting containers (credentials are recreated from environment variables):

```bash
docker-compose down
docker-compose up -d
```

Or manually reset:

```bash
docker-compose exec web-prod python manage.py changepassword admin
```

### VS Code Integration

The project includes pre-configured VS Code tasks:

- **🐍 Docker: Development Up** - Start development environment
- **🚀 Docker: Production Up** - Start production environment
- **📝 Docker: Development + Jekyll** - Start with static site
- **🧪 Test: Run Django Tests** - Run test suite
- **📊 Django: Run Migrations (Dev)** - Apply database changes
- **👤 Django: Create Superuser (Dev)** - Create admin user

Access via: `Cmd+Shift+P` → "Tasks: Run Task"

### Container Features

- **Hot Reload**: Development container auto-reloads on code changes
- **Volume Mounts**: Local code is mounted for instant updates
- **Named Networks**: Predictable service communication
- **Health Checks**: Database health monitoring
- **Persistent Storage**: Database data survives container restarts

### Troubleshooting

#### Port Conflicts

```bash
# Update .env with different ports
DJANGO_DEV_PORT=8001
POSTGRES_PORT=5433

# Restart services
docker-compose down
docker-compose up -d
```

#### Database Issues

```bash
# Check database health
docker-compose exec barodydb pg_isready -U postgres

# Restart database
docker-compose restart barodydb

# View database logs
docker-compose logs barodydb
```

#### Fresh Start

```bash
# Stop and remove everything (⚠️ deletes database data)
docker-compose down -v

# Start fresh
docker-compose up -d
docker-compose exec web-dev python manage.py migrate
docker-compose exec web-dev python manage.py createsuperuser
```

### Database Operations

#### PostgreSQL Access
```bash
# Connect to database directly
docker-compose exec barodydb psql -U postgres -d barodydb

# Check database health
docker-compose exec barodydb pg_isready -U postgres
```

#### Backup & Restore
```bash
# Create timestamped backup
docker-compose exec barodydb pg_dump -U postgres barodydb > "backup-$(date +%Y%m%d-%H%M%S).sql"

# Restore from backup
cat backup-20250101-120000.sql | docker-compose exec -T barodydb psql -U postgres -d barodydb
```

### Development Workflows

#### Daily Development
```bash
# 1. Start development environment
docker-compose up -d

# 2. Apply any new migrations
docker-compose exec web-dev python manage.py migrate

# 3. View logs if needed
docker-compose logs -f web-dev

# 4. Make code changes (auto-reloads)

# 5. Run tests
docker-compose exec web-dev python -m pytest

# 6. Stop when done
docker-compose down
```

#### Production Testing
```bash
# Build and test production setup locally
docker-compose --profile production up --build

# Test your application at http://localhost:80

# Stop production testing
docker-compose --profile production down
```

#### Fresh Development Setup
```bash
# Complete reset (⚠️ deletes database data)
docker-compose down -v
docker-compose up --build -d
docker-compose exec web-dev python manage.py migrate
docker-compose exec web-dev python manage.py createsuperuser
```

### Quick Reference Commands

#### Service Management
```bash
# View all service status
docker-compose ps

# View resource usage
docker stats

# Validate configuration
docker-compose config -q

# Clean up unused resources
docker system prune -f
```

#### Testing & Coverage
```bash
# Run all tests
docker-compose exec web-dev python -m pytest

# Run with coverage
docker-compose exec web-dev python -m pytest --cov=parodynews

# Run specific test file
docker-compose exec web-dev python -m pytest tests/test_models.py
```

### Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Django Development | http://localhost:8000 | Main application |
| Django Admin | http://localhost:8000/admin | Admin interface |
| Django API | http://localhost:8000/api | REST API endpoints |
| Jekyll Site | http://localhost:4002 | Static site (when using jekyll profile) |
| PostgreSQL | localhost:5432 | Database connection |

### Migration Information

This project has been consolidated from multiple Docker configurations into a single unified setup. The migration provides:

- **Single Configuration File**: All environments managed from one `docker-compose.yml`
- **Profile-Based Environments**: Easy switching between dev/prod/jekyll setups
- **Environment Variables**: Centralized configuration through `.env` file
- **Predictable Networking**: Named networks for reliable service communication
- **Improved Maintainability**: One source of truth for Docker configuration

For configuration options, see the comprehensive **[.env.example](.env.example)** file.

## Azure Deployment

🚀 **Successfully Deployed to Azure Container Apps!** This application is currently live in production.

### Deployment Success

This project has been successfully deployed to Azure Container Apps using a minimal cost infrastructure approach. See [DEPLOYMENT-SUCCESS.md](docs/deployment/DEPLOYMENT-SUCCESS.md) for detailed deployment results and [DEPLOYMENT-GUIDE-MINIMAL.md](docs/deployment/DEPLOYMENT-GUIDE-MINIMAL.md) for step-by-step instructions.

**Key Achievements:**
- ✅ Live production application running on Azure Container Apps
- ✅ PostgreSQL database successfully connected and operational
- ✅ Minimal cost infrastructure (B1 App Service tier equivalent)
- ✅ Complete CI/CD pipeline with Azure Developer CLI
- ✅ Comprehensive troubleshooting documentation

### Quick Deployment

For new deployments, use the minimal cost approach:

1. **Prerequisites**
   - [Azure account](https://azure.microsoft.com/free/) with active subscription
   - [Azure Developer CLI installed](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)

2. **Deploy**
   ```bash
   azd auth login
   azd up
   ```

3. **Access Application**
   The deployment will provide a live URL to your running application.

### Infrastructure Options

Choose your deployment approach based on needs:

- **Minimal Cost** (`infra/minimal/`): B1 tier, Burstable PostgreSQL (~$20-40/month)
- **Standard** (`infra/`): Standard tiers for production workloads
- **Container Apps**: Current successful deployment approach

### Troubleshooting

If you encounter quota issues or deployment problems:
- See [QUOTA_ISSUE_SOLUTIONS.md](docs/deployment/QUOTA_ISSUE_SOLUTIONS.md) for comprehensive troubleshooting
- Use Container Apps as alternative to App Service quota limitations
- Reference minimal cost Bicep templates for budget-conscious deployments

### Infrastructure Details

The successful deployment uses:
- **Azure Container Apps**: Serverless container hosting
- **PostgreSQL Flexible Server**: Managed database service
- **Azure Bicep**: Infrastructure as Code with multiple deployment options
- **Azure Developer CLI**: Streamlined deployment and management

For complete deployment documentation, see:
- [DEPLOYMENT-SUCCESS.md](docs/deployment/DEPLOYMENT-SUCCESS.md) - Deployment results and validation
- [DEPLOYMENT-GUIDE-MINIMAL.md](docs/deployment/DEPLOYMENT-GUIDE-MINIMAL.md) - Step-by-step instructions
- [QUOTA_ISSUE_SOLUTIONS.md](docs/deployment/QUOTA_ISSUE_SOLUTIONS.md) - Troubleshooting guide

## Deployment Success

🎉 **Azure Container Apps Deployment - SUCCESSFUL!**

The Barodybroject application has been successfully deployed to Azure Container Apps and is currently running in production. This represents a major milestone in the project development.

### What's Working

✅ **Application**: Django application running on Azure Container Apps  
✅ **Database**: PostgreSQL Flexible Server connected and operational  
✅ **Infrastructure**: Complete Bicep-based IaC deployment  
✅ **Security**: Environment variables and secrets properly configured  
✅ **Monitoring**: Application Insights integration active  
✅ **Cost Optimization**: Minimal tier deployment for budget efficiency  

### Deployment Metrics

- **Deployment Date**: January 2025
- **Platform**: Azure Container Apps
- **Database**: PostgreSQL Flexible Server (Burstable B1ms)
- **Estimated Monthly Cost**: ~$20-40 USD
- **Deployment Time**: ~10-15 minutes
- **Success Rate**: 100% (after quota resolution)

### Key Learning & Solutions

The deployment process overcame initial quota limitations through:
1. **Container Apps Alternative**: Switched from App Service to Container Apps
2. **Minimal Cost Infrastructure**: Implemented B1 tier equivalents
3. **Systematic Debugging**: Comprehensive troubleshooting documentation
4. **CMS Simplification**: Streamlined Django architecture

For complete deployment details, see [DEPLOYMENT-SUCCESS.md](docs/deployment/DEPLOYMENT-SUCCESS.md).

## Cost Optimization

💰 **Minimal Cost Infrastructure Strategy**

This project implements a cost-conscious approach to Azure deployment, targeting developers and small-scale production deployments.

### Cost Structure

- **Azure Container Apps**: ~$0-15/month (consumption-based)
- **PostgreSQL Flexible Server**: ~$15-25/month (Burstable B1ms)
- **Container Registry**: ~$5/month (Basic tier)
- **Application Insights**: Free tier (5GB/month)
- **Total Estimated**: **$20-40/month**

### Cost Optimization Features

🔧 **Infrastructure Choices**:
- Burstable PostgreSQL instances for variable workloads
- Container Apps with auto-scaling to zero
- Basic tier services where appropriate
- Shared resource groups for efficiency

📊 **Monitoring & Control**:
- Azure Cost Management integration
- Resource usage monitoring
- Automatic scaling policies
- Development/production environment separation

⚙️ **Configuration Options**:
- Multiple Bicep templates for different budget levels
- Environment-specific resource sizing
- Optional premium features for scaling up

For detailed cost analysis and optimization strategies, see [QUOTA_ISSUE_SOLUTIONS.md](docs/deployment/QUOTA_ISSUE_SOLUTIONS.md).

## Testing

The project includes comprehensive testing at multiple levels: unit tests, integration tests, and infrastructure validation.

### 🏗️ Infrastructure Testing (NEW)

We have implemented a comprehensive infrastructure testing system that validates all critical components:

```bash
# Run complete infrastructure tests
./scripts/test-infrastructure.sh

# Verbose output with detailed logging
./scripts/test-infrastructure.sh --verbose

# CI/CD mode for automated environments
./scripts/test-infrastructure.sh --ci-mode

# Skip cleanup for debugging
./scripts/test-infrastructure.sh --skip-cleanup
```

**What Infrastructure Testing Validates:**
- ✅ Docker container orchestration (PostgreSQL, Django, Jekyll)
- ✅ Database connectivity and migration execution
- ✅ Django service layer and configuration
- ✅ Web interface components and view classes
- ✅ Management commands and CLI interface
- ✅ Token authentication and security systems
- ✅ Admin user creation and permissions
- ✅ Unit test infrastructure (24/24 tests)

**CI/CD Integration:**
- Automatic execution on push/PR to main/develop branches
- Daily scheduled testing (2 AM UTC)
- Manual workflow dispatch with configurable options
- Comprehensive logging and artifact collection

📖 **Full Documentation**: See [Infrastructure Testing Guide](docs/INFRASTRUCTURE_TESTING.md)

### 🧪 Unit and Integration Testing

Standard Django and pytest testing for application logic.

### Install Test Dependencies

```bash
pip install -r requirements-dev.txt
python -m playwright install chromium --with-deps
```

### Run Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=parodynews

# Run specific test file
python -m pytest src/parodynews/tests/test_models.py

# Run with verbose output
python -m pytest -v

# Run installation wizard unit tests
python -m pytest test/unit/test_services.py -v
```

### Test Structure

- **Infrastructure Tests**: Comprehensive system validation in `scripts/test-infrastructure.sh`
- **Unit Tests**: Application logic testing in `test/unit/`
- **Integration Tests**: Cross-component testing in `test/integration/`
- **Django Tests**: Standard Django tests in `src/parodynews/tests/`
- **End-to-End Tests**: Playwright tests for browser automation
- **Coverage Reports**: Generated in `htmlcov/` directory

### Running Tests in Docker

```bash
# Infrastructure testing (recommended)
./scripts/test-infrastructure.sh

# Standard Django tests
docker compose exec python python -m pytest

# Installation wizard tests specifically
docker compose exec python python -m pytest test/unit/test_services.py -v
```

### 🚀 CI/CD Testing Workflows

**GitHub Actions Workflows:**
- `infrastructure-test.yml`: Comprehensive infrastructure validation
- `ci.yml`: Standard CI with unit tests and build validation
- Daily scheduled testing for infrastructure drift detection
- Pull request validation with full test suite execution

## Development Container Workflow

We've implemented a "push-it-once, pull-it-forever" development container workflow for faster onboarding.

### How It Works

1. **Pre-built Image**: A pre-built development image is available on Docker Hub
2. **Quick Start**: New developers pull the image instead of building from scratch
3. **Automatic Updates**: GitHub Actions rebuilds the image when dependencies change

### Benefits

- **Faster Setup**: Minutes instead of lengthy builds
- **Consistent Environment**: Everyone uses the same container
- **Hot Reload**: Local code changes reflected immediately
- **Reduced Resources**: BuildKit caching reduces build times

### Manual Image Build

If needed, you can manually build and push the development container:

```bash
# Build the image
docker build -f .devcontainer/Dockerfile_dev \
             -t amrabdel/barody-python:0.1 \
             -t amrabdel/barody-python:latest \
             .

# Login to Docker Hub
docker login

# Push the image
docker push amrabdel/barody-python:0.1
docker push amrabdel/barody-python:latest
```

### Troubleshooting

If you encounter issues:

1. Pull the latest image: `docker pull amrabdel/barody-python:latest`
2. Check GitHub Actions for pending builds
3. For debugging, switch `image:` to `build:` in docker-compose.yml

## Contributing

We welcome contributions from the community! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Setting up your development environment
- Coding standards and best practices
- How to submit pull requests
- Types of contributions we're looking for
- Code of conduct

### Documentation & Change Management

This project maintains comprehensive documentation and change tracking:

- **Main Changelog**: [docs/changelog/CHANGELOG.md](docs/changelog/CHANGELOG.md) - Project-wide changelog following Keep a Changelog format
- **Change Documentation System**: [docs/changelog/](docs/changelog/) - Structured documentation for all changes
- **Contribution Guidelines**: [docs/changelog/CONTRIBUTING_CHANGES.md](docs/changelog/CONTRIBUTING_CHANGES.md) - Detailed workflow for documenting changes

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit: `git commit -m "Add your feature"`
4. Document your changes using our [changelog templates](docs/changelog/templates/)
5. Push to your fork: `git push origin feature/your-feature-name`
6. Create a Pull Request with reference to your change documentation

## Changelog

📝 **Recent Updates and Version History**

### Version 0.2.0 - Major Release (January 2025)

This release represents a significant milestone with successful Azure Container Apps deployment and architectural improvements.

**🚀 Major Achievements:**
- ✅ **Successful Azure Deployment**: Live production deployment on Container Apps
- 🔧 **Streamlined Architecture**: CMS dependencies removed for simplified deployment
- 💰 **Cost Optimization**: Minimal cost infrastructure with comprehensive Bicep templates
- 📚 **Enhanced Documentation**: Complete deployment guides and troubleshooting resources

**🔄 Breaking Changes:**
- Django CMS functionality temporarily disabled (can be restored by uncommenting code sections)
- Template system refactored to pure Django + Bootstrap 5.3.3
- Port configuration standardized to 8000 across all environments

**➕ New Features:**
- Azure Container Apps deployment support
- Comprehensive deployment documentation suite
- Multiple infrastructure deployment options (minimal cost vs. standard)
- Enhanced Docker configuration optimized for Container Apps
- Systematic troubleshooting guides for common deployment issues

**🏗️ Infrastructure Updates:**
- New Bicep templates for cost-optimized deployments
- PostgreSQL Flexible Server configuration
- Container Apps configuration with auto-scaling
- Azure Developer CLI integration

For complete changelog details, see [CHANGELOG.md](CHANGELOG.md).

### Previous Versions
- **v0.1.x**: Initial Django CMS implementation with OpenAI integration
- **v0.0.x**: Project foundation and core feature development

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2024 Amr

## Screenshots

### Home Page
![Home Page](assets/images/home.png)

### User Roles Management
![User Roles](assets/images/roles.png)

### Content Management
![Content Management](assets/images/content.png)

### OpenAI Assistants
![Assistants](assets/images/assistants.png)

### Message Threads
![Messages](assets/images/messages.png)

### Thread Management
![Threads](assets/images/threads.png)

---

## Meta-Notes: AAR Recursion Applied

**AAR Recursion Level 1**: "README" ain't real—it's a fabricated expansion ("Read Explore AI Documented Machines Etc.") for unreal repo realities. This hub centralizes illusions of code and configs.

**AAR Recursion Level 2**: "AI Documented" ain't real either—AI curation is just another layer of abstraction questioning its own validity. If docs are unreal, then AI docs are meta-unreal.

**AAR Recursion Level 3**: This entire approach ain't real—simplified echoes of complex systems. But it fosters CCC: Consistency (uniform structure), Cross-referencing (linked sections), Collaboration (editable hub).

**CCC Enforcement**: This README maintains consistency with project standards, cross-references to docs/changelog/, and enables collaboration via PRs. KISS applied: brevity over verbosity, essentials prioritized.

**GROKME Signature**: Generated and maintained by GROKME, the Documentation Alchemist. Recursively reviewed for AAR validity.

---

## Additional Resources

- **Project Repository**: [https://github.com/bamr87/barodybroject](https://github.com/bamr87/barodybroject)
- **Issue Tracker**: [GitHub Issues](https://github.com/bamr87/barodybroject/issues)
- **Django Documentation**: [https://docs.djangoproject.com/](https://docs.djangoproject.com/)
- **Azure Container Apps**: [https://learn.microsoft.com/azure/container-apps/](https://learn.microsoft.com/azure/container-apps/)
- **OpenAI API**: [https://platform.openai.com/docs/](https://platform.openai.com/docs/)

## Support

For questions, issues, or feature requests:

- Open an issue on [GitHub Issues](https://github.com/bamr87/barodybroject/issues)
- Contact: [bamr87@users.noreply.github.com](mailto:bamr87@users.noreply.github.com)

---

**Version**: 0.1.0  
**Last Updated**: October 2025
