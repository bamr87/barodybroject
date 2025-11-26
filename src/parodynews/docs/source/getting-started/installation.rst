============
Installation
============

This guide walks you through installing Parodynews using Docker Compose, which is the
recommended approach for both development and production environments.

Docker Installation (Recommended)
==================================

Prerequisites
-------------

Ensure you have the following installed:

* Docker Desktop (or Docker Engine + Docker Compose)
* Git

Clone the Repository
--------------------

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/bamr87/barodybroject.git
   cd barodybroject

Development Environment
-----------------------

Start the development containers:

.. code-block:: bash

   # Start development environment
   docker-compose -f .devcontainer/docker-compose_dev.yml up -d
   
   # Check container status
   docker-compose -f .devcontainer/docker-compose_dev.yml ps

This will start:

* **python**: Django development server (port 8000)
* **barodydb**: PostgreSQL database (port 5432)
* **jekyll**: Jekyll static site server (port 4000)

Run Initial Setup
-----------------

After containers are running, set up the database:

.. code-block:: bash

   # Run database migrations
   docker-compose -f .devcontainer/docker-compose_dev.yml exec python \\
       python manage.py migrate
   
   # Create a superuser
   docker-compose -f .devcontainer/docker-compose_dev.yml exec python \\
       python manage.py createsuperuser
   
   # Collect static files
   docker-compose -f .devcontainer/docker-compose_dev.yml exec python \\
       python manage.py collectstatic --noinput

Verify Installation
-------------------

1. Open http://localhost:8000 in your browser
2. You should see the Parodynews home page
3. Navigate to http://localhost:8000/admin to access the Django admin interface
4. Log in with the superuser credentials you created

Production Environment
======================

For production deployment:

.. code-block:: bash

   # Start production containers
   docker-compose up -d
   
   # Run migrations
   docker-compose exec web-prod python manage.py migrate
   
   # Create superuser
   docker-compose exec web-prod python manage.py createsuperuser

Manual Installation (Without Docker)
=====================================

If you prefer not to use Docker:

System Requirements
-------------------

* Python 3.8 or higher
* PostgreSQL 13 or higher
* Node.js 16+ (for Jekyll/frontend tools)

Install Python Dependencies
----------------------------

.. code-block:: bash

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   
   # Install dependencies
   pip install -r requirements-dev.txt

Configure Database
------------------

Create a PostgreSQL database:

.. code-block:: bash

   createdb parodynews_dev

Set environment variables:

.. code-block:: bash

   export DATABASE_URL="postgresql://user:password@localhost:5432/parodynews_dev"
   export DJANGO_SECRET_KEY="your-secret-key-here"
   export OPENAI_API_KEY="your-openai-api-key"

Run Django
----------

.. code-block:: bash

   cd src
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic --noinput
   python manage.py runserver

Troubleshooting
===============

Port Conflicts
--------------

If ports 8000, 5432, or 4000 are already in use, you can change them in the
``docker-compose.yml`` file or use environment variables:

.. code-block:: bash

   DJANGO_DEV_PORT=8001 docker-compose -f .devcontainer/docker-compose_dev.yml up -d

Permission Issues
-----------------

If you encounter permission issues with Docker volumes:

.. code-block:: bash

   # Fix ownership (Linux/Mac)
   sudo chown -R $USER:$USER .

Database Connection Errors
---------------------------

If you can't connect to the database:

1. Ensure the database container is running
2. Check that the DATABASE_URL is correct
3. Verify PostgreSQL is accepting connections

Next Steps
==========

* :doc:`configuration` - Configure your environment
* :doc:`quickstart` - Quick start guide
* :doc:`../how-to/troubleshooting` - More troubleshooting tips
