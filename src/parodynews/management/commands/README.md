
# commands Directory

## Purpose
This directory contains Django management commands that provide administrative and utility functions for the parodynews application. These custom commands extend Django's built-in management system to handle application-specific tasks like database operations, model management, and OpenAI integration.

## Contents
- `__init__.py`: Python package initialization file
- `fetch_models.py`: Django command to fetch and update OpenAI model choices from the OpenAI API
- `generate_field_defaults.py`: Django command to generate FieldDefaults records with base templates of model defaults
- `refreshmigrations.py`: Django command for refreshing database migrations
- `reset_db.py`: Django command to reset the database by deleting db.sqlite3 and migration files for a fresh start

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

**Note:** The `reset_db` command is intended for development use only and will delete your database and migration history.

## Container Configuration
These commands run within the Django application container:
- Executed via `python manage.py <command_name>`
- Require access to Django settings and database connections
- Some commands (like `fetch_models`) require OpenAI API access
- Can be run during container initialization or as maintenance tasks

## Related Paths
- Incoming: Called via Django's management command system (`python manage.py`)
- Outgoing: Interact with Django models, database, and external APIs (OpenAI)
