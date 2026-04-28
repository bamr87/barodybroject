
# parodynews Directory

## Purpose
This is the main Django application directory for the parody news generator. It contains the core functionality for creating, managing, and generating parody news content using OpenAI assistants. The app handles user interactions, content management, AI assistant configurations, and the complete workflow for content generation from prompts to published articles.

## Recent Changes (v2.0.0)

**Models Refactoring**: The monolithic `models.py` file has been split into a well-organized package structure for better maintainability. See [`models/README.md`](models/README.md) for details.

- ✅ **Backward Compatible**: Current domain model imports continue to work
- 📦 **Better Organization**: Models grouped by domain (AI, Content, Publishing, etc.)
- 🧹 **Placeholder Models Removed**: obsolete generic demo models were removed during repository cleanup
- 📚 **Improved Documentation**: Each model module has comprehensive docstrings

## Contents

### Core Files
- `admin.py`: Django admin interface configurations (organized by model category)
- `apps.py`: Django app configuration (ParodynewsConfig)
- `context_processors.py`: Django context processors for template rendering
- `forms.py`: Django forms for user input (organized by model category)
- `mixins.py`: Reusable class mixins for views and models
- `resources.py`: Import/export resource definitions
- `serializers.py`: Django REST framework serializers (organized by model category)
- `tests.py`: Main test file
- `urls.py`: URL routing configurations
- `utils.py`: Main utilities file for OpenAI integration

### Directories
- `docs/`: Documentation directory with detailed app documentation
- `management/`: Django management commands directory
- `migrations/`: Database migration files
- **`models/`**: **NEW** - Organized model package (see [models/README.md](models/README.md))
  - `base.py`: Abstract base classes and mixins
  - `config.py`: Application configuration models
  - `ai.py`: OpenAI and AI assistant models
  - `content.py`: Content generation models
  - `conversation.py`: Thread and message models
  - `publishing.py`: Post and publishing models
- `schema/`: JSON schema definitions for data validation
- `scripts/`: Application-specific utility scripts
- `templates/`: HTML templates for the application UI
- `templatetags/`: Custom Django template tags
- `tests/`: Test suite for the application
- `utils/`: Utility functions and helper modules
- `views/`: Package-based Django views and REST API viewsets

### Legacy Data
- `model_choices.json`: JSON file containing model choice configurations

## Usage
This Django app provides the core functionality of the parody news generator:

```python
# In Django settings
INSTALLED_APPS = [
    'parodynews.apps.ParodynewsConfig',
    # other apps...
]

# URL inclusion in main urls.py
from django.urls import path, include
urlpatterns = [
    path('', include('parodynews.urls')),
]
```

Key features include:
- OpenAI assistant management and configuration
- Content generation workflows using AI
- User interface for creating and managing parody news articles
- REST API endpoints for programmatic access

## Container Configuration
The app runs within the Django container environment:
- Requires OpenAI API credentials for assistant functionality
- Database access for model persistence
- Static file serving for templates and assets
- Environment variables for configuration (OpenAI API keys, etc.)

## Related Paths
- Incoming: Receives requests through Django URL routing, integrates with barodybroject settings
- Outgoing: Interfaces with OpenAI API, renders templates, manages database through Django ORM
