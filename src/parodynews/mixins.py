from django.views.generic import View
from .models import AppConfig
from openai import OpenAI

class ModelFieldsMixin(View):
    model = None

    def get_model_fields(self):
        if self.model is None:
                raise ValueError("ModelFieldsMixin requires a 'model' attribute to be defined.")
        fields = self.model._meta.get_fields()
        display_fields = self.model().get_display_fields()
        return fields, display_fields
    
class AppConfigClientMixin(View):
    def get_client(self):
        app_config = AppConfig.objects.first()
        if not app_config:
            raise ValueError("AppConfig not found.")
        api_key = app_config.api_key
        org_id = app_config.org_id
        project_id = app_config.project_id
        client = OpenAI(organization=org_id, project=project_id, api_key=api_key)
        return client