===========
Serializers
===========

Django REST Framework serializers for API endpoints.

.. currentmodule:: parodynews.serializers

.. automodule:: parodynews.serializers
   :members:
   :undoc-members:
   :show-inheritance:

Overview
========

Serializers convert model instances to/from JSON for the REST API.

Key Serializers
===============

(Serializers will be auto-documented from docstrings when built)

Usage Examples
==============

Using Serializers
-----------------

.. code-block:: python

   from parodynews.serializers import AssistantSerializer
   from parodynews.models import Assistant
   
   # Serialize an assistant
   assistant = Assistant.objects.get(pk=1)
   serializer = AssistantSerializer(assistant)
   data = serializer.data
   
   # Deserialize data
   serializer = AssistantSerializer(data=request.data)
   if serializer.is_valid():
       assistant = serializer.save()

See Also
========

* :doc:`models` - Models being serialized
* :doc:`rest-api` - REST API endpoints
* :doc:`views` - API views
