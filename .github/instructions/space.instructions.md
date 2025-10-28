---
file: space.instructions.md
description: VS Code Copilot-optimized workspace organization and project structure guidelines for Django/OpenAI development
author: Barodybroject Team
created: 2025-10-28
lastModified: 2025-10-28
version: 1.0.0
applyTo: "**"
dependencies:
  - copilot-instructions.md: Core principles and project context
  - languages.instructions.md: Language-specific patterns
containerRequirements:
  description: "Django development workspace optimized for VS Code Copilot assistance"
  validation: "project-structure validation, AI-readability scoring"
paths:
  django_organization_path:
    - project_structure_design
    - ai_assisted_organization
    - django_app_architecture
    - workspace_optimization
    - continuous_improvement
---

# Workspace Organization Guidelines for Barodybroject

These instructions provide comprehensive guidance for organizing Django/OpenAI workspaces and implementing project structure best practices optimized for VS Code Copilot assistance. They focus on creating clear, navigable project structures that enhance AI understanding and collaboration throughout the Django development process.

## 🤖 VS Code Copilot Integration for Django Workspace Organization

### AI-Assisted Django Project Structure

**When organizing Django projects with VS Code Copilot**:

1. **Project Structure Planning**: Use AI to generate optimal Django layouts:
   ```markdown
   // Prompt: "Generate an optimal Django project structure for [project type] that:
   // - Follows Django best practices and conventions
   // - Supports OpenAI API integration patterns
   // - Enables clear navigation and discovery
   // - Optimizes for VS Code Copilot understanding
   // - Includes proper separation of concerns
   // - Supports containerized development"
   ```

2. **Django App Organization**: Leverage VS Code Copilot for:
   - Django app structure creation and organization
   - Model, view, and template organization
   - API endpoint structure and documentation
   - Service layer architecture design
   - Static asset organization and management
   - Configuration file placement and structure

3. **Workspace Optimization**: Use AI to:
   - Analyze and improve Django project structure
   - Identify organizational inconsistencies
   - Suggest better file placement and naming
   - Enhance discoverability and navigation
   - Optimize for AI assistance and understanding

## Django Project Structure Standards

### Root Level Organization
```
barodybroject/
├── .github/                 # GitHub-specific configuration and workflows
├── .vscode/                 # VS Code workspace settings and extensions
├── docs/                    # Project documentation and guides
├── infra/                   # Azure Bicep infrastructure as code
├── scripts/                 # Automation and utility scripts
├── src/                     # Django application source code
│   ├── barodybroject/      # Django project settings and configuration
│   ├── parodynews/         # Main Django application
│   ├── static/             # Static assets (CSS, JS, images)
│   ├── templates/          # Global Django templates
│   ├── media/              # User-uploaded media files
│   ├── manage.py           # Django management script
│   └── requirements.txt    # Python dependencies
├── tests/                   # Test files and test data
├── docker-compose.yml      # Local development environment
├── Dockerfile              # Container configuration
└── README.md               # Project overview and setup
```

### Django Application Structure
```
src/parodynews/
├── __init__.py
├── admin.py                # Django admin configuration
├── apps.py                 # Application configuration
├── models.py               # Database models
├── views.py                # View logic (or views/ directory for complex apps)
├── urls.py                 # URL routing configuration
├── forms.py                # Form definitions
├── serializers.py          # DRF serializers
├── services/               # Business logic layer
│   ├── __init__.py
│   ├── openai_service.py   # OpenAI API integration
│   ├── content_service.py  # Content management logic
│   └── email_service.py    # Email handling
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── validators.py       # Custom validators
│   └── helpers.py          # Helper functions
├── templates/              # App-specific templates
│   └── parodynews/
│       ├── base.html
│       ├── article_list.html
│       └── article_detail.html
├── static/                 # App-specific static files
│   └── parodynews/
│       ├── css/
│       ├── js/
│       └── images/
├── migrations/             # Database migrations
├── tests/                  # Application tests
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_services.py
│   └── test_utils.py
└── management/             # Custom Django management commands
    ├── __init__.py
    └── commands/
        ├── __init__.py
        └── generate_content.py
```

### Configuration and Settings Organization
```
src/barodybroject/
├── __init__.py
├── settings/               # Split settings for different environments
│   ├── __init__.py
│   ├── base.py            # Common settings
│   ├── development.py     # Development-specific settings
│   ├── production.py      # Production-specific settings
│   └── testing.py         # Test-specific settings
├── urls.py                # Root URL configuration
├── wsgi.py                # WSGI configuration
├── asgi.py                # ASGI configuration (for async support)
└── celery.py              # Celery configuration (if using)
```

## File Naming Conventions

### Django-Specific Naming
- **Models**: `PascalCase` for class names, `snake_case` for file names
- **Views**: `snake_case` for function names, `PascalCase` for class-based views
- **Templates**: `snake_case` with descriptive names (e.g., `article_detail.html`)
- **Static files**: Organized by type (`css/`, `js/`, `images/`)
- **URLs**: `kebab-case` for URL patterns

### Python Module Naming
- **Services**: `service_name_service.py` (e.g., `openai_service.py`)
- **Utils**: `utility_name.py` (e.g., `validators.py`)
- **Tests**: `test_component_name.py` (e.g., `test_models.py`)
- **Management commands**: `command_name.py` (e.g., `generate_content.py`)

## VS Code Workspace Configuration

### Settings Optimization for Django
```json
{
  "python.defaultInterpreterPath": "./src/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/"],
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/migrations/*.py": false,
    "**/.pytest_cache": true,
    "**/node_modules": true,
    "**/.git": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/bower_components": true,
    "**/.git": true,
    "**/__pycache__": true,
    "**/migrations": true
  },
  "emmet.includeLanguages": {
    "django-html": "html"
  },
  "files.associations": {
    "**/*.html": "django-html"
  }
}
```

### Extension Recommendations for Django
- Python for Python development
- Django for Django template support
- GitLens for version control integration
- Docker for container management
- REST Client for API testing
- SQLite Viewer for database inspection

## AI-Assisted Development Workflows

### Context-Aware Django Development
- Provide clear Django project context in prompts
- Include relevant model relationships and dependencies
- Specify target Django version and compatibility requirements
- Mention OpenAI API integration patterns and requirements

### Progressive Enhancement for Django
- Start with basic Django structure and enhance iteratively
- Use AI to suggest Django best practices and optimizations
- Maintain consistency across Django apps and components
- Document architectural decisions and rationale

### Quality Assurance for Django Projects
- Regular Django project structure validation
- AI-readability scoring for Django code organization
- Cross-reference integrity validation between models and views
- Navigation optimization for Django admin and user interfaces

## Integration with Barodybroject Ecosystem

### Django Application Organization
- Organize Django apps by business domain and functionality
- Create clear separation between presentation, business logic, and data layers
- Support cross-app communication through well-defined interfaces
- Enable efficient Django admin customization and management

### OpenAI Integration Patterns
- Maintain consistent OpenAI service integration across Django apps
- Support AI-assisted content generation workflows
- Enable efficient error handling and retry logic for AI operations
- Facilitate community contributions to AI integration features

### Container-First Development
- Follow Docker-first development principles for Django
- Maintain consistency with containerized deployment patterns
- Support efficient development and production environment parity
- Enable easy scaling and deployment through container orchestration

## Documentation Standards for Django Projects

### Django-Specific Documentation
- Follow Django documentation conventions and patterns
- Maintain consistency with Django community standards
- Support AI-assisted Django documentation generation
- Enable efficient maintenance and updates of Django-specific docs

### Code Documentation Patterns
- Use Django-style docstrings for models, views, and services
- Document Django admin customizations and configurations
- Maintain clear API documentation for Django REST Framework endpoints
- Include Django management command documentation and usage examples

---

*These workspace organization guidelines ensure that the Barodybroject Django project is optimally structured for VS Code Copilot assistance while maintaining Django best practices and supporting OpenAI integration patterns.*
