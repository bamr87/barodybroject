import json
from django.db import models
from django.utils import timezone
from martor.models import MartorField


print("Loading models.py")

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

    def __str__(self):
        return "App Configuration"


# JSON Schema model
class JSONSchema(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    schema = models.JSONField()

    def __str__(self):
        return self.name
    

# Load model choices from the JSON file
try:
    with open('model_choices.json', 'r') as f:
        MODEL_CHOICES = [(model, model) for model in json.load(f)]
except FileNotFoundError:
    MODEL_CHOICES = []

class Assistant(models.Model):
    id = models.CharField(max_length=225, primary_key=True)
    name = models.CharField(max_length=256, null=True, blank=True, default="system default")
    description = models.CharField(max_length=512, null=True, blank=True, default="Describe the assistant.")
    instructions = models.TextField(max_length=256000, default="you are a helpful assistant.")
    prompt = models.TextField(max_length=256000, default="you are a helpful assistant.")
    object = models.CharField(max_length=50, default="assistant")
    model = models.CharField(max_length=100, choices=MODEL_CHOICES, default='gpt-3.5-turbo')
    created_at = models.DateTimeField(default=timezone.now)
    tools = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)
    temperature = models.FloatField(null=True, blank=True)
    top_p = models.FloatField(null=True, blank=True)
    response_format = models.JSONField(default=dict)
    json_schema = models.ForeignKey(JSONSchema, on_delete=models.SET_NULL, null=True, blank=True)
    assistant_groups = models.ManyToManyField('AssistantGroup', related_name='assistant', blank=True)


    def get_display_fields(self):
        # List the fields you want to display
        return ['id', 'name', 'description', 'model', 'json_schema']
    
    def __str__(self):
        return self.name

class AssistantGroup(models.Model):
    name = models.CharField(max_length=256)
    assistants = models.ManyToManyField(Assistant, related_name='assistant_group')
    group_type = models.CharField(max_length=100, default="default")

    def __str__(self):
        return self.name


class ContentDetail(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, default="NEED TITLE.")
    description = models.TextField(blank=True)
    author = models.CharField(max_length=100, default="NEED AUTHOR.")
    published_at = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(max_length=255, unique=False, default="slug")
    keywords = models.JSONField(default=list)


    def get_display_fields(self):
        # List the fields you want to display
        return ['id', 'title', 'description', 'author', 'published_at']

    def __str__(self):
        return self.title
class ContentItem(models.Model):
    id = models.AutoField(primary_key=True)
    line_number = models.IntegerField(default=0)
    content_type = models.CharField(max_length=100, default="text")

    assistant = models.ForeignKey(Assistant, on_delete=models.SET_NULL, null=True, blank=True, related_name='content')
    prompt = models.TextField(default="say this is a test")
    content = models.TextField()
    detail = models.ForeignKey(ContentDetail, on_delete=models.CASCADE, related_name='content')

    def get_display_fields(self):
        # List the fields you want to display
        return ['id', 'assistant', 'prompt', 'content', 'detail']
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Check if this is a new record
            last_item = ContentItem.objects.filter(detail=self.detail).order_by('-line_number').first()
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
    created_at = models.DateTimeField(default=timezone.now)

    def get_display_fields(self):
        # List the fields you want to display
        return ['id', 'name', 'created_at']

    def __str__(self):
        return self.name
    
# New model for storing messages
# https://platform.openai.com/docs/api-reference/messages
class Message(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    created_at = models.DateTimeField(default=timezone.now)
    content = models.ForeignKey(ContentItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    thread = models.ForeignKey(Thread, on_delete=models.SET_NULL, null=True, related_name='messages')
    assistant = models.ForeignKey(Assistant, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    status = models.CharField(max_length=100, default="initial")
    run_id = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return self.id

# Post Model

class Post(models.Model):
    id = models.AutoField(primary_key = True)
    content_detail = models.ForeignKey(ContentDetail, on_delete=models.CASCADE, related_name='posts')
    thread = models.ForeignKey(Thread, on_delete=models.SET_NULL, null=True, related_name='posts')
    message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, related_name='posts')
    assistant = models.ForeignKey(Assistant, on_delete=models.SET_NULL, null=True, related_name='posts')
    content = MartorField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    filename = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=100, default="draft")

    def get_display_fields(self):
        # List the fields you want to display
        return ['id', 'title', 'created_at', 'slug', 'status']

    def __str__(self):
        return self.content_detail.title

class PostFrontMatter(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='front_matter')
    title = models.CharField(max_length=255)
    description = models.TextField()
    author = models.CharField(max_length=100)
    published_at = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(max_length=255, unique=False, default="slug")

    def __str__(self):
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
    hash = models.CharField(max_length=256,)

    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.name