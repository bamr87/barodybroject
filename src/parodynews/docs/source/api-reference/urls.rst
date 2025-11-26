====
URLs
====

URL routing configuration for Parodynews.

.. currentmodule:: parodynews.urls

.. automodule:: parodynews.urls
   :members:
   :undoc-members:

URL Patterns
============

The Parodynews application defines URL patterns for:

* Web interface views
* REST API endpoints
* Admin interface (via Django admin)

Configuration
=============

Include in your project's ``urls.py``:

.. code-block:: python

   from django.urls import path, include
   
   urlpatterns = [
       path('', include('parodynews.urls')),
   ]

See Also
========

* :doc:`views` - Views mapped to URLs
* :doc:`rest-api` - REST API endpoints
