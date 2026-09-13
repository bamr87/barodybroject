---
title: "[Improvement] fetch_models — filter to assistant-capable models, describe them, and retire delisted ones"
type: "improvement"
version: "0.4.0"
date: "2026-09-01"
author: "Barodybroject Team <team@example.com>"
reviewers: []
related_issues: ["#110"]
related_prs: []
impact: "medium"
breaking: false
---

# Improvement: `fetch_models` stops offering models that cannot back an assistant

> **Summary**: The assistant model dropdown was already dynamic — `manage.py fetch_models` upserts `OpenAIModel` rows and `Assistant.model` is a foreign key to that table. What it was not was *correct*: the fetch was unfiltered, so image, speech, transcription, embedding and legacy-completion models were all selectable, `description` was never populated, delisted models were never retired, and none of it was tested.

## 🎯 Overview

### Purpose

Issue #110 asked for a dynamic model list. That already existed. The real gap was the delta this change closes: the dropdown offered choices that fail at *generation* time rather than at *selection* time.

### Scope

- `src/parodynews/management/commands/fetch_models.py` — rewritten (21 → ~150 lines).
- `src/parodynews/models/ai.py` — `OpenAIModel.is_available`.
- `src/parodynews/migrations/0002_openaimodel_is_available.py` — new.
- `src/parodynews/forms.py` — `AssistantForm` offers only available models.
- `src/parodynews/admin.py` — `is_available` and `description` on the changelist, filterable.
- `src/parodynews/model_choices.json` — **deleted** (orphaned snapshot; `git grep model_choices` now returns nothing).
- `src/parodynews/tests/test_fetch_models.py` — new.

## 🔧 What changed

### 1. An explicit, reviewable filter

OpenAI's `/models` endpoint returns the account's whole catalogue with **no capability field**, so the only honest filter is one a reviewer can read. Two module-level constants, not logic inlined in `handle()`:

```python
ASSISTANT_MODEL_PREFIXES = ("gpt-", "o1", "o3", "o4")
ASSISTANT_MODEL_EXCLUDED = (
    "-instruct", "-audio", "-realtime", "-search",
    "-transcribe", "-tts", "-image", "-moderation",
)
```

`is_assistant_model()` applies them and is unit-tested on its own, with no database.

### 2. `description` is populated

`OpenAIModel.description` is a non-null `TextField` the old command never wrote, so every row carried an empty string. The endpoint supplies no description, so `describe_model()` composes one from `id`, `owned_by` and `created`.

### 3. Delisted models are retired, not deleted

`Assistant.model` is `on_delete=SET_NULL`. Deleting a delisted `OpenAIModel` row would silently strip the model from every assistant that referenced it. The new `is_available` boolean is cleared instead; `AssistantForm` filters its `model` queryset to `is_available=True`, so a retired model stops being *offered* without any existing assistant changing.

### 4. An API failure changes nothing

The catalogue is fully resolved **before** the first write, and the writes run in one `transaction.atomic()` block. A failure raises `CommandError` — Django's `ManagementUtility` turns that into `sys.exit(1)` — with the table untouched.

## 🧪 Testing and Validation

`src/parodynews/tests/test_fetch_models.py`. The OpenAI client is faked in every case through `Command.get_client`, so the suite passes with `OPENAI_API_KEY` unset and never contacts the live API.

| Test | Asserts |
| --- | --- |
| `test_chat_models_are_assistant_capable` / `test_other_modalities_are_not` | the filter, on 4 + 14 ids, with no database (`SimpleTestCase`) |
| `test_only_assistant_capable_models_are_persisted` | given `dall-e-3`, `tts-1`, `whisper-1`, `text-embedding-3-large`, `babbage-002`, `gpt-4o`, **only** `gpt-4o` is written |
| `test_every_persisted_row_has_a_description` | no persisted row has an empty description |
| `test_a_delisted_model_is_retired_without_unassigning_its_assistants` | an assistant's `model_id` is unchanged after its model is delisted, the model is `is_available=False`, and it is gone from the form's choices |
| `test_a_retired_model_becomes_available_again_when_relisted` | retirement is reversible |
| `test_an_api_error_fails_loudly_and_writes_nothing` | `CommandError` with `returncode == 1`, zero rows written |
| `test_an_api_error_does_not_retire_already_recorded_models` | a failed fetch does not retire what a good one recorded |
| `test_the_command_builds_a_real_openai_client_by_default` | `get_client()` is the only place `OpenAI()` is constructed |

### Test results

The DB-backed cases need the project's PostgreSQL test database (`settings/base.py` rejects SQLite outright), so — exactly as for the issue #30 fix — the full run happens in the `tests` job of `.github/workflows/ci.yml`, which provides a `postgres:15-alpine` service.

Verified locally without a database:

```console
$ python -m pytest parodynews/tests/test_fetch_models.py::IsAssistantModelTests
3 passed in 0.43s

$ python manage.py check --settings barodybroject.settings.testing
System check identified 4 issues (0 silenced)   # 4 pre-existing allauth deprecations

$ python manage.py makemigrations --check --dry-run --settings barodybroject.settings.testing
No changes detected                              # the hand-written migration matches the models

$ ruff check <changed files>      → All checks passed!
$ black --check <changed files>   → 6 files would be left unchanged
```

## ⚠️ Breaking Changes and Migration

None for existing data. `0002_openaimodel_is_available` adds one boolean defaulting to `True`, so every existing row stays available until the next fetch decides otherwise.

Operationally: the first `fetch_models` run after this change marks every already-recorded non-assistant model (`dall-e-*`, `tts-*`, `whisper-*`, embeddings, `babbage-002`, …) unavailable, and they disappear from the assistant dropdown. **An assistant currently pointing at one keeps pointing at it** — nothing is unassigned — but it can no longer be re-selected. That is the intended correction.

## 🔄 Prevention Measures

- The filter is a named constant with its own unit tests, so widening or narrowing it is a one-line, reviewable diff.
- `test_the_command_builds_a_real_openai_client_by_default` pins the injection point, so re-inlining `OpenAI()` into `handle()` would be caught rather than silently making the suite need a live key.

## 🔗 Related Resources

- Issue: #110
- Command: `src/parodynews/management/commands/fetch_models.py`
- Model: `src/parodynews/models/ai.py` → `OpenAIModel`, `Assistant.model`
- Form: `src/parodynews/forms.py` → `AssistantForm`
- [OpenAI — List models](https://platform.openai.com/docs/api-reference/models/list)
- [OpenAI — Assistants API overview](https://platform.openai.com/docs/assistants/overview)
