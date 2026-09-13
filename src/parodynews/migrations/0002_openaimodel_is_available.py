"""Add `OpenAIModel.is_available`.

`manage.py fetch_models` marks a model unavailable when OpenAI stops listing
it, instead of deleting the row: `Assistant.model` is `on_delete=SET_NULL`, so
a delete would silently strip the model from every assistant that used it.
Existing rows default to available — they were all listed at the time they were
written, and the next fetch retires whatever is genuinely gone.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("parodynews", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="openaimodel",
            name="is_available",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Still listed by the OpenAI models endpoint. Cleared by "
                    "`manage.py fetch_models` when a model is delisted; unavailable "
                    "models are hidden from the assistant form but keep their rows so "
                    "existing assistants are not silently unassigned."
                ),
            ),
        ),
    ]
