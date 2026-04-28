"""Test settings for Barodybroject."""

import os
from pathlib import Path

os.environ["RUNNING_IN_PRODUCTION"] = "False"
os.environ["DEBUG"] = "True"
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-installation-wizard-testing-only")
os.environ["SKIP_INSTALLATION_CHECK"] = "true"

from .base import *  # noqa: F403

IS_PRODUCTION = False
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
AUTH_PASSWORD_VALIDATORS = []
STATIC_ROOT = "/tmp/staticfiles"
INSTALLATION_CONFIG_PATH = Path("/tmp/installation_config.json")
INSTALLATION_TOKEN_EXPIRY_MINUTES = 30
CSRF_TRUSTED_ORIGINS = []

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "setup": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
