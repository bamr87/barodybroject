import os

from django.core.exceptions import ImproperlyConfigured
from django.views.generic import View
from openai import OpenAI

from .models import AppConfig


class ModelFieldsMixin(View):
    model = None

    def get_model_fields(self):
        if self.model is None:
            raise ValueError(
                "ModelFieldsMixin requires a 'model' attribute to be defined."
            )
        fields = self.model._meta.get_fields()
        display_fields = self.model().get_display_fields()
        return fields, display_fields


class AppConfigClientMixin(View):
    def get_client(self):
        app_config = AppConfig.objects.first()
        api_key = (app_config.api_key if app_config else None) or os.environ.get(
            "OPENAI_API_KEY"
        )
        org_id = (app_config.org_id if app_config else None) or os.environ.get(
            "OPENAI_ORG_ID"
        )
        project_id = (app_config.project_id if app_config else None) or os.environ.get(
            "OPENAI_PROJECT_ID"
        )

        if not api_key:
            raise ImproperlyConfigured(
                "OpenAI API key is not configured. Set OPENAI_API_KEY or add an AppConfig row."
            )

        client_kwargs = {"api_key": api_key}
        if org_id:
            client_kwargs["organization"] = org_id
        if project_id:
            client_kwargs["project"] = project_id

        return OpenAI(**client_kwargs)


# myapp/mixins.py


class DefaultFormFieldsMixin:
    """
    If the `FieldDefaults` JSON has a default for a field,
    set the form's 'initial' value to that default.
    This way, the DB-based default overrides the model's default.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If there's no model on this form, do nothing:
        if not getattr(self, "instance", None) or not self._meta.model:
            return

        # We only apply defaults if this is a new (unsaved) instance.
        # If you also want to override existing data, remove the `pk` check.
        if self.instance.pk is None:
            model_name = self._meta.model.__name__

            # Local import to avoid circular references:
            from .utils import get_model_defaults

            db_defaults = get_model_defaults(model_name)

            # For each field in the form, if there's a DB default, use it.
            for field_name, field_obj in self.fields.items():
                if field_name in db_defaults:
                    # This sets the initial value if no other initial was provided.
                    # If you want the DB default to *always* override, remove the `or ...` check.
                    if not field_obj.initial:
                        field_obj.initial = db_defaults[field_name]
