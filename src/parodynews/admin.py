# parodynews/admin.py
"""
Django admin configuration for parodynews application.

Organized by model category matching the models package structure.
"""

import json

from django import forms
from django.contrib import admin, messages
from django.db import models
from django.http import HttpResponse
from django_json_widget.widgets import JSONEditorWidget
from import_export.admin import ImportExportModelAdmin
from martor.widgets import AdminMartorWidget

from .ai import AIError, available_providers
from .models import (
    AIModel,
    AIProviderConfig,
    AppConfig,
    Assistant,
    AssistantGroup,
    AssistantGroupMembership,
    FieldDefaults,
    JSONSchema,
    Post,
    PostFrontMatter,
    PostPageConfigModel,
    PostVersion,
    PoweredBy,
)
from .resources import (
    AIModelResource,
    AssistantResource,
    JSONSchemaResource,
    PostResource,
)
from .services.assistants import sync_models

# =============================================================================
# CONFIGURATION MODELS
# =============================================================================

admin.site.register(AppConfig)
admin.site.register(PoweredBy)


class AIProviderConfigForm(forms.ModelForm):
    api_key = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=True),
        help_text=(
            "Credential for this provider (Claude Code OAuth token, API key...). "
            "Leave empty to use the provider's environment variables."
        ),
    )

    class Meta:
        model = AIProviderConfig
        fields = [
            "provider",
            "display_name",
            "api_key",
            "base_url",
            "organization_id",
            "project_id",
            "default_model",
            "is_default",
            "is_enabled",
            "extra",
        ]
        widgets = {"extra": JSONEditorWidget}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(slug, slug) for slug in available_providers()]
        self.fields["provider"].widget = forms.Select(choices=choices)


@admin.register(AIProviderConfig)
class AIProviderConfigAdmin(admin.ModelAdmin):
    form = AIProviderConfigForm
    list_display = (
        "provider",
        "display_name",
        "has_credential",
        "default_model",
        "is_default",
        "is_enabled",
        "updated_at",
    )
    list_filter = ("is_default", "is_enabled")

    @admin.display(boolean=True, description="Credential stored")
    def has_credential(self, obj):
        return obj.has_credential


# =============================================================================
# AI MODELS
# =============================================================================


class JSONSchemaForm(forms.ModelForm):
    class Meta:
        model = JSONSchema
        fields = ["name", "description", "schema"]
        widgets = {"schema": JSONEditorWidget}


class JSONSchemaAdmin(ImportExportModelAdmin):
    form = JSONSchemaForm
    list_display = ("name", "description")
    actions = ["export_selected_schemas"]
    resource_class = JSONSchemaResource

    @admin.action(description="Export selected schemas to JSON")
    def export_selected_schemas(self, request, queryset):
        response = HttpResponse(content_type="application/json")
        response["Content-Disposition"] = 'attachment; filename="schemas.json"'
        schemas = list(queryset.values("name", "schema"))
        response.write(json.dumps(schemas, indent=4))
        return response


admin.site.register(JSONSchema, JSONSchemaAdmin)


class FieldDefaultsForm(forms.ModelForm):
    class Meta:
        model = FieldDefaults
        fields = ["type", "defaults"]
        widgets = {"defaults": JSONEditorWidget}


@admin.register(FieldDefaults)
class FieldDefaultsAdmin(admin.ModelAdmin):
    form = FieldDefaultsForm
    list_display = ["type"]


class AssistantAdmin(ImportExportModelAdmin):
    list_display = ("name", "description", "model", "json_schema", "created_at")
    list_filter = ("model__provider",)
    search_fields = ("name", "description", "instructions")
    resource_class = AssistantResource


admin.site.register(Assistant, AssistantAdmin)


class AIModelAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ("model_id", "provider", "display_name", "is_active", "updated_at")
    list_filter = ("provider", "is_active")
    search_fields = ("model_id", "display_name")
    actions = ["sync_from_provider"]
    resource_class = AIModelResource

    @admin.action(description="Sync models from the selected rows' providers")
    def sync_from_provider(self, request, queryset):
        providers = sorted(set(queryset.values_list("provider", flat=True)))
        for slug in providers:
            try:
                report = sync_models(slug)
            except AIError as exc:
                self.message_user(request, f"{slug}: {exc}", messages.ERROR)
                continue
            self.message_user(
                request,
                f"{slug}: {len(report.created)} created, {len(report.updated)} updated",
                messages.SUCCESS,
            )


admin.site.register(AIModel, AIModelAdmin)


# =============================================================================
# PUBLISHING MODELS
# =============================================================================


class PostAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = PostResource
    list_display = (
        "content_detail",
        "thread",
        "message",
        "assistant",
        "created_at",
        "status",
    )

    formfield_overrides = {models.TextField: {"widget": AdminMartorWidget}}


admin.site.register(Post, PostAdmin)

admin.site.register(PostFrontMatter)
admin.site.register(PostPageConfigModel)
admin.site.register(PostVersion)


# =============================================================================
# INLINE ADMINS
# =============================================================================


class AssistantGroupMembershipInline(admin.TabularInline):
    model = AssistantGroupMembership
    extra = 1
    ordering = ["position"]
    fields = ["assistant", "position"]


class AssistantGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "sequence", "is_active", "priority")
    inlines = [AssistantGroupMembershipInline]


admin.site.register(AssistantGroup, AssistantGroupAdmin)
