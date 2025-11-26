=============
API Reference
=============

Complete API reference for the Parodynews Django application. This section documents
all models, views, forms, serializers, and utilities.

Overview
========

The Parodynews API is organized into several key components:

* **Models**: Database models for content, assistants, and configuration
* **Views**: Django views and viewsets for handling requests
* **Forms**: Form classes for user input validation
* **Serializers**: DRF serializers for API endpoints
* **URLs**: URL routing configuration
* **Admin**: Django admin customizations
* **Mixins**: Reusable view and model mixins
* **Utils**: Utility functions and helpers
* **Management Commands**: Custom Django management commands

Quick Navigation
================

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Component
     - Description
   * - :doc:`models`
     - Database models (Assistant, ContentItem, OpenAIModel, etc.)
   * - :doc:`views`
     - Django views and class-based views
   * - :doc:`forms`
     - Form classes for data validation
   * - :doc:`serializers`
     - REST API serializers
   * - :doc:`urls`
     - URL routing patterns
   * - :doc:`admin`
     - Admin interface customizations
   * - :doc:`mixins`
     - Reusable mixin classes
   * - :doc:`utils`
     - Utility functions
   * - :doc:`management`
     - Custom management commands
   * - :doc:`rest-api`
     - REST API endpoints

.. toctree::
   :maxdepth: 2
   :caption: Core Components
   
   models
   views
   forms
   serializers
   urls
   admin

.. toctree::
   :maxdepth: 2
   :caption: Supporting Components
   
   mixins
   utils
   management
   rest-api

Code Organization
=================

The parodynews application follows Django best practices for code organization:

.. code-block:: text

   parodynews/
   ├── models.py           # Database models
   ├── views.py            # View logic
   ├── forms.py            # Form definitions
   ├── serializers.py      # DRF serializers
   ├── urls.py             # URL configuration
   ├── admin.py            # Admin customizations
   ├── mixins.py           # Reusable mixins
   ├── utils/              # Utility modules
   │   └── dkim_backend.py
   ├── management/         # Custom commands
   │   └── commands/
   ├── templates/          # HTML templates
   └── tests/              # Test suite

Usage Examples
==============

Import and use the API:

.. code-block:: python

   from parodynews.models import Assistant, ContentItem
   from parodynews.views import AssistantListView
   from parodynews.forms import AssistantForm
   
   # Create an assistant
   assistant = Assistant.objects.create(
       name="News Generator",
       instructions="Generate satirical news articles"
   )
   
   # Use in a view
   class MyView(AssistantListView):
       template_name = 'my_template.html'

See Also
========

* :doc:`../user-guide/index` - User-facing documentation
* :doc:`../developer-guide/index` - Development guidelines
* :doc:`../integrations/openai` - OpenAI integration details
