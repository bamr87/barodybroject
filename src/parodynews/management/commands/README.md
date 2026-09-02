
# commands Directory

## Purpose
This directory contains Django management commands that provide administrative and utility functions for the parodynews application. These custom commands extend Django's built-in management system to handle application-specific tasks like database operations, model management, and OpenAI integration.

## Contents
- `__init__.py`: Python package initialization file
- `fetch_models.py`: Django command to refresh the `OpenAIModel` table — the source of the assistant form's model dropdown — from the OpenAI API
- `generate_field_defaults.py`: Django command to generate FieldDefaults records with base templates of model defaults
- `refreshmigrations.py`: Django command for refreshing database migrations
- `reset_db.py`: Django command to reset the database to an empty state (PostgreSQL-only)

## Usage
These commands are executed using Django's management system:

```bash
# Fetch latest OpenAI models and update the database
python manage.py fetch_models

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

### `fetch_models` — what it filters and why

`Assistant.model` is a foreign key to `OpenAIModel`, so this command decides what the assistant form's model dropdown offers. OpenAI's `/models` endpoint returns the account's **whole catalogue** with no capability field — image (`dall-e-*`), speech (`tts-*`), transcription (`whisper-*`), embedding (`text-embedding-*`) and legacy completion (`babbage-002`, `davinci-002`) ids come back alongside the chat models — and none of those can back an assistant. Persisting all of them made selecting one fail at generation time instead of at selection time, so the command:

- keeps only ids matching the explicit allowlist in `fetch_models.py` (`ASSISTANT_MODEL_PREFIXES` minus `ASSISTANT_MODEL_EXCLUDED`) — a reviewable constant, not a heuristic buried in the loop;
- writes a non-empty `description` for every row (the endpoint has none of its own, so it is composed from `id`, `owned_by` and `created`);
- marks models OpenAI no longer lists `is_available = False` rather than deleting them — `Assistant.model` is `on_delete=SET_NULL`, so a delete would silently unassign the model from every assistant using it. Unavailable models are hidden from the assistant form and filterable in the admin;
- resolves the whole catalogue **before** writing anything and writes inside one transaction, then raises `CommandError` (exit 1) on an API failure — a bad or missing `OPENAI_API_KEY` leaves the table exactly as it was.

Covered by `src/parodynews/tests/test_fetch_models.py`, which fakes the client and never contacts the live API.

## Container Configuration
These commands run within the Django application container:
- Executed via `python manage.py <command_name>`
- Require access to Django settings and database connections
- Some commands (like `fetch_models`) require OpenAI API access
- Can be run during container initialization or as maintenance tasks

## Related Paths
- Incoming: Called via Django's management command system (`python manage.py`)
- Outgoing: Interact with Django models, database, and external APIs (OpenAI)
