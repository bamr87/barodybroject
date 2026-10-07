---
title: "[Feature] File unhandled exceptions as deduplicated GitHub issues"
type: "feature"
version: "0.4.0"
date: "2026-08-30"
author: "Barodybroject Team <team@example.com>"
reviewers: []
related_issues: ["#59", "#60"]
related_prs: ["#166"]
impact: "medium"
breaking: false
affected_versions: ["0.4.0"]
---

# Feature: unhandled exceptions can be filed as deduplicated GitHub issues

> **Summary**: A `logging` handler on `django.request` turns an unhandled exception into a GitHub issue in a configured tracker, deduplicated by fingerprint and rate limited. It is **off by default**, has no default target repository, and refuses a public target unless explicitly overridden.

## 🎯 Motivation

#60 asked for runtime errors to become tracked work without manual transcription. #59 is the same request from the deployment side, where eight unattended `Deployment failure` issues had already demonstrated the failure mode this feature has to avoid: one issue per occurrence.

## ✅ What changed

A `logging` handler — the same hook Django's own `AdminEmailHandler` uses — rather than middleware, because a handler also catches exceptions that never traverse the middleware chain (management commands, background tasks, errors raised while rendering a response). Filing happens on a background worker, never on the request path, so a GitHub outage cannot turn a 500 into a timeout.

| Concern | Behaviour |
| --- | --- |
| Duplicates | Fingerprinted; repeats comment on the open issue instead of filing a new one, and are throttled |
| Volume | A creation ceiling (default 5/hour) caps the worst case during a novel outage |
| Failure | Every failure path returns after a local log; `emit` falls back to `logging.Handler.handleError` and never raises into the app |
| Data | Allow-list only — a field is transmitted because it was named, not because no rule removed it |

### It is off by default, and stays off

`GITHUB_ISSUE_REPORTER` is inert unless **both** `ENABLED` and `REPO` are set. There is deliberately no default repository and no fallback to "this repo": error reports are application data and `bamr87/barodybroject` is **public**. Filing into a public tracker requires a separate, explicitly named `ALLOW_PUBLIC_REPO` override, and the reporter keeps warning for as long as that override is active.

### Redaction is an allow-list, not a denylist

Only fields named in `ALLOWED_REQUEST_HEADERS` / `ALLOWED_REQUEST_FIELDS` / `ALLOWED_USER_ATTRIBUTES` are ever transmitted. `Authorization`, `Cookie`, the session, the query string and every form field are absent because they were never added. That distinction is the point: a denylist fails open on the field nobody thought of, and this application handles OpenAI keys and user accounts. Defaults transmit no form data at all and no username or email — `ALLOWED_USER_ATTRIBUTES = ("pk",)`.

Frame locals are excluded (`INCLUDE_FRAME_LOCALS = False`); Django's traceback machinery can surface settings values and credentials through them. Values named in `SCRUB_SETTINGS`, plus the reporter's own token, are replaced wherever they appear in the body — a backstop for a credential arriving by an unpredicted route, not a substitute for the allow-list.

### Consider a hosted tracker first

Sentry or Rollbar solve this with redaction, deduplication, rate limiting and release tracking already built and audited, and would not put application error data in an issue tracker at all. This feature exists because #59 asked specifically for the GitHub flow.

## 🧪 Testing

`src/parodynews/tests/test_error_reporting.py` — capture and redaction, fingerprint dedupe (including the cross-process marker lookup), the rate-limit ceiling, the public-repo refusal, off-by-default inertness, swallowed API failures, and that `emit` returns immediately while the API hangs.

`python manage.py check` is the one to run first by hand: it exercises the `dictConfig` import path that attaching the handler in `LOGGING` introduces.

## ⚠️ Breaking changes and migration

None. No migrations, no new required configuration. The handler is attached to `django.request` unconditionally and does nothing for anyone who has not configured it, but it is the change that touches every process's startup — hence the `manage.py check` note above.

Known limitation, called out rather than hidden: in-memory dedupe state is per process, so multiple workers could briefly race to file the same defect. The marker lookup closes the window in the common case; a true simultaneous race could still produce two issues. A distributed lock is the fix if that ever bites.

## 🔗 Related resources

- Issues: #59 (deployment-failure flood), #60 (specification)
- Handler: `src/parodynews/utils/error_reporting.py`
- Settings: `src/barodybroject/settings/base.py` → `GITHUB_ISSUE_REPORTER`, `LOGGING`
- Configuration guide: [`docs/configuration/error-reporting.md`](../../configuration/error-reporting.md)
