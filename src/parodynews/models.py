"""
File: models.py
Description: Django models for parody news articles and content management
Author: Barodybroject Team
Created: 2024-01-01
Last Modified: 2025-11-25
Version: 2.0.0

Dependencies:
- django: >=4.0
- martor: Markdown editor field

Note: Django CMS integration has been removed as of 2025-11-25.
      Historical CMS code preserved in git history if needed.
"""

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from martor.models import MartorField

print("Loading models.py")
# TODO: Update assistant model to include dynamic type fields for categorization and organization of assistants.
# TODO: add attachment file handling for image storage (use an image description placeholder for now)
# TODO: Add user id to models for tracking and ownership


class PoweredBy(models.Model):
    """Configuration for 'Powered By' attribution links.
    
    This model stores information about technologies and services that power
    the application, typically displayed in the footer or about page.
    
    Attributes:
        name (str): Display name of the technology/service (max 100 chars)
        icon (str): CSS class or icon identifier for visual representation
        url (str): URL to the technology's website or documentation
    
    Examples:
        >>> powered_by = PoweredBy.objects.create(
        ...     name="OpenAI",
        ...     icon="fa-robot",
        ...     url="https://openai.com"
        ... )
        >>> str(powered_by)
        'OpenAI'
    """
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100)
    url = models.URLField()

    def __str__(self):
        """Return the name of the technology/service.
        
        Returns:
            str: The name field value
        """
        return self.name


class AppConfig(models.Model):
    """Application-wide configuration settings.
    
    Singleton model that stores API keys, project identifiers, and GitHub Pages
    configuration. Should only have one instance in the database.
    
    Attributes:
        api_key (str): OpenAI API key for authentication (max 255 chars)
        project_id (str): Project identifier for OpenAI API (max 255 chars)
        org_id (str): Organization identifier for OpenAI API (max 255 chars)
        github_pages_repo (str): GitHub repository for publishing (format: 'owner/repo')
        github_pages_branch (str): Target branch for publishing (default: 'main')
        github_pages_token (str): GitHub Personal Access Token for API authentication
        github_pages_post_dir (str): Directory path for posts (default: 'posts/')
    
    Note:
        API keys and tokens should be kept secure. Consider using environment
        variables or secret management systems in production.
    
    Examples:
        >>> config = AppConfig.objects.first()
        >>> if config:
        ...     print(f"Publishing to {config.github_pages_repo}")
        Publishing to username/my-blog
    """
    api_key = models.CharField(max_length=255)
    project_id = models.CharField(max_length=255)
    org_id = models.CharField(max_length=255)
    github_pages_repo = models.CharField(max_length=255)
    github_pages_branch = models.CharField(max_length=255, default="main")
    github_pages_token = models.CharField(max_length=255)
    github_pages_post_dir = models.CharField(max_length=255, default="posts/")

    def __str__(self):
        """Return a human-readable string representation.
        
        Returns:
            str: Always returns 'App Configuration'
        """
        return "App Configuration"


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


# Assistant Group to group assistants into a workflow and order of execution.
class AssistantGroupMembership(models.Model):
    """Many-to-many relationship for assistants in groups.
    
    Defines membership of assistants in groups with positional ordering
    for sequential workflow execution.
    
    Attributes:
        id (int): Auto-incrementing primary key
        assistantgroup (AssistantGroup): Foreign key to the group
        assistants (Assistant): Foreign key to the assistant
        position (int): Position in execution order (used for sorting)
    
    Examples:
        >>> from parodynews.models import Assistant, AssistantGroup, AssistantGroupMembership
        >>> group = AssistantGroup.objects.get(name="Content Pipeline")
        >>> assistant1 = Assistant.objects.get(name="Researcher")
        >>> assistant2 = Assistant.objects.get(name="Writer")
        >>> membership1 = AssistantGroupMembership.objects.create(
        ...     assistantgroup=group,
        ...     assistants=assistant1,
        ...     position=1
        ... )
        >>> membership2 = AssistantGroupMembership.objects.create(
        ...     assistantgroup=group,
        ...     assistants=assistant2,
        ...     position=2
        ... )
    
    Note:
        Lower position values execute first. Use consistent numbering (1, 2, 3...)
        for clarity in multi-assistant workflows.
    """
    id = models.AutoField(primary_key=True)
    assistantgroup = models.ForeignKey(
        "AssistantGroup", on_delete=models.SET_NULL, null=True
    )
    assistants = models.ForeignKey("Assistant", on_delete=models.SET_NULL, null=True)
    position = models.PositiveIntegerField()

    class Meta:
        ordering = ["position"]

    def __str__(self):
        """Return membership description with position.
        
        Returns:
            str: Formatted string showing assistant, group, and position
        """
        return f"{self.assistant.name} in {self.assistantgroup.name} at position {self.position}"


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
        ...     assistantgroup=group, assistants=researcher, position=1
        ... )
        >>> AssistantGroupMembership.objects.create(
        ...     assistantgroup=group, assistants=writer, position=2
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

    def get_display_fields(self):
        """Return list of fields to display in admin and list views.
        
        Returns:
            list: Field names ['name', 'sequence', 'is_active', 'priority']
        """
        # List the fields you want to display
        return ["name", "sequence", "is_active", "priority"]

    def __str__(self):
        """Return the group name.
        
        Returns:
            str: The name field value
        """
        return self.name


class FieldDefaults(models.Model):
    """Stores default values grouped by type for model fields.
    
    Provides centralized default value management for dynamically configuring
    model instances. Supports multiple models with their field defaults in
    a single JSON structure.
    
    Attributes:
        type (str): Category or purpose of these defaults (max 255 chars)
        defaults (list): List of model definitions with fields and default values
    
    JSON Structure:
        defaults = [
            {
                "model_name": "MyModel",
                "fields": {
                    "field1": "some default",
                    "field2": 42
                }
            },
            ...
        ]
    
    Examples:
        >>> from parodynews.models import FieldDefaults
        >>> defaults = FieldDefaults.objects.create(
        ...     type="post_defaults",
        ...     defaults=[
        ...         {
        ...             "model_name": "Post",
        ...             "fields": {
        ...                 "status": "draft",
        ...                 "author": "ParodyNews Staff"
        ...             }
        ...         },
        ...         {
        ...             "model_name": "ContentDetail",
        ...             "fields": {
        ...                 "keywords": ["news", "parody"],
        ...                 "description": "AI-generated content"
        ...             }
        ...         }
        ...     ]
        ... )
        >>> print(defaults)
        Defaults for post_defaults
    
    Note:
        Saving this model clears the 'field_defaults' cache to ensure
        updated defaults are immediately available.
    """

    type = models.CharField(max_length=255, default="default_type")
    defaults = models.JSONField(
        default=list,
        help_text="A list of model definitions with their fields and default values.",
    )

    def __str__(self):
        """Return the type description.
        
        Returns:
            str: Formatted string 'Defaults for {type}'
        """
        return f"Defaults for {self.type}"

    def save(self, *args, **kwargs):
        """Clear cached defaults and save.
        
        Ensures the cache is invalidated whenever defaults are updated.
        """
        # Clear cached defaults when updated
        cache.delete("field_defaults")
        super().save(*args, **kwargs)


class ContentDetail(models.Model):
    """Metadata for generated content pieces.
    
    Stores high-level information about content including title, description,
    author, and SEO-related fields. Acts as a container for ContentItems.
    
    Attributes:
        id (int): Auto-incrementing primary key
        title (str): Content title (max 255 chars)
        description (str): Full text description of the content
        author (str): Author name (max 100 chars)
        published_at (datetime): Publication timestamp (default: now)
        slug (str): URL-friendly identifier (max 255 chars, non-unique)
        keywords (list): JSON array of SEO keywords
        user (User): Foreign key to the content creator
        contentitem (RelatedManager): Related content items (reverse relation)
        posts (RelatedManager): Related posts (reverse relation)
    
    Examples:
        >>> from parodynews.models import ContentDetail
        >>> from django.contrib.auth.models import User
        >>> user = User.objects.first()
        >>> detail = ContentDetail.objects.create(
        ...     title="Breaking: Local Cat Declares Independence",
        ...     description="Satirical article about feline autonomy",
        ...     author="ParodyNews Staff",
        ...     slug="cat-independence-2024",
        ...     keywords=["cats", "parody", "independence"],
        ...     user=user
        ... )
        >>> print(detail.get_display_fields())
        ['id', 'title', 'description', 'author', 'published_at']
    
    Note:
        The slug field is not enforced as unique to allow reuse across
        different contexts or versions.
    """
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    author = models.CharField(max_length=100, blank=True)
    published_at = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(max_length=255, unique=False, default="slug")
    keywords = models.JSONField(default=list)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="content_details",
    )

    def get_display_fields(self):
        """Return list of fields to display in admin and list views.
        
        Returns:
            list: Field names ['id', 'title', 'description', 'author', 'published_at']
        """
        # List the fields you want to display
        return ["id", "title", "description", "author", "published_at"]

    def __str__(self):
        """Return the content title.
        
        Returns:
            str: The title field value
        """
        return self.title


class ContentItem(models.Model):
    """Individual content segment generated by an assistant.
    
    Represents a single piece of AI-generated content within a larger
    ContentDetail. Items are automatically numbered sequentially.
    
    Attributes:
        id (int): Auto-incrementing primary key
        line_number (int): Sequential position within the parent ContentDetail
        content_type (str): Type of content (default: 'text', max 100 chars)
        content_text (str): The actual generated text content
        assistant (Assistant): Assistant that generated this content
        prompt (str): The prompt used to generate this content
        detail (ContentDetail): Parent content detail container
        messages (RelatedManager): Related messages (reverse relation)
    
    Examples:
        >>> from parodynews.models import ContentItem, ContentDetail, Assistant
        >>> detail = ContentDetail.objects.first()
        >>> assistant = Assistant.objects.get(name="News Writer")
        >>> item = ContentItem.objects.create(
        ...     content_text="In a shocking turn of events...",
        ...     content_type="paragraph",
        ...     assistant=assistant,
        ...     prompt="Write an opening paragraph about cat independence",
        ...     detail=detail
        ... )
        >>> print(item.line_number)  # Automatically set to 1 (first item)
        1
        >>> item2 = ContentItem.objects.create(
        ...     content_text="Local residents were stunned...",
        ...     assistant=assistant,
        ...     prompt="Write a follow-up paragraph",
        ...     detail=detail
        ... )
        >>> print(item2.line_number)  # Automatically set to 2
        2
    
    Note:
        line_number is automatically assigned on save() based on existing
        items for the same ContentDetail. Manual assignment is overridden.
    """
    id = models.AutoField(primary_key=True)
    line_number = models.IntegerField(default=0)
    content_type = models.CharField(max_length=100, default="text")
    content_text = models.TextField()

    assistant = models.ForeignKey(
        Assistant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contentitem",
    )
    prompt = models.TextField()
    detail = models.ForeignKey(
        ContentDetail, on_delete=models.CASCADE, related_name="contentitem"
    )

    def get_display_fields(self):
        """Return list of fields to display in admin and list views.
        
        Returns:
            list: Field names ['id', 'assistant', 'prompt', 'content_text', 'detail']
        """
        # List the fields you want to display
        return ["id", "assistant", "prompt", "content_text", "detail"]

    def save(self, *args, **kwargs):
        """Save with automatic line_number assignment.
        
        On creation, automatically assigns the next available line_number
        for this ContentDetail.
        """
        if not self.pk:  # Check if this is a new record
            last_item = (
                ContentItem.objects.filter(detail=self.detail)
                .order_by("-line_number")
                .first()
            )
            if last_item:
                self.line_number = last_item.line_number + 1
            else:
                self.line_number = 1
        super(ContentItem, self).save(*args, **kwargs)

    def __str__(self):
        """Return the prompt text.
        
        Returns:
            str: The prompt field value
        """
        return self.prompt


# New model for threads
class Thread(models.Model):
    """Conversation thread for multi-turn content generation.
    
    Represents a persistent conversation context for interacting with
    assistant groups. Threads maintain conversation history and can be
    associated with users and assistant groups.
    
    Attributes:
        id (str): Unique thread identifier (primary key, max 255 chars)
        name (str): Human-readable thread name (default: 'New Thread', max 100 chars)
        description (str): Text description of thread purpose
        assistant_group (AssistantGroup): Group of assistants used in this thread
        created_at (datetime): Timestamp when thread was created
        user (User): User who owns this thread
        messages (RelatedManager): Messages in this thread (reverse relation)
        posts (RelatedManager): Posts generated from this thread (reverse relation)
    
    Examples:
        >>> from parodynews.models import Thread, AssistantGroup
        >>> from django.contrib.auth.models import User
        >>> user = User.objects.first()
        >>> group = AssistantGroup.objects.get(name="Content Pipeline")
        >>> thread = Thread.objects.create(
        ...     id="thread_news_article_123",
        ...     name="Cat Independence Article",
        ...     description="Multi-assistant thread for generating satirical news",
        ...     assistant_group=group,
        ...     user=user
        ... )
        >>> print(thread.get_display_fields())
        ['name', 'description', 'assistant_group', 'created_at']
    
    Note:
        Thread IDs should be unique and descriptive. Consider using prefixes
        like 'thread_' for clarity.
    """
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=100, default="New Thread")
    description = models.TextField(blank=True)

    assistant_group = models.ForeignKey(
        AssistantGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="threads",
    )
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="threads"
    )

    def get_display_fields(self):
        """Return list of fields to display in admin and list views.
        
        Returns:
            list: Field names ['name', 'description', 'assistant_group', 'created_at']
        """
        # List the fields you want to display
        return ["name", "description", "assistant_group", "created_at"]

    def __str__(self):
        """Return the thread name.
        
        Returns:
            str: The name field value
        """
        return self.name


# New model for storing messages
# https://platform.openai.com/docs/api-reference/messages
class Message(models.Model):
    """Individual message in a conversation thread.
    
    Represents a single message exchange in an OpenAI conversation thread.
    Messages track the assistant used, content generated, and processing status.
    
    Attributes:
        id (str): Unique message identifier (primary key, max 255 chars)
        created_at (datetime): Timestamp when message was created
        contentitem (ContentItem): Associated content item for this message
        thread (Thread): Parent conversation thread
        assistant (Assistant): Assistant that generated or processed this message
        status (str): Processing status (default: 'initial', max 100 chars)
        run_id (str): OpenAI run ID for tracking API execution (max 255 chars)
        posts (RelatedManager): Posts created from this message (reverse relation)
    
    Examples:
        >>> from parodynews.models import Message, Thread, Assistant, ContentItem
        >>> thread = Thread.objects.get(name="Cat Independence Article")
        >>> assistant = Assistant.objects.get(name="News Writer")
        >>> contentitem = ContentItem.objects.first()
        >>> message = Message.objects.create(
        ...     id="msg_abc123xyz",
        ...     thread=thread,
        ...     assistant=assistant,
        ...     contentitem=contentitem,
        ...     status="completed",
        ...     run_id="run_def456uvw"
        ... )
        >>> print(message.status)
        completed
        >>> print(message.get_display_fields())
        ['contentitem', 'assistant', 'created_at', 'status']
    
    Status Values:
        - initial: Message created but not processed
        - queued: Message queued for processing
        - in_progress: Currently being processed
        - completed: Successfully processed
        - failed: Processing failed
    
    See Also:
        https://platform.openai.com/docs/api-reference/messages
    """
    id = models.CharField(max_length=255, primary_key=True)

    created_at = models.DateTimeField(default=timezone.now)
    contentitem = models.ForeignKey(
        ContentItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages",
    )
    thread = models.ForeignKey(
        Thread, on_delete=models.SET_NULL, null=True, related_name="messages"
    )
    assistant = models.ForeignKey(
        Assistant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages",
    )
    status = models.CharField(max_length=100, default="initial")
    run_id = models.CharField(max_length=255, null=True, blank=True)

    def get_display_fields(self):
        """Return list of fields to display in admin and list views.
        
        Returns:
            list: Field names ['contentitem', 'assistant', 'created_at', 'status']
        """
        # List the fields you want to display
        return ["contentitem", "assistant", "created_at", "status"]

    def __str__(self):
        """Return the message ID.
        
        Returns:
            str: The id field value
        """
        return self.id


# New model for storing posts
class PostPageConfigModel(models.Model):
    """Configuration for post pagination settings.
    
    Manages pagination settings for different post namespaces, allowing
    customized page sizes for different sections or post types.
    
    Attributes:
        namespace (str): Unique identifier for this config (max 255 chars, unique)
        paginated_by (int): Number of posts per page (default: 5)
    
    Examples:
        >>> from parodynews.models import PostPageConfigModel
        >>> config = PostPageConfigModel.objects.create(
        ...     namespace="news",
        ...     paginated_by=10
        ... )
        >>> blog_config = PostPageConfigModel.objects.create(
        ...     namespace="blog",
        ...     paginated_by=5
        ... )
        >>> print(config.namespace)
        news
    
    Note:
        Namespace must be unique. Use descriptive names that match your
        post categories or sections (e.g., 'news', 'blog', 'articles').
    """
    namespace = models.CharField(
        _("instance namespace"), default=None, max_length=255, unique=True
    )

    paginated_by = models.IntegerField(_("paginate size"), blank=False, default=5)


class Post(models.Model):
    """Published content post with markdown support.
    
    Represents a complete, publishable post with content, metadata, and
    relationships to content generation components. Supports markdown
    formatting via Martor field.
    
    Attributes:
        content_detail (ContentDetail): Metadata for this post
        thread (Thread): Conversation thread that generated this post
        message (Message): Specific message that created this post
        post_content (MartorField): Markdown content with editor support
        assistant (Assistant): Assistant that generated the content
        created_at (datetime): Timestamp when post was created
        updated_at (datetime): Timestamp of last update (auto-updated)
        filename (str): Target filename for file export (max 255 chars)
        status (str): Publication status (default: 'draft', max 100 chars)
        postfrontmatter (PostFrontMatter): Front matter metadata for this post
        user (User): User who owns this post
    
    Examples:
        >>> from parodynews.models import Post, ContentDetail, Assistant
        >>> from django.contrib.auth.models import User
        >>> detail = ContentDetail.objects.first()
        >>> assistant = Assistant.objects.get(name="News Writer")
        >>> user = User.objects.first()
        >>> post = Post.objects.create(
        ...     content_detail=detail,
        ...     post_content="# Breaking News\n\nLocal cat declares independence...",
        ...     assistant=assistant,
        ...     filename="2024-01-15-cat-independence.md",
        ...     status="published",
        ...     user=user
        ... )
        >>> print(post.get_absolute_url())
        /post/1/
        >>> print(post.get_display_fields())
        ['id', 'content_detail', 'thread', 'message', 'assistant', 'created_at', 'status']
    
    Status Values:
        - draft: Not published, work in progress
        - review: Ready for review
        - published: Publicly visible
        - archived: No longer active but preserved
    
    Note:
        updated_at is automatically set on every save(). The MartorField
        provides a rich markdown editor in the Django admin.
    """
    content_detail = models.ForeignKey(
        ContentDetail, on_delete=models.SET_NULL, null=True, related_name="posts"
    )
    thread = models.ForeignKey(
        Thread, on_delete=models.SET_NULL, null=True, related_name="posts"
    )
    message = models.ForeignKey(
        Message, on_delete=models.SET_NULL, null=True, related_name="posts"
    )
    post_content = MartorField()
    assistant = models.ForeignKey(
        Assistant, on_delete=models.SET_NULL, null=True, related_name="posts"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    filename = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=100, default="draft")
    postfrontmatter = models.ForeignKey(
        "PostFrontMatter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="posts"
    )

    def get_display_fields(self):
        """Return list of fields to display in admin and list views.
        
        Returns:
            list: Field names for display
        """
        return [
            "id",
            "content_detail",
            "thread",
            "message",
            "assistant",
            "created_at",
            "status",
        ]

    def get_absolute_url(self):
        """Return the canonical URL for this post.
        
        Returns:
            str: URL path to post detail view
        """
        return reverse("post_detail", kwargs={"pk": self.pk})

    def __str__(self):
        """Return the post title from content_detail.
        
        Returns:
            str: The title from the related ContentDetail
        """
        return self.content_detail.title

class PostFrontMatter(models.Model):
    """YAML front matter metadata for post export.
    
    Stores metadata that will be included as YAML front matter when
    exporting posts to markdown files (Jekyll, Hugo, etc.).
    
    Attributes:
        post (Post): One-to-one relationship to parent post
        title (str): Post title for front matter (max 255 chars)
        description (str): Full text description
        author (str): Author name (max 100 chars)
        published_at (datetime): Publication date (default: now)
        slug (str): URL slug (max 255 chars, non-unique)
    
    Examples:
        >>> from parodynews.models import Post, PostFrontMatter
        >>> post = Post.objects.first()
        >>> frontmatter = PostFrontMatter.objects.create(
        ...     post=post,
        ...     title="Cat Independence Day",
        ...     description="A satirical look at feline autonomy",
        ...     author="ParodyNews Staff",
        ...     slug="cat-independence-day"
        ... )
        >>> print(frontmatter)
        Cat Independence Day
        >>> print(frontmatter.get_display_fields())
        ['post', 'title', 'author', 'published_at', 'slug']
    
    YAML Output Format:
        ---
        title: "Cat Independence Day"
        description: "A satirical look at feline autonomy"
        author: "ParodyNews Staff"
        date: "2024-01-15 10:30:00"
        slug: "cat-independence-day"
        ---
    
    Note:
        One-to-one relationship with Post ensures each post has at most
        one front matter configuration.
    """
    post = models.OneToOneField(
        Post, on_delete=models.CASCADE, related_name="front_matter"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    author = models.CharField(max_length=100)
    published_at = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(max_length=255, unique=False, default="slug")

    def get_display_fields(self):
        """Return list of fields to display in admin and list views.
        
        Returns:
            list: Field names ['post', 'title', 'author', 'published_at', 'slug']
        """
        # Added missing get_display_fields method
        return ["post", "title", "author", "published_at", "slug"]

    def __str__(self):
        """Return the front matter title.
        
        Returns:
            str: The title field value
        """
        # Updated __str__ method for consistency
        return self.title


class MyObject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()


class GeneralizedCodes(models.Model):
    code = models.CharField(max_length=256, unique=True)
    name = models.CharField(max_length=256)
    description = models.TextField()
    type = models.CharField(max_length=256, default="system")
    items = models.JSONField(default=list)
    model = models.CharField(max_length=256, default="default")
    table = models.CharField(max_length=256, default="default")
    field = models.CharField(max_length=256, default="default")
    database = models.CharField(max_length=256, default="default")
    category = models.CharField(max_length=256, default="default")
    domain = models.CharField(max_length=256, default="default")
    entity = models.CharField(max_length=256, default="default")
    project = models.CharField(max_length=256, default="default")
    module = models.CharField(max_length=256, default="default")
    hash = models.CharField(
        max_length=256,
    )

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class PostVersion(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveIntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    frontmatter = models.TextField()

    def __str__(self):
        return f"Version {self.version_number} of Post {self.post.id}"
