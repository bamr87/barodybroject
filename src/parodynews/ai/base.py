"""
File: base.py
Description: Provider-agnostic request/response types and the AIProvider contract
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 0.6.0

Dependencies:
- jsonschema: >=4.20

Usage:
    from parodynews.ai import GenerationRequest, ChatMessage, get_provider

    provider = get_provider()  # the configured default (Claude Code by default)
    result = provider.generate(
        GenerationRequest(
            system="You write satirical news.",
            messages=[ChatMessage("user", "Write a headline about cats.")],
        )
    )
    print(result.text)

Every provider speaks the same three types: a ``GenerationRequest`` goes in, a
``GenerationResult`` comes out, and ``ModelInfo`` describes what the provider
can run. Nothing outside ``parodynews.ai.providers`` imports a vendor SDK.
"""

from __future__ import annotations

import json
import os
import re
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from typing import Any, ClassVar, Literal

from jsonschema import Draft7Validator

from .exceptions import AIResponseError

Role = Literal["system", "user", "assistant"]

VALID_ROLES: frozenset[str] = frozenset({"system", "user", "assistant"})

# A user turn appended when a conversation ends with an assistant message.
# Every current provider (and the Anthropic API in particular, which rejects
# assistant prefill) needs the final turn to come from the user.
CONTINUATION_PROMPT = (
    "Continue from the conversation above and produce your contribution, "
    "following your instructions."
)

_CODE_FENCE_RE = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.DOTALL)


@dataclass(frozen=True)
class ChatMessage:
    """One turn of a conversation, independent of any vendor's wire format."""

    role: Role
    content: str

    def __post_init__(self) -> None:
        if self.role not in VALID_ROLES:
            raise ValueError(f"unsupported chat role {self.role!r}")

    def as_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass
class GenerationRequest:
    """What the application wants generated.

    Attributes:
        messages: The conversation so far. ``system`` turns are folded into
            ``system`` by :meth:`AIProvider.normalize` before a provider sees
            them, so callers may use either mechanism.
        system: System / instruction prompt.
        model: Provider model id. Empty means "the provider's default".
        json_schema: When set, the provider must return JSON that validates
            against this Draft-7 schema; ``GenerationResult.data`` carries the
            parsed object.
        schema_name / schema_description: Metadata some providers attach to
            the structured-output request.
        temperature / max_tokens: Optional sampling limits. Providers ignore
            what their models do not support.
        metadata: Free-form context (thread id, user id...) for logging.
    """

    messages: list[ChatMessage]
    system: str = ""
    model: str = ""
    json_schema: dict[str, Any] | None = None
    schema_name: str = "response"
    schema_description: str = ""
    temperature: float | None = None
    max_tokens: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def wants_structured_output(self) -> bool:
        return self.json_schema is not None

    def last_user_text(self) -> str:
        for message in reversed(self.messages):
            if message.role == "user":
                return message.content
        return ""


@dataclass
class GenerationResult:
    """What came back, normalized.

    ``text`` is always populated (for structured requests it is the JSON
    document as text). ``data`` is the parsed and schema-validated object for
    structured requests and ``None`` otherwise. ``raw`` keeps the vendor
    response for debugging and is excluded from comparisons and ``repr``.
    """

    text: str
    data: Any = None
    provider: str = ""
    model: str = ""
    usage: dict[str, Any] = field(default_factory=dict)
    remote_id: str = ""
    stop_reason: str = ""
    raw: Any = field(default=None, repr=False, compare=False)

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.pop("raw", None)
        return payload


@dataclass(frozen=True)
class ModelInfo:
    """A model a provider can run."""

    id: str
    provider: str
    display_name: str = ""
    description: str = ""

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "provider": self.provider,
            "display_name": self.display_name or self.id,
            "description": self.description,
        }


@dataclass
class ProviderConfig:
    """Resolved configuration for one provider instance.

    Built by :mod:`parodynews.ai.registry` from, in priority order, the
    ``AIProviderConfig`` database row, environment variables, and settings.
    ``source`` records where the credential came from so the UI can say so.
    """

    slug: str
    api_key: str = ""
    base_url: str = ""
    organization_id: str = ""
    project_id: str = ""
    default_model: str = ""
    extra: dict[str, Any] = field(default_factory=dict)
    source: str = "settings"
    enabled: bool = True


class AIProvider(ABC):
    """Contract every provider implements.

    Subclasses set the class attributes and implement :meth:`generate`.
    Everything else (credential lookup, model resolution, message
    normalization, structured-output parsing) is shared so providers stay
    small and behave identically at the edges.
    """

    #: Registry key, also stored on ``AIModel.provider`` and ``AIProviderConfig``.
    slug: ClassVar[str] = ""
    #: Human-readable name for the UI.
    display_name: ClassVar[str] = ""
    #: Model used when neither the request nor the configuration names one.
    default_model: ClassVar[str] = ""
    #: Environment variables consulted for a credential, highest priority first.
    credential_env_vars: ClassVar[tuple[str, ...]] = ()
    #: Environment variable that overrides ``default_model``.
    model_env_var: ClassVar[str] = ""
    #: Whether :meth:`list_models` can ask the vendor for a live catalogue.
    supports_model_discovery: ClassVar[bool] = False
    #: Short description shown in the settings UI.
    description: ClassVar[str] = ""

    def __init__(self, config: ProviderConfig | None = None):
        self.config = config or ProviderConfig(slug=self.slug)

    # ------------------------------------------------------------------ config
    def credential(self) -> str:
        """The API key / token to use, or ``""`` when none is configured."""
        if self.config.api_key:
            return self.config.api_key
        for name in self.credential_env_vars:
            value = os.environ.get(name, "")
            if value:
                return value
        return ""

    def credential_source(self) -> str:
        """Where :meth:`credential` came from: ``database``, an env var name, or ``""``."""
        if self.config.api_key:
            return self.config.source or "database"
        for name in self.credential_env_vars:
            if os.environ.get(name, ""):
                return name
        return ""

    def is_configured(self) -> bool:
        return bool(self.credential())

    @property
    def model(self) -> str:
        """The default model for this provider instance."""
        if self.config.default_model:
            return self.config.default_model
        if self.model_env_var:
            from_env = os.environ.get(self.model_env_var, "")
            if from_env:
                return from_env
        return self.default_model

    def resolve_model(self, requested: str = "") -> str:
        return requested or self.model

    def describe(self) -> dict[str, Any]:
        """Serializable summary for the settings UI and ``/api/providers/``."""
        return {
            "slug": self.slug,
            "display_name": self.display_name,
            "description": self.description,
            "default_model": self.model,
            "configured": self.is_configured(),
            "credential_source": self.credential_source(),
            "credential_env_vars": list(self.credential_env_vars),
            "model_env_var": self.model_env_var,
            "supports_model_discovery": self.supports_model_discovery,
            "base_url": self.config.base_url,
            "enabled": self.config.enabled,
        }

    # ---------------------------------------------------------------- catalog
    def static_models(self) -> Iterable[ModelInfo]:
        """Models known to work, used when the vendor cannot be asked."""
        return ()

    def list_models(self) -> list[ModelInfo]:
        """Models the provider can run. Overridden by providers with discovery."""
        return list(self.static_models())

    # ------------------------------------------------------------- generation
    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Run one generation. Must raise ``AIError`` subclasses on failure."""

    def health_check(self) -> dict[str, Any]:
        """Cheap liveness probe: a one-word completion on the default model."""
        result = self.generate(
            GenerationRequest(
                system="Reply with the single word OK.",
                messages=[ChatMessage("user", "Health check.")],
                max_tokens=16,
            )
        )
        return {"ok": True, "model": result.model, "text": result.text.strip()[:80]}

    # ---------------------------------------------------------------- helpers
    @staticmethod
    def normalize(request: GenerationRequest) -> tuple[str, list[ChatMessage]]:
        """Return ``(system_prompt, turns)`` in the shape every vendor accepts.

        * ``system``-role turns are merged into the system prompt.
        * The first turn is a ``user`` turn (a placeholder is inserted if the
          history starts with the assistant).
        * The last turn is a ``user`` turn (``CONTINUATION_PROMPT`` is appended
          when the caller wants the model to react to its own prior output,
          as happens when an assistant group runs in sequence).
        """
        system_parts = [request.system.strip()] if request.system.strip() else []
        turns: list[ChatMessage] = []
        for message in request.messages:
            if message.role == "system":
                if message.content.strip():
                    system_parts.append(message.content.strip())
            else:
                turns.append(message)

        if not turns:
            raise AIResponseError("a generation request needs at least one user turn")
        if turns[0].role != "user":
            turns.insert(0, ChatMessage("user", "(conversation start)"))
        if turns[-1].role != "user":
            turns.append(ChatMessage("user", CONTINUATION_PROMPT))
        return "\n\n".join(system_parts), turns

    @staticmethod
    def parse_structured(
        text: str, schema: dict[str, Any], *, provider: str = ""
    ) -> Any:
        """Parse ``text`` as JSON and validate it against ``schema``.

        Tolerates a surrounding Markdown code fence, which some models add
        even when asked for bare JSON.
        """
        candidate = text.strip()
        fenced = _CODE_FENCE_RE.match(candidate)
        if fenced:
            candidate = fenced.group(1)
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError as exc:
            raise AIResponseError(
                f"model did not return valid JSON: {exc.msg}", provider=provider
            ) from exc
        return AIProvider.validate_structured(data, schema, provider=provider)

    @staticmethod
    def validate_structured(
        data: Any, schema: dict[str, Any], *, provider: str = ""
    ) -> Any:
        errors = sorted(
            Draft7Validator(schema).iter_errors(data), key=lambda e: list(e.path)
        )
        if errors:
            first = errors[0]
            where = "/".join(str(p) for p in first.path) or "<root>"
            raise AIResponseError(
                f"structured output failed schema validation at {where}: {first.message}",
                provider=provider,
            )
        return data
