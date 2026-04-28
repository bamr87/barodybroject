"""
File: config.py
Description: Configuration helpers for loading OpenAI settings and app config
Author: Barodybroject Team <team@example.com>
Created: 2025-12-19
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- django: >=5.1
- openai: >=1.57.0

Usage: from parodynews.utils.config import get_openai_client
"""

import os

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q


def table_exists_and_fields_populated(model_name):
    """
    Validate that a model table exists and has required API configuration fields populated.

    Args:
        model_name: Name of the Django model to validate

    Returns:
        bool: True if table exists and has valid API configuration, False otherwise
    """
    try:
        model = apps.get_model("parodynews", model_name)
        if model.objects.exists():
            return model.objects.filter(
                Q(api_key__isnull=False)
                & ~Q(api_key="")
                & Q(project_id__isnull=False)
                & ~Q(project_id="")
                & Q(org_id__isnull=False)
                & ~Q(org_id="")
            ).exists()
        return False
    except LookupError:
        return False


def get_config_value(key):
    """
    Retrieve a configuration value from the AppConfig model.

    Args:
        key: The attribute name to retrieve from AppConfig

    Returns:
        The configuration value if found, None otherwise
    """
    from ..models import AppConfig

    try:
        config = AppConfig.objects.first()
        return getattr(config, key, None)
    except AppConfig.DoesNotExist:
        return None


def get_openai_client():
    """
    Initialize and return an OpenAI client from database or environment config.

    Returns:
        OpenAI client configured with api_key and optional organization/project
    """
    from openai import OpenAI

    api_key = get_config_value("api_key") or os.environ.get("OPENAI_API_KEY")
    org_id = get_config_value("org_id") or os.environ.get("OPENAI_ORG_ID")
    project_id = get_config_value("project_id") or os.environ.get("OPENAI_PROJECT_ID")

    if not api_key:
        raise ImproperlyConfigured(
            "OpenAI API key is not configured. Set OPENAI_API_KEY or add an AppConfig row."
        )

    client_kwargs = {"api_key": api_key}
    if org_id:
        client_kwargs["organization"] = org_id
    if project_id:
        client_kwargs["project"] = project_id

    return OpenAI(**client_kwargs)

