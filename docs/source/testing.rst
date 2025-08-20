Testing
=======

This section covers the testing framework and practices used in Barodybroject.

Test Framework
--------------

Barodybroject uses the following testing tools:

- **pytest**: Primary testing framework
- **pytest-django**: Django-specific pytest extensions
- **pytest-playwright**: End-to-end browser testing
- **pytest-cov**: Code coverage reporting
- **selenium**: Web driver testing
- **beautifulsoup4**: HTML parsing for tests

Running Tests
-------------

Basic Test Execution
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests
   python -m pytest
   
   # Run with verbose output
   python -m pytest -v
   
   # Run specific test file
   python -m pytest parodynews/tests/test_models.py
   
   # Run specific test function
   python -m pytest parodynews/tests/test_models.py::test_content_creation

Coverage Reports
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run tests with coverage
   python -m pytest --cov=parodynews
   
   # Generate HTML coverage report
   python -m pytest --cov=parodynews --cov-report=html
   
   # Generate XML coverage report for CI
   python -m pytest --cov=parodynews --cov-report=xml

Browser Testing
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install browser dependencies
   python -m playwright install chromium --with-deps
   
   # Run browser tests
   python -m pytest --browser chromium

Test Structure
--------------

Tests are organized in the following structure:

.. code-block::

   parodynews/
   ├── tests/
   │   ├── __init__.py
   │   ├── test_models.py
   │   ├── test_views.py
   │   ├── test_admin.py
   │   ├── test_forms.py
   │   └── test_management_commands.py
   └── tests.py  # Legacy test file

Test Categories
---------------

Unit Tests
~~~~~~~~~~

Test individual components in isolation:

.. code-block:: python

   def test_content_str_representation():
       """Test Content model string representation."""
       content = Content(title="Test Content")
       assert str(content) == "Test Content"

Integration Tests
~~~~~~~~~~~~~~~~~

Test interactions between components:

.. code-block:: python

   def test_content_creation_view(client):
       """Test content creation through view."""
       response = client.post('/content/create/', {
           'title': 'New Content',
           'body': 'Content body'
       })
       assert response.status_code == 201

End-to-End Tests
~~~~~~~~~~~~~~~~

Test complete user workflows:

.. code-block:: python

   def test_user_login_flow(page):
       """Test complete user login flow."""
       page.goto("/login/")
       page.fill("input[name='username']", "testuser")
       page.fill("input[name='password']", "password")
       page.click("button[type='submit']")
       expect(page).to_have_url("/dashboard/")

Writing Tests
-------------

Test Best Practices
~~~~~~~~~~~~~~~~~~~

1. **Follow AAA Pattern**: Arrange, Act, Assert
2. **Use Descriptive Names**: Test names should describe what they test
3. **One Assertion Per Test**: Focus on testing one thing at a time
4. **Use Fixtures**: Share common setup between tests
5. **Mock External Dependencies**: Don't depend on external services

Django Test Utilities
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pytest
   from django.test import Client
   from django.contrib.auth.models import User
   from parodynews.models import Content

   @pytest.fixture
   def user():
       """Create test user."""
       return User.objects.create_user(
           username='testuser',
           email='test@example.com',
           password='password'
       )

   @pytest.fixture
   def content(user):
       """Create test content."""
       return Content.objects.create(
           title='Test Content',
           body='Test body',
           author=user
       )

   def test_content_creation(content):
       """Test content is created properly."""
       assert content.title == 'Test Content'
       assert content.body == 'Test body'

Model Testing
~~~~~~~~~~~~~

.. code-block:: python

   def test_content_model_creation():
       """Test Content model creation."""
       content = Content.objects.create(
           title="Test Content",
           body="Test body content",
           published=True
       )
       assert content.title == "Test Content"
       assert content.published is True
       assert content.slug  # Auto-generated slug

View Testing
~~~~~~~~~~~~

.. code-block:: python

   def test_content_list_view(client):
       """Test content list view."""
       response = client.get('/content/')
       assert response.status_code == 200
       assert 'content_list' in response.context

Admin Testing
~~~~~~~~~~~~~

.. code-block:: python

   def test_content_admin_creation(admin_client):
       """Test content creation through admin."""
       response = admin_client.post('/admin/parodynews/content/add/', {
           'title': 'Admin Content',
           'body': 'Created through admin',
           'published': True
       })
       assert response.status_code == 302  # Redirect after creation

Form Testing
~~~~~~~~~~~~

.. code-block:: python

   def test_content_form_validation():
       """Test content form validation."""
       form_data = {
           'title': '',  # Invalid: required field
           'body': 'Some content'
       }
       form = ContentForm(data=form_data)
       assert not form.is_valid()
       assert 'title' in form.errors

API Testing
~~~~~~~~~~~

.. code-block:: python

   def test_api_content_creation(api_client):
       """Test content creation via API."""
       data = {
           'title': 'API Content',
           'body': 'Created via API'
       }
       response = api_client.post('/api/content/', data)
       assert response.status_code == 201
       assert response.json()['title'] == 'API Content'

Test Configuration
------------------

pytest Configuration
~~~~~~~~~~~~~~~~~~~~

Configuration in ``pyproject.toml``:

.. code-block:: toml

   [tool.pytest.ini_options]
   minversion = "6.0"
   addopts = "--strict-markers"
   testpaths = ["tests"]
   django_find_project = false
   DJANGO_SETTINGS_MODULE = "barodybroject.settings"

Django Test Settings
~~~~~~~~~~~~~~~~~~~~

Test-specific settings can be configured in a separate settings file:

.. code-block:: python

   # settings/test.py
   from .base import *

   # Use in-memory database for tests
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': ':memory:',
       }
   }

   # Disable migrations for faster tests
   class DisableMigrations:
       def __contains__(self, item):
           return True
       def __getitem__(self, item):
           return None

   MIGRATION_MODULES = DisableMigrations()

Continuous Integration
----------------------

GitHub Actions
~~~~~~~~~~~~~~

The project includes GitHub Actions for automated testing:

.. code-block:: yaml

   name: Tests
   on: [push, pull_request]
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - uses: actions/setup-python@v2
           with:
             python-version: 3.8
         - run: pip install -r requirements-dev.txt
         - run: python -m pytest --cov=parodynews

Coverage Requirements
~~~~~~~~~~~~~~~~~~~~

Maintain test coverage above 80%:

.. code-block:: bash

   python -m pytest --cov=parodynews --cov-fail-under=80

Performance Testing
-------------------

For performance-critical code, include performance tests:

.. code-block:: python

   import time
   import pytest

   def test_content_query_performance():
       """Test content query performance."""
       start_time = time.time()
       list(Content.objects.all()[:100])
       end_time = time.time()
       
       # Should complete within 1 second
       assert (end_time - start_time) < 1.0

Debugging Tests
---------------

Use pytest debugging features:

.. code-block:: bash

   # Drop into debugger on failure
   python -m pytest --pdb
   
   # Show local variables on failure
   python -m pytest -l
   
   # Run last failed tests only
   python -m pytest --lf