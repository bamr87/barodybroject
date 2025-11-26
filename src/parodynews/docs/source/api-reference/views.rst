=====
Views
=====

This page documents all Django views in the Parodynews application. Views handle
HTTP requests and return HTTP responses, implementing the application's user interface
and API endpoints.

.. currentmodule:: parodynews.views

.. automodule:: parodynews.views
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: get,post,put,patch,delete

Class-Based Views
=================

Home and Navigation
-------------------

The main entry points for the application.

Assistant Views
---------------

Views for managing AI assistants and assistant groups.

Content Generation Views
------------------------

Views for generating and managing content.

Thread and Message Views
------------------------

Views for managing conversation threads and messages.

API ViewSets
============

REST API viewsets for programmatic access.

.. note::
   
   For detailed REST API documentation, see :doc:`rest-api`.

Function-Based Views
====================

Utility and helper views that don't fit the class-based view pattern.

View Mixins
===========

See :doc:`mixins` for reusable view mixins.

Usage Examples
==============

Using Views in URLs
-------------------

.. code-block:: python

   from django.urls import path
   from parodynews.views import AssistantListView, AssistantDetailView
   
   urlpatterns = [
       path('assistants/', AssistantListView.as_view(), name='assistant-list'),
       path('assistants/<int:pk>/', AssistantDetailView.as_view(), name='assistant-detail'),
   ]

Extending Views
---------------

.. code-block:: python

   from parodynews.views import AssistantListView
   
   class MyCustomAssistantList(AssistantListView):
       template_name = 'my_custom_template.html'
       paginate_by = 20
       
       def get_queryset(self):
           qs = super().get_queryset()
           return qs.filter(is_active=True)

See Also
========

* :doc:`urls` - URL configuration
* :doc:`forms` - Forms used by views
* :doc:`models` - Models accessed by views
* :doc:`mixins` - View mixins
