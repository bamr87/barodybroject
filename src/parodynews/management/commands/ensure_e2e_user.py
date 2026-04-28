"""
File: ensure_e2e_user.py
Description: Management command to create/update a deterministic E2E login user for Playwright CI runs
Author: Barodybroject Team <team@example.com>
Created: 2025-12-19
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- django: >=5.1

Usage:
  python src/manage.py ensure_e2e_user --username e2e_user --email e2e@example.com --password secret

Environment:
  E2E_USERNAME, E2E_EMAIL, E2E_PASSWORD (used as defaults)
"""

from __future__ import annotations

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create/update an E2E user for Playwright login."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username", default=os.environ.get("E2E_USERNAME", "e2e_user")
        )
        parser.add_argument(
            "--email",
            default=os.environ.get("E2E_EMAIL", "e2e_user@example.com"),
        )
        parser.add_argument("--password", default=os.environ.get("E2E_PASSWORD"))
        parser.add_argument("--is-staff", action="store_true", default=False)
        parser.add_argument("--is-superuser", action="store_true", default=False)

    def handle(self, *args, **options):
        username: str = options["username"]
        email: str = options["email"]
        password: str | None = options["password"]
        is_staff: bool = options["is_staff"]
        is_superuser: bool = options["is_superuser"]

        if not password:
            raise CommandError(
                "Missing password. Provide --password or set E2E_PASSWORD in the environment."
            )

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username, defaults={"email": email}
        )
        changed = False

        if user.email != email:
            user.email = email
            changed = True

        if user.is_staff != is_staff:
            user.is_staff = is_staff
            changed = True

        if user.is_superuser != is_superuser:
            user.is_superuser = is_superuser
            changed = True

        user.set_password(password)
        changed = True

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created E2E user '{username}'."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated E2E user '{username}'."))

        if changed:
            user.save()
