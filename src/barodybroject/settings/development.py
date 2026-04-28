"""Development settings for Barodybroject."""

import os

os.environ["RUNNING_IN_PRODUCTION"] = "False"
os.environ["DEBUG"] = "True"

from .base import *  # noqa: F403

IS_PRODUCTION = False
DEBUG = True

# Safari (and any browser) refuses to send Secure cookies over plain HTTP.
# Override the base.py defaults (True) so sessions work on http://localhost.
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
