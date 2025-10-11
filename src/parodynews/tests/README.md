
# tests Directory

## Purpose
This directory contains the comprehensive test suite for the parodynews Django application, including unit tests, integration tests, test configuration, and test data. It provides automated testing infrastructure to ensure code quality, functionality verification, and regression prevention for the parody news generator.

## Contents
- `conftest.py`: pytest configuration file with shared fixtures, test setup, and common test utilities
- `__init__.py`: Python package initialization file making the directory a Python module
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

# Run specific test categories
python -m pytest src/parodynews/tests/ -k "test_models"
python -m pytest src/parodynews/tests/ -k "test_views"

# Run tests with verbose output
python -m pytest src/parodynews/tests/ -v

# Example conftest.py fixtures
@pytest.fixture
def authenticated_user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass'
    )

@pytest.fixture
def sample_article(db):
    return Article.objects.create(
        title='Test Article',
        content='Test content'
    )
```

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
