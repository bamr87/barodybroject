from django.contrib import admin
from django import forms
from django.db import models
from .models import AppConfig, PoweredBy, Assistant, JSONSchema, Post
from django_json_widget.widgets import JSONEditorWidget
from import_export.admin import ImportExportModelAdmin
from .resources import AssistantResource, JSONSchemaResource
from martor.widgets import AdminMartorWidget

print("Registering AppConfig model")

# Register your models here.
admin.site.register(AppConfig)
admin.site.register(PoweredBy)


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

class PostAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }


admin.site.register(Post)