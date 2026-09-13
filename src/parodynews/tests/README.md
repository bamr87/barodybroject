
# tests Directory

## Purpose
This directory contains the comprehensive test suite for the parodynews Django application, including unit tests, integration tests, test configuration, and test data. It provides automated testing infrastructure to ensure code quality, functionality verification, and regression prevention for the parody news generator.

## Contents
- `conftest.py`: shared fixtures — the Playwright/e2e session fixtures, plus the **model factories** every `test_models_*.py` module builds on (`user`, `openai_model`, `json_schema`, `assistant`, `assistant_group`, `content_detail`, `content_item`, `thread`, `message`, `post`) and the `*_export` fixtures that read `data/*.json`. Factories live here, not per file, so a field rename breaks in one place
- `__init__.py`: Python package initialization file making the directory a Python module
- `test_models_base.py`: `TimestampedModel` (abstract — asserted through its field definitions, since it has no concrete subclass) and `DisplayFieldsMixin`
- `test_models_config.py`: `PoweredBy`, `AppConfig`, `FieldDefaults` — including the custom `save()` that invalidates the `field_defaults` cache key
- `test_models_ai.py`: `JSONSchema`, `OpenAIModel`, `Assistant`, `AssistantGroup`, `AssistantGroupMembership` — the through-model's join, ordering, and `SET_NULL` behaviour on both sides
- `test_models_content.py`: `ContentDetail` and `ContentItem` — including the custom `save()` that numbers items sequentially *per parent detail*
- `test_models_conversation.py`: `Thread` and `Message` model semantics (the delete *route* is covered by `test_thread_message_delete.py`; these do not duplicate it)
- `test_models_publishing.py`: `PostPageConfigModel`, `Post`, `PostFrontMatter`, `PostVersion` — `get_absolute_url()`, `auto_now`, the one-to-one and `unique_together` constraints, plus a completeness guard asserting every name in `parodynews.models.__all__` is referenced by one of these six modules
- `test_templates.py`: Django template structure, accessibility, and Bootstrap 5 usage tests
- `test_model_table.py`: regression tests for the `model_table.html` ↔ `table_utils.js` markup contract (the `sortable` class and `data-type` a column needs for sorting to bind and order correctly)
- `e2e/`: Playwright end-to-end specs, marked `@pytest.mark.e2e` and deselected by default (`pytest.ini` sets `-m "not e2e"`); run them with `pytest -m e2e --browser chromium` against a running server
- `test_thread_message_delete.py`: regression tests for the thread-message delete route — pins the `openai_delete_message` arity and the remote-before-local delete ordering (issue #30)
- `test_fetch_models.py`: tests for `manage.py fetch_models` — the assistant-capable model filter, populated descriptions, retiring delisted models without unassigning their assistants, and failing loudly on an API error (issue #110). The OpenAI client is faked in every case via `Command.get_client`, so nothing here contacts the live API; the `IsAssistantModelTests` class is a `SimpleTestCase` and needs no database
- `data/`: Test data directory containing sample data, fixtures, and mock responses (has its own README)
- `scripts/`: Test scripts directory containing testing utilities and automation scripts (has its own README)
- `.pytest_cache/`: Subdirectory for pytest cache files (auto-generated)
- `__pycache__/`: Subdirectory for Python bytecode cache (auto-generated)

## Usage
Tests are executed using pytest with Django integration:

```bash
# Run all tests
python -m pytest src/parodynews/tests/

# Run tests with coverage
python -m pytest src/parodynews/tests/ --cov=src/parodynews

# Model unit tests only, with their coverage
python -m pytest src/parodynews/tests/ -k "test_models" \
  --cov=parodynews.models --cov-report=term-missing

# Run specific test categories
python -m pytest src/parodynews/tests/ -k "test_views"

# Run tests with verbose output
python -m pytest src/parodynews/tests/ -v

# Real conftest.py fixtures — compose them, don't rebuild them
def test_a_post_belongs_to_its_author(post, user):
    assert post.user == user

def test_an_assistant_comes_from_the_real_export(assistant, assistant_export):
    assert assistant.name == assistant_export[0]["name"]
```

The factories chain, so asking for `post` transitively creates the `user`,
`content_detail`, `thread`, `message`, `assistant`, `openai_model` and
`json_schema` it needs. Each depends on `db`, so requesting one is enough to get
database access — no extra `@pytest.mark.django_db` on the test itself.

Testing features:
- **Unit Tests**: Individual component testing for models, views, forms, and utilities
- **Integration Tests**: End-to-end testing of complete user workflows
- **API Tests**: REST API endpoint testing with authentication and permissions
- **Database Tests**: Model relationships, constraints, and data integrity
- **Authentication Tests**: User authentication, authorization, and session management
- **OpenAI Integration Tests**: Mocked testing of AI content generation features

## Container Configuration
Tests run within containerized development environment:
- pytest executed in Django development container
- Database tests use isolated test database
- Test fixtures provide consistent test data
- Coverage reports generated for code quality metrics
- CI/CD integration through GitHub Actions workflows

## Related Paths
- Incoming: Tests validate functionality of Django models, views, forms, and utilities from parent directories
- Outgoing: Generates test reports, coverage data, and validation results for CI/CD pipelines
