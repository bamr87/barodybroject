"""Development settings for Barodybroject."""

import os

os.environ["RUNNING_IN_PRODUCTION"] = "False"
os.environ["DEBUG"] = "True"

from .base import *  # noqa: F403
from .base import CSRF_TRUSTED_ORIGINS, FRONTEND_DEV_SERVER_URL

IS_PRODUCTION = False
DEBUG = True

# Safari (and any browser) refuses to send Secure cookies over plain HTTP.
# Override the base.py defaults (True) so sessions work on http://localhost.
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# When the SPA is served by the Vite dev server, its origin posts back to
# Django, so it has to be a trusted CSRF origin.
if FRONTEND_DEV_SERVER_URL:
    CSRF_TRUSTED_ORIGINS = [*CSRF_TRUSTED_ORIGINS, FRONTEND_DEV_SERVER_URL]
