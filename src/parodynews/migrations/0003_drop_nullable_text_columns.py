"""Make three text columns non-nullable (ruff DJ001).

``Assistant.name``, ``Assistant.description`` and ``Message.run_id`` were
``null=True`` *and* had a default, so an unset value could be either NULL or
the default string and every reader had to handle both. They are now
``blank=True`` with a default, which leaves exactly one empty value.

Rows written before this migration can still hold NULL, and Postgres refuses
``SET NOT NULL`` while they do, so each column is backfilled first. Reversing
only widens the columns again, so no data step is needed on the way back.
"""

from django.db import migrations, models


def backfill_nulls(apps, schema_editor):
    """Replace NULL with each column's default before it becomes NOT NULL."""
    Assistant = apps.get_model("parodynews", "Assistant")
    Message = apps.get_model("parodynews", "Message")

    Assistant.objects.filter(name__isnull=True).update(name="system default")
    Assistant.objects.filter(description__isnull=True).update(
        description="Describe the assistant."
    )
    Message.objects.filter(run_id__isnull=True).update(run_id="")


class Migration(migrations.Migration):
    dependencies = [
        ("parodynews", "0002_provider_agnostic_ai"),
    ]

    operations = [
        migrations.RunPython(backfill_nulls, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="assistant",
            name="name",
            field=models.CharField(
                blank=True, default="system default", max_length=256
            ),
        ),
        migrations.AlterField(
            model_name="assistant",
            name="description",
            field=models.CharField(
                blank=True, default="Describe the assistant.", max_length=512
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="run_id",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
