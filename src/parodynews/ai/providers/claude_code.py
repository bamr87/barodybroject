"""
File: claude_code.py
Description: Default provider - Claude through the Claude Agent SDK, authenticated with a Claude Code OAuth token
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 0.6.0

Dependencies:
- claude-agent-sdk: >=0.2.152 (bundles the Claude Code CLI binary)

Usage:
    export CLAUDE_CODE_OAUTH_TOKEN="$(claude setup-token)"   # or ANTHROPIC_API_KEY
    from parodynews.ai import get_provider
    get_provider("claude_code").generate(...)

Why the Agent SDK and not the Messages API: a Claude Code OAuth token
(``claude setup-token``) is a Claude Code credential. The Agent SDK is Claude
Code packaged as a library and is the supported way to drive it
programmatically with that token, the same convention this repository already
uses in ``.github/workflows/claude.yml``. Calls that only need a plain API key
can use the ``anthropic`` provider instead.

Each generation is a single-shot ``query()`` with every built-in tool switched
off and filesystem settings disabled, so the agent behaves like a stateless
chat completion. Multi-turn threads are rendered into the prompt because the
SDK's prompt is a single user turn.
"""

from __future__ import annotations

import os
import tempfile
from typing import Any

from .._async import run_sync
from ..base import (
    AIProvider,
    ChatMessage,
    GenerationRequest,
    GenerationResult,
    ModelInfo,
)
from ..exceptions import AIConfigurationError, AIProviderError, AIResponseError

OAUTH_TOKEN_PREFIX = "sk-ant-oat"
API_KEY_PREFIX = "sk-ant-api"

# Models the Claude Code CLI accepts. The CLI also understands the aliases
# ``opus``, ``sonnet`` and ``haiku``.
STATIC_MODELS: tuple[tuple[str, str, str], ...] = (
    ("claude-opus-5", "Claude Opus 5", "Default. Best quality for long-form writing."),
    (
        "claude-sonnet-5",
        "Claude Sonnet 5",
        "Fast and capable; good for bulk generation.",
    ),
    ("claude-haiku-4-5", "Claude Haiku 4.5", "Cheapest and fastest; short outputs."),
    ("claude-opus-4-8", "Claude Opus 4.8", "Previous Opus generation."),
    ("claude-sonnet-4-6", "Claude Sonnet 4.6", "Previous Sonnet generation."),
    ("claude-fable-5-1", "Claude Fable 5.1", "Most capable model; premium pricing."),
)


def render_transcript(turns: list[ChatMessage]) -> str:
    """Fold a multi-turn conversation into the single prompt the SDK accepts."""
    if len(turns) == 1:
        return turns[0].content
    lines = ["<conversation>"]
    for turn in turns[:-1]:
        label = "User" if turn.role == "user" else "Assistant"
        lines.append(f"[{label}]\n{turn.content}\n")
    lines.append("</conversation>")
    lines.append("")
    lines.append(
        "Reply to the final user message below, keeping the conversation in mind."
    )
    lines.append("")
    lines.append(turns[-1].content)
    return "\n".join(lines)


class ClaudeCodeProvider(AIProvider):
    slug = "claude_code"
    display_name = "Claude Code (Agent SDK)"
    description = (
        "Claude via the Claude Agent SDK, authenticated with a Claude Code OAuth "
        "token from `claude setup-token`. Falls back to ANTHROPIC_API_KEY."
    )
    default_model = "claude-opus-5"
    credential_env_vars = ("CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY")
    model_env_var = "CLAUDE_CODE_MODEL"

    def static_models(self):
        return tuple(
            ModelInfo(mid, self.slug, name, desc) for mid, name, desc in STATIC_MODELS
        )

    # ---------------------------------------------------------------- options
    def credential_env(self) -> dict[str, str]:
        """Environment overrides that make the CLI use the configured credential.

        A credential stored in the database wins over the process environment.
        The variable it is exported as follows the token shape: Claude Code
        OAuth tokens start with ``sk-ant-oat``, API keys with ``sk-ant-api``.
        The competing variable is blanked so the CLI cannot pick a stale value
        from the container environment.
        """
        token = self.config.api_key
        if not token:
            return {}
        if token.startswith(API_KEY_PREFIX):
            return {"ANTHROPIC_API_KEY": token, "CLAUDE_CODE_OAUTH_TOKEN": ""}
        return {"CLAUDE_CODE_OAUTH_TOKEN": token, "ANTHROPIC_API_KEY": ""}

    def build_options(self, request: GenerationRequest) -> Any:
        """Translate a request into ``ClaudeAgentOptions``."""
        try:
            from claude_agent_sdk import ClaudeAgentOptions
        except ImportError as exc:  # pragma: no cover - depends on install
            raise AIConfigurationError(
                "claude-agent-sdk is not installed; run `pip install claude-agent-sdk`",
                provider=self.slug,
            ) from exc

        extra = self.config.extra or {}
        system, _turns = self.normalize(request)
        env = {
            # Equivalent to DISABLE_AUTOUPDATER, DISABLE_BUG_COMMAND,
            # DISABLE_ERROR_REPORTING and DISABLE_TELEMETRY.
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
            **self.credential_env(),
            **{str(k): str(v) for k, v in (extra.get("env") or {}).items()},
        }
        if self.config.base_url:
            env["ANTHROPIC_BASE_URL"] = self.config.base_url

        kwargs: dict[str, Any] = {
            "system_prompt": system,
            "model": self.resolve_model(request.model),
            # Behave like a chat completion: no built-in tools, deny anything
            # that would prompt, and never read CLAUDE.md / settings files.
            "tools": [],
            "allowed_tools": [],
            "permission_mode": "dontAsk",
            "max_turns": int(extra.get("max_turns", 3)),
            "setting_sources": [],
            "cwd": extra.get("cwd") or tempfile.gettempdir(),
            "env": env,
        }
        cli_path = extra.get("cli_path") or os.environ.get("CLAUDE_CLI_PATH", "")
        if cli_path:
            kwargs["cli_path"] = cli_path
        if extra.get("effort"):
            kwargs["effort"] = extra["effort"]
        if extra.get("max_budget_usd") is not None:
            kwargs["max_budget_usd"] = float(extra["max_budget_usd"])
        if request.json_schema is not None:
            kwargs["output_format"] = {
                "type": "json_schema",
                "schema": request.json_schema,
            }
        return ClaudeAgentOptions(**kwargs)

    # ------------------------------------------------------------- generation
    async def _collect(self, prompt: str, options: Any) -> tuple[list[str], Any]:
        from claude_agent_sdk import AssistantMessage, ResultMessage, TextBlock, query

        texts: list[str] = []
        result = None
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                texts.extend(
                    block.text
                    for block in message.content
                    if isinstance(block, TextBlock) and block.text
                )
            elif isinstance(message, ResultMessage):
                result = message
        return texts, result

    def generate(self, request: GenerationRequest) -> GenerationResult:
        options = self.build_options(request)
        _system, turns = self.normalize(request)
        prompt = render_transcript(turns)

        try:
            from claude_agent_sdk import (
                CLIConnectionError,
                CLIJSONDecodeError,
                CLINotFoundError,
                ProcessError,
            )
        except ImportError as exc:  # pragma: no cover - depends on install
            raise AIConfigurationError(
                "claude-agent-sdk is not installed", provider=self.slug
            ) from exc

        try:
            texts, result = run_sync(self._collect(prompt, options))
        except CLINotFoundError as exc:
            raise AIConfigurationError(
                f"Claude Code CLI not found: {exc}", provider=self.slug
            ) from exc
        except (CLIConnectionError, ProcessError, CLIJSONDecodeError) as exc:
            raise AIProviderError(
                f"Claude Code CLI failed: {exc}", provider=self.slug, retryable=True
            ) from exc

        if result is None:
            raise AIProviderError(
                "Claude Code CLI ended without a result message", provider=self.slug
            )
        if result.is_error or result.subtype != "success":
            detail = "; ".join(result.errors or []) or result.result or result.subtype
            raise AIProviderError(
                f"Claude Code run failed ({result.subtype}): {detail}",
                provider=self.slug,
            )

        text = result.result or "\n".join(texts)
        data: Any = None
        if request.json_schema is not None:
            data = result.structured_output
            if data is None:
                if not text.strip():
                    raise AIResponseError(
                        "run finished without structured output", provider=self.slug
                    )
                data = self.parse_structured(
                    text, request.json_schema, provider=self.slug
                )
            else:
                data = self.validate_structured(
                    data, request.json_schema, provider=self.slug
                )
            if not text.strip():
                import json

                text = json.dumps(data, indent=2)

        usage_raw = result.usage or {}
        usage = {
            "input_tokens": usage_raw.get("input_tokens", 0),
            "output_tokens": usage_raw.get("output_tokens", 0),
            "cache_read_input_tokens": usage_raw.get("cache_read_input_tokens", 0),
            "cache_creation_input_tokens": usage_raw.get(
                "cache_creation_input_tokens", 0
            ),
            "cost_usd": result.total_cost_usd,
            "num_turns": result.num_turns,
            "duration_ms": result.duration_ms,
        }
        model_used = options.model or ""
        if result.model_usage:
            model_used = next(iter(result.model_usage), model_used)

        return GenerationResult(
            text=text,
            data=data,
            provider=self.slug,
            model=model_used,
            usage=usage,
            remote_id=result.session_id or "",
            stop_reason=result.stop_reason or "",
            raw=result,
        )
