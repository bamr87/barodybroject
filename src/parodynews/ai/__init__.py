"""
File: __init__.py
Description: Provider-agnostic AI layer for parodynews
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 0.6.0

Usage:
    from parodynews.ai import ChatMessage, GenerationRequest, get_provider

    result = get_provider().generate(
        GenerationRequest(
            system="You are a satirical news writer.",
            messages=[ChatMessage("user", "Write a headline about tax season.")],
        )
    )

The application never imports a vendor SDK directly. It builds a
``GenerationRequest``, asks the registry for a provider, and reads a
``GenerationResult``. Providers live in ``parodynews.ai.providers`` and are
selected by slug: ``claude_code`` (default), ``anthropic``, ``openai``, ``mock``.
"""

from .base import (
    AIProvider,
    ChatMessage,
    GenerationRequest,
    GenerationResult,
    ModelInfo,
    ProviderConfig,
)
from .exceptions import (
    AIConfigurationError,
    AIError,
    AIProviderError,
    AIResponseError,
)
from .registry import (
    available_providers,
    describe_providers,
    get_default_provider_slug,
    get_provider,
    get_provider_class,
)

__all__ = [
    "AIConfigurationError",
    "AIError",
    "AIProvider",
    "AIProviderError",
    "AIResponseError",
    "ChatMessage",
    "GenerationRequest",
    "GenerationResult",
    "ModelInfo",
    "ProviderConfig",
    "available_providers",
    "describe_providers",
    "get_default_provider_slug",
    "get_provider",
    "get_provider_class",
]
