"""
File: refreshmigrations.py
Description: Regenerate migrations for selected apps (PostgreSQL-only project).
Author: Barodybroject Team <team@example.com>
Created: 2025-10-30
Last Modified: 2025-12-19
Version: 1.1.0

Dependencies:
- django: management commands

Usage: python manage.py refreshmigrations
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run makemigrations for project apps (PostgreSQL-only)."

    def handle(self, *args, **options):
        apps = ["parodynews"]
        self.stdout.write(f"Running makemigrations for: {', '.join(apps)}")
        call_command("makemigrations", *apps)
