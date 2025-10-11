Quick Start Guide
=================

This guide will get you up and running with Barodybroject quickly.

Basic Usage
-----------

After installation, you can start using Barodybroject immediately:

1. **Access the Application**
   
   Navigate to http://localhost:8000 in your web browser.

2. **Admin Interface**
   
   Access the Django admin at http://localhost:8000/admin using your superuser credentials.

3. **API Endpoints**
   
   The application provides RESTful API endpoints for programmatic access.

Key Features
------------

User Authentication
~~~~~~~~~~~~~~~~~~~

Barodybroject supports:

- User registration and login
- Password management
- Multi-factor authentication (MFA)
- Social authentication
- SAML integration

Content Management
~~~~~~~~~~~~~~~~~~

- Dynamic content creation and management
- Blog module with categories and tags
- Rich text editing with CKEditor
- File and image management
- Import/export functionality

API Integration
~~~~~~~~~~~~~~~

- OpenAI integration for content generation
- RESTful API for external integrations
- Real-time messaging system
- Thread-based conversation management

Development Features
~~~~~~~~~~~~~~~~~~~~

- Hot reload development environment
- Comprehensive test suite
- Code quality tools (Ruff linter)
- Documentation generation with Sphinx

Next Steps
----------

1. **Explore the Admin Interface**: Create content, manage users, and configure settings.
2. **Review the API Documentation**: Learn about available endpoints and data models.
3. **Set up OpenAI Integration**: Configure your OpenAI API key for content generation features.
4. **Customize Templates**: Modify templates to match your branding.
5. **Deploy to Production**: Follow the deployment guide for production setup.

Common Tasks
------------

Creating Content
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Example of creating content programmatically
   from parodynews.models import Content
   
   content = Content.objects.create(
       title="Sample Content",
       body="This is sample content",
       published=True
   )

Running Tests
~~~~~~~~~~~~~

.. code-block:: bash

   python -m pytest

Building Documentation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd docs
   make html

For more detailed information, see the :doc:`configuration` and :doc:`api/index` sections.