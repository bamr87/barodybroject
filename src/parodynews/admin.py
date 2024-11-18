from django.contrib import admin
from django import forms
from django.db import models
from .models import AppConfig, PoweredBy, Assistant, JSONSchema, Post, GeneralizedCodes
from django_json_widget.widgets import JSONEditorWidget
from import_export.admin import ImportExportModelAdmin
from .resources import AssistantResource, JSONSchemaResource
from martor.widgets import AdminMartorWidget

print("Registering AppConfig model")

# Register your models here.
admin.site.register(AppConfig)
admin.site.register(PoweredBy)
admin.site.register(GeneralizedCodes)


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

@admin.register(Assistant)
class AssistantAdmin(ImportExportModelAdmin):
    resource_class = AssistantResource

# parodynews/admin.py
from django.core.management import call_command
from django.contrib import messages
from .models import OpenAIModel

@admin.register(OpenAIModel)
class OpenAIModelAdmin(admin.ModelAdmin):
    list_display = ('model_id', 'created_at', 'updated_at')
    search_fields = ('model_id',)
    actions = ['fetch_openai_models']

    def fetch_openai_models(self, request, queryset):
        try:
            call_command('fetch_models')
            self.message_user(request, "Successfully fetched and saved model choices", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Error fetching models: {e}", messages.ERROR)

    fetch_openai_models.short_description = "Fetch and update OpenAI models"


class PostAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }


admin.site.register(Post)