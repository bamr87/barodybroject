"""
File: test_models_ai.py
Description: Unit tests for parodynews.models.ai — JSONSchema, OpenAIModel, Assistant, AssistantGroup, AssistantGroupMembership
Author: Barodybroject Team <team@example.com>
Created: 2026-09-11
Version: 1.0.0

Dependencies:
- django
- pytest-django

Usage: python -m pytest parodynews/tests/test_models_ai.py (run from src/)
"""

import json

import pytest
from django.db import IntegrityError, transaction

from parodynews.models import (
    Assistant,
    AssistantGroup,
    AssistantGroupMembership,
    JSONSchema,
    OpenAIModel,
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
# OpenAIModel
# --------------------------------------------------------------------------- #
def test_openai_model_round_trips_a_real_export(openai_model, openai_model_export):
    stored = OpenAIModel.objects.get(pk=openai_model.pk)
    assert stored.model_id == openai_model_export[0]["model_id"]


def test_openai_model_str_is_the_model_id(openai_model):
    assert str(openai_model) == openai_model.model_id


def test_openai_model_stamps_both_timestamps(openai_model):
    """`auto_now_add` / `auto_now` — no concrete model inherits TimestampedModel,
    so these columns are declared on OpenAIModel itself."""
    assert openai_model.created_at is not None
    assert openai_model.updated_at is not None


def test_model_id_is_unique():
    OpenAIModel.objects.create(model_id="gpt-4", description="")
    with pytest.raises(IntegrityError), transaction.atomic():
        OpenAIModel.objects.create(model_id="gpt-4", description="other")


def test_openai_models_are_ordered_by_model_id():
    OpenAIModel.objects.create(model_id="gpt-4o", description="")
    OpenAIModel.objects.create(model_id="gpt-3.5-turbo", description="")
    assert list(OpenAIModel.objects.values_list("model_id", flat=True)) == [
        "gpt-3.5-turbo",
        "gpt-4o",
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


def test_assistant_primary_key_is_the_openai_id(assistant):
    """Not an AutoField — the OpenAI assistant id IS the primary key, which is
    what lets a local row be matched to a remote assistant."""
    assert Assistant._meta.pk.name == "id"
    assert assistant.pk.startswith("asst_")


def test_assistant_defaults():
    bare = Assistant.objects.create(id="asst_defaults")
    assert bare.name == "system default"
    assert bare.description == "Describe the assistant."
    assert bare.object == "assistant"
    assert bare.instructions == "you are a helpful assistant."
    assert bare.tools == []
    assert bare.metadata == {}
    assert bare.response_format == {}


def test_assistant_links_to_its_model_and_schema(assistant, openai_model, json_schema):
    stored = Assistant.objects.get(pk=assistant.pk)
    assert stored.model == openai_model
    assert stored.json_schema == json_schema


def test_deleting_the_openai_model_nulls_the_assistant(assistant, openai_model):
    """SET_NULL, not CASCADE: retiring a model must not delete the assistants
    configured against it."""
    openai_model.delete()
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


# --------------------------------------------------------------------------- #
# AssistantGroupMembership — the through model
# --------------------------------------------------------------------------- #
@pytest.fixture
def membership(db, assistant_group, assistant) -> AssistantGroupMembership:
    # The FK is `assistants` (plural) with `db_column="assistants_id"`; the
    # docstrings say `assistant`. The field name is the one that exists.
    return AssistantGroupMembership.objects.create(
        assistantgroup=assistant_group, assistants=assistant, position=1
    )


def test_membership_joins_a_group_and_an_assistant(
    membership, assistant_group, assistant
):
    stored = AssistantGroupMembership.objects.get(pk=membership.pk)
    assert stored.assistantgroup == assistant_group
    assert stored.assistants == assistant
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
        assistantgroup=assistant_group, assistants=second, position=2
    )
    AssistantGroupMembership.objects.create(
        assistantgroup=assistant_group, assistants=assistant, position=1
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
    assert membership.assistants is None
    assert AssistantGroupMembership.objects.filter(pk=membership.pk).exists()


def test_deleting_the_group_keeps_the_membership_row(membership, assistant_group):
    assistant_group.delete()
    membership.refresh_from_db()
    assert membership.assistantgroup is None
    assert AssistantGroupMembership.objects.filter(pk=membership.pk).exists()
