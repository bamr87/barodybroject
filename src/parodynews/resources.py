# resources.py
from import_export import resources
from .models import Assistant, JSONSchema, Post, OpenAIModel


class AssistantResource(resources.ModelResource):
    class Meta:
        model = Assistant


class OpenAIModelResource(resources.ModelResource):
    class Meta:
        model = OpenAIModel


class JSONSchemaResource(resources.ModelResource):
    class Meta:
        model = JSONSchema


class PostResource(resources.ModelResource):
    class Meta:
        model = Post
