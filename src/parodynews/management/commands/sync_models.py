"""
File: sync_models.py
Description: Refresh the AIModel catalogue from one or every configured provider
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 0.6.0

Usage:
  python manage.py sync_models                 # default provider
  python manage.py sync_models --provider openai
  python manage.py sync_models --all
"""

from django.core.management.base import BaseCommand, CommandError

from parodynews.ai import AIError, available_providers
from parodynews.services.assistants import sync_models


class Command(BaseCommand):
    help = "Fetch the models a provider offers and upsert them as AIModel rows"

    def add_arguments(self, parser):
        parser.add_argument(
            "--provider", help="Provider slug (default: the default provider)"
        )
        parser.add_argument(
            "--all", action="store_true", help="Sync every registered provider"
        )

    def handle(self, *args, **options):
        slugs = available_providers() if options["all"] else [options.get("provider")]
        failures = 0
        for slug in slugs:
            try:
                report = sync_models(slug)
            except AIError as exc:
                failures += 1
                self.stdout.write(self.style.WARNING(f"{slug or 'default'}: {exc}"))
                continue
            self.stdout.write(
                self.style.SUCCESS(
                    f"{report.provider}: {len(report.created)} created, "
                    f"{len(report.updated)} updated, {report.total} total"
                )
            )
        if failures and not options["all"]:
            raise CommandError("model sync failed")
