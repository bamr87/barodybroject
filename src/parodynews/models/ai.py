"""
File: ai.py
Description: Provider-agnostic AI models (model catalogue, assistants, schemas, groups)
Author: Barodybroject Team <team@example.com>
Created: 2025-11-30
Last Modified: 2026-09-14
Version: 0.6.0

Dependencies:
- django: >=5.1

Usage: from parodynews.models.ai import Assistant, AIModel
"""

from django.db import models
from django.utils import timezone

from .base import generate_prefixed_id


class JSONSchema(models.Model):
    """JSON schema definitions for structured data validation.

    Stores JSON Schema specifications used to validate and structure AI-generated
    content. These schemas can be attached to assistants to ensure consistent
    output formats regardless of which provider generates the content.

    Attributes:
        name (str): Unique identifier for the schema (max 255 chars)
        description (str): Human-readable description of schema purpose
        schema (dict): JSON Schema specification following JSON Schema standard

    See Also:
        https://json-schema.org/ for JSON Schema specification
    """

    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    schema = models.JSONField()

    class Meta:
        app_label = "parodynews"
        verbose_name = "JSON Schema"
        verbose_name_plural = "JSON Schemas"

    def __str__(self):
        return self.name


class AIModel(models.Model):
    """A model offered by an AI provider.

    Replaces the OpenAI-only ``OpenAIModel``. A row is identified by the pair
    ``(provider, model_id)``: ``claude-opus-5`` can exist for both the
    ``claude_code`` and the ``anthropic`` provider, and ``gpt-4o-mini`` for
    ``openai``. Rows are created from the settings UI ("Sync models"), by the
    ``sync_models`` management command, or by hand in the admin.

    Attributes:
        provider (str): Provider slug from ``parodynews.ai`` (``claude_code``,
            ``anthropic``, ``openai``, ``mock``)
        model_id (str): The provider's model identifier
        display_name (str): Optional friendly name
        description (str): Free-text notes
        is_active (bool): Hidden from pickers when False
    """

    provider = models.CharField(max_length=50, default="claude_code", db_index=True)
    model_id = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "parodynews"
        verbose_name = "AI Model"
        verbose_name_plural = "AI Models"
        ordering = ["provider", "model_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "model_id"],
                name="parodynews_aimodel_provider_model",
            )
        ]

    def __str__(self):
        return self.model_id

    @property
    def label(self) -> str:
        return f"{self.provider}: {self.display_name or self.model_id}"


class Assistant(models.Model):
    """AI assistant configuration for content generation.

    An assistant is a named set of instructions plus the model that should
    run them and, optionally, a JSON schema its output must follow. It is
    stored locally and is independent of any provider: the same assistant can
    be pointed at a Claude model today and an OpenAI model tomorrow by
    changing ``model``.

    Attributes:
        id (str): Locally generated primary key (``asst_...``). Rows imported
            from the OpenAI Assistants API keep their original id.
        name / description / instructions / prompt: Persona definition
        model (AIModel): Model to run; ``None`` means the provider default
        remote_id (str): Identifier in a provider that persists assistants
            (unused by the built-in providers; kept for extensions)
        json_schema (JSONSchema): Optional structured-output schema
        temperature / top_p: Sampling hints, applied where the model allows
        tools / metadata / response_format: Free-form provider extras
    """

    id = models.CharField(max_length=225, blank=True, primary_key=True)
    # `blank=True` without `null=True`: an unset name is "", never NULL, so
    # callers have one empty value to check rather than two.
    name = models.CharField(max_length=256, blank=True, default="system default")
    description = models.CharField(
        max_length=512, blank=True, default="Describe the assistant."
    )
    instructions = models.TextField(
        max_length=256000, default="you are a helpful assistant."
    )
    prompt = models.TextField(max_length=256000, default="you are a helpful assistant.")
    object = models.CharField(max_length=50, default="assistant")
    model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, blank=True)
    remote_id = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)
    tools = models.JSONField(default=list, null=True, blank=True)
    metadata = models.JSONField(default=dict, null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    top_p = models.FloatField(null=True, blank=True)
    response_format = models.JSONField(default=dict, null=True, blank=True)
    json_schema = models.ForeignKey(
        JSONSchema, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        app_label = "parodynews"
        verbose_name = "Assistant"
        verbose_name_plural = "Assistants"
        ordering = ["name"]

    def __str__(self):
        return self.name or self.id

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_prefixed_id("asst")
        super().save(*args, **kwargs)

    @property
    def provider(self) -> str:
        """Provider slug of the configured model, or ``""`` for the default."""
        return self.model.provider if self.model_id else ""

    def get_display_fields(self):
        return ["name", "description", "model", "json_schema"]


class AssistantGroup(models.Model):
    """Group of assistants for workflow orchestration.

    Organizes multiple assistants into a sequential pipeline: running a group
    on a thread runs each member in ``position`` order, and every member sees
    the output of the members before it.

    Attributes:
        name (str): Human-readable name for the group (max 256 chars)
        assistants (ManyToMany): Assistants in this group (through AssistantGroupMembership)
        group_type (str): Type classification (default: 'default', max 100 chars)
        sequence (int): Execution sequence number (default: 0)
        is_active (bool): Whether this group is currently active (default: True)
        priority (int): Priority level for conflict resolution (default: 0)
        created_at (datetime): Timestamp when group was created
    """

    name = models.CharField(max_length=256)
    assistants = models.ManyToManyField(
        Assistant,
        through="AssistantGroupMembership",
        related_name="assistant_groups",
    )
    group_type = models.CharField(max_length=100, default="default")
    sequence = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = "parodynews"
        verbose_name = "Assistant Group"
        verbose_name_plural = "Assistant Groups"
        ordering = ["sequence", "name"]

    def __str__(self):
        return self.name

    def get_display_fields(self):
        return ["name", "sequence", "is_active", "priority"]

    def ordered_assistants(self):
        """Assistants in execution order, skipping memberships whose assistant was deleted."""
        return [
            membership.assistant
            for membership in self.assistantgroupmembership_set.select_related(
                "assistant", "assistant__model"
            ).order_by("position", "id")
            if membership.assistant is not None
        ]


class AssistantGroupMembership(models.Model):
    """Many-to-many relationship for assistants in groups with positional ordering."""

    id = models.AutoField(primary_key=True)
    assistantgroup = models.ForeignKey(
        "AssistantGroup", on_delete=models.SET_NULL, null=True
    )
    assistant = models.ForeignKey("Assistant", on_delete=models.SET_NULL, null=True)
    position = models.PositiveIntegerField()

    class Meta:
        app_label = "parodynews"
        verbose_name = "Assistant Group Membership"
        verbose_name_plural = "Assistant Group Memberships"
        ordering = ["position"]

    def __str__(self):
        assistant_name = self.assistant.name if self.assistant else "Unknown"
        group_name = self.assistantgroup.name if self.assistantgroup else "Unknown"
        return f"{assistant_name} in {group_name} at position {self.position}"
