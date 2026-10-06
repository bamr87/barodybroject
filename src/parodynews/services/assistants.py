"""
File: assistants.py
Description: Assistant and model-catalogue workflows
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 0.6.0

Dependencies:
- django: >=5.1

Usage:
    from parodynews.services import assistants
    report = assistants.sync_models("claude_code")
"""

from __future__ import annotations

from dataclasses import dataclass, field

from django.db import transaction

from parodynews.ai import get_provider
from parodynews.models import AIModel, Assistant


@dataclass
class SyncReport:
    provider: str
    created: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    total: int = 0

    def as_dict(self) -> dict:
        return {
            "provider": self.provider,
            "created": self.created,
            "updated": self.updated,
            "total": self.total,
        }


@transaction.atomic
def sync_models(provider_slug: str | None = None) -> SyncReport:
    """Upsert ``AIModel`` rows from what the provider says it can run."""
    provider = get_provider(provider_slug, require_enabled=False)
    report = SyncReport(provider=provider.slug)
    for info in provider.list_models():
        row, created = AIModel.objects.update_or_create(
            provider=provider.slug,
            model_id=info.id,
            defaults={
                "display_name": info.display_name or "",
                "description": info.description or "",
                "is_active": True,
            },
        )
        (report.created if created else report.updated).append(row.model_id)
    report.total = AIModel.objects.filter(provider=provider.slug).count()
    return report


def ensure_default_model(provider_slug: str | None = None) -> AIModel:
    """Make sure the provider's default model exists in the catalogue."""
    provider = get_provider(provider_slug, require_enabled=False)
    row, _ = AIModel.objects.get_or_create(
        provider=provider.slug,
        model_id=provider.model,
        defaults={"display_name": provider.model, "description": "Provider default"},
    )
    return row


def delete_assistant(assistant: Assistant) -> None:
    """Delete an assistant. Nothing remote to clean up: assistants are local."""
    assistant.delete()
