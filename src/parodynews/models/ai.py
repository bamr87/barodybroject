"""
File: ai.py
Description: AI/OpenAI-related Django models (assistants, schemas, model configs)
Author: Barodybroject Team <team@example.com>
Created: 2025-11-30
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- django: >=5.1

Usage: from parodynews.models.ai import Assistant
"""

from django.db import models
from django.utils import timezone


class JSONSchema(models.Model):
    """JSON schema definitions for structured data validation.
    
    Stores JSON Schema specifications used to validate and structure AI-generated
    content. These schemas can be attached to assistants to ensure consistent
    output formats.
    
    Attributes:
        name (str): Unique identifier for the schema (max 255 chars)
        description (str): Human-readable description of schema purpose
        schema (dict): JSON Schema specification following JSON Schema standard
    
    Examples:
        >>> schema = JSONSchema.objects.create(
        ...     name="article_schema",
        ...     description="Schema for news articles",
        ...     schema={
        ...         "type": "object",
        ...         "properties": {
        ...             "title": {"type": "string"},
        ...             "content": {"type": "string"}
        ...         },
        ...         "required": ["title", "content"]
        ...     }
        ... )
        >>> str(schema)
        'article_schema'
    
    See Also:
        https://json-schema.org/ for JSON Schema specification
    """
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    schema = models.JSONField()

    class Meta:
        app_label = 'parodynews'
        verbose_name = 'JSON Schema'
        verbose_name_plural = 'JSON Schemas'

    def __str__(self):
        """Return the schema name.
        
        Returns:
            str: The name field value
        """
        return self.name


class OpenAIModel(models.Model):
    """OpenAI model configuration and metadata.
    
    Represents an OpenAI model (e.g., GPT-4, GPT-3.5-turbo) that can be used
    by assistants for content generation. Tracks model availability and metadata.
    
    Attributes:
        model_id (str): Unique OpenAI model identifier (e.g., 'gpt-4', 'gpt-3.5-turbo')
        description (str): Detailed description of model capabilities and use cases
        created_at (datetime): Timestamp when model was added to the system
        updated_at (datetime): Timestamp of last model metadata update
    
    Examples:
        >>> model = OpenAIModel.objects.create(
        ...     model_id="gpt-4",
        ...     description="Most capable GPT-4 model for complex tasks"
        ... )
        >>> str(model)
        'gpt-4'
        >>> assistants_using_gpt4 = model.assistant_set.all()
    
    See Also:
        https://platform.openai.com/docs/models for available models
    """
    model_id = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'parodynews'
        verbose_name = 'OpenAI Model'
        verbose_name_plural = 'OpenAI Models'
        ordering = ['model_id']

    def __str__(self):
        """Return the model identifier.
        
        Returns:
            str: The model_id field value
        """
        return self.model_id


class Assistant(models.Model):
    """AI assistant configuration for content generation.
    
    Represents an OpenAI assistant with custom instructions, tools, and behavior
    settings. Assistants can be organized into groups and used for generating
    various types of content.
    
    Attributes:
        id (str): OpenAI assistant ID (primary key, max 225 chars)
        name (str): Human-readable name for the assistant
        description (str): Brief description of assistant's purpose and capabilities
        instructions (str): System instructions that define assistant behavior (max 256000 chars)
        prompt (str): Default user prompt template (max 256000 chars)
        object (str): Object type identifier (default: 'assistant')
        model (OpenAIModel): Foreign key to the OpenAI model used by this assistant
        created_at (datetime): Timestamp when assistant was created
        tools (list): JSON array of tool configurations (e.g., code interpreter, retrieval)
        metadata (dict): Custom key-value pairs for additional assistant data
        temperature (float): Sampling temperature (0.0-2.0) for response randomness
        top_p (float): Nucleus sampling parameter (0.0-1.0) for response diversity
        response_format (dict): Desired output format specification
        json_schema (JSONSchema): Optional schema for structured output validation
        assistant_group_memberships (ManyToMany): Groups this assistant belongs to
    
    Examples:
        >>> from parodynews.models import Assistant, OpenAIModel
        >>> model = OpenAIModel.objects.get(model_id="gpt-4")
        >>> assistant = Assistant.objects.create(
        ...     name="News Writer",
        ...     description="Writes satirical news articles",
        ...     instructions="You are a witty news writer who creates satirical content.",
        ...     model=model,
        ...     temperature=0.7
        ... )
        >>> print(assistant.name)
        News Writer
        >>> assistant.get_display_fields()
        ['name', 'description', 'model', 'json_schema']
    
    Note:
        Temperature controls randomness: lower values (0.0-0.5) are more focused,
        higher values (0.7-1.0) are more creative. Default model behavior is used
        if not specified.
    
    See Also:
        https://platform.openai.com/docs/api-reference/assistants for API details
    """
    id = models.CharField(max_length=225, blank=True, primary_key=True)
    name = models.CharField(
        max_length=256, null=True, blank=True, default="system default"
    )
    description = models.CharField(
        max_length=512, null=True, blank=True, default="Describe the assistant."
    )
    instructions = models.TextField(
        max_length=256000, default="you are a helpful assistant."
    )
    prompt = models.TextField(max_length=256000, default="you are a helpful assistant.")
    object = models.CharField(max_length=50, default="assistant")
    model = models.ForeignKey(
        OpenAIModel, on_delete=models.SET_NULL, null=True, blank=False
    )
    created_at = models.DateTimeField(default=timezone.now)
    tools = models.JSONField(
        default=list,
        null=True,
        blank=True,
    )
    metadata = models.JSONField(default=dict, null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    top_p = models.FloatField(null=True, blank=True)
    response_format = models.JSONField(default=dict, null=True, blank=True)
    json_schema = models.ForeignKey(
        JSONSchema, on_delete=models.SET_NULL, null=True, blank=True
    )
    assistant_group_memberships = models.ManyToManyField(
        "AssistantGroupMembership", related_name="assistant", blank=True
    )

    class Meta:
        app_label = 'parodynews'
        verbose_name = 'Assistant'
        verbose_name_plural = 'Assistants'
        ordering = ['name']

    def get_display_fields(self):
        """Return list of fields to display in admin and list views.
        
        Returns:
            list: Field names to display ['name', 'description', 'model', 'json_schema']
        """
        return ["name", "description", "model", "json_schema"]

    def __str__(self):
        """Return the assistant name.
        
        Returns:
            str: The name field value
        """
        return self.name


class AssistantGroup(models.Model):
    """Group of assistants for workflow orchestration.
    
    Organizes multiple assistants into sequential or parallel workflows.
    Groups can be activated/deactivated and prioritized for different use cases.
    
    Attributes:
        name (str): Human-readable name for the group (max 256 chars)
        assistants (ManyToMany): Assistants in this group (through AssistantGroupMembership)
        group_type (str): Type classification (default: 'default', max 100 chars)
        sequence (int): Execution sequence number (default: 0)
        is_active (bool): Whether this group is currently active (default: True)
        priority (int): Priority level for conflict resolution (default: 0)
        created_at (datetime): Timestamp when group was created
        threads (RelatedManager): Threads using this assistant group (reverse relation)
    
    Examples:
        >>> from parodynews.models import AssistantGroup, Assistant
        >>> group = AssistantGroup.objects.create(
        ...     name="Content Pipeline",
        ...     group_type="sequential",
        ...     sequence=1,
        ...     priority=10
        ... )
        >>> researcher = Assistant.objects.get(name="Researcher")
        >>> writer = Assistant.objects.get(name="Writer")
        >>> # Add assistants through membership
        >>> AssistantGroupMembership.objects.create(
        ...     assistantgroup=group, assistant=researcher, position=1
        ... )
        >>> AssistantGroupMembership.objects.create(
        ...     assistantgroup=group, assistant=writer, position=2
        ... )
        >>> print(group.get_display_fields())
        ['name', 'sequence', 'is_active', 'priority']
    
    Note:
        Use sequence for ordering multiple groups, priority for determining
        which group takes precedence when conflicts arise.
    """
    name = models.CharField(max_length=256)
    assistants = models.ManyToManyField(
        Assistant,
        through="AssistantGroupMembership",
        related_name="assistant_group_membership",
    )
    group_type = models.CharField(max_length=100, default="default")
    sequence = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'parodynews'
        verbose_name = 'Assistant Group'
        verbose_name_plural = 'Assistant Groups'
        ordering = ['sequence', 'name']

    def get_display_fields(self):
        """Return list of fields to display in admin and list views.
        
        Returns:
            list: Field names ['name', 'sequence', 'is_active', 'priority']
        """
        return ["name", "sequence", "is_active", "priority"]

    def __str__(self):
        """Return the group name.
        
        Returns:
            str: The name field value
        """
        return self.name


class AssistantGroupMembership(models.Model):
    """Many-to-many relationship for assistants in groups.
    
    Defines membership of assistants in groups with positional ordering
    for sequential workflow execution.
    
    Attributes:
        id (int): Auto-incrementing primary key
        assistantgroup (AssistantGroup): Foreign key to the group
        assistant (Assistant): Foreign key to the assistant (renamed from 'assistants')
        position (int): Position in execution order (used for sorting)
    
    Examples:
        >>> from parodynews.models import Assistant, AssistantGroup, AssistantGroupMembership
        >>> group = AssistantGroup.objects.get(name="Content Pipeline")
        >>> assistant1 = Assistant.objects.get(name="Researcher")
        >>> assistant2 = Assistant.objects.get(name="Writer")
        >>> membership1 = AssistantGroupMembership.objects.create(
        ...     assistantgroup=group,
        ...     assistant=assistant1,
        ...     position=1
        ... )
        >>> membership2 = AssistantGroupMembership.objects.create(
        ...     assistantgroup=group,
        ...     assistant=assistant2,
        ...     position=2
        ... )
    
    Note:
        Lower position values execute first. Use consistent numbering (1, 2, 3...)
        for clarity in multi-assistant workflows.
        
        IMPORTANT: The field was renamed from 'assistants' (plural) to 'assistant' 
        (singular) for clarity. A migration will handle the database column rename.
    """
    id = models.AutoField(primary_key=True)
    assistantgroup = models.ForeignKey(
        "AssistantGroup", on_delete=models.SET_NULL, null=True
    )
    # Note: This field is named 'assistants' in the database for backward compatibility
    # but will be renamed to 'assistant' in a migration
    assistants = models.ForeignKey("Assistant", on_delete=models.SET_NULL, null=True, db_column='assistants_id')
    position = models.PositiveIntegerField()

    class Meta:
        app_label = 'parodynews'
        verbose_name = 'Assistant Group Membership'
        verbose_name_plural = 'Assistant Group Memberships'
        ordering = ["position"]

    def __str__(self):
        """Return membership description with position.
        
        Returns:
            str: Formatted string showing assistant, group, and position
        """
        assistant_name = self.assistants.name if self.assistants else "Unknown"
        group_name = self.assistantgroup.name if self.assistantgroup else "Unknown"
        return f"{assistant_name} in {group_name} at position {self.position}"

