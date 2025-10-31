"""
File: test_settings.py
Description: Django settings configuration for testing the installation wizard
Author: Barodybroject Team <team@example.com>
Created: 2025-01-27
Last Modified: 2025-01-27
Version: 1.0.0

Dependencies:
- django: 4.2.20
- pytest: for test execution

Container Requirements:
- Base Image: python:3.11
- Environment: DJANGO_SETTINGS_MODULE=barodybroject.test_settings

Usage: Django test settings for installation wizard testing
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Basic Django settings for testing
SECRET_KEY = 'test-secret-key-for-installation-wizard-testing-only'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'setup',  # Our installation wizard app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'setup.middleware.InstallationMiddleware',  # Our installation middleware
]

ROOT_URLCONF = 'barodybroject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'barodybroject.wsgi.application'

# Database - use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/tmp/test_installation_wizard.db',
    }
}

# Password validation (simplified for testing)
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = '/tmp/staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Installation wizard configuration
INSTALLATION_CONFIG_PATH = Path('/tmp/installation_config.json')
INSTALLATION_TOKEN_EXPIRY_MINUTES = 30

# Security settings (relaxed for testing)
CSRF_TRUSTED_ORIGINS = []

# Logging configuration for testing
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'setup': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}