=============
Configuration
=============

This guide covers configuring Parodynews for your environment.

Environment Variables
=====================

Required Variables
------------------

The following environment variables must be set:

.. code-block:: bash

   # Django Configuration
   DJANGO_SECRET_KEY=your-secret-key-here
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Database Configuration
   DATABASE_URL=postgresql://user:password@localhost:5432/parodynews
   
   # OpenAI Configuration
   OPENAI_API_KEY=sk-your-openai-api-key-here
   OPENAI_ORG_ID=org-your-organization-id
   
   # GitHub Configuration (for publishing)
   GITHUB_TOKEN=ghp_your-github-token
   GITHUB_REPO=username/repository
   GITHUB_BRANCH=main

Optional Variables
------------------

.. code-block:: bash

   # OpenAI Model Configuration
   OPENAI_MODEL=gpt-4
   OPENAI_MAX_TOKENS=2000
   OPENAI_TEMPERATURE=0.7
   
   # Application Settings
   DJANGO_LANGUAGE_CODE=en-us
   DJANGO_TIME_ZONE=UTC
   
   # Static and Media Files
   STATIC_ROOT=/app/staticfiles
   MEDIA_ROOT=/app/media

Django Settings
===============

See :doc:`../reference/settings` for detailed Django settings documentation.

Next Steps
==========

* :doc:`quickstart` - Quick start guide
* :doc:`first-content` - Create your first content
* :doc:`../reference/environment-vars` - Complete environment variable reference
