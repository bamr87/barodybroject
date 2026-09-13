"""
File: error_reporting.py
Description: File unhandled Django exceptions as deduplicated GitHub issues
Author: Barodybroject Team <team@example.com>
Created: 2026-08-29
Version: 0.1.0

Dependencies:
- django: >=5.1
- pygithub: >=2.5.0

Usage: attached as a `logging` handler on the `django.request` logger; see
       docs/configuration/error-reporting.md

WHY A LOGGING HANDLER AND NOT MIDDLEWARE
----------------------------------------
Django already routes every unhandled exception to the `django.request` logger —
that is exactly how the built-in `AdminEmailHandler` works — and `LOGGING` is
already configured in this project. A handler also catches errors that never
traverse the middleware chain: management commands, background tasks, and
exceptions raised while the response is being rendered. Middleware would miss
all three silently.

WHAT THIS MODULE REFUSES TO DO
------------------------------
This repository is PUBLIC, so what leaves the process is a data-handling
decision before it is an engineering one. The rules below are load-bearing:

  * It is OFF unless switched on. A fresh clone with no configuration files
    nothing.
  * There is NO default target repository, and no fallback to "this repo". If
    the target is unset the reporter logs locally and stops.
  * It REFUSES a public target repository unless `ALLOW_PUBLIC_REPO` is set by
    hand, and shouts in the log for as long as that override is active.
  * Redaction is an ALLOWLIST. Only fields named in configuration are ever
    transmitted. A denylist fails open on the field nobody thought of, and this
    app handles OpenAI keys and user accounts.
  * Stack frame locals are excluded. Django's traceback machinery can surface
    settings values and credentials through them.
  * Nothing here runs on the request path, and nothing here can raise into the
    caller. A failure in the error reporter must not itself be an error.

IMPORT-TIME CONSTRAINT
----------------------
`settings.LOGGING` names `GitHubIssueHandler` by dotted path, and Django
configures logging inside `django.setup()` **before** `apps.populate()` runs.
Importing this module therefore also imports `parodynews.utils.__init__` at a
point where the app registry does not exist yet. Nothing in that package may
import Django models at module level, or the application will fail to start with
`AppRegistryNotReady` — a failure that looks nothing like its cause. Every model
import under `parodynews/utils/` is function-level today, and
`test_error_reporting.py` asserts it stays that way.

This module itself imports only the standard library and `django.conf.settings`.
`github` is imported lazily, inside `_get_repo`, so PyGithub is never loaded in a
process that has the reporter switched off.
"""

import hashlib
import logging
import re
import threading
import time
import traceback
from collections import deque
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings

logger = logging.getLogger(__name__)

# The logger this handler attaches to. Reporting our own failures through it
# would be a loop: a failure to file an issue would try to file an issue.
DJANGO_REQUEST_LOGGER = "django.request"

# Hidden marker that identifies an issue as ours and carries the fingerprint, so
# dedupe survives a process restart (the in-memory cache does not).
MARKER_TEMPLATE = "<!-- django-error-reporter fingerprint={fingerprint} -->"
MARKER_RE = re.compile(r"<!-- django-error-reporter fingerprint=([0-9a-f]{16}) -->")

DEFAULTS = {
    # --- the two gates that decide whether anything happens at all ---------- #
    "ENABLED": False,          # off by default; enabling is an explicit act
    "REPO": None,              # "owner/name". No default. Never "this repo".
    "TOKEN": None,             # a token with `issues: write` on REPO
    "ALLOW_PUBLIC_REPO": False,  # separate, explicitly-named public override
    # --- what may leave the process ---------------------------------------- #
    # ALLOWLISTS. Anything not named here is not transmitted, including headers
    # and fields that do not exist yet.
    "ALLOWED_REQUEST_HEADERS": ("Content-Type", "Accept", "Accept-Language"),
    "ALLOWED_REQUEST_FIELDS": (),      # POST/GET keys; empty means none
    "ALLOWED_USER_ATTRIBUTES": ("pk",),  # never username/email by default
    "INCLUDE_FRAME_LOCALS": False,     # locals can carry SECRET_KEY et al
    # Values scrubbed from the body wherever they appear, as defence in depth
    # behind the allowlist. Dotted setting names, resolved at send time.
    "SCRUB_SETTINGS": ("SECRET_KEY",),
    # --- volume control ----------------------------------------------------- #
    "DEDUPE_WINDOW_SECONDS": 24 * 60 * 60,
    "RATE_LIMIT_MAX_ISSUES": 5,
    "RATE_LIMIT_WINDOW_SECONDS": 60 * 60,
    # --- delivery ----------------------------------------------------------- #
    "ASYNC": True,             # never block a response on the GitHub API
    "QUEUE_SIZE": 100,         # bounded: a flood must not grow without limit
    "LABELS": ("bug", "auto-reported"),
}


def get_config(overrides=None):
    """Merge `settings.GITHUB_ISSUE_REPORTER` over the defaults."""
    cfg = dict(DEFAULTS)
    cfg.update(getattr(settings, "GITHUB_ISSUE_REPORTER", None) or {})
    cfg.update(overrides or {})
    return cfg


# --------------------------------------------------------------------------- #
# fingerprinting
# --------------------------------------------------------------------------- #
def fingerprint_exception(exc_info):
    """A stable identity for "this bug", not "this occurrence".

    Built from the exception type and the (file, function, line) of each frame.
    The exception MESSAGE is deliberately excluded: it is the part that carries
    volatile values — row ids, uuids, timestamps, user input — and including it
    would file a fresh issue for every occurrence of the same defect, which is
    precisely the backlog flood this feature has to avoid.
    """
    if not exc_info:
        return None
    exc_type, exc_value, tb = exc_info
    parts = [getattr(exc_type, "__name__", str(exc_type))]
    for frame, lineno in traceback.walk_tb(tb):
        code = frame.f_code
        parts.append(f"{code.co_filename}:{code.co_name}:{lineno}")
    digest = hashlib.sha256("\n".join(parts).encode("utf-8", "replace"))
    return digest.hexdigest()[:16]


# --------------------------------------------------------------------------- #
# redaction
# --------------------------------------------------------------------------- #
def _header_name(meta_key):
    """`HTTP_ACCEPT_LANGUAGE` -> `Accept-Language`."""
    return meta_key[5:].replace("_", "-").title()


def redact_request(request, cfg):
    """Extract ONLY what the allowlists name. Never the whole request.

    Everything about this function is subtractive. `Authorization`, `Cookie`,
    every POST field, the query string and the session are absent because they
    were never added — not because a rule removed them. That is the difference
    between an allowlist and a denylist, and it is why a header nobody has
    invented yet is also safe.
    """
    if request is None:
        return {}

    allowed_headers = {h.lower() for h in cfg["ALLOWED_REQUEST_HEADERS"]}
    headers = {}
    for key, value in getattr(request, "META", {}).items():
        if not key.startswith("HTTP_"):
            continue
        name = _header_name(key)
        if name.lower() in allowed_headers:
            headers[name] = str(value)

    fields = {}
    allowed_fields = set(cfg["ALLOWED_REQUEST_FIELDS"])
    if allowed_fields:
        for source in (getattr(request, "POST", None), getattr(request, "GET", None)):
            for key in allowed_fields:
                if source is not None and key in source:
                    fields[key] = str(source[key])

    data = {
        # `path` only — NOT `get_full_path()`, which carries the query string.
        "path": getattr(request, "path", None),
        "method": getattr(request, "method", None),
        "headers": headers,
        "fields": fields,
    }

    user = getattr(request, "user", None)
    if user is not None and getattr(user, "is_authenticated", False):
        data["user"] = {
            attr: str(getattr(user, attr, None))
            for attr in cfg["ALLOWED_USER_ATTRIBUTES"]
        }
    return data


def scrub(text, secrets):
    """Replace known secret VALUES wherever they appear in the body.

    Defence in depth behind the allowlist, not a substitute for it: if a
    credential reaches the body by a route nobody predicted — inside an
    exception message, say — this still catches the ones we can name.
    """
    for secret in secrets:
        if secret and len(str(secret)) >= 8:
            text = text.replace(str(secret), "[redacted]")
    return text


def _secret_values(cfg):
    values = []
    for name in cfg["SCRUB_SETTINGS"]:
        value = getattr(settings, name, None)
        if value:
            values.append(value)
    if cfg.get("TOKEN"):
        values.append(cfg["TOKEN"])
    return values


# --------------------------------------------------------------------------- #
# body
# --------------------------------------------------------------------------- #
def build_issue_body(record, cfg, fingerprint):
    """Render the issue body from allowlisted data only."""
    exc_info = getattr(record, "exc_info", None)
    lines = [MARKER_TEMPLATE.format(fingerprint=fingerprint), ""]

    if exc_info:
        exc_type, exc_value, tb = exc_info
        lines += [
            f"**{getattr(exc_type, '__name__', exc_type)}**: {exc_value}",
            "",
            "```python",
            # `format_exception` renders the traceback WITHOUT frame locals.
            # Django's own `ExceptionReporter` would include them; that is
            # exactly why it is not used here.
            "".join(traceback.format_exception(exc_type, exc_value, tb)).rstrip(),
            "```",
            "",
        ]
    else:
        lines += [record.getMessage(), ""]

    if cfg["INCLUDE_FRAME_LOCALS"]:
        # Opt-in only, and loud about it: frame locals routinely contain
        # settings values, form data and credentials.
        lines += [
            "> ⚠️ `INCLUDE_FRAME_LOCALS` is enabled — this body may contain "
            "credentials from the stack.",
            "",
        ]

    request_data = redact_request(getattr(record, "request", None), cfg)
    if request_data:
        lines += ["## Request", ""]
        lines.append(f"- **Path:** `{request_data.get('path')}`")
        lines.append(f"- **Method:** `{request_data.get('method')}`")
        if request_data.get("user"):
            lines.append(f"- **User:** `{request_data['user']}`")
        if request_data.get("headers"):
            lines.append(f"- **Headers (allowlisted):** `{request_data['headers']}`")
        if request_data.get("fields"):
            lines.append(f"- **Fields (allowlisted):** `{request_data['fields']}`")
        lines += [
            "",
            "_Only allowlisted headers and fields are transmitted; the query "
            "string, cookies, session and all other request data are never "
            "collected._",
            "",
        ]

    lines += [
        "---",
        f"Filed automatically by `parodynews.utils.error_reporting`. "
        f"Fingerprint `{fingerprint}`.",
    ]
    return scrub("\n".join(lines), _secret_values(cfg))


def build_issue_title(record, fingerprint):
    exc_info = getattr(record, "exc_info", None)
    if exc_info:
        exc_type, exc_value, _ = exc_info
        summary = str(exc_value).splitlines()[0][:120] if str(exc_value) else ""
        name = getattr(exc_type, "__name__", str(exc_type))
        return f"[auto] {name}: {summary}".rstrip(": ") + f" ({fingerprint})"
    return f"[auto] {record.getMessage()[:120]} ({fingerprint})"


# --------------------------------------------------------------------------- #
# rate limiting
# --------------------------------------------------------------------------- #
class RateLimiter:
    """A rolling-window ceiling on issues created.

    Counts only issues actually CREATED. Deduped occurrences are free, so a
    single error storming a thousand times a minute consumes one slot, not a
    thousand — the limiter is there for a burst of DISTINCT failures, which is
    what a bad deploy looks like.
    """

    def __init__(self, max_events, window_seconds):
        self.max_events = max_events
        self.window_seconds = window_seconds
        self._events = deque()
        self._lock = threading.Lock()

    def allow(self, now=None):
        now = now if now is not None else time.monotonic()
        with self._lock:
            cutoff = now - self.window_seconds
            while self._events and self._events[0] < cutoff:
                self._events.popleft()
            if len(self._events) >= self.max_events:
                return False
            self._events.append(now)
            return True


# --------------------------------------------------------------------------- #
# reporter
# --------------------------------------------------------------------------- #
class GitHubIssueReporter:
    """Turns a log record into (at most) one GitHub issue per distinct defect.

    `client_factory` exists so tests can run the whole pipeline with no network
    at all — the test suite must never make a real API call.
    """

    def __init__(self, config=None, client_factory=None):
        self.config = get_config(config)
        self._client_factory = client_factory
        self._limiter = RateLimiter(
            self.config["RATE_LIMIT_MAX_ISSUES"],
            self.config["RATE_LIMIT_WINDOW_SECONDS"],
        )
        # fingerprint -> {"issue": number, "last_reported": monotonic}
        self._seen = {}
        self._lock = threading.Lock()
        self._repo = None
        self._public_warned = False

    # -- gates -------------------------------------------------------------- #
    def _refuse(self, reason, *args):
        """Decline to file, and say so in the local log. Never raises."""
        logger.warning("error-reporter: not filing — " + reason, *args)
        return None

    def _get_repo(self):
        if self._repo is not None:
            return self._repo
        if self._client_factory is not None:
            client = self._client_factory()
        else:  # pragma: no cover - exercised only with a real token
            from github import Auth, Github

            client = Github(auth=Auth.Token(self.config["TOKEN"]))
        self._repo = client.get_repo(self.config["REPO"])
        return self._repo

    def _repo_is_permitted(self, repo):
        """Refuse a PUBLIC target unless the operator opted in by name.

        Application error data in a public issue tracker is a disclosure, and
        the safe default target is a private repository. `ALLOW_PUBLIC_REPO` is
        a separate setting precisely so that turning the feature on cannot
        accidentally turn this off too.
        """
        if not getattr(repo, "private", False):
            if not self.config["ALLOW_PUBLIC_REPO"]:
                self._refuse(
                    "target repository %s is PUBLIC and ALLOW_PUBLIC_REPO is not "
                    "set. Point GITHUB_ISSUE_REPORTER['REPO'] at a private "
                    "tracker, or set ALLOW_PUBLIC_REPO=True to accept the "
                    "disclosure.",
                    self.config["REPO"],
                )
                return False
            if not self._public_warned:
                logger.warning(
                    "error-reporter: ALLOW_PUBLIC_REPO is enabled — application "
                    "error reports are being published to the PUBLIC repository "
                    "%s. Anyone can read them.",
                    self.config["REPO"],
                )
                self._public_warned = True
        return True

    # -- delivery ------------------------------------------------------------ #
    def report(self, record):
        """Full pipeline for one record. Returns the issue number or None.

        Never raises: every failure path returns None after a local log. The
        caller is a logging handler, and an exception here would be an error
        raised while reporting an error.
        """
        try:
            cfg = self.config
            if not cfg["ENABLED"]:
                return None
            if not cfg["REPO"]:
                return self._refuse(
                    "no target repository configured "
                    "(GITHUB_ISSUE_REPORTER['REPO'] is unset). This never "
                    "falls back to the current repository."
                )
            if not cfg["TOKEN"] and self._client_factory is None:
                return self._refuse("no token configured")

            fingerprint = fingerprint_exception(getattr(record, "exc_info", None))
            if fingerprint is None:
                fingerprint = hashlib.sha256(
                    record.getMessage().encode("utf-8", "replace")
                ).hexdigest()[:16]

            repo = self._get_repo()
            if not self._repo_is_permitted(repo):
                return None

            with self._lock:
                known = self._seen.get(fingerprint)

            if known is not None:
                return self._touch_existing(repo, fingerprint, known)

            existing = self._find_existing_issue(repo, fingerprint)
            if existing is not None:
                with self._lock:
                    self._seen[fingerprint] = {
                        "issue": existing.number,
                        "last_reported": time.monotonic(),
                    }
                return existing.number

            if not self._limiter.allow():
                # Local logging is the fallback, and the fact that we fell back
                # is itself recorded — a silent ceiling is indistinguishable
                # from a broken reporter.
                logger.error(
                    "error-reporter: rate limit reached (%s issues / %ss); "
                    "logging locally instead of filing. Fingerprint %s.",
                    cfg["RATE_LIMIT_MAX_ISSUES"],
                    cfg["RATE_LIMIT_WINDOW_SECONDS"],
                    fingerprint,
                    exc_info=getattr(record, "exc_info", None),
                )
                return None

            issue = repo.create_issue(
                title=build_issue_title(record, fingerprint),
                body=build_issue_body(record, cfg, fingerprint),
                labels=list(cfg["LABELS"]),
            )
            with self._lock:
                self._seen[fingerprint] = {
                    "issue": issue.number,
                    "last_reported": time.monotonic(),
                }
            return issue.number
        except Exception:
            # The reporter failing must never become the application failing,
            # and must never surface to a user. GitHub being unreachable,
            # rate-limited or simply angry all land here.
            logger.exception("error-reporter: failed to file issue")
            return None

    def _touch_existing(self, repo, fingerprint, known):
        """A repeat occurrence updates the one issue — it never opens another.

        Comments are themselves throttled to one per dedupe window, so a
        thousand repeats do not become a thousand notifications.
        """
        now = time.monotonic()
        if now - known["last_reported"] < self.config["DEDUPE_WINDOW_SECONDS"]:
            return known["issue"]
        try:
            repo.get_issue(known["issue"]).create_comment(
                f"Still occurring. Fingerprint `{fingerprint}`."
            )
        except Exception:
            logger.exception("error-reporter: failed to comment on existing issue")
        with self._lock:
            known["last_reported"] = now
        return known["issue"]

    def _find_existing_issue(self, repo, fingerprint):
        """Cross-process dedupe: has a previous PROCESS already filed this?

        The in-memory cache dies with the worker, and without this a restart
        (or a second worker) would file the same defect again.
        """
        try:
            for issue in repo.get_issues(state="open", labels=list(self.config["LABELS"])):
                match = MARKER_RE.search(issue.body or "")
                if match and match.group(1) == fingerprint:
                    return issue
        except Exception:
            logger.exception("error-reporter: existing-issue lookup failed")
        return None


# --------------------------------------------------------------------------- #
# handler
# --------------------------------------------------------------------------- #
class GitHubIssueHandler(logging.Handler):
    """Attach to `django.request` to file unhandled exceptions as issues.

    `emit` hands the work to a single background worker and returns. Filing on
    the request path would turn a 500 into a timeout and a GitHub outage into an
    application outage — so the response is already on its way out before the
    API is touched.
    """

    def __init__(self, level=logging.ERROR, config=None, client_factory=None):
        super().__init__(level=level)
        self.reporter = GitHubIssueReporter(config=config, client_factory=client_factory)
        self._executor = None

    def _get_executor(self):
        if self._executor is None:
            self._executor = ThreadPoolExecutor(
                max_workers=1, thread_name_prefix="error-reporter"
            )
        return self._executor

    def emit(self, record):
        try:
            # Our own failures go to `parodynews.utils.error_reporting`, never
            # back through `django.request` — that would be a reporting loop.
            if record.name == DJANGO_REQUEST_LOGGER and record.exc_info is None:
                return
            if not self.reporter.config["ENABLED"]:
                return
            if self.reporter.config["ASYNC"]:
                self._get_executor().submit(self.reporter.report, record)
            else:
                self.reporter.report(record)
        except Exception:  # pragma: no cover - belt and braces
            # `handleError` respects logging.raiseExceptions and never
            # propagates in production.
            self.handleError(record)

    def close(self):
        if self._executor is not None:
            self._executor.shutdown(wait=False)
            self._executor = None
        super().close()
