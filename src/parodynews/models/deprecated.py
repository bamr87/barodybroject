"""
File: deprecated.py
Description: Deprecated Django models kept for compatibility (scheduled for removal)
Author: Barodybroject Team <team@example.com>
Created: 2025-11-30
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- django: >=5.1

Usage: Avoid in new code; retained for compatibility.
"""

# DEPRECATION NOTICE:
# All models in this module are deprecated and will be removed in a future version.
# Please migrate away from these models as soon as possible.

import warnings
from django.db import models
from django.utils import timezone


class MyObject(models.Model):
    """DEPRECATED: Test/example model with no clear purpose.
    
    This model appears to be a placeholder or test model and should not be used.
    It will be removed in a future version.
    
    Attributes:
        name (str): Object name (max 100 chars)
        description (str): Object description
    
    Deprecation:
        Deprecated as of 2025-11-30. Will be removed in version 3.0.0.
        No replacement model is provided as this appears to be test code.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        app_label = 'parodynews'
        verbose_name = 'My Object (DEPRECATED)'
        verbose_name_plural = 'My Objects (DEPRECATED)'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Save with deprecation warning."""
        warnings.warn(
            "MyObject model is deprecated and will be removed in version 3.0.0. "
            "Please migrate to an appropriate model.",
            DeprecationWarning,
            stacklevel=2
        )
        super().save(*args, **kwargs)


class GeneralizedCodes(models.Model):
    """DEPRECATED: Generic code/lookup table with unclear purpose.
    
    This model appears to be an overly generic lookup table that lacks
    clear business logic. It should be replaced with specific, purpose-built
    models for each use case.
    
    Attributes:
        code (str): Unique code identifier (max 256 chars)
        name (str): Display name (max 256 chars)
        description (str): Full text description
        type (str): Type classification (default: 'system', max 256 chars)
        items (list): JSON array of items
        model (str): Model name (default: 'default', max 256 chars)
        table (str): Table name (default: 'default', max 256 chars)
        field (str): Field name (default: 'default', max 256 chars)
        database (str): Database name (default: 'default', max 256 chars)
        category (str): Category (default: 'default', max 256 chars)
        domain (str): Domain (default: 'default', max 256 chars)
        entity (str): Entity (default: 'default', max 256 chars)
        project (str): Project (default: 'default', max 256 chars)
        module (str): Module (default: 'default', max 256 chars)
        hash (str): Hash value (max 256 chars)
        created_at (datetime): Creation timestamp
    
    Deprecation:
        Deprecated as of 2025-11-30. Will be removed in version 3.0.0.
        Replace with specific models for your use case (e.g., Category, Tag, etc.)
    """
    code = models.CharField(max_length=256, unique=True)
    name = models.CharField(max_length=256)
    description = models.TextField()
    type = models.CharField(max_length=256, default="system")
    items = models.JSONField(default=list)
    model = models.CharField(max_length=256, default="default")
    table = models.CharField(max_length=256, default="default")
    field = models.CharField(max_length=256, default="default")
    database = models.CharField(max_length=256, default="default")
    category = models.CharField(max_length=256, default="default")
    domain = models.CharField(max_length=256, default="default")
    entity = models.CharField(max_length=256, default="default")
    project = models.CharField(max_length=256, default="default")
    module = models.CharField(max_length=256, default="default")
    hash = models.CharField(max_length=256)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'parodynews'
        verbose_name = 'Generalized Code (DEPRECATED)'
        verbose_name_plural = 'Generalized Codes (DEPRECATED)'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Save with deprecation warning."""
        warnings.warn(
            "GeneralizedCodes model is deprecated and will be removed in version 3.0.0. "
            "Please replace with specific, purpose-built models for your use case.",
            DeprecationWarning,
            stacklevel=2
        )
        super().save(*args, **kwargs)

