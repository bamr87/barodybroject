"""
File: settings.py
Description: Django settings for barodybroject project with optimized production and development configurations
Author: Barodybroject Team <team@example.com>
Created: 2025-10-27
Last Modified: 2025-10-27
Version: 2.0.0

Dependencies:
- django: >=4.2
- django-environ: for environment variable management
- boto3: for AWS services integration
- psycopg2-binary: for PostgreSQL support

Container Requirements:
- Base Image: python:3.11-slim
- Exposed Ports: 8000/tcp (development), 80/tcp (production)
- Volumes: /app/src:rw, /app/static:rw, /app/media:rw
- Environment: See .env file for required variables

Usage: Configure via environment variables in .env file
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

import boto3
import environ
from botocore.exceptions import ClientError
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _

# ==============================================================================
# BASE CONFIGURATION
# ==============================================================================

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables with type checking
env = environ.Env(
    # Cast environment variables to proper types
    DEBUG=(bool, False),
    RUNNING_IN_PRODUCTION=(bool, True),
    USE_HTTPS=(bool, False),
    DB_CHOICE=(str, "postgres"),
    POSTGRES_SSL=(str, ""),
    ENABLE_DEBUG_TOOLBAR=(bool, False),
    LOG_LEVEL=(str, "INFO"),
)

# Read environment file if it exists
env_file = os.path.join(BASE_DIR.parent, ".env")
if os.path.exists(env_file):
    environ.Env.read_env(env_file)

# Determine environment
IS_PRODUCTION = env.bool(
    "RUNNING_IN_PRODUCTION", default=False
)  # Default to development
DEBUG = env.bool("DEBUG", default=not IS_PRODUCTION)

# Installation wizard configuration
SKIP_INSTALLATION_CHECK = env.bool("SKIP_INSTALLATION_CHECK", default=False)

# Basic validation
if not env.str("SECRET_KEY", default="") and IS_PRODUCTION:
    raise ImproperlyConfigured("SECRET_KEY must be set in production")

# System administrators
ADMINS = [
    ("Barodybroject Team", "admin@barodybroject.com"),
]
MANAGERS = ADMINS


# ==============================================================================
# AWS SECRETS MANAGER CONFIGURATION
# ==============================================================================


def get_secret(
    secret_name: str = "barodybroject/env", region_name: str = "us-east-1"
) -> Dict:
    """
    Retrieve secrets from AWS Secrets Manager with comprehensive error handling

    Args:
        secret_name: Name of the secret in AWS Secrets Manager
        region_name: AWS region name

    Returns:
        Dict containing secrets or empty dict if not available
    """
    # Skip AWS Secrets Manager if we have local environment variables or in development without AWS setup
    if not IS_PRODUCTION or not env.str("AWS_ACCESS_KEY_ID", default=""):
        return {}

    try:
        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager", region_name=region_name)

        response = client.get_secret_value(SecretId=secret_name)
        secrets = json.loads(response["SecretString"])

        logging.info(
            f"Successfully loaded secrets from AWS Secrets Manager: {secret_name}"
        )
        return secrets

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_messages = {
            "DecryptionFailureException": "Unable to decrypt the secret",
            "ResourceNotFoundException": "Secret not found in AWS Secrets Manager",
            "InvalidParameterException": "Invalid parameter provided to AWS Secrets Manager",
            "InvalidRequestException": "Invalid request to AWS Secrets Manager",
        }

        error_msg = error_messages.get(
            error_code, f"AWS Secrets Manager error: {error_code}"
        )
        logging.warning(f"AWS Secrets Manager error: {error_msg}")

        # Only raise in production with proper AWS setup
        if IS_PRODUCTION and env.str("AWS_ACCESS_KEY_ID", default=""):
            raise ImproperlyConfigured(
                f"Failed to load production secrets: {error_msg}"
            )

        return {}

    except Exception as e:
        logging.error(f"Unexpected error loading secrets: {e}")
        # Only raise in production with proper AWS setup
        if IS_PRODUCTION and env.str("AWS_ACCESS_KEY_ID", default=""):
            raise ImproperlyConfigured(f"Failed to load production secrets: {e}")
        return {}


# Load secrets early
try:
    secrets = get_secret()
except Exception as e:
    logging.error(f"Failed to load secrets: {e}")
    secrets = {}

# ==============================================================================
# SECURITY CONFIGURATION
# ==============================================================================

# Secret key with proper fallbacks
SECRET_KEY_FALLBACK = env.str(
    "DJANGO_SECRET_KEY_DEV_FALLBACK",
    default="dev-only-insecure-key-change-in-production",
)
SECRET_KEY = secrets.get("DJANGO_SECRET_KEY") or env.str(
    "SECRET_KEY", default=SECRET_KEY_FALLBACK
)

if not SECRET_KEY or (IS_PRODUCTION and SECRET_KEY == SECRET_KEY_FALLBACK):
    raise ImproperlyConfigured(
        "SECRET_KEY must be set for production. "
        "Set it in environment variables or AWS Secrets Manager."
    )

# ==============================================================================
# SECURITY SETTINGS
# ==============================================================================

# SSL/HTTPS Configuration
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# HSTS (HTTP Strict Transport Security) - Always set for deploy check compatibility
# In development, this won't affect local HTTP traffic but satisfies security checks
SECURE_HSTS_SECONDS = 31536000  # 1 year - required for deploy check
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Required for deploy check
SECURE_HSTS_PRELOAD = True  # Required for deploy check

# Content Security
SECURE_CONTENT_TYPE_NOSNIFF = True  # Always enabled for security
SECURE_BROWSER_XSS_FILTER = True  # Always enabled for security
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Cookie Security - Set secure defaults for deploy check while allowing dev override via environment
# These will be secure by default but can be overridden in local development if needed
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=True)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=True)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = IS_PRODUCTION

# Cookie SameSite policy
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# Frame options - Secure default for deploy check
X_FRAME_OPTIONS = "DENY"

# Development-specific overrides when DEBUG is True
if DEBUG:
    # Override SSL redirect for local development (can be re-enabled via env var)
    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)
    # Note: Other security settings remain secure by default for deploy check compliance
    # This allows local development while maintaining security best practices

# ==============================================================================
# ENVIRONMENT-SPECIFIC CONFIGURATION
# ==============================================================================

# Container configuration with proper fallbacks
CONTAINER_APP_NAME = (
    env.str("CONTAINER_APP_NAME", default="")
    or secrets.get("CONTAINER_APP_NAME", "")
    or "barodybroject"
)
CONTAINER_APP_ENV_DNS_SUFFIX = (
    env.str("CONTAINER_APP_ENV_DNS_SUFFIX", default="")
    or secrets.get("CONTAINER_APP_ENV_DNS_SUFFIX", "")
    or "com"
)
AZURE_CONTAINER_REGISTRY_ENDPOINT = (
    env.str("AZURE_CONTAINER_REGISTRY_ENDPOINT", default="")
    or secrets.get("AZURE_CONTAINER_REGISTRY_ENDPOINT", "")
    or "https://barodybroject.azurecr.io"
)

# GitHub integration
GITHUB_ISSUE_REPO = env.str("GITHUB_ISSUE_REPO", default="") or secrets.get(
    "GITHUB_ISSUE_REPO", ""
)

if not IS_PRODUCTION:
    # Development environment settings
    ALLOWED_HOSTS = [
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        f"{CONTAINER_APP_NAME}.{CONTAINER_APP_ENV_DNS_SUFFIX}",
        "4itba3fqvd.us-east-1.awsapprunner.com",
        "barodybroject.com",
    ]

    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:8000",
        "http://localhost:8001",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8001",
        f"https://{CONTAINER_APP_NAME}.{CONTAINER_APP_ENV_DNS_SUFFIX}",
        f"{AZURE_CONTAINER_REGISTRY_ENDPOINT}.{CONTAINER_APP_ENV_DNS_SUFFIX}",
        "https://4itba3fqvd.us-east-1.awsapprunner.com",
        "https://barodybroject.com",
    ]

    # Development-specific settings
    INTERNAL_IPS = ["127.0.0.1", "localhost"]

else:
    # Production environment settings
    ALLOWED_HOSTS = [
        f"{CONTAINER_APP_NAME}.{CONTAINER_APP_ENV_DNS_SUFFIX}",
        "4itba3fqvd.us-east-1.awsapprunner.com",
        "barodybroject.com",
        "www.barodybroject.com",
    ]

    CSRF_TRUSTED_ORIGINS = [
        f"https://{CONTAINER_APP_NAME}.{CONTAINER_APP_ENV_DNS_SUFFIX}",
        "https://4itba3fqvd.us-east-1.awsapprunner.com",
        "https://barodybroject.com",
        "https://www.barodybroject.com",
    ]

# Additional allowed hosts from environment
additional_hosts = env.str("ALLOWED_HOSTS", default="").split(",")
ALLOWED_HOSTS.extend([host.strip() for host in additional_hosts if host.strip()])

# ==============================================================================
# APPLICATION CONFIGURATION
# ==============================================================================

SITE_ID = 1

# Application definition with logical grouping
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.humanize",
]

# CMS and content management apps
CMS_APPS = [
    "djangocms_admin_style",
    "cms",
    "menus",
    "sekizai",
    "treebeard",
    "filer",
    "easy_thumbnails",
    "djangocms_alias",
    "djangocms_versioning",
    "djangocms_text_ckeditor",
    "djangocms_link",
    "djangocms_frontend",
    "djangocms_frontend.contrib.accordion",
    "djangocms_frontend.contrib.alert",
    "djangocms_frontend.contrib.badge",
    "djangocms_frontend.contrib.card",
    "djangocms_frontend.contrib.carousel",
    "djangocms_frontend.contrib.collapse",
    "djangocms_frontend.contrib.content",
    "djangocms_frontend.contrib.grid",
    "djangocms_frontend.contrib.icon",
    "djangocms_frontend.contrib.image",
    "djangocms_frontend.contrib.jumbotron",
    "djangocms_frontend.contrib.link",
    "djangocms_frontend.contrib.listgroup",
    "djangocms_frontend.contrib.media",
    "djangocms_frontend.contrib.navigation",
    "djangocms_frontend.contrib.tabs",
    "djangocms_frontend.contrib.utilities",
]

# Authentication and user management
AUTH_APPS = [
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.mfa",
    "allauth.socialaccount.providers.github",
    "allauth.usersessions",
]

# Third-party applications
THIRD_PARTY_APPS = [
    "rest_framework",
    "django_json_widget",
    "markdownify",
    "martor",
    "import_export",
    "django_ses",
]

# Local applications
LOCAL_APPS = [
    "parodynews",
    "setup",  # Installation wizard application
]

# Development-only apps
DEV_APPS = []
if DEBUG and env.bool("ENABLE_DEBUG_TOOLBAR", default=False):
    try:
        import debug_toolbar

        DEV_APPS.append("debug_toolbar")
        THIRD_PARTY_APPS.append("debug_toolbar")
    except ImportError:
        pass

INSTALLED_APPS = (
    DJANGO_APPS + CMS_APPS + AUTH_APPS + THIRD_PARTY_APPS + LOCAL_APPS + DEV_APPS
)

# Middleware configuration with environment-specific additions
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "setup.middleware.InstallationMiddleware",  # Installation wizard middleware
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "cms.middleware.utils.ApphookReloadMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "cms.middleware.user.CurrentUserMiddleware",
    "cms.middleware.page.CurrentPageMiddleware",
    "cms.middleware.toolbar.ToolbarMiddleware",
    "cms.middleware.language.LanguageCookieMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

# Add debug toolbar middleware in development
if DEBUG and env.bool("ENABLE_DEBUG_TOOLBAR", default=False):
    try:
        import debug_toolbar

        MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")
    except ImportError:
        pass

ROOT_URLCONF = "barodybroject.urls"


# ==============================================================================
# TEMPLATE CONFIGURATION
# ==============================================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "parodynews" / "templates",
            BASE_DIR / "templates",  # Global templates directory
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "sekizai.context_processors.sekizai",
                "cms.context_processors.cms_settings",
                "parodynews.context_processors.footer_items",
                "parodynews.context_processors.issue_templates",
            ],
            # Enable template caching in production
            "loaders": (
                [
                    (
                        (
                            "django.template.loaders.cached.Loader",
                            [
                                "django.template.loaders.filesystem.Loader",
                                "django.template.loaders.app_directories.Loader",
                            ],
                        )
                        if IS_PRODUCTION
                        else "django.template.loaders.filesystem.Loader"
                    ),
                    (
                        "django.template.loaders.app_directories.Loader"
                        if not IS_PRODUCTION
                        else None
                    ),
                ]
                if IS_PRODUCTION
                else None
            ),
        },
    },
]

# Remove None values from loaders if not in production
if not IS_PRODUCTION:
    TEMPLATES[0]["OPTIONS"].pop("loaders", None)

WSGI_APPLICATION = "barodybroject.wsgi.application"

# ==============================================================================
# AUTHENTICATION CONFIGURATION
# ==============================================================================

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,  # Increased from 6 for better security
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Authentication backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Login/logout URLs
LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


# ==============================================================================
# DATABASE CONFIGURATION
# ==============================================================================

# Database configuration with improved connection settings
DB_CHOICE = env.str("DB_CHOICE", default="postgres")

if DB_CHOICE == "sqlite":
    # SQLite for local development
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
            "ATOMIC_REQUESTS": True,
            "OPTIONS": {
                "timeout": 20,
            },
        }
    }
else:
    # PostgreSQL configuration with connection pooling and optimization
    db_options = {
        "options": "-c search_path=public",
    }

    # SSL configuration for production
    ssl_mode = env.str("POSTGRES_SSL", default="")
    if ssl_mode:
        db_options["sslmode"] = ssl_mode

    # Connection pooling settings for production
    if IS_PRODUCTION:
        db_options.update(
            {
                "conn_max_age": 600,  # 10 minutes
                "conn_health_checks": True,
            }
        )

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env.str("DB_NAME", default="barodydb"),
            "USER": env.str("DB_USERNAME", default="postgres"),
            "PASSWORD": env.str("DB_PASSWORD", default="postgres"),
            "HOST": env.str("DB_HOST", default="localhost"),
            "PORT": env.int("DB_PORT", default=5432),
            "ATOMIC_REQUESTS": True,
            "OPTIONS": db_options,
            "TEST": {
                "NAME": f"test_{env.str('DB_NAME', default='barodydb')}",
            },
        }
    }

# Database connection timeout settings
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ==============================================================================
# EMAIL CONFIGURATION
# ==============================================================================

if IS_PRODUCTION:
    # Production email settings using AWS SES
    EMAIL_BACKEND = "django_ses.SESBackend"
    AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID", default="")
    AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY", default="")
    AWS_SES_REGION_NAME = env.str("AWS_SES_REGION_NAME", default="us-east-1")
    AWS_SES_REGION_ENDPOINT = f"email.{AWS_SES_REGION_NAME}.amazonaws.com"
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = env.str(
        "DEFAULT_FROM_EMAIL", default="no-reply@barodybroject.com"
    )
    SERVER_EMAIL = env.str("SERVER_EMAIL", default="server@barodybroject.com")
else:
    # Development email settings
    EMAIL_BACKEND = env.str(
        "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
    )
    DEFAULT_FROM_EMAIL = "no-reply@localhost"
    SERVER_EMAIL = "server@localhost"

# Email settings for account management
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_SUBJECT_PREFIX = "Parody News: "
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https" if IS_PRODUCTION else "http"

# ==============================================================================
# LOGGING CONFIGURATION
# ==============================================================================

LOG_LEVEL = env.str("LOG_LEVEL", default="INFO" if IS_PRODUCTION else "DEBUG")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {name} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "[{levelname}] {asctime} {name} {message}",
            "style": "{",
        },
        "json": {
            "format": '{{"timestamp": "{asctime}", "level": "{levelname}", "logger": "{name}", "message": "{message}"}}',
            "style": "{",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": LOG_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "maxBytes": 1024 * 1024 * 10,  # 10MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file", "mail_admins"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console", "file", "mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console", "file", "mail_admins"],
            "level": "WARNING",
            "propagate": False,
        },
        "parodynews": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "barodybroject": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.utils.autoreload": {
            "handlers": ["file"],  # Only log to file, not console
            "level": "INFO",  # Hide DEBUG messages from autoreload
            "propagate": False,
        },
    },
}

# Create logs directory if it doesn't exist
logs_dir = BASE_DIR / "logs"
logs_dir.mkdir(exist_ok=True)

# ==============================================================================
# SESSION AND CACHING CONFIGURATION
# ==============================================================================

# Session configuration
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 86400 * 7  # 1 week
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Cache configuration
if IS_PRODUCTION:
    # Production caching with Redis (with fallback)
    try:
        # Test if Redis cache backend is available
        from django.core.cache.backends.redis import RedisCache

        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": env.str("REDIS_URL", default="redis://127.0.0.1:6379/1"),
                "KEY_PREFIX": "barodybroject",
                "TIMEOUT": 300,  # 5 minutes default
                "VERSION": 1,
            }
        }

        # Enable cache middleware for production
        MIDDLEWARE.insert(1, "django.middleware.cache.UpdateCacheMiddleware")
        MIDDLEWARE.append("django.middleware.cache.FetchFromCacheMiddleware")

        CACHE_MIDDLEWARE_ALIAS = "default"
        CACHE_MIDDLEWARE_SECONDS = 600  # 10 minutes
        CACHE_MIDDLEWARE_KEY_PREFIX = "barodybroject"

    except ImportError:
        # Fallback to database cache if Redis is not available
        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.db.DatabaseCache",
                "LOCATION": "cache_table",
                "TIMEOUT": 300,
                "OPTIONS": {
                    "MAX_ENTRIES": 10000,
                    "CULL_FREQUENCY": 3,
                },
            }
        }

else:
    # Development caching
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "barodybroject-dev-cache",
            "TIMEOUT": 60,  # 1 minute for development
            "OPTIONS": {
                "MAX_ENTRIES": 1000,
                "CULL_FREQUENCY": 3,
            },
        }
    }

# ==============================================================================
# ALLAUTH AND SOCIAL AUTHENTICATION
# ==============================================================================

# Allauth settings
ACCOUNT_LOGIN_BY_CODE_ENABLED = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory" if IS_PRODUCTION else "optional"
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_PRESERVE_USERNAME_CASING = False
ACCOUNT_SESSION_REMEMBER = True

# Rate limiting configuration (replaces deprecated ACCOUNT_LOGIN_ATTEMPTS_LIMIT/TIMEOUT)
ACCOUNT_RATE_LIMITS = {
    "login_failed": "5/5m",  # 5 attempts per 5 minutes
}

# Multi-factor authentication
MFA_SUPPORTED_TYPES = [
    "webauthn",
    "totp",
    "recovery_codes",
]
MFA_PASSKEY_LOGIN_ENABLED = IS_PRODUCTION
MFA_PASSKEY_SIGNUP_ENABLED = IS_PRODUCTION

# Social account providers
SOCIALACCOUNT_PROVIDERS = {
    "github": {
        "SCOPE": [
            "read:user",
            "user:email",
        ],
        "VERIFIED_EMAIL": True,
        "APP": {
            "client_id": env.str("GITHUB_CLIENT_ID", default=""),
            "secret": env.str("GITHUB_CLIENT_SECRET", default=""),
        },
    }
}

# ==============================================================================
# INTERNATIONALIZATION CONFIGURATION
# ==============================================================================

LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("en", _("English")),
    # Add other languages as needed
    # ('de', _('German')),
    # ('fr', _('French')),
]

# Locale paths
LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# ==============================================================================
# STATIC FILES AND MEDIA CONFIGURATION
# ==============================================================================

# Static files configuration
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

STATICFILES_DIRS = [
    BASE_DIR / "assets",
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Static files storage for production
if IS_PRODUCTION:
    STATICFILES_STORAGE = (
        "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
    )

# Media files configuration
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = FILE_UPLOAD_MAX_MEMORY_SIZE
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# ==============================================================================
# CMS AND CONTENT CONFIGURATION
# ==============================================================================

# Django CMS settings
CMS_CONFIRM_VERSION4 = True
CMS_TOOLBAR_ANONYMOUS_ON = not IS_PRODUCTION
TEXT_INLINE_EDITING = True
DJANGOCMS_VERSIONING_ALLOW_DELETING_VERSIONS = True

CMS_TEMPLATES = [
    ("base.html", _("Base Template")),
    ("parodynews/cms.html", _("CMS Template")),
]

CMS_PLACEHOLDERS = [
    ("content", _("Content")),
    ("sidebar", _("Sidebar")),
]

# CKEditor settings
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "full",
        "height": 300,
        "width": "100%",
        "removePlugins": "stylesheetparser",
        "allowedContent": True,
        "extraAllowedContent": "iframe[*]",
    },
}

# ==============================================================================
# MARTOR (MARKDOWN EDITOR) CONFIGURATION
# ==============================================================================

MARTOR_THEME = "bootstrap"

MARTOR_ENABLE_CONFIGS = {
    "emoji": "true",
    "imgur": "false",  # Disabled for security
    "mention": "false",
    "jquery": "true",
    "living": "false",
    "spellcheck": "true",
    "hljs": "true",
}

MARTOR_TOOLBAR_BUTTONS = [
    "bold",
    "italic",
    "horizontal",
    "heading",
    "pre-code",
    "blockquote",
    "unordered-list",
    "ordered-list",
    "link",
    "image-link",
    "emoji",
    "toggle-maximize",
    "help",
]

MARTOR_ENABLE_LABEL = False
MARTOR_ENABLE_ADMIN_CSS = True
MARTOR_MARKDOWNIFY_FUNCTION = "martor.utils.markdownify"
MARTOR_MARKDOWNIFY_URL = "/martor/markdownify/"
MARTOR_MARKDOWNIFY_TIMEOUT = 1000

# Markdown extensions
MARTOR_MARKDOWN_EXTENSIONS = [
    "markdown.extensions.extra",
    "markdown.extensions.nl2br",
    "markdown.extensions.smarty",
    "markdown.extensions.fenced_code",
    "markdown.extensions.sane_lists",
    "martor.extensions.urlize",
    "martor.extensions.del_ins",
    "martor.extensions.emoji",
    "martor.extensions.escape_html",
    "martor.extensions.mdx_add_id",
]

MARTOR_MARKDOWN_EXTENSION_CONFIGS = {}
MARTOR_UPLOAD_URL = ""  # Disabled for security
MARTOR_SEARCH_USERS_URL = ""  # Disabled

# Content security settings
ALLOWED_URL_SCHEMES = [
    "http",
    "https",
    "mailto",
    "tel",
]

ALLOWED_HTML_TAGS = [
    "a",
    "abbr",
    "b",
    "blockquote",
    "br",
    "cite",
    "code",
    "command",
    "dd",
    "del",
    "dl",
    "dt",
    "em",
    "fieldset",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "i",
    "img",
    "ins",
    "kbd",
    "label",
    "legend",
    "li",
    "ol",
    "p",
    "pre",
    "small",
    "span",
    "strong",
    "sub",
    "sup",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "tr",
    "u",
    "ul",
]

ALLOWED_HTML_ATTRIBUTES = [
    "alt",
    "class",
    "color",
    "colspan",
    "datetime",
    "height",
    "href",
    "id",
    "name",
    "reversed",
    "rowspan",
    "scope",
    "src",
    "style",
    "title",
    "type",
    "width",
]

# ==============================================================================
# APPLICATION-SPECIFIC CONFIGURATION
# ==============================================================================

# Custom application paths
PAGES_DIR = BASE_DIR / "pages"
POST_DIR = PAGES_DIR / "_posts"

# REST Framework configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "100/day", "user": "1000/day"},
}

# ==============================================================================
# PERFORMANCE AND OPTIMIZATION
# ==============================================================================

# Optimize queries
if IS_PRODUCTION:
    # Enable query optimization in production
    DATABASES["default"]["OPTIONS"]["CONN_MAX_AGE"] = 600  # 10 minutes

    # File compression
    COMPRESS_ENABLED = True
    COMPRESS_OFFLINE = True

    # Template caching
    TEMPLATE_LOADERS = [
        (
            "django.template.loaders.cached.Loader",
            [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
        ),
    ]

# Debug toolbar configuration (development only)
if DEBUG and env.bool("ENABLE_DEBUG_TOOLBAR", default=False):
    try:
        import debug_toolbar

        # Add to installed apps and middleware
        INSTALLED_APPS.append("debug_toolbar")
        MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

        DEBUG_TOOLBAR_CONFIG = {
            "SHOW_TOOLBAR_CALLBACK": lambda request: True,
            "HIDE_DJANGO_SQL": False,
            "SHOW_TEMPLATE_CONTEXT": True,
        }
        DEBUG_TOOLBAR_PANELS = [
            "debug_toolbar.panels.versions.VersionsPanel",
            "debug_toolbar.panels.timer.TimerPanel",
            "debug_toolbar.panels.settings.SettingsPanel",
            "debug_toolbar.panels.headers.HeadersPanel",
            "debug_toolbar.panels.request.RequestPanel",
            "debug_toolbar.panels.sql.SQLPanel",
            "debug_toolbar.panels.staticfiles.StaticFilesPanel",
            "debug_toolbar.panels.templates.TemplatesPanel",
            "debug_toolbar.panels.cache.CachePanel",
            "debug_toolbar.panels.signals.SignalsPanel",
            "debug_toolbar.panels.redirects.RedirectsPanel",
            "debug_toolbar.panels.profiling.ProfilingPanel",
        ]

        INTERNAL_IPS = [
            "127.0.0.1",
            "localhost",
        ]

    except ImportError:
        # Debug toolbar not available, skip configuration
        pass
    except ImportError:
        pass
