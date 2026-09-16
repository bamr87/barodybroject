# Parodynews Models Package

## Overview

Models are organized into modules by domain rather than a single monolithic file.

As of v0.6.0 they are also provider-agnostic: nothing here is specific to a single AI vendor. A conversation is stored locally and replayed to whichever provider is configured, which is what lets a thread started on Claude be continued on GPT.

## Structure

```
models/
├── __init__.py              # Backward-compatible imports
├── base.py                  # Abstract base classes and mixins
├── config.py                # Application configuration models
├── ai.py                    # Model catalogue, assistants, schemas, groups
├── content.py               # Content generation models
├── conversation.py          # Thread and message models
└── publishing.py            # Post and publishing models
```

## Module Descriptions

### base.py
Contains abstract base classes and mixins that can be shared across different model modules:
- `TimestampedModel`: Abstract base for models with created_at/updated_at fields
- `DisplayFieldsMixin`: Mixin for get_display_fields() method

### config.py
Application-wide configuration and settings:
- `AppConfig`: GitHub publishing configuration
- `AIProviderConfig`: Per-provider credentials and defaults, one row per provider,
  at most one flagged `is_default` (enforced in `save()`)
- `PoweredBy`: Attribution links for technologies used
- `FieldDefaults`: Dynamic default values for model fields

### ai.py
Provider-agnostic AI models:
- `JSONSchema`: JSON schema definitions for structured content
- `AIModel`: A model offered by a provider, keyed by `(provider, model_id)`
- `Assistant`: Instructions + the model that runs them + an optional output schema
- `AssistantGroup`: Groups of assistants for sequential workflows
- `AssistantGroupMembership`: Positional membership in a group

### content.py
Content generation and management:
- `ContentDetail`: Metadata for generated content
- `ContentItem`: Individual content segments

### conversation.py
Conversation thread management:
- `Thread`: Conversation threads for multi-turn generation
- `Message`: Individual messages in threads

### publishing.py
Post publishing and versioning:
- `PostPageConfigModel`: Pagination configuration
- `Post`: Published content posts
- `PostFrontMatter`: YAML front matter for posts
- `PostVersion`: Version history for posts

## Tests

The test layout mirrors this package one-for-one — `parodynews/tests/test_models_<module>.py` covers `parodynews/models/<module>.py`. Add a model here and its tests go in the matching module; `test_models_publishing.py` carries a completeness guard that fails if a name in `__all__` is not referenced by any of them.

```bash
python -m pytest parodynews/tests/ -k "test_models" \
  --cov=parodynews.models --cov-report=term-missing   # run from src/
```

Model factories are shared from `parodynews/tests/conftest.py` and are built from the real exports under `parodynews/tests/data/`, not from invented literals. See [the tests README](../tests/README.md).

## Two things worth knowing

### Conversations are ours, not a vendor's

`Thread` and `Message` are the application's own record. Running an assistant reads the thread out of the database and replays it to the configured provider; no provider is asked to remember anything between calls. That is the whole reason threads survive a provider change, and it is why the OpenAI Assistants/Threads API could be dropped entirely.

`Message` records `role`, `provider`, `model_id`, `usage` and `error` so a thread shows what actually happened on each turn, including the failures.

### `AIModel` is keyed by a pair

`(provider, model_id)`, under a unique constraint — not by `model_id` alone. `claude-opus-5` legitimately exists for both the `claude_code` and `anthropic` providers, and they are different rows with different credentials behind them.

## Usage

### Backward Compatible Imports (Recommended)

The `__init__.py` file provides backward-compatible imports, so existing code continues to work:

```python
# Import as before - works exactly the same
from parodynews.models import Assistant, Post, ContentDetail
```

### Direct Module Imports (Optional)

You can also import directly from specific modules if you prefer:

```python
from parodynews.models.ai import Assistant
from parodynews.models.publishing import Post
from parodynews.models.content import ContentDetail
```

## Migration Guide

### Upgrading to v0.6.0

`0002_provider_agnostic_ai` and `0003_drop_nullable_text_columns` handle this. Both are reversible and were verified forward, reverse and forward again against seeded legacy-shaped rows.

What changes:

| Before | After |
|---|---|
| `OpenAIModel` | `AIModel`, with a `provider` field (existing rows become `openai`) |
| `AppConfig.api_key` / `org_id` / `project_id` | Copied into an `AIProviderConfig` row for `openai`, then dropped |
| `AssistantGroupMembership.assistants` | `assistant` (singular) |
| Integer thread/message ids | Locally minted `thread_…` / `msg_…` ids |

Existing assistant replies are identified by the OpenAI `run_id` they carry and tagged `role="assistant"`, `provider="openai"`, so old threads read correctly.

### Nullable text columns

`Assistant.name`, `Assistant.description` and `Message.run_id` were `null=True` *and* had a default, so "unset" could be either NULL or the default string and every reader had to handle both. `0003` backfills the NULLs and makes the columns `NOT NULL` with a default — one empty value, not two. The backfill is not optional: Postgres refuses `SET NOT NULL` while NULLs remain.

## Benefits

1. **Maintainability**: Easier to find and modify related models
2. **Clarity**: Clear separation of concerns by domain
3. **Scalability**: Easier to add new models in appropriate modules
4. **Testing**: Easier to test models in isolation
5. **Onboarding**: New developers can understand the domain structure faster
6. **Performance**: Added indexes for common queries

## Version History

- **0.6.0** (2026-09-14): Provider-agnostic models; `OpenAIModel` → `AIModel`; local thread/message ids; `AIProviderConfig`
- **2.0.0** (2025-11-30): Split models.py into package structure
- **1.0.0** (2024-01-01): Initial models.py implementation

## See Also

- [Main README](../README.md)
- [AI provider layer](../ai/README.md) — what consumes these models
- [Migrations](../migrations/README.md)
- [Django Models Documentation](https://docs.djangoproject.com/en/stable/topics/db/models/)

