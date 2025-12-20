"""
File: base.py
Description: Abstract base models and mixins for parodynews models
Author: Barodybroject Team <team@example.com>
Created: 2025-11-30
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- django: >=5.1

Usage: from parodynews.models.base import TimestampedModel
"""

from django.db import models
from django.utils import timezone


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

