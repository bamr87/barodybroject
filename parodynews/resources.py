# resources.py
from import_export import resources
from .models import Assistant, JSONSchema

class AssistantResource(resources.ModelResource):
    class Meta:
        model = Assistant

class JSONSchemaResource(resources.ModelResource):
    class Meta:
        model = JSONSchema