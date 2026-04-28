"""Development settings for Barodybroject."""

import os

os.environ["RUNNING_IN_PRODUCTION"] = "False"
os.environ["DEBUG"] = "True"

from .base import *  # noqa: F403

IS_PRODUCTION = False
DEBUG = True
