"""
Make the AI models provider-agnostic.

- ``OpenAIModel`` becomes ``AIModel`` keyed by ``(provider, model_id)``; existing
  rows are OpenAI models and are tagged ``provider="openai"``.
- ``AIProviderConfig`` replaces the OpenAI columns on ``AppConfig``. A legacy
  OpenAI credential is copied into an ``openai`` provider row and, because it
  is the only configured provider at that point, flagged as the default so an
  upgraded deployment keeps working until an operator switches providers.
- ``Assistant``, ``Thread`` and ``Message`` become local-first: ids are minted
  locally, ``Message`` records the speaker ``role`` and which provider/model
  produced it. Legacy assistant replies (rows carrying an OpenAI ``run_id``)
  are tagged ``role="assistant"``.
- ``AssistantGroupMembership.assistants`` is finally renamed to ``assistant``.
"""

import django.db.models.deletion
from django.db import migrations, models


def copy_legacy_openai_config(apps, schema_editor):
    AppConfig = apps.get_model("parodynews", "AppConfig")
    AIProviderConfig = apps.get_model("parodynews", "AIProviderConfig")

    legacy = AppConfig.objects.order_by("pk").first()
    if legacy is None or not (legacy.api_key or "").strip():
        return
    row, created = AIProviderConfig.objects.get_or_create(
        provider="openai",
        defaults={
            "display_name": "OpenAI (migrated from App Configuration)",
            "api_key": legacy.api_key.strip(),
            "organization_id": (legacy.org_id or "").strip(),
            "project_id": (legacy.project_id or "").strip(),
            "default_model": "gpt-4o-mini",
        },
    )
    if created and not AIProviderConfig.objects.filter(is_default=True).exists():
        row.is_default = True
        row.save(update_fields=["is_default"])


def restore_legacy_openai_config(apps, schema_editor):
    AppConfig = apps.get_model("parodynews", "AppConfig")
    AIProviderConfig = apps.get_model("parodynews", "AIProviderConfig")

    row = AIProviderConfig.objects.filter(provider="openai").first()
    if row is None:
        return
    for config in AppConfig.objects.all():
        config.api_key = row.api_key
        config.org_id = row.organization_id
        config.project_id = row.project_id
        config.save(update_fields=["api_key", "org_id", "project_id"])


def tag_legacy_assistant_replies(apps, schema_editor):
    Message = apps.get_model("parodynews", "Message")
    # Only assistant runs ever carried an OpenAI run id; user messages did not.
    Message.objects.filter(run_id__isnull=False).exclude(run_id="").update(
        role="assistant", provider="openai"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("parodynews", "0001_initial"),
    ]

    operations = [
        # ------------------------------------------------------------ AIModel
        migrations.RenameModel(old_name="OpenAIModel", new_name="AIModel"),
        migrations.AlterModelOptions(
            name="aimodel",
            options={
                "ordering": ["provider", "model_id"],
                "verbose_name": "AI Model",
                "verbose_name_plural": "AI Models",
            },
        ),
        migrations.AlterField(
            model_name="aimodel",
            name="model_id",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="aimodel",
            name="description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="aimodel",
            name="provider",
            field=models.CharField(db_index=True, default="openai", max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="aimodel",
            name="provider",
            field=models.CharField(db_index=True, default="claude_code", max_length=50),
        ),
        migrations.AddField(
            model_name="aimodel",
            name="display_name",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="aimodel",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddConstraint(
            model_name="aimodel",
            constraint=models.UniqueConstraint(
                fields=("provider", "model_id"),
                name="parodynews_aimodel_provider_model",
            ),
        ),
        # ---------------------------------------------------------- Assistant
        migrations.AlterField(
            model_name="assistant",
            name="model",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="parodynews.aimodel",
            ),
        ),
        migrations.AddField(
            model_name="assistant",
            name="remote_id",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.RemoveField(
            model_name="assistant",
            name="assistant_group_memberships",
        ),
        # ----------------------------------------------- group membership
        migrations.RenameField(
            model_name="assistantgroupmembership",
            old_name="assistants",
            new_name="assistant",
        ),
        migrations.AlterField(
            model_name="assistantgroupmembership",
            name="assistant",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="parodynews.assistant",
            ),
        ),
        migrations.AlterField(
            model_name="assistantgroup",
            name="assistants",
            field=models.ManyToManyField(
                related_name="assistant_groups",
                through="parodynews.AssistantGroupMembership",
                to="parodynews.assistant",
            ),
        ),
        # ------------------------------------------------------------- Thread
        migrations.AlterField(
            model_name="thread",
            name="id",
            field=models.CharField(
                blank=True, max_length=255, primary_key=True, serialize=False
            ),
        ),
        migrations.AddField(
            model_name="thread",
            name="provider",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AddField(
            model_name="thread",
            name="remote_id",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        # ------------------------------------------------------------ Message
        migrations.AlterField(
            model_name="message",
            name="id",
            field=models.CharField(
                blank=True, max_length=255, primary_key=True, serialize=False
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="role",
            field=models.CharField(
                choices=[
                    ("user", "User"),
                    ("assistant", "Assistant"),
                    ("system", "System"),
                ],
                default="user",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="provider",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AddField(
            model_name="message",
            name="model_id",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="message",
            name="remote_id",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="message",
            name="usage",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="message",
            name="error",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.RunPython(tag_legacy_assistant_replies, migrations.RunPython.noop),
        # --------------------------------------------------- AIProviderConfig
        migrations.CreateModel(
            name="AIProviderConfig",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("provider", models.CharField(max_length=50, unique=True)),
                (
                    "display_name",
                    models.CharField(blank=True, default="", max_length=100),
                ),
                ("api_key", models.CharField(blank=True, default="", max_length=1024)),
                ("base_url", models.CharField(blank=True, default="", max_length=255)),
                (
                    "organization_id",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                (
                    "project_id",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                (
                    "default_model",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                ("is_default", models.BooleanField(default=False)),
                ("is_enabled", models.BooleanField(default=True)),
                ("extra", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "AI Provider Configuration",
                "verbose_name_plural": "AI Provider Configurations",
                "ordering": ["-is_default", "provider"],
            },
        ),
        migrations.RunPython(copy_legacy_openai_config, restore_legacy_openai_config),
        # Give the three OpenAI columns a default before dropping them. The
        # columns were NOT NULL with no default, so reversing the RemoveField
        # on a populated table would otherwise fail before the restore step
        # could put the credential back.
        migrations.AlterField(
            model_name="appconfig",
            name="api_key",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="appconfig",
            name="org_id",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="appconfig",
            name="project_id",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.RemoveField(model_name="appconfig", name="api_key"),
        migrations.RemoveField(model_name="appconfig", name="org_id"),
        migrations.RemoveField(model_name="appconfig", name="project_id"),
    ]
