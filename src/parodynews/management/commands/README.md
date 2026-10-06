
# commands Directory

## Purpose
This directory contains Django management commands that provide administrative and utility functions for the parodynews application. These custom commands extend Django's built-in management system to handle application-specific tasks like database operations and refreshing the AI model catalogue.

## Contents
- `__init__.py`: Python package initialization file
- `sync_models.py`: Refresh the `AIModel` catalogue from a provider. Replaces the OpenAI-only `fetch_models`
- `ensure_admin.py` / `ensure_e2e_user.py`: Create the admin and end-to-end test users
- `generate_field_defaults.py`: Django command to generate FieldDefaults records with base templates of model defaults
- `refreshmigrations.py`: Django command for refreshing database migrations
- `reset_db.py`: Django command to reset the database to an empty state (PostgreSQL-only)

## Usage
These commands are executed using Django's management system:

```bash
# Refresh the model catalogue for the default provider
python manage.py sync_models

# ...or for one specific provider
python manage.py sync_models --provider anthropic

# Generate field defaults for models
python manage.py generate_field_defaults

# Reset the database and migrations (development only)
python manage.py reset_db

# Refresh migrations
python manage.py refreshmigrations
```

> **⚠️ WARNING:** The `reset_db` command is **highly destructive**. It will permanently delete your database and all migration history.
> **Before running this command, always back up your data.**
> **Never use this command in production environments.**

## Container Configuration
These commands run within the Django application container:
- Executed via `python manage.py <command_name>`
- Require access to Django settings and database connections
- `sync_models` needs a working credential for the provider it queries. Providers
that cannot enumerate their models report `supports_model_discovery = False` and are skipped rather than failing
- Can be run during container initialization or as maintenance tasks

## Related Paths
- Incoming: Called via Django's management command system (`python manage.py`)
- Outgoing: Interact with Django models, the database, and AI providers through
  [`parodynews.ai`](../../ai/README.md)
