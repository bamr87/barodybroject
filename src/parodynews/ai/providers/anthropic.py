"""
File: anthropic.py
Description: Claude through the Anthropic Messages API (API key or OAuth bearer token)
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 0.6.0

Dependencies:
- anthropic: >=1.5.0

Usage:
    export ANTHROPIC_API_KEY=sk-ant-api...
    from parodynews.ai import get_provider
    get_provider("anthropic").generate(...)

Structured output uses ``output_config.format`` (JSON schema) so the response
is guaranteed to be a JSON document; it is still validated locally with
``jsonschema`` like every other provider. On Claude Opus 5 / Fable models the
server-side refusal fallback is enabled by default (``fallbacks="default"``)
so a safety-classifier decline re-runs the request on a fallback model inside
the same call; set ``extra.server_side_fallbacks`` to ``false`` on the
provider configuration to opt out.
"""

from __future__ import annotations

import re
from typing import Any

from ..base import AIProvider, GenerationRequest, GenerationResult, ModelInfo
from ..exceptions import AIConfigurationError, AIProviderError, AIResponseError

OAUTH_TOKEN_PREFIX = "sk-ant-oat"
OAUTH_BETA_HEADER = "oauth-2025-04-20"
FALLBACK_BETA = "server-side-fallback-2026-07-01"
DEFAULT_MAX_TOKENS = 16000

STATIC_MODELS: tuple[tuple[str, str, str], ...] = (
    ("claude-opus-5", "Claude Opus 5", "Default. 1M context."),
    ("claude-sonnet-5", "Claude Sonnet 5", "Fast and capable."),
    ("claude-haiku-4-5", "Claude Haiku 4.5", "Cheapest; 200K context."),
    ("claude-opus-4-8", "Claude Opus 4.8", "Previous Opus generation."),
    ("claude-opus-4-6", "Claude Opus 4.6", "Supports sampling parameters."),
    ("claude-sonnet-4-6", "Claude Sonnet 4.6", "Supports sampling parameters."),
    ("claude-fable-5-1", "Claude Fable 5.1", "Most capable; premium pricing."),
)

# Model families that reject temperature / top_p (they run adaptive thinking).
_NO_SAMPLING_RE = re.compile(
    r"^claude-(opus-5|sonnet-5|opus-4-[78]|fable|mythos)", re.IGNORECASE
)
_FALLBACK_RE = re.compile(r"^claude-(opus-5|fable)", re.IGNORECASE)


class AnthropicProvider(AIProvider):
    slug = "anthropic"
    display_name = "Anthropic (Claude API)"
    description = (
        "Claude via the Messages API with an Anthropic API key. Use this for "
        "multi-tenant or commercial deployments."
    )
    default_model = "claude-opus-5"
    credential_env_vars = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")
    model_env_var = "ANTHROPIC_MODEL"
    supports_model_discovery = True

    def static_models(self):
        return tuple(
            ModelInfo(mid, self.slug, name, desc) for mid, name, desc in STATIC_MODELS
        )

    # ----------------------------------------------------------------- client
    def _client(self) -> Any:
        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover - depends on install
            raise AIConfigurationError(
                "anthropic is not installed; run `pip install anthropic`",
                provider=self.slug,
            ) from exc

        credential = self.credential()
        if not credential:
            raise AIConfigurationError(
                "Anthropic is not configured. Set ANTHROPIC_API_KEY or add a "
                "credential for the 'anthropic' provider in Settings.",
                provider=self.slug,
            )
        extra = self.config.extra or {}
        kwargs: dict[str, Any] = {
            "max_retries": int(extra.get("max_retries", 2)),
            "timeout": float(extra.get("timeout", 600)),
        }
        if credential.startswith(OAUTH_TOKEN_PREFIX) or self.credential_source() == (
            "ANTHROPIC_AUTH_TOKEN"
        ):
            # OAuth tokens travel as a bearer token plus the oauth beta header.
            kwargs["auth_token"] = credential
            kwargs["default_headers"] = {"anthropic-beta": OAUTH_BETA_HEADER}
        else:
            kwargs["api_key"] = credential
        if self.config.base_url:
            kwargs["base_url"] = self.config.base_url
        return anthropic.Anthropic(**kwargs)

    # ---------------------------------------------------------------- catalog
    def list_models(self) -> list[ModelInfo]:
        if not self.is_configured():
            return list(self.static_models())
        try:
            client = self._client()
            models = [
                ModelInfo(m.id, self.slug, getattr(m, "display_name", "") or m.id)
                for m in client.models.list()
            ]
        except Exception:  # noqa: BLE001 - discovery is best-effort
            return list(self.static_models())
        return models or list(self.static_models())

    # ------------------------------------------------------------- generation
    def build_kwargs(self, request: GenerationRequest) -> dict[str, Any]:
        system, turns = self.normalize(request)
        model = self.resolve_model(request.model)
        extra = self.config.extra or {}
        kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": request.max_tokens
            or int(extra.get("max_tokens", DEFAULT_MAX_TOKENS)),
            "messages": [turn.as_dict() for turn in turns],
        }
        if system:
            kwargs["system"] = system
        output_config: dict[str, Any] = {}
        if request.json_schema is not None:
            output_config["format"] = {
                "type": "json_schema",
                "schema": request.json_schema,
            }
        if extra.get("effort"):
            output_config["effort"] = extra["effort"]
        if output_config:
            kwargs["output_config"] = output_config
        if extra.get("thinking"):
            kwargs["thinking"] = extra["thinking"]
        if request.temperature is not None and not _NO_SAMPLING_RE.match(model):
            kwargs["temperature"] = request.temperature
        return kwargs

    def _use_fallbacks(self, model: str) -> bool:
        extra = self.config.extra or {}
        return bool(extra.get("server_side_fallbacks", True)) and bool(
            _FALLBACK_RE.match(model)
        )

    def generate(self, request: GenerationRequest) -> GenerationResult:
        import anthropic

        client = self._client()
        kwargs = self.build_kwargs(request)
        try:
            if self._use_fallbacks(kwargs["model"]):
                response = client.beta.messages.create(
                    betas=[FALLBACK_BETA], fallbacks="default", **kwargs
                )
            else:
                response = client.messages.create(**kwargs)
        except anthropic.AuthenticationError as exc:
            raise AIConfigurationError(
                f"Anthropic rejected the credential: {exc.message}", provider=self.slug
            ) from exc
        except anthropic.NotFoundError as exc:
            raise AIConfigurationError(
                f"Unknown Anthropic model {kwargs['model']!r}: {exc.message}",
                provider=self.slug,
            ) from exc
        except anthropic.RateLimitError as exc:
            raise AIProviderError(
                f"Anthropic rate limit: {exc.message}",
                provider=self.slug,
                retryable=True,
            ) from exc
        except anthropic.APIStatusError as exc:
            raise AIProviderError(
                f"Anthropic API error {exc.status_code}: {exc.message}",
                provider=self.slug,
                retryable=exc.status_code >= 500,
            ) from exc
        except anthropic.APIConnectionError as exc:
            raise AIProviderError(
                f"Could not reach Anthropic: {exc}", provider=self.slug, retryable=True
            ) from exc

        if response.stop_reason == "refusal":
            details = getattr(response, "stop_details", None)
            category = getattr(details, "category", None) or "unspecified"
            raise AIResponseError(
                f"Claude declined the request (category: {category})",
                provider=self.slug,
            )

        text = "".join(
            block.text
            for block in response.content
            if getattr(block, "type", "") == "text"
        )
        if not text.strip():
            raise AIResponseError(
                "Claude returned an empty response", provider=self.slug
            )

        data: Any = None
        if request.json_schema is not None:
            data = self.parse_structured(text, request.json_schema, provider=self.slug)

        usage_obj = getattr(response, "usage", None)
        usage = {
            "input_tokens": getattr(usage_obj, "input_tokens", 0),
            "output_tokens": getattr(usage_obj, "output_tokens", 0),
            "cache_read_input_tokens": getattr(usage_obj, "cache_read_input_tokens", 0)
            or 0,
            "cache_creation_input_tokens": getattr(
                usage_obj, "cache_creation_input_tokens", 0
            )
            or 0,
        }
        return GenerationResult(
            text=text,
            data=data,
            provider=self.slug,
            model=getattr(response, "model", "") or kwargs["model"],
            usage=usage,
            remote_id=getattr(response, "id", "") or "",
            stop_reason=response.stop_reason or "",
            raw=response,
        )
