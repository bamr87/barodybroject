# Parodynews Models Package

## Overview

The models package has been refactored to improve code organization and maintainability. Models are now organized into logical modules by domain rather than being in a single monolithic file.

## Structure

```
models/
├── __init__.py              # Backward-compatible imports
├── base.py                  # Abstract base classes and mixins
├── config.py                # Application configuration models
├── ai.py                    # OpenAI and AI assistant models
├── content.py               # Content generation models
├── conversation.py          # Thread and message models
└── publishing.py            # Post and publishing models
```

## Module Descriptions

### base.py
Contains abstract base classes and mixins that can be shared across different model modules:
- `TimestampedModel`: Abstract base for models with created_at/updated_at fields
- `DisplayFieldsMixin`: Mixin for get_display_fields() method

### config.py
Application-wide configuration and settings:
- `AppConfig`: OpenAI API keys, GitHub Pages configuration
- `PoweredBy`: Attribution links for technologies used
- `FieldDefaults`: Dynamic default values for model fields

### ai.py
AI and OpenAI integration models:
- `JSONSchema`: JSON schema definitions for structured content
- `OpenAIModel`: OpenAI model configurations (GPT-4, etc.)
- `Assistant`: AI assistant configurations
- `AssistantGroup`: Groups of assistants for workflows
- `AssistantGroupMembership`: Many-to-many relationship for assistant groups

### content.py
Content generation and management:
- `ContentDetail`: Metadata for generated content
- `ContentItem`: Individual content segments

### conversation.py
Conversation thread management:
- `Thread`: Conversation threads for multi-turn generation
- `Message`: Individual messages in threads

### publishing.py
Post publishing and versioning:
- `PostPageConfigModel`: Pagination configuration
- `Post`: Published content posts
- `PostFrontMatter`: YAML front matter for posts
- `PostVersion`: Version history for posts

## Usage

### Backward Compatible Imports (Recommended)

The `__init__.py` file provides backward-compatible imports, so existing code continues to work:

```python
# Import as before - works exactly the same
from parodynews.models import Assistant, Post, ContentDetail
```

### Direct Module Imports (Optional)

You can also import directly from specific modules if you prefer:

```python
from parodynews.models.ai import Assistant
from parodynews.models.publishing import Post
from parodynews.models.content import ContentDetail
```

## Migration Guide

### For Developers

1. **No immediate changes required**: All existing imports will continue to work due to the `__init__.py` file.

2. **Field rename**: `AssistantGroupMembership.assistants` will be renamed to `assistant` (singular) in a future migration for clarity.

### Database Migrations

The model split itself requires no database migrations as it's purely a code organization change. However, future migrations may include:

1. Renaming `AssistantGroupMembership.assistants` → `assistant`
2. Adding indexes for better query performance

## Benefits

1. **Maintainability**: Easier to find and modify related models
2. **Clarity**: Clear separation of concerns by domain
3. **Scalability**: Easier to add new models in appropriate modules
4. **Testing**: Easier to test models in isolation
5. **Onboarding**: New developers can understand the domain structure faster
6. **Performance**: Added indexes for common queries

## Version History

- **2.0.0** (2025-11-30): Split models.py into package structure
- **1.0.0** (2024-01-01): Initial models.py implementation

## See Also

- [Main README](../README.md)
- [Django Models Documentation](https://docs.djangoproject.com/en/stable/topics/db/models/)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)

