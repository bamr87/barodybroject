"""
File: base.py
Description: Abstract base models, mixins, and id helpers for parodynews models
Author: Barodybroject Team <team@example.com>
Created: 2025-11-30
Last Modified: 2026-09-14
Version: 0.6.0

Dependencies:
- django: >=5.1

Usage: from parodynews.models.base import TimestampedModel, generate_prefixed_id
"""

import uuid

from django.db import models


def generate_prefixed_id(prefix: str) -> str:
    """Return a locally generated identifier such as ``asst_3f9c...``.

    Assistants, threads and messages used to take their primary keys from the
    OpenAI Assistants API. They are now created locally, so the key is minted
    here; the familiar prefixes are kept so existing rows and new rows look
    alike in the UI and in logs.
    """
    return f"{prefix}_{uuid.uuid4().hex[:24]}"


class TimestampedModel(models.Model):
    """Abstract base class for models with timestamp fields.

    Provides created_at and updated_at fields that are automatically
    managed by Django.

    Attributes:
        created_at (datetime): Timestamp when record was created
        updated_at (datetime): Timestamp of last update (auto-updated)
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DisplayFieldsMixin:
    """Mixin to provide get_display_fields method for models.

    Models using this mixin should define their display fields
    by overriding get_display_fields().
    """

    def get_display_fields(self):
        """Return list of fields to display in admin and list views.

        Override this method in subclasses to specify which fields
        should be displayed.

        Returns:
            list: Field names to display
        """
        return []
