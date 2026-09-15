# resources.py
from import_export import resources

from .models import AIModel, Assistant, JSONSchema, Post


class AssistantResource(resources.ModelResource):
    class Meta:
        model = Assistant


class AIModelResource(resources.ModelResource):
    class Meta:
        model = AIModel


class JSONSchemaResource(resources.ModelResource):
    class Meta:
        model = JSONSchema


class PostResource(resources.ModelResource):
    class Meta:
        model = Post
