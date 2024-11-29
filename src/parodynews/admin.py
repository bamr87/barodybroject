# parodynews/admin.py
from django.contrib import admin
from django import forms
from .models import (
    AppConfig,
    PoweredBy,
    Assistant,
    JSONSchema,
    Post,
    PostFrontMatter,
    GeneralizedCodes,
    PostPageConfigModel,
    Entry
)

from django_json_widget.widgets import JSONEditorWidget
from import_export.admin import ImportExportModelAdmin
from .resources import (
    AssistantResource,
    JSONSchemaResource,
    PostResource,
    OpenAIModelResource,
)
from cms.admin.placeholderadmin import FrontendEditableAdminMixin
from django.core.management import call_command
from django.contrib import messages
from .models import OpenAIModel
from .utils import get_openai_client, delete_assistant

print("Registering AppConfig model")

# Register your models here.
admin.site.register(AppConfig)
admin.site.register(PoweredBy)
admin.site.register(GeneralizedCodes)
admin.site.register(Post)
admin.site.register(PostFrontMatter)
admin.site.register(Entry)
admin.site.register(PostPageConfigModel)
# JSON Schema model

class JSONSchemaForm(forms.ModelForm):
    class Meta:
        model = JSONSchema
        fields = ['name', 'schema']
        widgets = {
            'schema': JSONEditorWidget
        }

    def clean_schema(self):
        schema = self.cleaned_data['schema']
        # Add any custom validation for the JSON schema here
        return schema

class JSONSchemaAdmin(ImportExportModelAdmin):
    form = JSONSchemaForm
    list_display = ('name',)
    actions = ['export_selected_schemas']
    resource_class = JSONSchemaResource
    
    def export_selected_schemas(self, request, queryset):
        import json
        from django.http import HttpResponse

        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="schemas.json"'
        schemas = list(queryset.values('name', 'schema'))
        response.write(json.dumps(schemas, indent=4))
        return response

    export_selected_schemas.short_description = "Export selected schemas to JSON"

admin.site.register(JSONSchema, JSONSchemaAdmin)

class AssistantAdmin(ImportExportModelAdmin):
    list_display = ('name', 'description', 'created_at', 'model')
    resource_class = AssistantResource
    actions = ['fetch_openai_assistants']

    def fetch_openai_assistants(self, request, queryset):
        try:
            client = get_openai_client()

            # Fetch assistants from OpenAI API
            response = client.beta.assistants.list(
                limit="100"
            )

            for assistant_data in response.data:  # Changed from response.get('data', []) to response.data
                assistant_id = assistant_data.id  # Changed from assistant_data['id'] to assistant_data.id
                # Update or create Assistant instance
                assistant_model, created = Assistant.objects.update_or_create(
                    id=assistant_id,
                    defaults={
                        'name': assistant_data.name or '',
                        'description': assistant_data.description or '',
                        'instructions': assistant_data.instructions or '',
                        # Set the model field if the model exists
                        'model': OpenAIModel.objects.get_or_create(
                            model_id=assistant_data.model or ''
                        )[0],
                        # Add other fields as needed
                    }
                )
                # Handle json_schema if present
                if hasattr(assistant_data, 'response_format') and hasattr(assistant_data.response_format, 'json_schema'):
                    schema_data = assistant_data.response_format.json_schema
                    json_schema, _ = JSONSchema.objects.update_or_create(
                        name=schema_data.name or '',
                        defaults={
                            'description': schema_data.description or '',
                            'schema': schema_data.schema or {}
                        }
                    )
                    assistant_model.json_schema = json_schema
                    assistant_model.save()

            self.message_user(request, "Successfully synchronized assistants from OpenAI.", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Error fetching assistants: {e}", messages.ERROR)

    fetch_openai_assistants.short_description = "Fetch and synchronize assistants from OpenAI"

    def delete_model(self, request, obj):
        try:
            client = get_openai_client()
            delete_assistant(client, obj.id)
            self.message_user(request, f"Assistant '{obj.name}' deleted successfully.", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Error deleting assistant '{obj.name}': {e}", messages.ERROR)

    def delete_queryset(self, request, queryset):
        errors = False
        client = get_openai_client()
        for obj in queryset:
            try:
                delete_assistant(client, obj.id)
            except Exception as e:
                errors = True
                self.message_user(request, f"Error deleting assistant '{obj.name}': {e}", messages.ERROR)
        if not errors:
            self.message_user(request, "Selected assistants deleted successfully.", messages.SUCCESS)

admin.site.register(Assistant, AssistantAdmin)

class OpenAIModelAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('model_id', 'created_at', 'updated_at')

    actions = ['fetch_openai_models']
    resource_class = OpenAIModelResource

    def fetch_openai_models(self, request, queryset):
        try:
            call_command('fetch_models')
            self.message_user(request, "Successfully fetched and saved model choices", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Error fetching models: {e}", messages.ERROR)

    fetch_openai_models.short_description = "Fetch and update OpenAI models"

admin.site.register(OpenAIModel, OpenAIModelAdmin)


class PostAdmin(FrontendEditableAdminMixin, ImportExportModelAdmin, admin.ModelAdmin):
    frontend_editable_fields = ("post_content")
    resource_class = PostResource


class PostFrontMatterAdmin(FrontendEditableAdminMixin, admin.ModelAdmin):
    frontend_editable_fields = ("title", "description", "author", "date", "tags")

class EntryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'content_text',
        'app_config',
    )
    list_filter = (
        'app_config',
    )


class FaqConfigAdmin(admin.ModelAdmin):
    pass