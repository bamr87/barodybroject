from cms.models.fields import PlaceholderRelationField
from cms.models.pluginmodel import CMSPlugin
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
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100)
    url = models.URLField()

    def __str__(self):
        return self.name


class AppConfig(models.Model):
    api_key = models.CharField(max_length=255)
    project_id = models.CharField(max_length=255)
    org_id = models.CharField(max_length=255)
    github_pages_repo = models.CharField(max_length=255)
    github_pages_branch = models.CharField(max_length=255, default="main")
    github_pages_token = models.CharField(max_length=255)
    github_pages_post_dir = models.CharField(max_length=255, default="posts/")

    def __str__(self):
        return "App Configuration"


# JSON Schema model
class JSONSchema(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    schema = models.JSONField()

    def __str__(self):
        return self.name


class OpenAIModel(models.Model):
    model_id = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.model_id


class Assistant(models.Model):
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
        # List the fields you want to display
        return ["name", "description", "model", "json_schema"]

    def __str__(self):
        return self.name


# Assistant Group to group assistants into a workflow and order of execution.
class AssistantGroupMembership(models.Model):
    id = models.AutoField(primary_key=True)
    assistantgroup = models.ForeignKey(
        "AssistantGroup", on_delete=models.SET_NULL, null=True
    )
    assistants = models.ForeignKey("Assistant", on_delete=models.SET_NULL, null=True)
    position = models.PositiveIntegerField()

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"{self.assistant.name} in {self.assistantgroup.name} at position {self.position}"


class AssistantGroup(models.Model):
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
        # List the fields you want to display
        return ["name", "sequence", "is_active", "priority"]

    def __str__(self):
        return self.name


class FieldDefaults(models.Model):
    """
    Stores default values grouped by a 'type'.
    'defaults' is a list of dictionaries, each containing:
    {
        "model_name": "MyModel",
        "fields": {
            "field1": "some default",
            "field2": 42
        }
    }
    """

    type = models.CharField(max_length=255, default="default_type")
    defaults = models.JSONField(
        default=list,
        help_text="A list of model definitions with their fields and default values.",
    )

    def __str__(self):
        return f"Defaults for {self.type}"

    def save(self, *args, **kwargs):
        # Clear cached defaults when updated
        cache.delete("field_defaults")
        super().save(*args, **kwargs)


class ContentDetail(models.Model):
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
        # List the fields you want to display
        return ["id", "title", "description", "author", "published_at"]

    def __str__(self):
        return self.title


class ContentItem(models.Model):
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
        # List the fields you want to display
        return ["id", "assistant", "prompt", "content_text", "detail"]

    def save(self, *args, **kwargs):
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
        return self.prompt


# New model for threads
class Thread(models.Model):
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
        # List the fields you want to display
        return ["name", "description", "assistant_group", "created_at"]

    def __str__(self):
        return self.name


# New model for storing messages
# https://platform.openai.com/docs/api-reference/messages
class Message(models.Model):
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
        # List the fields you want to display
        return ["contentitem", "assistant", "created_at", "status"]

    def __str__(self):
        return self.id


# New model for storing posts
class PostPageConfigModel(models.Model):
    namespace = models.CharField(
        _("instance namespace"), default=None, max_length=255, unique=True
    )

    paginated_by = models.IntegerField(_("paginate size"), blank=False, default=5)


class Entry(models.Model):
    app_config = models.ForeignKey(
        PostPageConfigModel, null=False, on_delete=models.CASCADE
    )
    title = models.TextField(blank=True, default="")
    content_text = PlaceholderRelationField("page_content")

    def __str__(self):
        return self.title or "<no title>"

    class Meta:
        verbose_name = _("Entry")
        verbose_name_plural = _("Entries")


# Post Model


class Post(models.Model):
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
    # post_content = PlaceholderRelationField('post_content')  # Ensure placeholder name matches template
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
        return reverse("post_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.content_detail.title

    # Ensure TextPlugin is available in post_content
    def get_allowed_plugins(self):
        return ["TextPlugin", "ImagePlugin", "LinkPlugin"]


class PostPluginModel(CMSPlugin):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return self.post.content_detail.title

    class Meta:
        abstract = False  # Ensure this is either omitted or set to False


class PostFrontMatter(models.Model):
    post = models.OneToOneField(
        Post, on_delete=models.CASCADE, related_name="front_matter"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    author = models.CharField(max_length=100)
    published_at = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(max_length=255, unique=False, default="slug")

    def get_display_fields(self):
        # Added missing get_display_fields method
        return ["post", "title", "author", "published_at", "slug"]

    def __str__(self):
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
