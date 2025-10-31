#!/usr/bin/env python3
"""Debug script for installation service configuration"""

import os
import sys

sys.path.insert(0, "/workspace/src")
os.environ["DJANGO_SETTINGS_MODULE"] = "barodybroject.test_settings"

import django

django.setup()

from django.conf import settings

from setup.services import InstallationService

print("Debug Installation Service Config:")
print(f"BASE_DIR: {settings.BASE_DIR}")
config_path = getattr(settings, "INSTALLATION_CONFIG_PATH", "NOT SET")
print(f"INSTALLATION_CONFIG_PATH: {config_path}")

service = InstallationService()
print(f"config_file type: {type(service.config_file)}")
print(f"config_file value: {service.config_file}")
print(f"installation_file type: {type(service.installation_file)}")
print(f"installation_file value: {service.installation_file}")