import datetime
from django.core.management.base import BaseCommand
from django.apps import apps
from parodynews.models import FieldDefaults
from django.db.models import NOT_PROVIDED
from django.db import models  # Needed for type checking

def make_json_serializable(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    else:
        return obj

class Command(BaseCommand):
    help = 'Generate a FieldDefaults record with a base template of model defaults.'

    def handle(self, *args, **options):
        template = []
        app_label = "parodynews"  # adjust if needed
        for model in apps.get_app_config(app_label).get_models():
            fields_defaults = {}
            for field in model._meta.fields:
                # Skip primary keys (the "id" field or any designated primary key)
                if field.primary_key:
                    continue

                # Exclude default values for foreign keys and date/datetime fields.
                if isinstance(field, models.ForeignKey):
                    value = None
                elif isinstance(field, (models.DateField, models.DateTimeField)):
                    value = None
                else:
                    if hasattr(field, 'default') and field.default != NOT_PROVIDED:
                        value = field.default() if callable(field.default) else field.default
                    else:
                        value = None
                    value = make_json_serializable(value)
                fields_defaults[field.name] = value
            template.append({
                "model_name": model.__name__,
                "fields": fields_defaults,
            })

        serializable_template = make_json_serializable(template)

        FieldDefaults.objects.update_or_create(
            type="base_template",
            defaults={'defaults': serializable_template}
        )
        self.stdout.write(self.style.SUCCESS("FieldDefaults base template record generated."))