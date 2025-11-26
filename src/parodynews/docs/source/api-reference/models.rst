======
Models
======

This page documents all Django models in the Parodynews application. These models
represent the database schema and business logic for content generation, assistant
management, and configuration.

.. currentmodule:: parodynews.models

Core Models
===========

Assistant
---------

.. autoclass:: Assistant
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __str__

The Assistant model represents an OpenAI assistant configuration with custom instructions
and behavior settings.

AssistantGroup
--------------

.. autoclass:: AssistantGroup
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __str__

Groups multiple assistants together for organizational purposes.

ContentItem
-----------

.. autoclass:: ContentItem
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __str__

Represents a piece of generated content (article, post, etc.).

OpenAI Configuration Models
============================

OpenAIModel
-----------

.. autoclass:: OpenAIModel
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __str__

Represents an OpenAI model configuration (GPT-4, GPT-3.5, etc.).

Thread
------

.. autoclass:: Thread
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __str__

Represents a conversation thread with an OpenAI assistant.

Message
-------

.. autoclass:: Message
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __str__

Represents a message within a thread (user or assistant message).

Run
---

.. autoclass:: Run
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __str__

Represents an execution run of an assistant on a thread.

Configuration Models
====================

AppConfig
---------

.. autoclass:: AppConfig
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __str__

Application-wide configuration settings.

PoweredBy
---------

.. autoclass:: PoweredBy
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __str__

Configuration for "Powered By" attribution links.

Template and Schema Models
===========================

PostTemplate
------------

.. autoclass:: PostTemplate
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __str__

Templates for generating structured posts.

JSONSchema
----------

.. autoclass:: JSONSchema
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __str__

JSON schema definitions for structured output.

Model Relationships
===================

The following diagram shows the key relationships between models:

.. code-block:: text

   AppConfig (1)
   
   AssistantGroup (1) ──< Assistant (N)
                          ├──< Thread (N)
                          │    └──< Message (N)
                          │    └──< Run (N)
                          └──< ContentItem (N)
   
   OpenAIModel (N) ──< Assistant (N)
   
   PostTemplate (N) ──< ContentItem (N)
   JSONSchema (N) ──< ContentItem (N)

Usage Examples
==============

Creating an Assistant
---------------------

.. code-block:: python

   from parodynews.models import Assistant, OpenAIModel
   
   # Get or create a model
   model = OpenAIModel.objects.get_or_create(
       name='gpt-4',
       defaults={'description': 'GPT-4 model'}
   )[0]
   
   # Create an assistant
   assistant = Assistant.objects.create(
       name='Parody News Writer',
       instructions='Write satirical news articles',
       model=model
   )

Creating a Thread and Messages
-------------------------------

.. code-block:: python

   from parodynews.models import Thread, Message
   
   # Create a thread
   thread = Thread.objects.create(
       assistant=assistant,
       title='Tech News Parody'
   )
   
   # Add a user message
   message = Message.objects.create(
       thread=thread,
       role='user',
       content='Write about AI taking over the workplace'
   )

Generating Content
------------------

.. code-block:: python

   from parodynews.models import ContentItem
   
   # Create content item
   content = ContentItem.objects.create(
       assistant=assistant,
       thread=thread,
       title='AI Demands Coffee Breaks',
       content='In a shocking development...',
       status='published'
   )

See Also
========

* :doc:`views` - Views that use these models
* :doc:`forms` - Forms for model data entry
* :doc:`serializers` - API serializers for models
* :doc:`../user-guide/assistants` - User guide for assistants
