Installation
============

This guide covers the installation process for the Barodybroject Django application.

Prerequisites
-------------

Before installing Barodybroject, ensure you have the following prerequisites:

- **GitHub CLI**: For repository management
- **Python 3.8 or higher**: The application requires Python 3.8+
- **pip**: Python package manager
- **virtualenv**: Recommended for creating isolated Python environments

Installation Steps
------------------

1. Clone the Repository
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Using GitHub CLI
   gh repo clone bamr87/barodybroject
   cd barodybroject

   # Or using git
   git clone https://github.com/bamr87/barodybroject.git
   cd barodybroject

2. Create Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # For Unix/Linux/Mac
   python3 -m venv .venv
   source .venv/bin/activate

   # For Windows
   python -m venv venv
   venv\Scripts\activate

3. Install Dependencies
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install -r requirements-dev.txt

4. Environment Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a ``.env`` file in the project root:

.. code-block:: bash

   DEBUG=True
   SECRET_KEY=your_secret_key
   DATABASE_URL=sqlite:///db.sqlite3
   CONTAINER_APP_NAME=barodybroject-test
   CONTAINER_APP_ENV_DNS_SUFFIX=localhost

5. Database Setup
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd src
   python manage.py makemigrations
   python manage.py migrate

6. Create Superuser (Optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python manage.py createsuperuser

7. Run Development Server
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python manage.py runserver

Your application should now be running at http://localhost:8000.

Docker Installation
-------------------

You can also run the application using Docker:

.. code-block:: bash

   docker compose build
   docker compose up -d

Troubleshooting
---------------

Common installation issues and their solutions:

**Module Import Errors**
   Ensure you've activated your virtual environment and installed all dependencies.

**Database Connection Issues**
   Check your ``.env`` file configuration and ensure the database URL is correct.

**Port Already in Use**
   Use a different port: ``python manage.py runserver 8001``