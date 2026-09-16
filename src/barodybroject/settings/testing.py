"""Test settings for Barodybroject."""

import os
import tempfile
from pathlib import Path

os.environ["RUNNING_IN_PRODUCTION"] = "False"
os.environ["DEBUG"] = "True"
os.environ.setdefault(
    "SECRET_KEY", "test-secret-key-for-installation-wizard-testing-only"
)
os.environ["SKIP_INSTALLATION_CHECK"] = "true"

from .base import *  # noqa: F403

IS_PRODUCTION = False
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
AUTH_PASSWORD_VALIDATORS = []
STATIC_ROOT = os.path.join(tempfile.gettempdir(), "barodybroject-staticfiles")
INSTALLATION_CONFIG_PATH = Path(tempfile.gettempdir()) / "installation_config.json"
INSTALLATION_TOKEN_EXPIRY_MINUTES = 30
CSRF_TRUSTED_ORIGINS = []

# The suite must never reach a real provider: `mock` returns deterministic,
# schema-valid output and needs no credentials. Tests that want to assert on
# what was sent use `MockProvider.calls`.
AI_DEFAULT_PROVIDER = "mock"

# Plain storage: the hashed-manifest backend would require collectstatic to
# have run before any template rendering a {% static %} tag.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# Throttling would make repeated API tests flaky.
REST_FRAMEWORK = {
    **globals()["REST_FRAMEWORK"],
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {},
}

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
