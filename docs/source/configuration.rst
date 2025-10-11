Configuration
=============

This section covers the configuration options for Barodybroject.

Environment Variables
---------------------

Barodybroject uses environment variables for configuration. Create a ``.env`` file in your project root:

Required Settings
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Variable
     - Default
     - Description
   * - ``SECRET_KEY``
     - *Required*
     - Django secret key for cryptographic operations
   * - ``DATABASE_URL``
     - ``sqlite:///db.sqlite3``
     - Database connection string
   * - ``DEBUG``
     - ``False``
     - Enable/disable debug mode

Optional Settings
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Variable
     - Default
     - Description
   * - ``OPENAI_API_KEY``
     - ``None``
     - OpenAI API key for content generation
   * - ``ALLOWED_HOSTS``
     - ``localhost,127.0.0.1``
     - Comma-separated list of allowed hosts
   * - ``CONTAINER_APP_NAME``
     - ``barodybroject``
     - Container application name
   * - ``CONTAINER_APP_ENV_DNS_SUFFIX``
     - ``localhost``
     - DNS suffix for container environment

Database Configuration
----------------------

SQLite (Default)
~~~~~~~~~~~~~~~~

.. code-block:: bash

   DATABASE_URL=sqlite:///db.sqlite3

PostgreSQL
~~~~~~~~~~

.. code-block:: bash

   DATABASE_URL=postgresql://user:password@localhost:5432/dbname

MySQL
~~~~~

.. code-block:: bash

   DATABASE_URL=mysql://user:password@localhost:3306/dbname

OpenAI Integration
------------------

To enable OpenAI features, configure your API key:

.. code-block:: bash

   OPENAI_API_KEY=your_openai_api_key_here

Email Configuration
-------------------

Django SES (Amazon Simple Email Service)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   EMAIL_BACKEND=django_ses.SESBackend
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_SES_REGION_NAME=us-east-1

SMTP Configuration
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_password

Static Files Configuration
--------------------------

For production deployments:

.. code-block:: bash

   STATIC_URL=/static/
   STATIC_ROOT=/var/www/static/
   MEDIA_URL=/media/
   MEDIA_ROOT=/var/www/media/

Security Settings
-----------------

HTTPS Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   SECURE_SSL_REDIRECT=True
   SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
   SECURE_HSTS_SECONDS=31536000
   SECURE_HSTS_INCLUDE_SUBDOMAINS=True
   SECURE_HSTS_PRELOAD=True

Session Security
~~~~~~~~~~~~~~~~

.. code-block:: bash

   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   SESSION_COOKIE_HTTPONLY=True
   CSRF_COOKIE_HTTPONLY=True

Django CMS Configuration
-------------------------

CMS-specific settings are configured in the Django settings. See ``barodybroject/settings.py`` for CMS configuration options.

Logging Configuration
---------------------

Configure logging levels and handlers:

.. code-block:: bash

   LOG_LEVEL=INFO
   DJANGO_LOG_LEVEL=INFO

Azure Configuration
-------------------

For Azure deployments:

.. code-block:: bash

   AZURE_MONITOR_CONNECTION_STRING=your_connection_string
   AZURE_STORAGE_ACCOUNT_NAME=your_storage_account
   AZURE_STORAGE_ACCOUNT_KEY=your_storage_key

For more advanced configuration options, see the Django settings file at ``src/barodybroject/settings.py``.