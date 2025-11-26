========
REST API
========

REST API endpoints for programmatic access to Parodynews.

Overview
========

The Parodynews REST API provides programmatic access to:

* Assistants
* Content items
* Threads and messages
* Configuration

API Endpoints
=============

(Endpoints will be documented in detail in future updates)

Authentication
==============

API authentication methods and requirements.

(To be documented)

Usage Examples
==============

Making API Requests
-------------------

.. code-block:: python

   import requests
   
   # Get list of assistants
   response = requests.get('http://localhost:8000/api/assistants/')
   assistants = response.json()
   
   # Create a new assistant
   data = {
       'name': 'New Assistant',
       'instructions': 'Generate content...'
   }
   response = requests.post('http://localhost:8000/api/assistants/', json=data)

See Also
========

* :doc:`serializers` - API serializers
* :doc:`views` - API views
* :doc:`../integrations/index` - Integration guides
