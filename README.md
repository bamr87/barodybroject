# Parody News Generator

A Django-based web application integrated with OpenAI to generate AI-powered parody news content. This project combines modern web development practices with artificial intelligence to create a platform for generating and managing satirical news articles.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture & Design Patterns](#architecture--design-patterns)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [Docker Setup](#docker-setup)
- [Azure Deployment](#azure-deployment)
- [Testing](#testing)
- [Development Container Workflow](#development-container-workflow)
- [Contributing](#contributing)
- [License](#license)
- [Screenshots](#screenshots)

## Features

### Core Features

- **AI-Powered Content Generation**: Leverages OpenAI APIs to generate parody news articles with customizable assistants
- **User Authentication**: Complete user management with registration, login, logout, password management, and multi-factor authentication (MFA)
- **Dynamic Content Management**: Comprehensive admin interface for managing content, users, and site settings
- **RESTful API**: Full-featured API for programmatic interaction with application data
- **Responsive Design**: Bootstrap-based responsive UI that adapts to various screen sizes
- **Blog Module**: Integrated blog with categories, tags, and commenting system
- **Search Functionality**: Built-in search for finding content across the site
- **Security Features**: Django's built-in security protections against XSS, CSRF, SQL Injection, and more

### Advanced Features

- **Dynamic Form Support**: Reusable Django `DynamicFieldsMixin` with AJAX-powered form field updates
- **CMS Integration**: Django CMS support for flexible content management
- **Jekyll Static Site Generation**: Integrated Jekyll for static content and blog publishing
- **Enhanced Navigation**: YAML-based navigation and UI text management
- **GitHub Automation**: AI-assisted GitHub issue handling and repository management
- **Email Integration**: Django SES integration with DKIM support for secure email delivery

## Technology Stack

### Backend Framework & Tools

- **Django 4.2.20**: High-level Python web framework for rapid development
- **Django CMS**: Open-source content management system built on Django
- **Django REST Framework**: Powerful toolkit for building Web APIs
- **Python 3.8+**: Primary programming language
- **Gunicorn**: WSGI HTTP server for production deployment

### Frontend & UI

- **Bootstrap**: Responsive front-end toolkit for modern web design
- **jQuery**: JavaScript library for DOM manipulation
- **CKEditor**: Rich text editor for content creation
- **Martor**: Markdown editor for Django

### Databases

- **PostgreSQL**: Production database (powerful object-relational database system)
- **SQLite**: Development and testing database

### Infrastructure & Deployment

- **Docker & Docker Compose**: Containerization for consistent development and deployment
- **Azure Container Apps**: Cloud container hosting service
- **Azure Developer CLI (azd)**: Tool for provisioning and deploying Azure resources
- **Azure Bicep**: Infrastructure as Code (IaC) for Azure resources
- **Azure Application Insights**: Monitoring and diagnostics
- **Jekyll**: Static site generator for blog content

### AI Integration

- **OpenAI API**: Access to GPT models for content generation
- **Custom OpenAI Assistants**: Configurable AI assistants for specialized content creation

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

## Project Structure

```
barodybroject/
├── infra/                      # Azure infrastructure as code (Bicep)
│   ├── main.bicep             # Main infrastructure definition
│   ├── app/                   # Application-specific resources
│   └── shared/                # Shared resources (Key Vault, monitoring, etc.)
├── scripts/                    # Deployment and automation scripts
│   ├── azure-setup.py         # Azure setup automation
│   └── version-manager.sh     # Version management
├── src/                       # Django application source code
│   ├── barodybroject/         # Django project settings
│   │   ├── settings.py        # Application configuration
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
DATABASE_URL=sqlite:///db.sqlite3

# For PostgreSQL (optional, used with Docker)
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

### Using Docker Compose

The project includes a complete Docker Compose setup with three services:
- **python**: Django application
- **barodydb**: PostgreSQL database
- **jekyll**: Static site generator

1. **Build the Docker Image**

```bash
docker compose build
```

2. **Start All Services**

```bash
docker compose up -d
```

This will start:
- Django app on [http://localhost:80](http://localhost:80)
- PostgreSQL database on port 5432
- Jekyll site on [http://localhost:4002](http://localhost:4002)

3. **View Logs**

```bash
docker compose logs -f
```

4. **Stop Services**

```bash
docker compose down
```

5. **Run Django Commands in Container**

```bash
# Run migrations
docker compose exec python python manage.py migrate

# Create superuser
docker compose exec python python manage.py createsuperuser

# Collect static files
docker compose exec python python manage.py collectstatic --noinput
```

### Development Container Features

- **Hot Reload**: Code changes are immediately reflected (volume mounted)
- **Isolated Environment**: Consistent across all development machines
- **Database Persistence**: PostgreSQL data persists in Docker volumes
- **Multi-Service**: Run Django, PostgreSQL, and Jekyll simultaneously

## Azure Deployment

This project is configured for deployment to Azure Container Apps using the Azure Developer CLI.

### Prerequisites

1. [Azure account](https://azure.microsoft.com/free/) with an active subscription
2. [Azure Developer CLI installed](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)

### Deployment Steps

1. **Login to Azure**

```bash
azd auth login
```

2. **Initialize the Project** (first time only)

```bash
azd init
```

This will prompt you to:
- Provide an environment name (e.g., "prod", "dev")
- Select your Azure subscription
- Choose a deployment region (e.g., "eastus", "westus2")

3. **Deploy the Application**

```bash
azd up
```

This single command will:
- Provision all Azure resources (Container Apps, PostgreSQL, Key Vault, etc.)
- Build the Docker container
- Push the container to Azure Container Registry
- Deploy the application to Azure Container Apps
- Configure environment variables and secrets

4. **View the Deployed Application**

After deployment completes, `azd` will display the application URL. Visit it to see your live application.

### Incremental Deployments

After the initial deployment, you can deploy code changes with:

```bash
azd deploy
```

This is faster as it only rebuilds and redeploys the application without reprovisioning infrastructure.

### Infrastructure Details

The project uses Azure Bicep for Infrastructure as Code:

- **infra/main.bicep**: Main infrastructure definition
- **infra/app/src.bicep**: Container App configuration
- **infra/app/db-postgres.bicep**: PostgreSQL Flexible Server
- **infra/shared/**: Shared resources (Key Vault, monitoring, container registry)

### CI/CD Pipeline

To set up automated deployments with GitHub Actions:

```bash
azd pipeline config
```

This will:
- Create a GitHub Actions workflow
- Configure Azure authentication secrets
- Enable automatic deployments on push to main branch

## Testing

The project includes comprehensive testing using pytest and Playwright.

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
```

### Test Structure

- **Unit Tests**: Located in `src/parodynews/tests/`
- **Integration Tests**: Test API endpoints and views
- **End-to-End Tests**: Playwright tests for browser automation
- **Coverage Reports**: Generated in `htmlcov/` directory

### Running Tests in Docker

```bash
docker compose exec python python -m pytest
```

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

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit: `git commit -m "Add your feature"`
4. Push to your fork: `git push origin feature/your-feature-name`
5. Create a Pull Request

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
