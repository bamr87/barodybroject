---
title: "[Bug Fix] Thread message delete — pin helper arity and order the remote delete first"
type: "bugfix"
version: "0.4.0"
date: "2026-08-13"
author: "Barodybroject Team <team@example.com>"
reviewers: []
related_issues: ["#30"]
related_prs: []
impact: "medium"
breaking: false
severity: "high"
affected_versions: ["0.4.0"]
---

# Bug Fix: Thread message delete raised `TypeError`, and deleted locally before the remote call

> **Summary**: Adds the missing regression coverage for the thread-message delete route and reorders the view so the OpenAI-side delete runs before the local `Message` row is removed.

## 🐛 Problem Description

### Issue Summary

Deleting a message from a thread returned HTTP 500 with:

```
TypeError: openai_delete_message() missing 1 required positional argument: 'thread_id'
```

The reported traceback came from a deployed container (`/app/parodynews/views.py`) that predates the views refactor. The arity defect itself is **already fixed** on `main`: the monolithic `parodynews/views.py` was split into the `parodynews/views/` package, and the surviving call site in `parodynews/views/threads.py` passes all three arguments. Two problems remained:

1. **No regression test.** The fix was incidental to a refactor, so nothing pinned the helper's arity.
2. **Delete ordering.** `delete_thread_message` removed the local `Message` row *before* calling
OpenAI, so any upstream failure — including the original `TypeError` — left the local record and the OpenAI thread out of sync from the user's point of view.

### Affected Components

- **`parodynews/views/threads.py`**: `ProcessContentView.delete_thread_message` — the call site and the ordering.
- **`parodynews/utils/threads.py`**: `openai_delete_message(client, message_id, thread_id)` — unchanged.
- **User Experience**: `POST /threads/<thread_id>/messages/delete/<message_id>/` returned a 500 instead of redirecting.

### Reproduction Steps

1. Go to *Threads*.
2. Click *Delete* on a message.
3. Observe HTTP 500 (on the affected deployed build).
4. Expected: the message is deleted locally and in OpenAI, with a success flash and a redirect to `thread_detail`.

## 🔍 Root Cause Analysis

### Root Cause

`openai_delete_message` takes `(client, message_id, thread_id)`. The old call site passed only `(message_id, thread_id)`. The refactor corrected the call but added no test, and left the local `message.delete()` ahead of the remote call.

### Contributing Factors

- Missing test coverage for the delete-message route (`parodynews/tests/` held only `conftest.py`, `test_templates.py`, and `e2e/`).
- The local/remote delete ordering was never stated as an invariant anywhere.

## ✅ Solution Implementation

### Fix Description

The remote delete now runs first; the local row is deleted only after it succeeds. On failure the local `Message` survives and the operation stays retryable.

### Code Changes

```python
# Before
message = Message.objects.get(id=message_id)
message.delete()
client = AppConfigClientMixin.get_client(self)
openai_delete_message(client, message_id, thread_id)

# After
message = Message.objects.get(id=message_id)
client = AppConfigClientMixin.get_client(self)
openai_delete_message(client, message_id, thread_id)
message.delete()
```

No configuration or database changes.

## 🧪 Testing and Validation

### Test Cases Added

`src/parodynews/tests/test_thread_message_delete.py` — three tests on the real route (`POST /threads/<thread_id>/messages/delete/<message_id>/`):

- `test_delete_passes_client_message_and_thread` — asserts the helper is called with
`(client, message_id, thread_id)`, that the response redirects to `thread_detail`, and that the `Message` row is gone. Patched with `autospec=True`, so the two-argument form from issue #30 raises `TypeError: missing a required argument: 'thread_id'` here rather than passing.
- `test_openai_delete_runs_before_local_row_is_removed` — asserts the local row still exists at the
  moment the remote delete is invoked. This is the test that fails without the reordering.
- `test_local_row_survives_when_openai_delete_fails` — a raising remote delete leaves the local
  `Message` in place.

### Test Results

Run from `src/` (config: `src/pytest.ini`, `e2e` excluded by default):

```bash
DJANGO_SETTINGS_MODULE=barodybroject.settings.testing python -m pytest \
  parodynews/tests/test_thread_message_delete.py
```

These tests need the project's PostgreSQL test database (`base.py` rejects SQLite outright), so the DB-backed run happens in the `tests` job of `.github/workflows/ci.yml`, which provides a `postgres:15-alpine` service. All three pass there on Python 3.10, 3.11, and 3.12:

```
parodynews/tests/test_thread_message_delete.py::DeleteThreadMessageTests::test_delete_passes_client_message_and_thread PASSED [ 95%]
parodynews/tests/test_thread_message_delete.py::DeleteThreadMessageTests::test_local_row_survives_when_openai_delete_fails PASSED [ 97%]
parodynews/tests/test_thread_message_delete.py::DeleteThreadMessageTests::test_openai_delete_runs_before_local_row_is_removed PASSED [100%]
======================= 41 passed, 1 deselected in 8.40s =======================
```

The ordering invariant was additionally verified by executing the real `delete_thread_message` against mocked collaborators — failing on the pre-fix ordering (`['local_delete', 'remote_delete']`) and passing after (`['remote_delete', 'local_delete']`).

`ruff check` and `ruff format --check` pass on both changed files.

## ⚠️ Breaking Changes and Migration

None — this is a backward-compatible bug fix. No migrations, no configuration changes.

## 🔄 Prevention Measures

- The `autospec=True` patch pins the helper's real signature, so an arity regression fails the suite.
- The ordering invariant is now asserted, not implied.

## 🔗 Related Resources

- Original Bug Report: #30
- Helper: `src/parodynews/utils/threads.py` → `openai_delete_message`
- Call site: `src/parodynews/views/threads.py` → `ProcessContentView.delete_thread_message`
- Route: `src/parodynews/urls.py` → `delete_thread_message`
- [OpenAI message deletion](https://platform.openai.com/docs/api-reference/messages/deleteMessage)
