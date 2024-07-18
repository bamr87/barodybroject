# Generated by Django 4.2.13 on 2024-07-18 19:22

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_key', models.CharField(max_length=255)),
                ('project_id', models.CharField(max_length=255)),
                ('org_id', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Assistant',
            fields=[
                ('assistant_id', models.CharField(max_length=225, primary_key=True, serialize=False)),
                ('description', models.TextField(default='Describe the assistant.', max_length=225)),
                ('model', models.CharField(default='gpt-3.5-turbo', max_length=100)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prompt', models.TextField(default='say this is a test')),
                ('content', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ContentDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='NEED TITLE.', max_length=255)),
                ('description', models.TextField(blank=True)),
                ('author', models.CharField(default='NEED AUTHOR.', max_length=100)),
                ('published_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='SystemRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_name', models.CharField(default='system default', max_length=100)),
                ('instructions', models.TextField(default='you are a helpful assistant.')),
                ('role_type', models.CharField(choices=[('system', 'System'), ('assistant', 'Assistant')], default='system', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('thread_id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('name', models.CharField(default='New Thread', max_length=100)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('message_id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('assistant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='messages', to='parodynews.assistant')),
                ('content', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='messages', to='parodynews.content')),
                ('thread', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='messages', to='parodynews.thread')),
            ],
        ),
        migrations.AddField(
            model_name='content',
            name='detail',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='content', to='parodynews.contentdetail'),
        ),
        migrations.AddField(
            model_name='content',
            name='system_role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contents', to='parodynews.systemrole'),
        ),
        migrations.AddField(
            model_name='assistant',
            name='system_role',
            field=models.ForeignKey(limit_choices_to={'role_type': 'assistant'}, on_delete=django.db.models.deletion.CASCADE, related_name='assistants', to='parodynews.systemrole'),
        ),
    ]
