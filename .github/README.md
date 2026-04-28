# Parody News Generator - Developer Guide

AI-powered Django application for generating parody news content using OpenAI APIs. Production-ready with Azure Container Apps deployment, PostgreSQL, and Jekyll static site integration.

> 📘 **General Users**: See the [comprehensive README](../README.md) for detailed documentation.

## Tech Stack

**Backend**: Django 5.1 • Python 3.10+ • DRF  
**Database**: PostgreSQL  
**Infrastructure**: Docker • Azure Container Apps • Azure Bicep  
**AI**: OpenAI API • Custom Assistants  
**Testing**: Pytest • Playwright • Selenium  
**Frontend**: Bootstrap • CKEditor • Jekyll

## Quick Start

```bash
# Clone and setup
git clone https://github.com/bamr87/barodybroject.git && cd barodybroject
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

# Configure environment
cat > .env << EOF
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
DB_CHOICE=postgres
DB_HOST=localhost
DB_NAME=barodydb
DB_USERNAME=postgres
DB_PASSWORD=postgres
OPENAI_API_KEY=your-key-here
EOF

# Database setup
cd src && python manage.py migrate && python manage.py createsuperuser

# Run
python manage.py runserver
# App: http://localhost:8000 | Admin: http://localhost:8000/admin
```

## Docker Quick Start

```bash
# Start Django + PostgreSQL development services
docker compose -f .devcontainer/docker-compose_dev.yml up -d barodydb python

# Run Django commands
docker compose -f .devcontainer/docker-compose_dev.yml exec python python manage.py migrate
docker compose -f .devcontainer/docker-compose_dev.yml exec python python manage.py createsuperuser

# Access: http://localhost:8000 after attaching the debugger on port 5678
```

## Project Structure

```
barodybroject/
├── infra/              # Azure Bicep IaC
│   ├── main.bicep     # Infrastructure entry point
│   ├── app/           # Container Apps, PostgreSQL
│   └── shared/        # Key Vault, monitoring, registry
├── scripts/           # Deployment automation
├── src/
│   ├── barodybroject/ # Django project config
│   ├── parodynews/    # Main app (models, views, API)
│   │   ├── models/
│   │   ├── views/
│   │   ├── management/commands/  # Custom commands
│   │   ├── tests/
│   │   └── templates/
│   ├── pages/         # Jekyll blog (59 posts)
│   ├── static/        # CSS, JS, images
│   └── requirements.txt
├── docker-compose.yml
├── azure.yaml         # Azure Developer CLI config
└── pyproject.toml
```

## Key Commands

### Django
```bash
python manage.py runserver              # Dev server
python manage.py makemigrations         # Create migrations
python manage.py migrate                # Apply migrations
python manage.py createsuperuser        # Admin user
python manage.py collectstatic          # Collect static files
python manage.py shell                  # Django shell
```

### Docker
```bash
docker compose -f .devcontainer/docker-compose_dev.yml up -d barodydb python
docker compose -f .devcontainer/docker-compose_dev.yml down
docker compose -f .devcontainer/docker-compose_dev.yml logs -f python
docker compose -f .devcontainer/docker-compose_dev.yml exec python bash
docker compose -f .devcontainer/docker-compose_dev.yml build
```

### Testing
```bash
docker compose -f .devcontainer/docker-compose_dev.yml exec -e DJANGO_SETTINGS_MODULE=barodybroject.settings.testing python python -m pytest
docker compose -f .devcontainer/docker-compose_dev.yml exec -e DJANGO_SETTINGS_MODULE=barodybroject.settings.testing python python -m pytest --cov=parodynews
docker compose -f .devcontainer/docker-compose_dev.yml exec -e DJANGO_SETTINGS_MODULE=barodybroject.settings.testing python python -m pytest -v -k test_name
python -m playwright install --with-deps chromium   # Setup browser
```

### Azure Deployment
```bash
azd auth login                         # Authenticate
azd up                                 # Provision + deploy
azd deploy                             # Deploy only
azd down                               # Tear down
azd pipeline config                    # Setup CI/CD
```

## Architecture

### Django App Structure
```
MVC Pattern:
- Models: src/parodynews/models/ (AI, content, conversation, publishing, config)
- Views: src/parodynews/views/ (API, assistants, content, posts, threads, schemas)
- Templates: Bootstrap-based responsive UI
- API: Django REST Framework endpoints

Authentication:
- django-allauth (social auth, MFA, SAML)
- Custom middleware & context processors

Settings:
- `barodybroject.settings.development` for dev compose and local manage.py defaults
- `barodybroject.settings.production` for WSGI/ASGI and production compose
- `barodybroject.settings.testing` for pytest and infrastructure scripts
```

### Database Schema
```
Core Models:
- Content: AI-generated articles
- Assistant: OpenAI assistant configurations
- Thread: Conversation threads
- Message: Thread messages
- User: Django auth + custom profile
```

### API Endpoints
```
/api/                  # API root
/api/content/          # Content CRUD
/api/assistants/       # Assistant management
/api/threads/          # Thread operations
/admin/                # Django admin
/accounts/             # Auth endpoints
```

## Development Workflow

### Local Development
1. Use PostgreSQL (required)
2. DEBUG=True in .env
3. Hot reload enabled by default
4. Django Debug Toolbar recommended

### Containerized Development
1. Docker Compose for full stack
2. PostgreSQL for production parity
3. Volume mounts for hot reload
4. Separate Jekyll service for blog

### Testing Strategy
```bash
# Unit tests
DJANGO_SETTINGS_MODULE=barodybroject.settings.testing pytest src/parodynews/tests/

# Integration tests
DJANGO_SETTINGS_MODULE=barodybroject.settings.testing pytest -m integration

# E2E tests
DJANGO_SETTINGS_MODULE=barodybroject.settings.testing pytest src/parodynews/tests/ --headed

# Coverage requirements
DJANGO_SETTINGS_MODULE=barodybroject.settings.testing pytest --cov --cov-fail-under=80
```

## CI/CD

### GitHub Actions
- **Status**: ⚠️ Not configured (see [TODO.md](../TODO.md))
- **Planned**: PR validation, security scanning, auto-deployment

### Deployment Pipeline
```bash
# Manual deployment
azd deploy

# CI/CD setup
azd pipeline config  # Creates GitHub workflow
```

## Environment Variables

### Required
```bash
SECRET_KEY              # Django secret (generate with get_random_secret_key())
DATABASE_URL            # Database connection string
OPENAI_API_KEY          # OpenAI API key
```

### Optional
```bash
DEBUG                   # Debug mode (default: False)
ALLOWED_HOSTS           # Comma-separated hosts
DB_HOST, DB_NAME        # Database config (if not using DATABASE_URL)
DB_USERNAME, DB_PASSWORD
AZURE_INSIGHTS_KEY      # Application Insights
```

## Common Tasks

### Add New Model
```bash
# Edit the appropriate module under parodynews/models/
python manage.py makemigrations
python manage.py migrate
# Register in admin.py
```

### Add New API Endpoint
```python
# 1. Create serializer in serializers.py
# 2. Create viewset in the appropriate module under parodynews/views/
# 3. Register in urls.py
# 4. Add tests in tests/
```

### Add Management Command
```bash
# Create: parodynews/management/commands/command_name.py
# Run: python manage.py command_name
```

## Troubleshooting

### Database Issues
```bash
# Reset database (PostgreSQL-only)
python manage.py reset_db
python manage.py createsuperuser
```

### Docker Issues
```bash
# Clean rebuild
docker compose down -v
docker compose build --no-cache
docker compose up
```

### Azure Issues
```bash
# View logs
azd logs
# Environment info
azd env list
```

## Security Notes

- Never commit `.env` files
- Use Azure Key Vault in production
- SECRET_KEY must be unique per environment
- Set DEBUG=False in production
- Configure ALLOWED_HOSTS properly
- Review [TODO.md](../TODO.md) for security tasks

## Performance

### Database
- PostgreSQL connection pooling via Gunicorn
- Indexes on frequently queried fields
- Use select_related/prefetch_related

### Caching
- ⚠️ Not implemented (see [TODO.md](../TODO.md))
- Planned: Redis for session/cache backend

### Static Files
- Collected via collectstatic
- Served via Gunicorn in dev
- ⚠️ CDN not configured (see [TODO.md](../TODO.md))

## Contributing

1. Fork the repo
2. Create feature branch: `git checkout -b feature/name`
3. Run tests: `pytest`
4. Run linter: `ruff check .`
5. Commit: `git commit -m "Description"`
6. Push and create PR

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.

## Resources

- **Full README**: [../README.md](../README.md)
- **TODO**: [../TODO.md](../TODO.md) - Known issues & enhancements
- **Issues**: [GitHub Issues](https://github.com/bamr87/barodybroject/issues)
- **Django Docs**: https://docs.djangoproject.com/
- **DRF Docs**: https://www.django-rest-framework.org/
- **Azure Docs**: https://learn.microsoft.com/azure/container-apps/

---

**Version**: 0.1.0 | **License**: MIT | **Maintainer**: [@bamr87](https://github.com/bamr87)
