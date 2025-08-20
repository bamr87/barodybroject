Deployment
==========

This section covers various deployment options for Barodybroject.

Azure Container Apps
--------------------

Barodybroject is designed for deployment on Azure Container Apps using the Azure Developer CLI.

Prerequisites
~~~~~~~~~~~~~

- Azure account with active subscription
- Azure Developer CLI (azd) installed
- Docker installed locally

Quick Deployment
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Login to Azure
   azd auth login
   
   # Initialize the project
   azd init
   
   # Deploy to Azure
   azd up

The ``azd up`` command will:

1. Provision Azure resources
2. Build and push the Docker image
3. Deploy the application
4. Configure environment variables

Environment Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

Configure environment variables in Azure:

.. code-block:: bash

   azd env set SECRET_KEY "your-secret-key"
   azd env set OPENAI_API_KEY "your-openai-key"
   azd env set DATABASE_URL "postgresql://..."

Manual Azure Deployment
~~~~~~~~~~~~~~~~~~~~~~~

For manual deployment, you can use the Azure CLI:

.. code-block:: bash

   # Create resource group
   az group create --name barodybroject-rg --location eastus
   
   # Create container app environment
   az containerapp env create \
     --name barodybroject-env \
     --resource-group barodybroject-rg \
     --location eastus
   
   # Deploy container app
   az containerapp create \
     --name barodybroject \
     --resource-group barodybroject-rg \
     --environment barodybroject-env \
     --image your-registry/barodybroject:latest

Docker Deployment
-----------------

Using Docker Compose
~~~~~~~~~~~~~~~~~~~~

For production deployment with Docker Compose:

.. code-block:: yaml

   version: '3.8'
   services:
     web:
       build: .
       ports:
         - "8000:8000"
       environment:
         - DEBUG=False
         - SECRET_KEY=your-secret-key
         - DATABASE_URL=postgresql://...
       depends_on:
         - db
     
     db:
       image: postgres:13
       environment:
         - POSTGRES_DB=barodybroject
         - POSTGRES_USER=postgres
         - POSTGRES_PASSWORD=password
       volumes:
         - postgres_data:/var/lib/postgresql/data
   
   volumes:
     postgres_data:

Single Container
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Build the image
   docker build -t barodybroject .
   
   # Run the container
   docker run -d \
     -p 8000:8000 \
     -e DEBUG=False \
     -e SECRET_KEY=your-secret-key \
     -e DATABASE_URL=sqlite:///app/db.sqlite3 \
     --name barodybroject-app \
     barodybroject

Kubernetes Deployment
---------------------

Deployment Manifest
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: barodybroject
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: barodybroject
     template:
       metadata:
         labels:
           app: barodybroject
       spec:
         containers:
         - name: barodybroject
           image: your-registry/barodybroject:latest
           ports:
           - containerPort: 8000
           env:
           - name: DEBUG
             value: "False"
           - name: SECRET_KEY
             valueFrom:
               secretKeyRef:
                 name: barodybroject-secrets
                 key: secret-key

Service Manifest
~~~~~~~~~~~~~~~~

.. code-block:: yaml

   apiVersion: v1
   kind: Service
   metadata:
     name: barodybroject-service
   spec:
     selector:
       app: barodybroject
     ports:
     - protocol: TCP
       port: 80
       targetPort: 8000
     type: LoadBalancer

Traditional Hosting
-------------------

VPS/Dedicated Server
~~~~~~~~~~~~~~~~~~~

For deployment on a VPS or dedicated server:

1. **Set up the server**:

   .. code-block:: bash

      # Update system
      sudo apt update && sudo apt upgrade -y
      
      # Install Python and dependencies
      sudo apt install python3 python3-pip python3-venv nginx postgresql

2. **Deploy the application**:

   .. code-block:: bash

      # Clone repository
      git clone https://github.com/bamr87/barodybroject.git
      cd barodybroject
      
      # Create virtual environment
      python3 -m venv venv
      source venv/bin/activate
      
      # Install dependencies
      pip install -r requirements.txt
      
      # Configure environment
      cp .env.example .env
      # Edit .env with production values

3. **Configure Gunicorn**:

   .. code-block:: bash

      # Test Gunicorn
      cd src
      gunicorn barodybroject.wsgi:application --bind 0.0.0.0:8000

4. **Set up Nginx**:

   .. code-block:: nginx

      server {
          listen 80;
          server_name your-domain.com;
          
          location /static/ {
              alias /path/to/barodybroject/static/;
          }
          
          location /media/ {
              alias /path/to/barodybroject/media/;
          }
          
          location / {
              proxy_pass http://127.0.0.1:8000;
              proxy_set_header Host $host;
              proxy_set_header X-Real-IP $remote_addr;
          }
      }

5. **Set up systemd service**:

   .. code-block:: ini

      [Unit]
      Description=Barodybroject Django Application
      After=network.target
      
      [Service]
      User=www-data
      Group=www-data
      WorkingDirectory=/path/to/barodybroject/src
      ExecStart=/path/to/barodybroject/venv/bin/gunicorn \
                --workers 3 \
                --bind 127.0.0.1:8000 \
                barodybroject.wsgi:application
      Restart=always
      
      [Install]
      WantedBy=multi-user.target

Heroku Deployment
-----------------

Prepare for Heroku
~~~~~~~~~~~~~~~~~~

1. **Create Procfile**:

   .. code-block::

      web: cd src && gunicorn barodybroject.wsgi:application --bind 0.0.0.0:$PORT

2. **Configure static files**:

   .. code-block:: python

      # settings.py
      STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
      STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

Deploy to Heroku
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install Heroku CLI and login
   heroku login
   
   # Create Heroku app
   heroku create your-app-name
   
   # Add PostgreSQL addon
   heroku addons:create heroku-postgresql:hobby-dev
   
   # Set environment variables
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   
   # Deploy
   git push heroku main
   
   # Run migrations
   heroku run python src/manage.py migrate
   
   # Create superuser
   heroku run python src/manage.py createsuperuser

Environment Variables
---------------------

Production Settings
~~~~~~~~~~~~~~~~~~

Essential environment variables for production:

.. code-block:: bash

   # Security
   SECRET_KEY=your-very-secure-secret-key
   DEBUG=False
   ALLOWED_HOSTS=your-domain.com,www.your-domain.com
   
   # Database
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   
   # Static files
   STATIC_URL=/static/
   STATIC_ROOT=/var/www/static/
   
   # Media files
   MEDIA_URL=/media/
   MEDIA_ROOT=/var/www/media/
   
   # Email
   EMAIL_BACKEND=django_ses.SESBackend
   AWS_ACCESS_KEY_ID=your-key
   AWS_SECRET_ACCESS_KEY=your-secret
   
   # OpenAI
   OPENAI_API_KEY=your-openai-key

SSL/HTTPS Configuration
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # HTTPS settings
   SECURE_SSL_REDIRECT=True
   SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
   SECURE_HSTS_SECONDS=31536000
   SECURE_HSTS_INCLUDE_SUBDOMAINS=True
   SECURE_HSTS_PRELOAD=True
   
   # Session security
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True

Database Migration
------------------

Production Database Setup
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run migrations
   python manage.py migrate
   
   # Create superuser
   python manage.py createsuperuser
   
   # Collect static files
   python manage.py collectstatic --noinput

Backup and Restore
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Create database backup
   python manage.py dumpdata > backup.json
   
   # Restore from backup
   python manage.py loaddata backup.json

Monitoring and Logging
----------------------

Application Monitoring
~~~~~~~~~~~~~~~~~~~~~

Configure monitoring with Azure Monitor:

.. code-block:: python

   # settings.py
   from azure.monitor.opentelemetry import configure_azure_monitor
   
   configure_azure_monitor(
       connection_string="your-connection-string"
   )

Log Configuration
~~~~~~~~~~~~~~~~

.. code-block:: python

   LOGGING = {
       'version': 1,
       'disable_existing_loggers': False,
       'handlers': {
           'file': {
               'level': 'INFO',
               'class': 'logging.FileHandler',
               'filename': '/var/log/barodybroject/django.log',
           },
       },
       'loggers': {
           'django': {
               'handlers': ['file'],
               'level': 'INFO',
               'propagate': True,
           },
       },
   }

Performance Optimization
-----------------------

Database Optimization
~~~~~~~~~~~~~~~~~~~~

- Use database connection pooling
- Implement proper indexing
- Use select_related() and prefetch_related()
- Monitor slow queries

Caching
~~~~~~~

Configure Redis for caching:

.. code-block:: python

   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
           'OPTIONS': {
               'CLIENT_CLASS': 'django_redis.client.DefaultClient',
           }
       }
   }

Static File Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

- Use CDN for static files
- Enable gzip compression
- Implement proper caching headers
- Optimize images and assets

Security Checklist
------------------

Pre-deployment Security
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run Django security check
   python manage.py check --deploy
   
   # Update dependencies
   pip-audit
   
   # Check for vulnerabilities
   safety check

Production Security
~~~~~~~~~~~~~~~~~~~

- Enable HTTPS
- Configure proper CORS settings
- Set up rate limiting
- Implement proper authentication
- Regular security updates
- Monitor for suspicious activity

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Static files not loading**
   - Check STATIC_ROOT and STATIC_URL settings
   - Run collectstatic command
   - Verify web server configuration

**Database connection errors**
   - Verify DATABASE_URL format
   - Check database server status
   - Ensure proper network connectivity

**Import errors**
   - Check PYTHONPATH settings
   - Verify virtual environment activation
   - Ensure all dependencies are installed

**Performance issues**
   - Enable database query logging
   - Check for N+1 queries
   - Monitor memory usage
   - Review caching strategy