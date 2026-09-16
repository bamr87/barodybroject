"""
File: registry.py
Description: Resolve provider classes and their configuration (database, environment, settings)
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 0.6.0

Dependencies:
- django: >=5.1

Usage:
    from parodynews.ai.registry import get_provider, get_default_provider_slug

Resolution order for the default provider:
    1. the enabled ``AIProviderConfig`` row flagged ``is_default``
    2. ``settings.AI_DEFAULT_PROVIDER`` (env ``AI_DEFAULT_PROVIDER``)
    3. ``"claude_code"``

Resolution order for a provider's credential / model:
    1. its ``AIProviderConfig`` row (when the table exists and the row is set)
    2. the provider's environment variables (``credential_env_vars`` /
       ``model_env_var``)
    3. the provider class defaults

Provider classes come from ``settings.AI_PROVIDERS`` (slug -> dotted path)
merged over the built-in set, so a deployment can register its own provider
without touching this package.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from django.conf import settings
from django.db import DatabaseError
from django.utils.module_loading import import_string

from .base import AIProvider, ProviderConfig
from .exceptions import AIConfigurationError

BUILTIN_PROVIDERS: dict[str, str] = {
    "claude_code": "parodynews.ai.providers.claude_code.ClaudeCodeProvider",
    "anthropic": "parodynews.ai.providers.anthropic.AnthropicProvider",
    "openai": "parodynews.ai.providers.openai.OpenAIProvider",
    "mock": "parodynews.ai.providers.mock.MockProvider",
}

FALLBACK_DEFAULT_PROVIDER = "claude_code"


@lru_cache(maxsize=1)
def provider_classes() -> dict[str, type[AIProvider]]:
    """Slug -> provider class, built-ins merged with ``settings.AI_PROVIDERS``."""
    paths = {**BUILTIN_PROVIDERS, **getattr(settings, "AI_PROVIDERS", {})}
    classes: dict[str, type[AIProvider]] = {}
    for slug, dotted in paths.items():
        if not dotted:  # allow a deployment to disable a built-in with ""
            continue
        cls = import_string(dotted)
        if not issubclass(cls, AIProvider):
            raise AIConfigurationError(f"{dotted} is not an AIProvider subclass")
        classes[slug] = cls
    return classes


def clear_cache() -> None:
    """Forget cached classes (tests override ``AI_PROVIDERS``)."""
    provider_classes.cache_clear()


def available_providers() -> list[str]:
    return list(provider_classes())


def get_provider_class(slug: str) -> type[AIProvider]:
    try:
        return provider_classes()[slug]
    except KeyError as exc:
        raise AIConfigurationError(
            f"unknown AI provider {slug!r}; available: {', '.join(available_providers())}"
        ) from exc


def _db_config(slug: str) -> Any | None:
    """The ``AIProviderConfig`` row for ``slug``, or ``None`` (also before migrations)."""
    try:
        from parodynews.models import AIProviderConfig
    except Exception:  # pragma: no cover - app registry not ready
        return None
    try:
        return AIProviderConfig.objects.filter(provider=slug).first()
    except DatabaseError:
        return None


def load_config(slug: str) -> ProviderConfig:
    """Build the :class:`ProviderConfig` for ``slug``."""
    config = ProviderConfig(slug=slug)
    row = _db_config(slug)
    if row is not None:
        config.api_key = row.api_key or ""
        config.base_url = row.base_url or ""
        config.organization_id = row.organization_id or ""
        config.project_id = row.project_id or ""
        config.default_model = row.default_model or ""
        config.extra = dict(row.extra or {})
        config.enabled = bool(row.is_enabled)
        config.source = "database" if row.api_key else "environment"
    else:
        config.source = "environment"
    return config


def get_default_provider_slug() -> str:
    try:
        from parodynews.models import AIProviderConfig

        row = (
            AIProviderConfig.objects.filter(is_default=True, is_enabled=True)
            .order_by("pk")
            .first()
        )
    except Exception:  # noqa: BLE001 - table missing / app not ready
        row = None
    if row is not None and row.provider in provider_classes():
        return row.provider
    configured = (
        getattr(settings, "AI_DEFAULT_PROVIDER", "") or FALLBACK_DEFAULT_PROVIDER
    )
    return configured if configured in provider_classes() else FALLBACK_DEFAULT_PROVIDER


def get_provider(
    slug: str | None = None, *, require_enabled: bool = True
) -> AIProvider:
    """Instantiate the provider for ``slug`` (default provider when ``None``)."""
    resolved = slug or get_default_provider_slug()
    cls = get_provider_class(resolved)
    config = load_config(resolved)
    if require_enabled and not config.enabled:
        raise AIConfigurationError(
            f"AI provider {resolved!r} is disabled", provider=resolved
        )
    return cls(config)


def describe_providers() -> list[dict[str, Any]]:
    """Summaries for every registered provider, default first."""
    default = get_default_provider_slug()
    summaries = []
    for slug in available_providers():
        provider = get_provider(slug, require_enabled=False)
        info = provider.describe()
        info["is_default"] = slug == default
        summaries.append(info)
    summaries.sort(key=lambda item: (not item["is_default"], item["slug"]))
    return summaries
