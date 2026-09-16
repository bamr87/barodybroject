---
title: "[Bug Fix] Publication failures reach the reader as messages instead of a 500"
type: "bugfix"
version: "0.6.0"
date: "2026-09-13"
author: "Barodybroject Team <team@example.com>"
reviewers: []
related_issues: ["#114"]
related_prs: ["#181"]
impact: "high"
breaking: false
severity: "high"
affected_versions: ["0.6.0"]
---

# Bug Fix: every error during publication is now communicated to the user

> **Summary**: Translates every GitHub API failure in
> `services.publishing.push_to_github_and_create_pr()` into a `PublicationError`
> whose message names what failed and what to change, and narrows the
> `except GithubException:` handlers that were converting *any* failure —
> including an expired token or a rate limit — into a second, unrelated write.

## 🐛 Problem Description

### Issue Summary

Publishing a post reported nothing a reader could act on. `PostViewSet.publish` distinguished only `PublishingNotConfigured`; every other failure fell through to a generic `Publishing failed: <repr>` 502. An expired token, a repository the token cannot see, a wrong base branch and an exhausted rate limit were all the same opaque string.

One path was worse than opaque — it was *swallowed*. `repo.get_contents()` and `repo.update_file()` shared a single `except GithubException:` whose handler called `create_file()`. Any failure of either was therefore answered by attempting a different write, and the error the reader eventually saw was that second write's, not the real one.

> **Note on history.** This defect was originally filed against `ManagePostView.publish()` and `push_to_github_and_create_pr()` in `src/parodynews/views/posts.py`. That module was deleted by #183 ("provider-agnostic AI framework … React frontend"), which moved publication into `src/parodynews/services/publishing.py`. The rewrite carried the same two defects into the new module; this change fixes them there.

### Affected Components

| Component | Role |
|---|---|
| `src/parodynews/services/publishing.py` | Where publication happens, and where the defects live |
| `src/parodynews/api/views.py` (`PostViewSet.publish`) | What the React UI calls; turns the failure into a response |
| `src/frontend/src/pages/Posts.tsx` | Renders `detail` from the response — unchanged, it already did the right thing with a good message |

### Reproduction Steps

1. Configure GitHub publishing with a token that has expired.
2. `POST /api/posts/{id}/publish/`.
3. **Before:** `502 {"detail": "Publishing failed: 401 {\"message\": \"Bad credentials\"}"}` — or, if the failure landed on `get_contents`, a confusing error about creating a file that already exists.
4. **After:** `502 {"detail": "Could not read posts/… in bamr87/it-journey: GitHub rejected the credential (401). The GitHub token in the application configuration is invalid or has expired — update the token and publish again."}`

## 🔍 Root Cause Analysis

### Root Cause

`GithubException` was caught by *status-blind* handlers. Only a **404** means "this branch/file is not there yet, create it"; every other status is a real failure. Because the handlers did not check `exc.status`, a 401 or a 403 selected the create-it branch.

### Contributing Factors

- The GitHub client raises one exception type for every HTTP status, so `except GithubException:` reads as narrow while behaving as broad.
- `push_to_github_and_create_pr()` had no failure vocabulary of its own, so the view had nothing to translate and could only stringify whatever arrived.

## ✅ Solution Implementation

### Fix Description

- New `PublicationError(message, *, url=None)` in `services/publishing.py`: raised, never returned, so a caller cannot mistake a failure for a pull-request URL.
- `_github_error_message()` maps 401 / 403 / 404 / other onto text naming the repository, the branch and the remedy; `_github_detail()` surfaces GitHub's own message for anything unmapped.
- Every GitHub call is wrapped, and each "not there yet" probe checks `exc.status != 404` before deciding.
- The read and the write are now in **separate** `try` blocks, so a failed `update_file` can no longer fall through to `create_file`.
- A 422 on `create_pull` looks up the pull request already open for the branch and returns its URL — best-effort, so a failure of that lookup degrades to "no link" rather than masking the 422.
- `PostViewSet.publish` catches `PublicationError` and passes `message` through verbatim (plus `url` when set). The generic `Publishing failed:` prefix now only covers failures the service did not anticipate.

### Code Changes

```python
# Before — one handler over the read AND the write
try:
    existing_file = repo.get_contents(repo_path, ref=new_branch_name)
    repo.update_file(..., sha=existing_file.sha, ...)
except GithubException:
    repo.create_file(...)          # reached by a 401, a 403, a 500...

# After — the probe is separated, and only a 404 means "create it"
try:
    existing_file = repo.get_contents(repo_path, ref=new_branch_name)
except GithubException as exc:
    if exc.status != 404:
        raise PublicationError(describe(exc, action=f"read {repo_path} …")) from exc
    existing_file = None

try:
    if existing_file is None:
        repo.create_file(...)
    else:
        repo.update_file(..., sha=existing_file.sha, ...)
except GithubException as exc:
    raise PublicationError(describe(exc, action=f"write {repo_path} …")) from exc
```

## 🧪 Testing and Validation

### Test Cases Added

`src/parodynews/tests/test_post_publish.py` — 12 tests, driving the real service and the real endpoint with a mocked `github.Github`:

| Test | Asserts |
|---|---|
| `test_a_bad_credential_names_the_token` | A 401 message says "token" and "401" |
| `test_a_missing_repository_names_the_repository` | A 404 names the repo and the base branch |
| `test_a_rate_limit_is_reported_as_itself` | A 403 on `get_contents` → no `create_file`, no `update_file`, no `create_pull` |
| `test_a_failed_update_is_not_retried_as_a_create` | A failing `update_file` does not fall through to `create_file` |
| `test_a_branch_lookup_failure_does_not_create_a_branch` | A 403 on `get_branch` does not call `create_git_ref` |
| `test_an_existing_pull_request_is_reported_with_its_link` | A 422 carries the open PR's URL in both `message` and `.url` |
| `test_an_unlinkable_422_still_explains_itself` | `get_pulls` failing leaves `url is None` and keeps GitHub's own text |
| `test_a_new_file_is_created…` / `…updated_rather_than_created` | The happy path still creates, updates and returns the PR URL |
| `test_the_publish_endpoint_returns_the_message_not_a_500` | 502 carrying the specific message, *not* the `Publishing failed` prefix |
| `test_the_publish_endpoint_passes_through_the_existing_pull_request_link` | The response body carries `url` |
| `test_an_unconfigured_deployment_is_still_a_400` | `PublishingNotConfigured` keeps its 400 |

### Test Results

```console
$ cd src && pytest
367 passed, 7 deselected in 37.89s

$ ruff check src/ && black --check src/ && isort --profile=black --check-only src/
All checks passed!
96 files would be left unchanged.
```

Reverting `services/publishing.py` and `api/views.py` to their pre-fix state fails 9 of the 12 new tests — the three that still pass are the two happy-path cases and the 400, which is correct: those describe behaviour the fix preserves rather than introduces.

## ⚠️ Breaking Changes and Migration

None. `push_to_github_and_create_pr()` keeps its signature and return type; it now raises `PublicationError` where it previously let a `GithubException` escape. `publish_post()` is unchanged in shape.

## 🔄 Prevention Measures

- `services/README.md` records the rule the next change has to keep: **a 404 is the only status that means "not there yet"**.
- `api/README.md` documents the publish endpoint's status/body contract alongside the existing AI error mapping.

## 🔗 Related Resources

- Issue [#114](https://github.com/bamr87/barodybroject/issues/114)
- [`src/parodynews/services/README.md`](../../../src/parodynews/services/README.md)
- [`src/parodynews/api/README.md`](../../../src/parodynews/api/README.md)
