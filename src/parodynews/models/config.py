"""
File: config.py
Description: Application-wide configuration (AI provider credentials, publishing, attribution)
Author: Barodybroject Team <team@example.com>
Created: 2025-11-30
Last Modified: 2026-09-14
Version: 0.6.0

Dependencies:
- django: >=5.1

Usage: from parodynews.models.config import AIProviderConfig, AppConfig
"""

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models, transaction


class PoweredBy(models.Model):
    """Configuration for 'Powered By' attribution links shown in the footer."""

    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100)
    url = models.URLField()

    class Meta:
        app_label = "parodynews"
        verbose_name = "Powered By"
        verbose_name_plural = "Powered By"

    def __str__(self):
        return self.name


class AppConfig(models.Model):
    """Publishing configuration (GitHub Pages target).

    Singleton-style model: the application reads the first row. AI provider
    credentials used to live here as OpenAI-specific columns; they moved to
    :class:`AIProviderConfig` so every provider is configured the same way.

    Attributes:
        github_pages_repo (str): GitHub repository for publishing ('owner/repo')
        github_pages_branch (str): Target branch for publishing (default: 'main')
        github_pages_token (str): GitHub token used to open publish pull requests
        github_pages_post_dir (str): Directory for posts (default: 'posts/')
    """

    github_pages_repo = models.CharField(max_length=255)
    github_pages_branch = models.CharField(max_length=255, default="main")
    github_pages_token = models.CharField(max_length=255)
    github_pages_post_dir = models.CharField(max_length=255, default="posts/")

    class Meta:
        app_label = "parodynews"
        verbose_name = "App Configuration"
        verbose_name_plural = "App Configurations"

    def __str__(self):
        return "App Configuration"


class AIProviderConfig(models.Model):
    """Per-provider credentials and defaults, editable from the settings UI.

    One row per provider slug (``claude_code``, ``anthropic``, ``openai``,
    ``mock``...). Every field is optional: a provider with no row, or a row
    with an empty ``api_key``, falls back to its environment variables (for
    example ``CLAUDE_CODE_OAUTH_TOKEN``). The row flagged ``is_default`` is
    the provider used when a request does not name one; without such a row
    ``settings.AI_DEFAULT_PROVIDER`` applies.

    Attributes:
        provider (str): Provider slug registered in ``parodynews.ai``
        api_key (str): Credential (Claude Code OAuth token, API key...)
        base_url (str): Optional API base URL override (proxies, gateways)
        organization_id / project_id (str): Provider-specific scoping ids
        default_model (str): Model used when an assistant has none
        is_default (bool): Whether this is the application's default provider
        is_enabled (bool): Disabled providers cannot be used
        extra (dict): Provider-specific options (``effort``, ``max_turns``,
            ``cli_path``, ``server_side_fallbacks``...)
    """

    provider = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100, blank=True, default="")
    api_key = models.CharField(max_length=1024, blank=True, default="")
    base_url = models.CharField(max_length=255, blank=True, default="")
    organization_id = models.CharField(max_length=255, blank=True, default="")
    project_id = models.CharField(max_length=255, blank=True, default="")
    default_model = models.CharField(max_length=255, blank=True, default="")
    is_default = models.BooleanField(default=False)
    is_enabled = models.BooleanField(default=True)
    extra = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "parodynews"
        verbose_name = "AI Provider Configuration"
        verbose_name_plural = "AI Provider Configurations"
        ordering = ["-is_default", "provider"]

    def __str__(self):
        return self.display_name or self.provider

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.is_default:
                # Exactly one default at a time.
                AIProviderConfig.objects.filter(is_default=True).exclude(
                    pk=self.pk
                ).update(is_default=False)
            super().save(*args, **kwargs)

    @property
    def has_credential(self) -> bool:
        return bool(self.api_key)

    def clean(self):
        from parodynews.ai.registry import available_providers

        if self.provider not in available_providers():
            raise ValidationError({"provider": f"Unknown provider {self.provider!r}."})
        if self.is_default and not self.is_enabled:
            raise ValidationError(
                {"is_default": "The default provider must be enabled."}
            )


class FieldDefaults(models.Model):
    """Stores default values grouped by type for model fields.

    JSON structure::

        defaults = [
            {"model_name": "MyModel", "fields": {"field1": "some default"}},
            ...
        ]

    Saving clears the ``field_defaults`` cache so updated defaults are
    immediately available.
    """

    type = models.CharField(max_length=255, default="default_type")
    defaults = models.JSONField(
        default=list,
        help_text="A list of model definitions with their fields and default values.",
    )

    class Meta:
        app_label = "parodynews"
        verbose_name = "Field Defaults"
        verbose_name_plural = "Field Defaults"

    def __str__(self):
        return f"Defaults for {self.type}"

    def save(self, *args, **kwargs):
        cache.delete("field_defaults")
        super().save(*args, **kwargs)
