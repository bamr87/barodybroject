"""
File: ensure_admin.py
Description: Management command to automatically create/update admin superuser with fallback defaults
Author: Barodybroject Team <team@example.com>
Created: 2025-12-20
Last Modified: 2025-12-20
Version: 1.0.0

Dependencies:
- django: >=5.1

Usage:
  python manage.py ensure_admin

  # Or with explicit credentials
  python manage.py ensure_admin --username admin --email admin@example.com --password secret123

  # Save credentials to file
  python manage.py ensure_admin --save-credentials

Environment Variables (in order of precedence):
  DJANGO_SUPERUSER_USERNAME (default: admin)
  DJANGO_SUPERUSER_EMAIL (default: admin@localhost.local)
  DJANGO_SUPERUSER_PASSWORD (default: admin)
  ADMIN_CREDENTIALS_FILE (default: setup_data/admin_credentials.txt)

Security Notes:
  - Default credentials are intentionally weak for development only
  - Always set strong credentials via environment variables in production
  - Credential file is saved with restricted permissions (600)
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Automatically create/update admin superuser with environment variable or fallback defaults"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            default=None,
            help="Admin username (overrides env var)",
        )
        parser.add_argument(
            "--email",
            default=None,
            help="Admin email (overrides env var)",
        )
        parser.add_argument(
            "--password",
            default=None,
            help="Admin password (overrides env var)",
        )
        parser.add_argument(
            "--save-credentials",
            action="store_true",
            default=True,
            help="Save credentials to file for reference (default: True)",
        )
        parser.add_argument(
            "--no-save-credentials",
            action="store_false",
            dest="save_credentials",
            help="Do not save credentials to file",
        )
        parser.add_argument(
            "--credentials-file",
            default=None,
            help="Path to credentials file (overrides env var)",
        )

    def handle(self, *args, **options):
        User = get_user_model()

        # Get credentials from options, environment, or defaults
        username = self._get_credential(
            options.get("username"),
            "DJANGO_SUPERUSER_USERNAME",
            "admin",
        )
        email = self._get_credential(
            options.get("email"),
            "DJANGO_SUPERUSER_EMAIL",
            "admin@localhost.local",
        )
        password = self._get_credential(
            options.get("password"),
            "DJANGO_SUPERUSER_PASSWORD",
            "admin",
        )

        # Validate credentials
        if not username or not email or not password:
            self.stdout.write(
                self.style.ERROR("❌ Error: Username, email, and password are required")
            )
            sys.exit(1)

        # Create or update user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        changed = False

        # Update existing user if necessary
        if not created:
            if user.email != email:
                user.email = email
                changed = True

            if not user.is_staff:
                user.is_staff = True
                changed = True

            if not user.is_superuser:
                user.is_superuser = True
                changed = True

            # Always update password to match environment
            user.set_password(password)
            changed = True

            if changed:
                user.save()
        else:
            # Set password for new user
            user.set_password(password)
            user.save()

        # Display result
        if created:
            self.stdout.write(
                self.style.SUCCESS(f"✅ Created admin superuser: {username}")
            )
        else:
            if changed:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Updated admin superuser: {username}")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Admin superuser already exists: {username}")
                )

        # Show credential source warnings
        self._show_credential_warnings(options, username, email)

        # Save credentials if requested
        if options.get("save_credentials", True):
            credentials_file = self._get_credentials_file_path(options)
            self._save_credentials(credentials_file, username, email, password, created)

    def _get_credential(self, option_value, env_var, default):
        """Get credential from option, environment, or default (in that order)"""
        return option_value or os.environ.get(env_var) or default

    def _show_credential_warnings(self, options, username, email):
        """Display warnings about credential sources"""
        # Check if using defaults
        using_default_username = not options.get("username") and not os.environ.get(
            "DJANGO_SUPERUSER_USERNAME"
        )
        using_default_password = not options.get("password") and not os.environ.get(
            "DJANGO_SUPERUSER_PASSWORD"
        )

        if using_default_username or using_default_password:
            self.stdout.write(
                self.style.WARNING(
                    "\n⚠️  WARNING: Using default credentials (NOT SECURE for production!)"
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    "   Set DJANGO_SUPERUSER_USERNAME and DJANGO_SUPERUSER_PASSWORD"
                )
            )
            self.stdout.write(
                self.style.WARNING("   environment variables for production use.\n")
            )

        # Show what was used
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.HTTP_INFO("📋 Admin Credentials Summary"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"Username: {username}")
        self.stdout.write(f"Email:    {email}")
        self.stdout.write(
            f"Password: {'*' * len(self._get_credential(options.get('password'), 'DJANGO_SUPERUSER_PASSWORD', 'admin'))}"
        )
        self.stdout.write("=" * 60 + "\n")

    def _get_credentials_file_path(self, options):
        """Get the path to save credentials"""
        credentials_file = (
            options.get("credentials_file")
            or os.environ.get("ADMIN_CREDENTIALS_FILE")
            or "setup_data/admin_credentials.txt"
        )

        # Resolve path
        if not os.path.isabs(credentials_file):
            # Make relative to project root (parent of src/)
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            credentials_file = base_dir / credentials_file

        return Path(credentials_file)

    def _save_credentials(self, file_path, username, email, password, was_created):
        """Save credentials to file with restricted permissions"""
        try:
            # Create directory if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Prepare content
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            action = "CREATED" if was_created else "VERIFIED/UPDATED"

            content = f"""
{'=' * 70}
Django Admin Credentials
{'=' * 70}
Generated: {timestamp}
Action:    {action}
{'=' * 70}

Username: {username}
Email:    {email}
Password: {password}

Admin URL (development): http://localhost:8000/admin/
Admin URL (production):  http://localhost/admin/ (or your domain)

{'=' * 70}
SECURITY WARNING
{'=' * 70}
This file contains sensitive credentials in plaintext!

For Development:
  - This is acceptable for local development environments
  - Keep this file in .gitignore (should already be configured)
  
For Production:
  - DO NOT use default credentials
  - Set strong credentials via environment variables:
    * DJANGO_SUPERUSER_USERNAME
    * DJANGO_SUPERUSER_EMAIL
    * DJANGO_SUPERUSER_PASSWORD
  - Use secrets management (GitHub Secrets, Azure Key Vault, etc.)
  - Consider deleting this file after first login

{'=' * 70}
"""

            # Write file
            file_path.write_text(content.strip() + "\n")

            # Set restrictive permissions (Unix-like systems only)
            if hasattr(os, "chmod"):
                os.chmod(file_path, 0o600)

            self.stdout.write(
                self.style.SUCCESS(f"💾 Credentials saved to: {file_path.absolute()}")
            )
            self.stdout.write(
                self.style.WARNING("   (Readable only by file owner for security)")
            )

        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️  Could not save credentials to file: {e}")
            )
            self.stdout.write(
                self.style.WARNING(
                    f"   Manual credentials - Username: {username}, Password: {password}"
                )
            )
