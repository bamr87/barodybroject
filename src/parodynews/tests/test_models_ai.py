"""
File: test_models_ai.py
Description: Unit tests for parodynews.models.ai — JSONSchema, AIModel, Assistant, AssistantGroup, AssistantGroupMembership
Author: Barodybroject Team <team@example.com>
Created: 2026-09-11
Last Modified: 2026-09-14
Version: 2.0.0

Dependencies:
- django
- pytest-django

Usage: python -m pytest parodynews/tests/test_models_ai.py (run from src/)
"""

import json

import pytest
from django.db import IntegrityError, transaction

from parodynews.models import (
    AIModel,
    Assistant,
    AssistantGroup,
    AssistantGroupMembership,
    JSONSchema,
)

pytestmark = pytest.mark.django_db


# --------------------------------------------------------------------------- #
# JSONSchema
# --------------------------------------------------------------------------- #
def test_json_schema_round_trips_a_real_export(json_schema, json_schema_export):
    stored = JSONSchema.objects.get(pk=json_schema.pk)
    assert stored.name == json_schema_export[0]["name"]
    # The export stores the schema as a STRING; the field is a JSONField, so a
    # dict must come back out — not the string that went into the export file.
    assert isinstance(stored.schema, dict)
    assert stored.schema == json.loads(json_schema_export[0]["schema"])


def test_json_schema_str_is_the_name(json_schema):
    assert str(json_schema) == json_schema.name


def test_json_schema_survives_a_nested_structure():
    schema = JSONSchema.objects.create(
        name="article_schema",
        description="Schema for news articles",
        schema={
            "type": "object",
            "properties": {"title": {"type": "string"}},
            "required": ["title"],
        },
    )
    assert JSONSchema.objects.get(pk=schema.pk).schema["required"] == ["title"]


# --------------------------------------------------------------------------- #
# AIModel — the provider-agnostic replacement for OpenAIModel
# --------------------------------------------------------------------------- #
def test_ai_model_round_trips(ai_model):
    stored = AIModel.objects.get(pk=ai_model.pk)
    assert (stored.provider, stored.model_id) == ("mock", "mock-1")
    assert stored.is_active is True


def test_ai_model_str_is_the_model_id(ai_model):
    assert str(ai_model) == "mock-1"


def test_ai_model_label_names_the_provider(ai_model):
    """The picker shows both halves: the same model id can exist twice."""
    assert ai_model.label == "mock: Mock model"


def test_ai_model_stamps_both_timestamps(ai_model):
    assert ai_model.created_at is not None
    assert ai_model.updated_at is not None


def test_the_same_model_id_may_exist_for_two_providers():
    """`claude-opus-5` is reachable through both claude_code and anthropic, so
    uniqueness is on the PAIR, not on model_id alone."""
    AIModel.objects.create(provider="claude_code", model_id="claude-opus-5")
    AIModel.objects.create(provider="anthropic", model_id="claude-opus-5")
    assert AIModel.objects.filter(model_id="claude-opus-5").count() == 2


def test_a_model_id_is_unique_within_one_provider():
    AIModel.objects.create(provider="openai", model_id="gpt-4o-mini")
    with pytest.raises(IntegrityError), transaction.atomic():
        AIModel.objects.create(provider="openai", model_id="gpt-4o-mini")


def test_ai_models_are_ordered_by_provider_then_model_id():
    AIModel.objects.create(provider="openai", model_id="gpt-4o")
    AIModel.objects.create(provider="anthropic", model_id="claude-sonnet-5")
    AIModel.objects.create(provider="anthropic", model_id="claude-opus-5")
    assert list(AIModel.objects.values_list("provider", "model_id")) == [
        ("anthropic", "claude-opus-5"),
        ("anthropic", "claude-sonnet-5"),
        ("openai", "gpt-4o"),
    ]


# --------------------------------------------------------------------------- #
# Assistant
# --------------------------------------------------------------------------- #
def test_assistant_round_trips_a_real_export(assistant, assistant_export):
    stored = Assistant.objects.get(pk=assistant.pk)
    assert stored.pk == assistant_export[0]["id"]
    assert stored.name == assistant_export[0]["name"]
    assert stored.instructions == assistant_export[0]["instructions"]


def test_assistant_str_is_the_name(assistant):
    assert str(assistant) == assistant.name


def test_assistant_display_fields(assistant):
    assert assistant.get_display_fields() == [
        "name",
        "description",
        "model",
        "json_schema",
    ]


def test_assistant_mints_its_own_id():
    """Ids used to come from the OpenAI Assistants API. They are now local, so
    saving without one must still produce a usable primary key."""
    created = Assistant.objects.create(name="Local")
    assert created.pk.startswith("asst_")
    assert Assistant.objects.filter(pk=created.pk).exists()


def test_assistant_keeps_an_id_it_was_given(assistant, assistant_export):
    """Rows imported from the old OpenAI export keep their original id."""
    assert assistant.pk == assistant_export[0]["id"]
    assert assistant.pk.startswith("asst_")


def test_assistant_provider_follows_its_model(assistant, ai_model):
    assert assistant.provider == ai_model.provider == "mock"


def test_assistant_without_a_model_has_no_provider():
    """An assistant with no model runs on the application default, so it can
    name no provider of its own."""
    assert Assistant.objects.create(name="Default runner").provider == ""


def test_assistant_defaults():
    bare = Assistant.objects.create(id="asst_defaults")
    assert bare.name == "system default"
    assert bare.description == "Describe the assistant."
    assert bare.object == "assistant"
    assert bare.instructions == "you are a helpful assistant."
    assert bare.tools == []
    assert bare.metadata == {}
    assert bare.response_format == {}
    assert bare.remote_id == ""


def test_assistant_links_to_its_model_and_schema(assistant, ai_model, json_schema):
    stored = Assistant.objects.get(pk=assistant.pk)
    assert stored.model == ai_model
    assert stored.json_schema == json_schema


def test_deleting_the_model_nulls_the_assistant(assistant, ai_model):
    """SET_NULL, not CASCADE: retiring a model must not delete the assistants
    configured against it."""
    ai_model.delete()
    assistant.refresh_from_db()
    assert assistant.model is None
    assert Assistant.objects.filter(pk=assistant.pk).exists()


def test_deleting_the_json_schema_nulls_the_assistant(assistant, json_schema):
    json_schema.delete()
    assistant.refresh_from_db()
    assert assistant.json_schema is None
    assert Assistant.objects.filter(pk=assistant.pk).exists()


def test_assistants_are_ordered_by_name():
    Assistant.objects.create(id="asst_b", name="Zed")
    Assistant.objects.create(id="asst_a", name="Alice")
    assert list(Assistant.objects.values_list("name", flat=True)) == ["Alice", "Zed"]


# --------------------------------------------------------------------------- #
# AssistantGroup
# --------------------------------------------------------------------------- #
def test_assistant_group_str_is_the_name(assistant_group):
    assert str(assistant_group) == "Content Pipeline"


def test_assistant_group_display_fields(assistant_group):
    assert assistant_group.get_display_fields() == [
        "name",
        "sequence",
        "is_active",
        "priority",
    ]


def test_assistant_group_defaults(assistant_group):
    assert assistant_group.group_type == "default"
    assert assistant_group.sequence == 0
    assert assistant_group.is_active is True
    assert assistant_group.priority == 0
    assert assistant_group.created_at is not None


def test_assistant_groups_are_ordered_by_sequence_then_name():
    AssistantGroup.objects.create(name="Beta", sequence=2)
    AssistantGroup.objects.create(name="Zulu", sequence=1)
    AssistantGroup.objects.create(name="Alpha", sequence=1)
    assert list(AssistantGroup.objects.values_list("name", flat=True)) == [
        "Alpha",
        "Zulu",
        "Beta",
    ]


def test_ordered_assistants_follows_position(assistant_group, assistant, ai_model):
    second = Assistant.objects.create(id="asst_second", name="Writer", model=ai_model)
    AssistantGroupMembership.objects.create(
        assistantgroup=assistant_group, assistant=second, position=2
    )
    AssistantGroupMembership.objects.create(
        assistantgroup=assistant_group, assistant=assistant, position=1
    )
    assert assistant_group.ordered_assistants() == [assistant, second]


def test_ordered_assistants_skips_an_orphaned_membership(
    assistant_group, assistant, membership
):
    """Both FKs are SET_NULL, so a membership can outlive its assistant. The
    runner iterates this list, so a None would crash a group run."""
    assistant.delete()
    assert assistant_group.ordered_assistants() == []


# --------------------------------------------------------------------------- #
# AssistantGroupMembership — the through model
# --------------------------------------------------------------------------- #
def test_membership_joins_a_group_and_an_assistant(
    membership, assistant_group, assistant
):
    stored = AssistantGroupMembership.objects.get(pk=membership.pk)
    assert stored.assistantgroup == assistant_group
    assert stored.assistant == assistant
    assert stored.position == 1


def test_membership_str_names_both_sides_and_the_position(membership):
    assert str(membership) == "parody maker in Content Pipeline at position 1"


def test_membership_str_tolerates_both_sides_being_null():
    """Both FKs are SET_NULL, so an orphaned membership must still render."""
    orphan = AssistantGroupMembership.objects.create(position=3)
    assert str(orphan) == "Unknown in Unknown at position 3"


def test_the_group_reaches_its_assistants_through_the_membership(
    membership, assistant_group, assistant
):
    """The point of the through model: `AssistantGroup.assistants` resolves."""
    assert list(assistant_group.assistants.all()) == [assistant]


def test_memberships_are_ordered_by_position(assistant_group, assistant):
    second = Assistant.objects.create(id="asst_second", name="Writer")
    AssistantGroupMembership.objects.create(
        assistantgroup=assistant_group, assistant=second, position=2
    )
    AssistantGroupMembership.objects.create(
        assistantgroup=assistant_group, assistant=assistant, position=1
    )
    positions = list(
        AssistantGroupMembership.objects.values_list("position", flat=True)
    )
    assert positions == [1, 2]


def test_deleting_the_assistant_keeps_the_membership_row(membership, assistant):
    """SET_NULL on both FKs: the join row outlives either side. Asserted so the
    `str()` fallback above is covering a state that can really occur."""
    assistant.delete()
    membership.refresh_from_db()
    assert membership.assistant is None
    assert AssistantGroupMembership.objects.filter(pk=membership.pk).exists()


def test_deleting_the_group_keeps_the_membership_row(membership, assistant_group):
    assistant_group.delete()
    membership.refresh_from_db()
    assert membership.assistantgroup is None
    assert AssistantGroupMembership.objects.filter(pk=membership.pk).exists()
