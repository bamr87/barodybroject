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

from django.apps import apps
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
    Initialize and return an OpenAI client with configuration from database.

    Returns:
        OpenAI module configured with api_key and organization
    """
    import openai

    api_key = get_config_value("api_key")
    org_id = get_config_value("org_id")

    openai.api_key = api_key
    if org_id:
        openai.organization = org_id

    return openai

