from django.contrib import admin
from .models import AppConfig

print("Registering AppConfig model")

# Register your models here.
admin.site.register(AppConfig)

# JSON Schema model
from django.contrib import admin
from django import forms
from django_json_widget.widgets import JSONEditorWidget
from .models import JSONSchema

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

class JSONSchemaAdmin(admin.ModelAdmin):
    form = JSONSchemaForm
    list_display = ('name',)
    actions = ['export_selected_schemas']

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