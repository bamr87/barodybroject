# Automatic GitHub issue reporting

Unhandled Django exceptions can be filed automatically as **deduplicated GitHub
issues**, so runtime errors become tracked work without manual transcription.

**It is off by default and stays off until you configure a target.** Read the
[Data handling](#data-handling) section before enabling it — what gets sent is a
data-handling decision before it is an engineering one.

## Before you enable it

Consider a hosted error tracker (Sentry, Rollbar) first. It solves this problem
with redaction, deduplication, rate limiting and release tracking already built
and audited, and it would not put application error data in an issue tracker at
all. This feature exists because [#59](https://github.com/bamr87/barodybroject/issues/59)
asked specifically for the GitHub flow; if a hosted tracker is acceptable, it is
less work and lower risk.

## How it works

A `logging` handler on the `django.request` logger — the same hook Django's
built-in `AdminEmailHandler` uses. Not middleware: a handler also catches
exceptions that never traverse the middleware chain (management commands,
background tasks, and errors raised while rendering a response).

Filing happens on a background worker, never on the request path. A GitHub
outage cannot turn a 500 into a timeout, and a failure inside the reporter is
logged locally and never surfaces to a user.

| Concern | Behaviour |
| --- | --- |
| Identity | Fingerprint = exception type + `(file, function, line)` of every frame. The exception **message is excluded**, so the same defect carrying different row ids is one issue, not thousands. |
| Repeats | The one issue is commented on, at most once per dedupe window. A second issue is never opened. |
| Restarts | The fingerprint is written into the issue body as an HTML comment, so a new process finds the existing issue instead of re-filing. |
| Volume | A rolling-window ceiling on issues **created**. Deduplicated repeats are free, so the ceiling protects against a burst of *distinct* failures — what a bad deploy looks like. |
| Exceeding the ceiling | Drops to local logging **and records that it did so**. A silent ceiling is indistinguishable from a broken reporter. |

## Configuration

Set `GITHUB_ISSUE_REPORTER` in settings, or the environment variables below.

| Key | Env var | Default | Meaning |
| --- | --- | --- | --- |
| `ENABLED` | `GITHUB_ISSUE_REPORTER_ENABLED` | `False` | Master switch. |
| `REPO` | `GITHUB_ISSUE_REPORTER_REPO` | `None` | `owner/name` of the tracker. **No default, and no fallback to this repository.** Unset means the reporter logs locally and does nothing else. |
| `TOKEN` | `GITHUB_ISSUE_REPORTER_TOKEN` | `None` | A token with `issues: write` on `REPO`. |
| `ALLOW_PUBLIC_REPO` | `GITHUB_ISSUE_REPORTER_ALLOW_PUBLIC_REPO` | `False` | Required to file into a **public** repository. See below. |
| `ALLOWED_REQUEST_HEADERS` | — | `Content-Type`, `Accept`, `Accept-Language` | Allowlist. Only these headers are transmitted. |
| `ALLOWED_REQUEST_FIELDS` | — | `()` | Allowlist of POST/GET keys. Empty means **no** form data is transmitted. |
| `ALLOWED_USER_ATTRIBUTES` | — | `("pk",)` | Allowlist of user attributes. Username and email are **not** included by default. |
| `INCLUDE_FRAME_LOCALS` | — | `False` | Stack frame locals. Leave off — see below. |
| `SCRUB_SETTINGS` | — | `("SECRET_KEY",)` | Setting **values** replaced with `[redacted]` wherever they appear. |
| `DEDUPE_WINDOW_SECONDS` | `GITHUB_ISSUE_REPORTER_DEDUPE_WINDOW` | `86400` | How often a recurring error may add a comment. |
| `RATE_LIMIT_MAX_ISSUES` | `GITHUB_ISSUE_REPORTER_RATE_LIMIT` | `5` | Issues created per window. |
| `RATE_LIMIT_WINDOW_SECONDS` | `GITHUB_ISSUE_REPORTER_RATE_WINDOW` | `3600` | The window. |
| `ASYNC` | — | `True` | Off-request-path delivery. Only set `False` in tests. |
| `LABELS` | — | `("bug", "auto-reported")` | Applied to filed issues, and used to scope the existing-issue lookup. |

### Minimal working configuration

```bash
export GITHUB_ISSUE_REPORTER_ENABLED=true
export GITHUB_ISSUE_REPORTER_REPO="your-org/your-private-tracker"
export GITHUB_ISSUE_REPORTER_TOKEN="ghp_..."
```

## Data handling

### The target should be private

`bamr87/barodybroject` is **public**. Filing application errors into a public
issue tracker publishes them to anyone. The reporter therefore **refuses a public
target repository** unless you also set `ALLOW_PUBLIC_REPO`, and logs a warning
for as long as that override is active. The safe target is a private tracker.

### Redaction is an allowlist, not a denylist

Only fields named in `ALLOWED_REQUEST_HEADERS` / `ALLOWED_REQUEST_FIELDS` /
`ALLOWED_USER_ATTRIBUTES` are ever transmitted. `Authorization`, `Cookie`, the
session, the query string and every form field are absent because they were
never added — not because a rule removed them.

That distinction matters: a denylist fails open on the field nobody thought of,
and this application handles OpenAI keys and user accounts. A header invented
next year is safe under an allowlist and leaky under a denylist.

### Frame locals are excluded

Django's traceback machinery can surface settings values and credentials through
frame locals. `INCLUDE_FRAME_LOCALS` is `False` and should stay that way; turning
it on adds a warning banner to every issue body.

### Scrubbing is defence in depth

Values named in `SCRUB_SETTINGS` (and the reporter's own token) are replaced
wherever they appear in the body. This is a backstop for a credential arriving
by a route nobody predicted — for example inside an exception message — not a
substitute for the allowlist.

### Adding a field to the allowlist

Adding a key to `ALLOWED_REQUEST_FIELDS` transmits that field's value verbatim
for every reported error. Confirm it can never hold a credential, a token, or
personal data before you add it.

## Testing

```bash
cd src && pytest parodynews/tests/test_error_reporting.py -v
```

No test makes a network call; every one injects a fake client, and one test
replaces the `github` module with a booby trap that fails if the real client is
ever constructed.

## Related

- [`src/parodynews/utils/error_reporting.py`](../../src/parodynews/utils/error_reporting.py) — the implementation
- [`docs/SECURITY_DOCUMENTATION.md`](../SECURITY_DOCUMENTATION.md)
- Existing auto-filer precedent and its failure mode: the unattended
  `Deployment failure: <sha>` issues (#139, #141, #145, #148, #150, #152, #153,
  #163). Deduplication and rate limiting exist so this feature does not repeat
  that.
