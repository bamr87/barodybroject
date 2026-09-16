"""
File: test_ai_layer.py
Description: Unit tests for parodynews.ai — the provider contract, registry, and each built-in provider
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 1.0.0

Dependencies:
- django
- pytest-django

Usage: python -m pytest parodynews/tests/test_ai_layer.py (run from src/)

No test here reaches the network: the mock provider answers locally, and the
three real providers are exercised through the request they would send rather
than the response they would get.
"""

import pytest
from django.test import override_settings

from parodynews.ai import (
    AIConfigurationError,
    AIProvider,
    AIResponseError,
    ChatMessage,
    GenerationRequest,
    ModelInfo,
    ProviderConfig,
    available_providers,
    describe_providers,
    get_default_provider_slug,
    get_provider,
    get_provider_class,
)
from parodynews.ai.base import CONTINUATION_PROMPT
from parodynews.ai.providers.anthropic import AnthropicProvider
from parodynews.ai.providers.claude_code import ClaudeCodeProvider, render_transcript
from parodynews.ai.providers.mock import MockProvider
from parodynews.ai.providers.openai import OpenAIProvider
from parodynews.ai.registry import clear_cache
from parodynews.ai.schema_stub import build_example
from parodynews.models import AIProviderConfig
from parodynews.utils.schemas import get_schema, load_schemas

SIMPLE_SCHEMA = {
    "type": "object",
    "properties": {"headline": {"type": "string"}, "score": {"type": "integer"}},
    "required": ["headline", "score"],
    "additionalProperties": False,
}


def request_with(**kwargs) -> GenerationRequest:
    kwargs.setdefault("messages", [ChatMessage("user", "Write something.")])
    return GenerationRequest(**kwargs)


# --------------------------------------------------------------------------- #
# ChatMessage / GenerationRequest
# --------------------------------------------------------------------------- #
def test_chat_message_rejects_an_unknown_role():
    with pytest.raises(ValueError):
        ChatMessage("narrator", "hello")


def test_request_reports_whether_it_wants_structured_output():
    assert request_with().wants_structured_output is False
    assert request_with(json_schema=SIMPLE_SCHEMA).wants_structured_output is True


def test_last_user_text_finds_the_most_recent_user_turn():
    request = request_with(
        messages=[
            ChatMessage("user", "first"),
            ChatMessage("assistant", "reply"),
            ChatMessage("user", "second"),
        ]
    )
    assert request.last_user_text() == "second"


# --------------------------------------------------------------------------- #
# AIProvider.normalize — the shape every vendor accepts
# --------------------------------------------------------------------------- #
def test_normalize_folds_system_turns_into_the_system_prompt():
    system, turns = AIProvider.normalize(
        request_with(
            system="Base instructions.",
            messages=[ChatMessage("system", "Extra rule."), ChatMessage("user", "Go.")],
        )
    )
    assert system == "Base instructions.\n\nExtra rule."
    assert [t.role for t in turns] == ["user"]


def test_normalize_appends_a_user_turn_when_history_ends_with_the_assistant():
    """Assistant prefill is rejected by current Claude models, and an assistant
    group runs each member over the previous member's output — so the last turn
    has to be a user turn."""
    _system, turns = AIProvider.normalize(
        request_with(
            messages=[
                ChatMessage("user", "Draft it."),
                ChatMessage("assistant", "Draft."),
            ]
        )
    )
    assert turns[-1].role == "user"
    assert turns[-1].content == CONTINUATION_PROMPT


def test_normalize_inserts_a_user_turn_when_history_starts_with_the_assistant():
    _system, turns = AIProvider.normalize(
        request_with(
            messages=[
                ChatMessage("assistant", "Opening line."),
                ChatMessage("user", "Go"),
            ]
        )
    )
    assert turns[0].role == "user"


def test_normalize_rejects_a_request_with_no_turns():
    with pytest.raises(AIResponseError):
        AIProvider.normalize(
            request_with(messages=[ChatMessage("system", "only system")])
        )


def test_normalize_leaves_a_well_formed_conversation_alone():
    _system, turns = AIProvider.normalize(
        request_with(
            messages=[
                ChatMessage("user", "a"),
                ChatMessage("assistant", "b"),
                ChatMessage("user", "c"),
            ]
        )
    )
    assert [t.content for t in turns] == ["a", "b", "c"]


# --------------------------------------------------------------------------- #
# Structured output parsing
# --------------------------------------------------------------------------- #
def test_parse_structured_accepts_plain_json():
    assert AIProvider.parse_structured(
        '{"headline": "hi", "score": 1}', SIMPLE_SCHEMA
    ) == {
        "headline": "hi",
        "score": 1,
    }


def test_parse_structured_tolerates_a_markdown_code_fence():
    """Models add a fence even when asked for bare JSON; failing on that would
    throw away a perfectly good response."""
    fenced = '```json\n{"headline": "hi", "score": 1}\n```'
    assert AIProvider.parse_structured(fenced, SIMPLE_SCHEMA)["headline"] == "hi"


def test_parse_structured_rejects_invalid_json():
    with pytest.raises(AIResponseError, match="valid JSON"):
        AIProvider.parse_structured("not json at all", SIMPLE_SCHEMA)


def test_parse_structured_rejects_json_that_breaks_the_schema():
    with pytest.raises(AIResponseError, match="schema validation"):
        AIProvider.parse_structured('{"headline": "hi"}', SIMPLE_SCHEMA)


def test_schema_validation_names_the_offending_field():
    with pytest.raises(AIResponseError, match="score"):
        AIProvider.parse_structured(
            '{"headline": "hi", "score": "not a number"}', SIMPLE_SCHEMA
        )


# --------------------------------------------------------------------------- #
# schema_stub — the mock provider's offline article generator
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", sorted(load_schemas()))
def test_the_stub_satisfies_every_bundled_schema(name):
    """The mock provider's output goes through the same jsonschema validation
    as a real provider's, so a stub that drifted would fail the whole suite."""
    from jsonschema import Draft7Validator

    schema = get_schema(name)
    example = build_example(schema, seed="Cats declare independence")
    assert list(Draft7Validator(schema).iter_errors(example)) == []


def test_the_stub_honours_enum_and_default():
    assert build_example({"enum": ["a", "b"]}) == "a"
    assert build_example({"type": "string", "default": "fixed"}) == "fixed"


def test_the_stub_flattens_a_multiline_seed_into_a_heading():
    """The seed is whatever prompt or article text was passed in, which may be
    multi-line Markdown; a title with newlines in it looks broken in the UI."""
    value = build_example(
        {"type": "string"}, key="title", seed="# Heading\n\nBody text"
    )
    assert "\n" not in value
    assert "#" not in value


# --------------------------------------------------------------------------- #
# Registry
# --------------------------------------------------------------------------- #
def test_the_four_built_in_providers_are_registered():
    assert set(available_providers()) == {"claude_code", "anthropic", "openai", "mock"}


def test_get_provider_class_returns_the_right_class():
    assert get_provider_class("claude_code") is ClaudeCodeProvider
    assert get_provider_class("anthropic") is AnthropicProvider
    assert get_provider_class("openai") is OpenAIProvider
    assert get_provider_class("mock") is MockProvider


def test_an_unknown_slug_is_a_configuration_error():
    with pytest.raises(AIConfigurationError, match="unknown AI provider"):
        get_provider_class("gpt-9000")


@override_settings(AI_DEFAULT_PROVIDER="anthropic")
def test_the_settings_default_applies_without_a_database_row(db):
    assert get_default_provider_slug() == "anthropic"


def test_a_default_provider_row_beats_the_settings_default(db):
    """An operator switching providers in the UI must not need a redeploy."""
    AIProviderConfig.objects.create(provider="openai", is_default=True)
    assert get_default_provider_slug() == "openai"


def test_a_disabled_default_row_is_ignored(db):
    AIProviderConfig.objects.create(
        provider="openai", is_default=True, is_enabled=False
    )
    # settings.testing pins the default to mock.
    assert get_default_provider_slug() == "mock"


@override_settings(AI_DEFAULT_PROVIDER="not-a-provider")
def test_an_unusable_settings_default_falls_back_to_claude_code(db):
    """A typo in configuration must not take the whole app down."""
    assert get_default_provider_slug() == "claude_code"


def test_get_provider_reads_credentials_from_the_database(db):
    AIProviderConfig.objects.create(
        provider="anthropic", api_key="sk-ant-api-db", default_model="claude-sonnet-5"
    )
    provider = get_provider("anthropic")
    assert provider.credential() == "sk-ant-api-db"
    assert provider.credential_source() == "database"
    assert provider.model == "claude-sonnet-5"


def test_a_database_credential_beats_the_environment(db, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-api-env")
    AIProviderConfig.objects.create(provider="anthropic", api_key="sk-ant-api-db")
    assert get_provider("anthropic").credential() == "sk-ant-api-db"


def test_the_environment_is_used_when_no_row_stores_a_key(db, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-api-env")
    provider = get_provider("anthropic")
    assert provider.credential() == "sk-ant-api-env"
    assert provider.credential_source() == "ANTHROPIC_API_KEY"


def test_a_disabled_provider_cannot_be_used(db):
    AIProviderConfig.objects.create(provider="openai", is_enabled=False)
    with pytest.raises(AIConfigurationError, match="disabled"):
        get_provider("openai")


def test_a_disabled_provider_can_still_be_inspected(db):
    """The settings screen lists disabled providers so they can be re-enabled."""
    AIProviderConfig.objects.create(provider="openai", is_enabled=False)
    assert get_provider("openai", require_enabled=False).slug == "openai"


def test_describe_providers_puts_the_default_first(db):
    summaries = describe_providers()
    assert summaries[0]["slug"] == get_default_provider_slug()
    assert {s["slug"] for s in summaries} == set(available_providers())


def test_a_deployment_can_register_its_own_provider(db):
    with override_settings(
        AI_PROVIDERS={"house": "parodynews.ai.providers.mock.MockProvider"}
    ):
        clear_cache()
        try:
            assert "house" in available_providers()
            assert get_provider_class("house") is MockProvider
        finally:
            clear_cache()


# --------------------------------------------------------------------------- #
# MockProvider
# --------------------------------------------------------------------------- #
def test_mock_needs_no_credential():
    assert MockProvider().is_configured() is True


def test_mock_records_what_it_was_asked(mock_provider):
    MockProvider().generate(request_with(messages=[ChatMessage("user", "the prompt")]))
    assert mock_provider.calls[0].last_user_text() == "the prompt"


def test_mock_returns_schema_valid_structured_output():
    result = MockProvider().generate(request_with(json_schema=SIMPLE_SCHEMA))
    assert set(result.data) == {"headline", "score"}
    assert isinstance(result.data["score"], int)


def test_mock_can_be_scripted_with_a_canned_response():
    MockProvider.queue_response("exactly this")
    assert MockProvider().generate(request_with()).text == "exactly this"


def test_mock_can_be_scripted_to_raise():
    from parodynews.ai import AIProviderError

    MockProvider.queue_response(AIProviderError("provider is down", provider="mock"))
    with pytest.raises(AIProviderError, match="down"):
        MockProvider().generate(request_with())


def test_mock_validates_a_scripted_structured_response():
    """Scripting must not be a way to smuggle invalid output past validation."""
    MockProvider.queue_response({"headline": "hi"})  # missing `score`
    with pytest.raises(AIResponseError):
        MockProvider().generate(request_with(json_schema=SIMPLE_SCHEMA))


def test_mock_health_check_round_trips():
    assert MockProvider().health_check()["ok"] is True


# --------------------------------------------------------------------------- #
# ClaudeCodeProvider — the default
# --------------------------------------------------------------------------- #
def test_claude_code_is_the_project_default():
    from parodynews.ai.registry import FALLBACK_DEFAULT_PROVIDER

    assert FALLBACK_DEFAULT_PROVIDER == "claude_code"


def test_claude_code_prefers_the_oauth_token(monkeypatch):
    monkeypatch.setenv("CLAUDE_CODE_OAUTH_TOKEN", "sk-ant-oat01-token")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-api-key")
    assert ClaudeCodeProvider().credential() == "sk-ant-oat01-token"


def test_claude_code_falls_back_to_the_api_key(monkeypatch):
    monkeypatch.delenv("CLAUDE_CODE_OAUTH_TOKEN", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-api-key")
    assert ClaudeCodeProvider().credential_source() == "ANTHROPIC_API_KEY"


def test_claude_code_exports_an_oauth_token_as_the_oauth_variable():
    """The CLI reads whichever variable matches the token's shape, and the
    other one is blanked so a stale container value cannot win."""
    provider = ClaudeCodeProvider(
        ProviderConfig(slug="claude_code", api_key="sk-ant-oat01-x")
    )
    env = provider.credential_env()
    assert env["CLAUDE_CODE_OAUTH_TOKEN"] == "sk-ant-oat01-x"
    assert env["ANTHROPIC_API_KEY"] == ""


def test_claude_code_exports_an_api_key_as_the_api_key_variable():
    provider = ClaudeCodeProvider(
        ProviderConfig(slug="claude_code", api_key="sk-ant-api03-x")
    )
    env = provider.credential_env()
    assert env["ANTHROPIC_API_KEY"] == "sk-ant-api03-x"
    assert env["CLAUDE_CODE_OAUTH_TOKEN"] == ""


def test_claude_code_runs_with_no_tools_and_no_project_settings():
    """Each generation is a stateless completion, not an agent session: no
    built-in tools, no prompting, and CLAUDE.md is never read."""
    options = ClaudeCodeProvider().build_options(request_with(system="Be terse."))
    assert options.tools == []
    assert options.allowed_tools == []
    assert options.permission_mode == "dontAsk"
    assert options.setting_sources == []
    assert options.system_prompt == "Be terse."


def test_claude_code_passes_the_schema_as_structured_output():
    options = ClaudeCodeProvider().build_options(
        request_with(json_schema=SIMPLE_SCHEMA)
    )
    assert options.output_format == {"type": "json_schema", "schema": SIMPLE_SCHEMA}


def test_claude_code_uses_the_requested_model_over_the_default():
    options = ClaudeCodeProvider().build_options(request_with(model="claude-haiku-4-5"))
    assert options.model == "claude-haiku-4-5"


def test_claude_code_default_model_is_opus_5():
    assert ClaudeCodeProvider().model == "claude-opus-5"


def test_claude_code_model_can_be_set_by_environment(monkeypatch):
    monkeypatch.setenv("CLAUDE_CODE_MODEL", "claude-sonnet-5")
    assert ClaudeCodeProvider().model == "claude-sonnet-5"


def test_claude_code_extra_options_reach_the_sdk():
    provider = ClaudeCodeProvider(
        ProviderConfig(slug="claude_code", extra={"effort": "low", "max_turns": 1})
    )
    options = provider.build_options(request_with())
    assert options.effort == "low"
    assert options.max_turns == 1


def test_render_transcript_passes_a_single_turn_through():
    assert render_transcript([ChatMessage("user", "just this")]) == "just this"


def test_render_transcript_labels_a_multi_turn_conversation():
    """The SDK's prompt is one user turn, so history is folded into the text."""
    text = render_transcript(
        [
            ChatMessage("user", "first"),
            ChatMessage("assistant", "reply"),
            ChatMessage("user", "second"),
        ]
    )
    assert "[User]\nfirst" in text
    assert "[Assistant]\nreply" in text
    assert text.rstrip().endswith("second")


# --------------------------------------------------------------------------- #
# AnthropicProvider
# --------------------------------------------------------------------------- #
def test_anthropic_builds_a_messages_request():
    kwargs = AnthropicProvider().build_kwargs(request_with(system="sys"))
    assert kwargs["model"] == "claude-opus-5"
    assert kwargs["system"] == "sys"
    assert kwargs["messages"] == [{"role": "user", "content": "Write something."}]
    assert kwargs["max_tokens"] > 0


def test_anthropic_sends_the_schema_through_output_config():
    kwargs = AnthropicProvider().build_kwargs(request_with(json_schema=SIMPLE_SCHEMA))
    assert kwargs["output_config"]["format"] == {
        "type": "json_schema",
        "schema": SIMPLE_SCHEMA,
    }


def test_anthropic_omits_temperature_on_models_that_reject_it():
    """Opus 5 and the Fable family run adaptive thinking and 400 on sampling
    parameters, so passing one through would fail the whole request."""
    kwargs = AnthropicProvider().build_kwargs(
        request_with(model="claude-opus-5", temperature=0.7)
    )
    assert "temperature" not in kwargs


def test_anthropic_keeps_temperature_on_models_that_accept_it():
    kwargs = AnthropicProvider().build_kwargs(
        request_with(model="claude-sonnet-4-6", temperature=0.7)
    )
    assert kwargs["temperature"] == 0.7


def test_anthropic_enables_refusal_fallbacks_on_opus_5():
    assert AnthropicProvider()._use_fallbacks("claude-opus-5") is True


def test_anthropic_leaves_fallbacks_off_for_other_models():
    assert AnthropicProvider()._use_fallbacks("claude-sonnet-4-6") is False


def test_anthropic_fallbacks_can_be_switched_off():
    provider = AnthropicProvider(
        ProviderConfig(slug="anthropic", extra={"server_side_fallbacks": False})
    )
    assert provider._use_fallbacks("claude-opus-5") is False


def test_anthropic_without_a_credential_is_a_configuration_error(db, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    with pytest.raises(AIConfigurationError, match="not configured"):
        AnthropicProvider().generate(request_with())


def test_anthropic_lists_static_models_without_a_credential(db, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    models = AnthropicProvider().list_models()
    assert all(isinstance(m, ModelInfo) for m in models)
    assert "claude-opus-5" in {m.id for m in models}


# --------------------------------------------------------------------------- #
# OpenAIProvider
# --------------------------------------------------------------------------- #
def test_openai_puts_the_system_prompt_in_the_message_list():
    kwargs = OpenAIProvider().build_kwargs(request_with(system="sys"))
    assert kwargs["messages"][0] == {"role": "system", "content": "sys"}


def test_openai_sends_a_strict_json_schema():
    kwargs = OpenAIProvider().build_kwargs(
        request_with(json_schema=SIMPLE_SCHEMA, schema_name="News_Article")
    )
    schema_block = kwargs["response_format"]["json_schema"]
    assert schema_block["name"] == "News_Article"
    assert schema_block["strict"] is True
    assert schema_block["schema"] == SIMPLE_SCHEMA


def test_openai_passes_temperature_through():
    kwargs = OpenAIProvider().build_kwargs(request_with(temperature=0.3))
    assert kwargs["temperature"] == 0.3


def test_openai_without_a_credential_is_a_configuration_error(db, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(AIConfigurationError, match="not configured"):
        OpenAIProvider().generate(request_with())


# --------------------------------------------------------------------------- #
# describe() — what the settings screen renders
# --------------------------------------------------------------------------- #
def test_describe_reports_configuration_state(monkeypatch):
    monkeypatch.setenv("CLAUDE_CODE_OAUTH_TOKEN", "sk-ant-oat01-x")
    info = ClaudeCodeProvider().describe()
    assert info["slug"] == "claude_code"
    assert info["configured"] is True
    assert info["credential_source"] == "CLAUDE_CODE_OAUTH_TOKEN"
    assert "CLAUDE_CODE_OAUTH_TOKEN" in info["credential_env_vars"]


def test_describe_never_leaks_the_credential(monkeypatch):
    """The settings screen shows this to any signed-in user."""
    monkeypatch.setenv("CLAUDE_CODE_OAUTH_TOKEN", "sk-ant-oat01-secret")
    assert "secret" not in str(ClaudeCodeProvider().describe())
