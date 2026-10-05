"""
File: exceptions.py
Description: Exception hierarchy for the provider-agnostic AI layer
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 0.6.0

Usage: from parodynews.ai.exceptions import AIProviderError
"""


class AIError(Exception):
    """Base class for every error raised by ``parodynews.ai``."""

    def __init__(self, message: str, *, provider: str = ""):
        super().__init__(message)
        self.provider = provider

    def __str__(self) -> str:  # pragma: no cover - trivial
        base = super().__str__()
        return f"[{self.provider}] {base}" if self.provider else base


class AIConfigurationError(AIError):
    """A provider is unknown, disabled, or has no usable credentials."""


class AIProviderError(AIError):
    """The upstream provider call failed (network, auth, rate limit, 5xx...)."""

    def __init__(self, message: str, *, provider: str = "", retryable: bool = False):
        super().__init__(message, provider=provider)
        self.retryable = retryable


class AIResponseError(AIError):
    """The provider answered, but not with something the caller can use.

    Raised for refusals, empty completions, invalid JSON when a schema was
    requested, and JSON that does not validate against that schema.
    """
