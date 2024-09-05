import json
from django.db import models
from django.utils import timezone

print("Loading models.py")

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
    object = models.CharField(max_length=50, default="assistant")
    model = models.CharField(max_length=100, choices=MODEL_CHOICES, default='gpt-3.5-turbo')
    created_at = models.DateTimeField(default=timezone.now)
    tools = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)
    temperature = models.FloatField(null=True, blank=True)
    top_p = models.FloatField(null=True, blank=True)
    response_format = models.JSONField(default=dict)
    json_schema = models.ForeignKey(JSONSchema, on_delete=models.SET_NULL, null=True, blank=True)

    def get_display_fields(self):
        # List the fields you want to display
        return ['id', 'name', 'description', 'instructions', 'model', 'json_schema']
    
    def __str__(self):
        return self.name


class ContentDetail(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, default="NEED TITLE.")
    description = models.TextField(blank=True)
    author = models.CharField(max_length=100, default="NEED AUTHOR.")
    published_at = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(max_length=255, unique=False, default="slug")

    def get_display_fields(self):
        # List the fields you want to display
        return ['id', 'title', 'description', 'author', 'published_at']

    def __str__(self):
        return self.title
class ContentItem(models.Model):
    id = models.AutoField(primary_key=True)
    assistant = models.ForeignKey(Assistant, on_delete=models.SET_NULL, null=True, blank=True, related_name='content')
    prompt = models.TextField(default="say this is a test")
    content = models.TextField()
    detail = models.ForeignKey(ContentDetail, on_delete=models.CASCADE, related_name='content')

    def get_display_fields(self):
        # List the fields you want to display
        return ['id', 'assistant', 'prompt', 'content', 'detail']
    
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
    run_id = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        content_id = f"Content ID {self.content.id}" if self.content else "No Content"
        return f"Message for {content_id} with Thread ID {self.thread.id} created at {self.created_at}"

class MyObject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()


