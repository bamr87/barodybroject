"""
File: reset_db.py
Description: Reset the database to an empty state (PostgreSQL-only) for development/testing.
Author: Barodybroject Team <team@example.com>
Created: 2025-10-30
Last Modified: 2025-12-19
Version: 1.1.0

Dependencies:
- django: management commands

Usage: python manage.py reset_db
"""

import os

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Reset the database to an empty state (PostgreSQL-only)."

    def handle(self, *args, **kwargs):
        db_choice = os.environ.get("DB_CHOICE", "postgres")
        if db_choice == "sqlite":
            raise SystemExit(
                "SQLite is not supported in this project. Configure PostgreSQL via DB_HOST/DB_NAME/DB_USERNAME/DB_PASSWORD."
            )

        # Keep this command intentionally safe: do not delete migration files.
        # Instead, migrate to the latest schema, then flush all data.
        self.stdout.write("Applying migrations...")
        call_command("migrate", interactive=False, verbosity=kwargs.get("verbosity", 1))

        self.stdout.write("Flushing all data (this is destructive)...")
        call_command("flush", interactive=False, verbosity=kwargs.get("verbosity", 1))

        self.stdout.write(self.style.SUCCESS("Database reset complete (schema preserved, data cleared)."))
