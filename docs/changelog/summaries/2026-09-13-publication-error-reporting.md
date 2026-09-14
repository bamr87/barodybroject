---
title: "[Bug Fix] Publication failures reach the reader as messages instead of a 500"
type: "bugfix"
version: "0.4.0"
date: "2026-09-13"
author: "Barodybroject Team <team@example.com>"
reviewers: []
related_issues: ["#114"]
related_prs: []
impact: "high"
breaking: false
severity: "high"
affected_versions: ["0.4.0"]
---

# Bug Fix: every error during publication is now communicated to the user

> **Summary**: Routes every GitHub API failure in `push_to_github_and_create_pr()`
> into the Django messages framework the view already uses, and narrows the bare
> `except Exception` that was silently converting *any* failure — including a
> rate limit — into a file-creation attempt.

## 🐛 Problem Description

### Issue Summary

Publishing a post failed **silently from the reader's point of view**: every GitHub API error propagated uncaught out of `ManagePostView.publish()`, so the reader got a Django 500 page instead of a message naming what went wrong. One path was worse than uncaught — it was *swallowed*, and turned into a second, misleading failure.

### Affected Components

- **`src/parodynews/views/posts.py`**: `ManagePostView.publish()` and
  `push_to_github_and_create_pr()`.
- **User Experience**: an expired token, a renamed repository, a wrong base
branch, a missing post, or a pull request that already exists — all conditions the reader can act on — produced a stack trace.

### Reproduction Steps

1. Configure GitHub Pages publishing with a token that has expired.
2. Open a post and press *Publish*.
3. Observe a 500 rather than a message about the token.

## 🔍 Root Cause Analysis

### Root Cause

`push_to_github_and_create_pr()` was called with no `try`/`except` at all, and every call inside it — `Github(token)`, `get_repo`, `get_branch`, `create_pull` — raises `GithubException` on failure.

Separately, this handler:

```python
try:
    existing_file = repo.get_contents(repo_path, ref=new_branch_name)
    repo.update_file(...)
except Exception:              # ← swallows everything
    repo.create_file(...)
```

was intended to mean "the file does not exist yet, so create it". It caught *any* exception and answered by calling `create_file`. A reader who had hit their rate limit was told something about file creation instead — and, as the new tests show, publication then **appeared to succeed**, opening a pull request from content that was never reconciled with the file already in the branch. It also violated the repo's own rule in `CLAUDE.md` against empty exception handlers.

### Contributing Factors

- The mechanism for reporting these conditions already existed and was already
wired up (`base.html:229` renders `messages`, and `publish()` used it correctly for the missing-`AppConfig` case). Nothing routed the other failures into it.
- The helper signalled success by returning a URL, so any "return `None` on
  failure" shape would have turned into `redirect(None)`.

## ✅ Solution Implementation

### Fix Description

A `PublicationError` exception carries a reader-facing message out of the helper; `publish()` catches it and answers with `messages.error(...)` plus a redirect to `manage_post`, matching the existing `AppConfig` precedent. Each GitHub status is translated into a message that names the likely cause and the thing to change. Raising, rather than returning `None`, is what keeps `redirect(github_url)` from ever receiving a non-URL.

The local lookups before GitHub is reached — `Post`, `PostFrontMatter`, and an unset `published_at` — are guarded the same way.

### Code Changes

```python
# Before
except Exception:
    repo.create_file(...)

# After
except GithubException as exc:
    # Only a 404 means "no such file yet". A 403 rate limit or a 401 must
    # surface as itself, not as a confusing create_file failure.
    if exc.status != 404:
        raise PublicationError(describe(exc, action=f"read {repo_path}...")) from exc
    existing_file = None
```

The same 404-only narrowing is applied to the branch-existence check, which had the same shape (`except GithubException:` with no status test). A 422 from `create_pull` is special-cased: the already-open pull request is looked up and its URL included in the message.

`PostFrontMatter` is no longer fetched twice — `publish()` passes the object it already holds into the helper.

No configuration or database changes.

## 🧪 Testing and Validation

### Test Cases Added

`src/parodynews/tests/test_post_publish.py` — nine tests driving the real route (`POST /posts/` with `_method=publish`) and asserting on the messages the reader actually sees, with `parodynews.views.posts.Github` patched:

- `test_bad_credential_is_reported_not_raised` — 401 → redirect + a message
  naming the token.
- `test_rate_limit_is_reported_and_does_not_trigger_create_file` — 403 from
`get_contents` → `create_file`, `update_file` and `create_pull` are **not** called, and the message names the rate limit.
- `test_existing_pull_request_is_reported_with_its_link` — 422 from
  `create_pull` → the open pull request's URL is in the message.
- `test_missing_repository_is_reported` — 404 → the repository is named.
- `test_missing_post_is_reported`, `test_missing_front_matter_is_reported`,
  `test_missing_configuration_is_reported` — the local failures.
- `test_new_post_is_created_and_redirects_to_the_pull_request` and
`test_existing_file_is_updated_rather_than_created` — the happy paths, so the error handling cannot have broken publication.

### Test Results

Run from `src/` against the project's PostgreSQL test database:

```bash
DJANGO_SETTINGS_MODULE=barodybroject.settings.testing python -m pytest \
  src/parodynews/tests
```

Six of the nine fail before the change (four by raising the `GithubException` straight out of the view, two by raising `DoesNotExist`); the rate-limit test fails by *succeeding* — the old code swallowed the 403 and returned a pull request URL. After the change:

```
188 passed, 15 deselected in 17.24s
```

`ruff check` and `ruff format --check` are clean on both changed files, and `except Exception` no longer appears in `src/parodynews/views/posts.py`.

## ⚠️ Breaking Changes and Migration

None. `push_to_github_and_create_pr()` gains an optional `post_frontmatter` keyword argument and now raises `PublicationError` where it previously raised `GithubException`; its only caller is `ManagePostView.publish()`.

## 🔄 Prevention Measures

- Every error path is asserted through the real route, so a regression to a 500
  fails the suite.
- The "404 means create it" intent is now expressed as a status test rather than
  a catch-all.

## 🔗 Related Resources

- Original Bug Report: #114
- View and helper: `src/parodynews/views/posts.py`
- Message rendering: `src/parodynews/templates/base.html` L229-231
- [`GithubException.status`](https://pygithub.readthedocs.io/en/stable/utilities.html#github.GithubException.GithubException)
