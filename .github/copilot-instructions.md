# Copilot Instructions - Barodybroject

## Project Overview

This is a **Django-based parody news generator** that integrates with OpenAI APIs to create satirical content. The application emphasizes:

- **Container-First Development**: All development and deployment occurs in Docker containers
- **Django Best Practices**: Following Django conventions and security standards
- **Azure Cloud Deployment**: Designed for Azure Container Apps with Bicep infrastructure
- **AI Integration**: OpenAI API for content generation with proper error handling
- **Responsive Design**: Bootstrap-based UI with modern UX patterns

### Technology Stack

**Backend:**
- Django 4.x (Python 3.8+)
- Django REST Framework for APIs
- PostgreSQL (production), SQLite (development)
- OpenAI Python SDK

**Frontend:**
- Bootstrap 5
- JavaScript (ES6+)
- Jekyll for static site generation

**Infrastructure:**
- Docker & Docker Compose
- Azure Container Apps
- Azure Bicep (Infrastructure as Code)
- GitHub Actions for CI/CD

## Repository Structure

```
barodybroject/
├── src/                        # Django application source
│   ├── barodybroject/         # Project settings and configuration
│   ├── parodynews/            # Main Django app
│   │   ├── models.py          # Database models
│   │   ├── views.py           # Request handlers
│   │   ├── forms.py           # Form definitions
│   │   ├── templates/         # HTML templates
│   │   └── tests/             # Test suite
│   ├── manage.py              # Django management script
│   └── requirements.txt       # Python dependencies
├── infra/                     # Azure Bicep infrastructure
├── scripts/                   # Automation and utility scripts
├── .github/
│   ├── workflows/             # GitHub Actions workflows
│   └── instructions/          # AI coding instructions
└── docker-compose.yml         # Local development environment
```

## Core Development Principles

### DRY (Don't Repeat Yourself)
- Extract reusable code into functions, classes, or modules
- Use Django's built-in features (generic views, middleware, template tags)
- Create reusable utilities in `utils/` directories
- Leverage inheritance for models, forms, and views

### KISS (Keep It Simple)
- Prefer Django's conventions over custom solutions
- Use clear, descriptive names for variables and functions
- Break complex logic into smaller, focused functions
- Avoid over-engineering; start simple and refactor as needed

### Container-First Development
- All development occurs in Docker containers
- Use `docker-compose.yml` for local multi-service setup
- Match development environment to production closely
- Never install dependencies directly on host machine
- Document all container requirements (ports, volumes, environment variables)

### Security First
- Never commit secrets or API keys
- Use environment variables for sensitive configuration
- Follow Django security best practices (CSRF, XSS, SQL injection protection)
- Implement proper authentication and authorization
- Validate and sanitize all user inputs
- Use Django's `secrets` module for cryptographic operations

## File Header Requirements

Every source file MUST include a header with standardized metadata. Use language-appropriate comment syntax.

### Header Template

```python
"""
File: filename.py
Description: Brief one-sentence description of the file's purpose
Author: Name <email@domain.com>
Created: YYYY-MM-DD
Last Modified: YYYY-MM-DD
Version: X.Y.Z

Dependencies:
- package-name: version or description
- another-package: description

Container Requirements:
- Base Image: python:3.8-slim
- Exposed Ports: 8000/tcp
- Volumes: /app/src:rw, /app/static:rw
- Environment: DJANGO_SETTINGS_MODULE=barodybroject.settings

Usage: Brief example of how to use this module
"""
```

### Language-Specific Examples

**Python:**
```python
"""
File: models.py
Description: Django models for parody news articles and content management
Author: Barodybroject Team <team@example.com>
Created: 2025-01-15
Last Modified: 2025-01-20
Version: 1.2.0

Dependencies:
- django: >=4.0
- openai: >=1.0

Usage: from parodynews.models import Article
"""
```

**JavaScript:**
```javascript
/**
 * File: content_detail.js
 * Description: Dynamic content loading and AJAX form handling
 * Author: Barodybroject Team <team@example.com>
 * Created: 2025-01-15
 * Last Modified: 2025-01-20
 * Version: 1.0.0
 * 
 * Dependencies:
 * - Bootstrap 5
 * - jQuery (optional, prefer vanilla JS)
 * 
 * Usage: Include in content detail template
 */
```

**Bash:**
```bash
#!/bin/bash
# File: deploy.sh
# Description: Deployment automation script for Azure Container Apps
# Author: Barodybroject Team <team@example.com>
# Created: 2025-01-15
# Last Modified: 2025-01-20
# Version: 1.0.0
#
# Dependencies:
# - azure-cli
# - docker
#
# Usage: ./deploy.sh [environment]
```

## Container Development Practices

### Local Development Setup

Use Docker Compose for consistent local development:

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src:rw
      - ./static:/app/static:rw
    environment:
      - DEBUG=True
      - DATABASE_URL=postgresql://user:pass@db:5432/parody
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
    command: python manage.py runserver 0.0.0.0:8000

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=parody
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### Multi-Stage Dockerfile

```dockerfile
# Development stage
FROM python:3.8-slim AS development
WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Production stage
FROM python:3.8-slim AS production
WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

COPY src/ ./src/
RUN python src/manage.py collectstatic --noinput

USER 1000:1000
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--chdir", "src", "barodybroject.wsgi:application"]
```

## API Integration Best Practices

### OpenAI API Integration

**Configuration Management:**
```python
# settings.py
import os
from django.core.exceptions import ImproperlyConfigured

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ImproperlyConfigured('OPENAI_API_KEY environment variable is required')

OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4')
OPENAI_MAX_TOKENS = int(os.environ.get('OPENAI_MAX_TOKENS', '1000'))
OPENAI_TEMPERATURE = float(os.environ.get('OPENAI_TEMPERATURE', '0.7'))
```

**Service Layer Pattern:**
```python
# parodynews/services/openai_service.py
import openai
import logging
from django.conf import settings
from typing import Optional

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for OpenAI API interactions with error handling and retry logic"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.max_retries = 3
    
    def generate_parody_content(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """
        Generate parody content using OpenAI API
        
        Args:
            prompt: The input prompt for content generation
            max_tokens: Maximum tokens in response (default from settings)
        
        Returns:
            Generated content as string
        
        Raises:
            openai.OpenAIError: If API call fails after retries
        """
        max_tokens = max_tokens or settings.OPENAI_MAX_TOKENS
        
        for attempt in range(self.max_retries):
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a satirical news writer."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=settings.OPENAI_TEMPERATURE
                )
                
                content = response.choices[0].message.content
                logger.info(f"Generated content successfully (attempt {attempt + 1})")
                return content
                
            except openai.RateLimitError as e:
                logger.warning(f"Rate limit hit (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
                    
            except openai.APIError as e:
                logger.error(f"OpenAI API error (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                else:
                    raise
```

### Generic HTTP API Integration

**Reusable API Client Pattern:**
```python
# utils/api_client.py
import requests
import logging
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class APIClient:
    """Generic HTTP API client with retry logic and error handling"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set headers
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request with error handling"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"GET request failed: {url}, Error: {e}")
            raise
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request with error handling"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"POST request failed: {url}, Error: {e}")
            raise
```

## Django-Specific Best Practices

### Model Design

```python
from django.db import models
from django.contrib.auth.models import User

class Article(models.Model):
    """Parody news article model"""
    
    title = models.CharField(max_length=200, help_text="Article headline")
    content = models.TextField(help_text="Main article content")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    category = models.CharField(max_length=50, choices=[
        ('politics', 'Politics'),
        ('tech', 'Technology'),
        ('sports', 'Sports'),
    ])
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['category', '-published_at']),
        ]
    
    def __str__(self):
        return self.title
```

### View Patterns

```python
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Article
from .forms import ArticleForm

class ArticleListView(ListView):
    """Display list of published articles"""
    model = Article
    template_name = 'parodynews/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10
    
    def get_queryset(self):
        return Article.objects.filter(is_published=True)

class ArticleCreateView(LoginRequiredMixin, CreateView):
    """Create new article with OpenAI assistance"""
    model = Article
    form_class = ArticleForm
    template_name = 'parodynews/article_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
```

## Environment Configuration

### Settings Organization

```python
# barodybroject/settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError('SECRET_KEY environment variable must be set')

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'parody'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Use SQLite for local development if DATABASE_URL not set
if os.environ.get('USE_SQLITE', 'False').lower() == 'true':
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
```

### Environment Variables

Required environment variables:
- `SECRET_KEY` - Django secret key (generate with `django.core.management.utils.get_random_secret_key()`)
- `DATABASE_URL` or `DB_*` variables - Database connection
- `OPENAI_API_KEY` - OpenAI API authentication
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `DEBUG` - Set to 'True' for development only

Optional environment variables:
- `OPENAI_MODEL` - Model to use (default: gpt-4)
- `OPENAI_MAX_TOKENS` - Token limit (default: 1000)
- `OPENAI_TEMPERATURE` - Creativity setting (default: 0.7)
- `LOG_LEVEL` - Logging level (default: INFO)

## Error Handling Standards

### Django Exception Handling

```python
from django.core.exceptions import ValidationError
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

def api_view_with_error_handling(request):
    """Example API view with comprehensive error handling"""
    try:
        # Business logic
        data = process_request(request)
        return JsonResponse({'status': 'success', 'data': data})
        
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return JsonResponse(
            {'status': 'error', 'message': str(e)},
            status=400
        )
        
    except openai.OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        return JsonResponse(
            {'status': 'error', 'message': 'Content generation failed'},
            status=502
        )
        
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return JsonResponse(
            {'status': 'error', 'message': 'Internal server error'},
            status=500
        )
```

### Logging Configuration

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': os.environ.get('LOG_LEVEL', 'INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'parodynews': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

## Code Quality Standards

### Type Hints (Python)
```python
from typing import List, Optional, Dict, Any
from django.http import HttpRequest, HttpResponse

def generate_article(
    title: str,
    category: str,
    max_length: Optional[int] = None
) -> Dict[str, Any]:
    """Generate article with type hints for clarity"""
    # Implementation
    return {'title': title, 'content': '...'}
```

### Input Validation
```python
from django import forms
from django.core.validators import MinLengthValidator

class ArticleForm(forms.ModelForm):
    """Article creation form with validation"""
    
    class Meta:
        model = Article
        fields = ['title', 'content', 'category']
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 10:
            raise forms.ValidationError('Title must be at least 10 characters')
        return title
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 100:
            raise forms.ValidationError('Content must be at least 100 characters')
        return content
```

### Code Organization
- Keep views focused and single-purpose
- Use service layer for business logic
- Separate API logic from template views
- Group related functionality in Django apps
- Use managers for complex queryset logic

## Testing Requirements

All code should include appropriate tests:
- **Unit tests**: Test individual functions and methods
- **Integration tests**: Test Django views, forms, and database interactions
- **API tests**: Test REST endpoints with various inputs
- **UI tests**: Use Playwright for critical user flows

See `test.instructions.md` for detailed testing standards.

## Documentation Requirements

All code should be well-documented:
- **Docstrings**: Required for all classes, functions, and modules
- **README files**: Required in every directory explaining its purpose
- **Inline comments**: For complex logic or non-obvious decisions
- **API documentation**: Document all REST endpoints with request/response examples

See `documentation.instructions.md` for detailed documentation standards.

## Related Instructions

For language-specific guidance, refer to:
- `languages.instructions.md` - Python/Django, JavaScript, Bash standards
- `workflows.instructions.md` - GitHub Actions and CI/CD pipelines
- `documentation.instructions.md` - Markdown and documentation practices
- `test.instructions.md` - Testing standards and patterns
