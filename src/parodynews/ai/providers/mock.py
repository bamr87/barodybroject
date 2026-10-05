"""
File: mock.py
Description: Deterministic offline provider used by the test suite and demos
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 0.6.0

Usage:
    AI_DEFAULT_PROVIDER=mock  # settings.testing does this

    from parodynews.ai.providers.mock import MockProvider
    MockProvider.reset()
    MockProvider.queue_response("scripted text")   # optional
    ... exercise code ...
    assert MockProvider.calls[0].last_user_text() == "..."
"""

from __future__ import annotations

import json
from collections import deque
from typing import Any, ClassVar

from ..base import AIProvider, GenerationRequest, GenerationResult, ModelInfo
from ..schema_stub import build_example


class MockProvider(AIProvider):
    """Never touches the network.

    Structured requests get a schema-valid stub document built by
    :func:`parodynews.ai.schema_stub.build_example`; plain requests get a
    short deterministic sentence. Requests are recorded on the class so tests
    can assert on what the application sent, and canned responses can be
    queued to script specific outputs.
    """

    slug = "mock"
    display_name = "Mock (offline)"
    description = "Deterministic stand-in that needs no credentials. Used by tests."
    default_model = "mock-1"
    model_env_var = "MOCK_MODEL"

    calls: ClassVar[list[GenerationRequest]] = []
    _queued: ClassVar[deque[Any]] = deque()

    @classmethod
    def reset(cls) -> None:
        cls.calls.clear()
        cls._queued.clear()

    @classmethod
    def queue_response(cls, response: Any) -> None:
        """Script the next call. A ``str`` is returned as text; a ``dict``
        or ``list`` is returned as structured data (and serialized to text);
        an ``Exception`` instance is raised."""
        cls._queued.append(response)

    def is_configured(self) -> bool:
        return True

    def credential_source(self) -> str:
        # Nothing to configure, but the settings UI shows this next to a
        # "configured" badge, so say why rather than leaving it blank.
        return "no credential required"

    def static_models(self):
        return (
            ModelInfo("mock-1", self.slug, "Mock model", "Returns canned output."),
            ModelInfo(
                "mock-fast", self.slug, "Mock (fast)", "Same output, same speed."
            ),
        )

    def generate(self, request: GenerationRequest) -> GenerationResult:
        type(self).calls.append(request)
        system, turns = self.normalize(request)
        model = self.resolve_model(request.model)
        prompt_text = turns[-1].content

        scripted = type(self)._queued.popleft() if type(self)._queued else None
        if isinstance(scripted, Exception):
            raise scripted

        data: Any = None
        if request.json_schema is not None:
            if isinstance(scripted, (dict, list)):
                data = scripted
            elif isinstance(scripted, str):
                data = self.parse_structured(
                    scripted, request.json_schema, provider=self.slug
                )
            else:
                data = build_example(request.json_schema, seed=prompt_text)
            data = self.validate_structured(
                data, request.json_schema, provider=self.slug
            )
            text = json.dumps(data, indent=2)
        elif isinstance(scripted, str):
            text = scripted
        elif isinstance(scripted, (dict, list)):
            text = json.dumps(scripted, indent=2)
            data = scripted
        else:
            text = f"Mock response from {model} to: {prompt_text[:200]}"

        usage = {
            "input_tokens": len(
                (system + " " + " ".join(t.content for t in turns)).split()
            ),
            "output_tokens": len(text.split()),
            "cost_usd": 0.0,
        }
        return GenerationResult(
            text=text,
            data=data,
            provider=self.slug,
            model=model,
            usage=usage,
            stop_reason="end_turn",
        )
