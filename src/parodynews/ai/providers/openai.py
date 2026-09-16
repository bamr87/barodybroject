"""
File: openai.py
Description: OpenAI chat completions provider (kept for existing deployments)
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 0.6.0

Dependencies:
- openai: >=3.0

Usage:
    export OPENAI_API_KEY=sk-...
    from parodynews.ai import get_provider
    get_provider("openai").generate(...)

Structured output uses ``response_format={"type": "json_schema", ...}`` with
``strict`` mode, which is what the previous OpenAI-only implementation did.
The Assistants / Threads API is no longer used: conversation state lives in
the database and is replayed on every call, which is what makes the
application provider-agnostic.
"""

from __future__ import annotations

from typing import Any

from ..base import AIProvider, GenerationRequest, GenerationResult, ModelInfo
from ..exceptions import AIConfigurationError, AIProviderError, AIResponseError

STATIC_MODELS: tuple[tuple[str, str, str], ...] = (
    ("gpt-4o-mini", "GPT-4o mini", "Default. Inexpensive general model."),
    ("gpt-4o", "GPT-4o", "Higher quality general model."),
)


class OpenAIProvider(AIProvider):
    slug = "openai"
    display_name = "OpenAI"
    description = "OpenAI chat completions with JSON-schema structured output."
    default_model = "gpt-4o-mini"
    credential_env_vars = ("OPENAI_API_KEY",)
    model_env_var = "OPENAI_MODEL"
    supports_model_discovery = True

    def static_models(self):
        return tuple(
            ModelInfo(mid, self.slug, name, desc) for mid, name, desc in STATIC_MODELS
        )

    # ----------------------------------------------------------------- client
    def _client(self) -> Any:
        try:
            import openai
        except ImportError as exc:  # pragma: no cover - depends on install
            raise AIConfigurationError(
                "openai is not installed; run `pip install openai`", provider=self.slug
            ) from exc

        credential = self.credential()
        if not credential:
            raise AIConfigurationError(
                "OpenAI is not configured. Set OPENAI_API_KEY or add a credential "
                "for the 'openai' provider in Settings.",
                provider=self.slug,
            )
        extra = self.config.extra or {}
        kwargs: dict[str, Any] = {
            "api_key": credential,
            "max_retries": int(extra.get("max_retries", 2)),
            "timeout": float(extra.get("timeout", 600)),
        }
        if self.config.organization_id:
            kwargs["organization"] = self.config.organization_id
        if self.config.project_id:
            kwargs["project"] = self.config.project_id
        if self.config.base_url:
            kwargs["base_url"] = self.config.base_url
        return openai.OpenAI(**kwargs)

    # ---------------------------------------------------------------- catalog
    def list_models(self) -> list[ModelInfo]:
        if not self.is_configured():
            return list(self.static_models())
        try:
            models = [
                ModelInfo(m.id, self.slug, m.id) for m in self._client().models.list()
            ]
        except Exception:  # noqa: BLE001 - discovery is best-effort
            return list(self.static_models())
        return sorted(models, key=lambda m: m.id) or list(self.static_models())

    # ------------------------------------------------------------- generation
    def build_kwargs(self, request: GenerationRequest) -> dict[str, Any]:
        system, turns = self.normalize(request)
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.extend(turn.as_dict() for turn in turns)
        kwargs: dict[str, Any] = {
            "model": self.resolve_model(request.model),
            "messages": messages,
        }
        if request.json_schema is not None:
            kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": request.schema_name or "response",
                    "description": request.schema_description or "",
                    "schema": request.json_schema,
                    "strict": True,
                },
            }
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.max_tokens:
            kwargs["max_completion_tokens"] = request.max_tokens
        return kwargs

    def generate(self, request: GenerationRequest) -> GenerationResult:
        import openai

        client = self._client()
        kwargs = self.build_kwargs(request)
        try:
            response = client.chat.completions.create(**kwargs)
        except openai.AuthenticationError as exc:
            raise AIConfigurationError(
                f"OpenAI rejected the credential: {exc}", provider=self.slug
            ) from exc
        except openai.NotFoundError as exc:
            raise AIConfigurationError(
                f"Unknown OpenAI model {kwargs['model']!r}: {exc}", provider=self.slug
            ) from exc
        except openai.RateLimitError as exc:
            raise AIProviderError(
                f"OpenAI rate limit: {exc}", provider=self.slug, retryable=True
            ) from exc
        except openai.APIStatusError as exc:
            raise AIProviderError(
                f"OpenAI API error {exc.status_code}: {exc}",
                provider=self.slug,
                retryable=exc.status_code >= 500,
            ) from exc
        except openai.APIConnectionError as exc:
            raise AIProviderError(
                f"Could not reach OpenAI: {exc}", provider=self.slug, retryable=True
            ) from exc

        if not response.choices:
            raise AIResponseError("OpenAI returned no choices", provider=self.slug)
        choice = response.choices[0]
        message = choice.message
        if getattr(message, "refusal", None):
            raise AIResponseError(
                f"OpenAI declined the request: {message.refusal}", provider=self.slug
            )
        if choice.finish_reason == "content_filter":
            raise AIResponseError(
                "OpenAI content filter blocked the response", provider=self.slug
            )
        text = message.content or ""
        if not text.strip():
            raise AIResponseError(
                "OpenAI returned an empty response", provider=self.slug
            )

        data: Any = None
        if request.json_schema is not None:
            data = self.parse_structured(text, request.json_schema, provider=self.slug)

        usage_obj = getattr(response, "usage", None)
        usage = {
            "input_tokens": getattr(usage_obj, "prompt_tokens", 0) or 0,
            "output_tokens": getattr(usage_obj, "completion_tokens", 0) or 0,
        }
        return GenerationResult(
            text=text,
            data=data,
            provider=self.slug,
            model=getattr(response, "model", "") or kwargs["model"],
            usage=usage,
            remote_id=getattr(response, "id", "") or "",
            stop_reason=choice.finish_reason or "",
            raw=response,
        )
