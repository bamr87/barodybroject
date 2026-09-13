"""
File: test_error_reporting.py
Description: Tests for the GitHub issue error reporter
Author: Barodybroject Team
Created: 2026-08-29
Version: 1.0.0

Dependencies:
- django
- pytest (optional)

Usage: python manage.py test parodynews.tests.test_error_reporting

NO TEST HERE MAKES A NETWORK CALL. Every one injects a fake client through
`client_factory`; the real `github` import in `GitHubIssueReporter._get_repo` is
never reached. `test_no_network_client_is_ever_constructed` pins that.

The data-handling assertions come first, in the order the issue ranks them,
because they are the ones that decide whether this feature is safe to ship at
all: this repository is public, and an error reporter that leaks is worse than
no error reporter.
"""

import logging
import sys
import time
import unittest.mock as mock

from django.conf import settings
from django.test import RequestFactory, SimpleTestCase

from parodynews.utils import error_reporting
from parodynews.utils.error_reporting import (
    DEFAULTS,
    GitHubIssueHandler,
    GitHubIssueReporter,
    RateLimiter,
    build_issue_body,
    fingerprint_exception,
    redact_request,
)


# --------------------------------------------------------------------------- #
# fakes — the whole GitHub surface this module touches, and nothing else
# --------------------------------------------------------------------------- #
class FakeIssue:
    def __init__(self, number, title, body, labels):
        self.number = number
        self.title = title
        self.body = body
        self.labels = labels
        self.comments = []

    def create_comment(self, body):
        self.comments.append(body)
        return body


class FakeRepo:
    def __init__(self, private=True, seed_issues=(), fail_on_create=None):
        self.private = private
        self.issues = list(seed_issues)
        self.create_calls = 0
        self.fail_on_create = fail_on_create

    def create_issue(self, title, body, labels=None):
        self.create_calls += 1
        if self.fail_on_create:
            raise self.fail_on_create
        issue = FakeIssue(len(self.issues) + 1, title, body, labels or [])
        self.issues.append(issue)
        return issue

    def get_issues(self, state=None, labels=None):
        return list(self.issues)

    def get_issue(self, number):
        for issue in self.issues:
            if issue.number == number:
                return issue
        raise KeyError(number)


def fake_client(repo):
    class FakeClient:
        def get_repo(self, name):
            return repo

    return lambda: FakeClient()


BASE_CONFIG = {
    "ENABLED": True,
    "REPO": "acme/private-tracker",
    "TOKEN": "not-a-real-token",
    "ASYNC": False,
}


def make_reporter(repo=None, **overrides):
    repo = repo if repo is not None else FakeRepo(private=True)
    config = dict(BASE_CONFIG, **overrides)
    return GitHubIssueReporter(config=config, client_factory=fake_client(repo)), repo


def record_from_exception(exc, request=None, logger_name="django.request"):
    """A LogRecord shaped exactly like the one `django.request` emits."""
    try:
        raise exc
    except type(exc):
        exc_info = sys.exc_info()
    record = logging.LogRecord(
        name=logger_name,
        level=logging.ERROR,
        pathname=__file__,
        lineno=1,
        msg="Internal Server Error: /boom",
        args=(),
        exc_info=exc_info,
    )
    if request is not None:
        record.request = request
    return record


def raise_with_secret_in_locals():
    """Raise from a frame whose locals hold the SECRET_KEY.

    Django's own `ExceptionReporter` would surface this through frame locals.
    The reporter must not.
    """
    secret_key = settings.SECRET_KEY
    api_key = "sk-super-secret-openai-key"
    assert secret_key and api_key
    raise ValueError("boom")


# --------------------------------------------------------------------------- #
# 1. off by default, and no default target
# --------------------------------------------------------------------------- #
class DefaultsTests(SimpleTestCase):
    def test_disabled_by_default(self):
        """A fresh clone with no configuration files nothing."""
        self.assertFalse(DEFAULTS["ENABLED"])

    def test_no_default_target_repository(self):
        self.assertIsNone(DEFAULTS["REPO"])

    def test_never_falls_back_to_this_repository(self):
        """The fallback that would make this dangerous must not exist.

        No repository slug is hard-coded anywhere in the module, so there is
        nothing for an unset `REPO` to fall back to.
        """
        with open(error_reporting.__file__.replace(".pyc", ".py")) as fh:
            text = fh.read()
        for slug in ("bamr87/", "barodybroject/"):
            self.assertNotIn(slug, text)

    def test_disabled_reporter_does_nothing(self):
        reporter, repo = make_reporter(ENABLED=False)
        self.assertIsNone(reporter.report(record_from_exception(ValueError("x"))))
        self.assertEqual(repo.create_calls, 0)

    def test_unset_repo_files_nothing(self):
        reporter, repo = make_reporter(REPO=None)
        with self.assertLogs("parodynews.utils.error_reporting", "WARNING") as logs:
            self.assertIsNone(reporter.report(record_from_exception(ValueError("x"))))
        self.assertEqual(repo.create_calls, 0)
        self.assertIn("no target repository", "\n".join(logs.output))

    def test_frame_locals_excluded_by_default(self):
        self.assertFalse(DEFAULTS["INCLUDE_FRAME_LOCALS"])


# --------------------------------------------------------------------------- #
# 2. the public-repository gate
# --------------------------------------------------------------------------- #
class PublicRepositoryGateTests(SimpleTestCase):
    def test_public_target_refused_without_the_override(self):
        reporter, repo = make_reporter(repo=FakeRepo(private=False))
        with self.assertLogs("parodynews.utils.error_reporting", "WARNING") as logs:
            self.assertIsNone(reporter.report(record_from_exception(ValueError("x"))))
        self.assertEqual(repo.create_calls, 0)
        self.assertIn("PUBLIC", "\n".join(logs.output))

    def test_public_target_allowed_only_with_the_named_override(self):
        reporter, repo = make_reporter(
            repo=FakeRepo(private=False), ALLOW_PUBLIC_REPO=True
        )
        with self.assertLogs("parodynews.utils.error_reporting", "WARNING") as logs:
            reporter.report(record_from_exception(ValueError("x")))
        self.assertEqual(repo.create_calls, 1)
        self.assertIn("ALLOW_PUBLIC_REPO is enabled", "\n".join(logs.output))

    def test_private_target_needs_no_override(self):
        reporter, repo = make_reporter(repo=FakeRepo(private=True))
        reporter.report(record_from_exception(ValueError("x")))
        self.assertEqual(repo.create_calls, 1)


# --------------------------------------------------------------------------- #
# 3. redaction — allowlist, not denylist
# --------------------------------------------------------------------------- #
class RedactionTests(SimpleTestCase):
    def _sensitive_request(self):
        return RequestFactory().post(
            "/checkout",
            {"password": "hunter2-not-in-the-issue", "note": "safe-note"},
            HTTP_AUTHORIZATION="Bearer tok-abcdef1234567890",
            HTTP_COOKIE="sessionid=sekrit-session-value-123",
            HTTP_ACCEPT="text/html",
        )

    def _body_for_sensitive_request(self, **overrides):
        request = self._sensitive_request()
        try:
            raise_with_secret_in_locals()
        except ValueError:
            exc_info = sys.exc_info()
        record = logging.LogRecord(
            "django.request", logging.ERROR, __file__, 1,
            "Internal Server Error: /checkout", (), exc_info,
        )
        record.request = request
        cfg = error_reporting.get_config(dict(BASE_CONFIG, **overrides))
        return build_issue_body(record, cfg, "deadbeefdeadbeef")

    def test_no_secret_reaches_the_issue_body(self):
        """The criterion, asserted as one test: password, Authorization header,
        session cookie and SECRET_KEY must all be absent."""
        body = self._body_for_sensitive_request()
        for secret in (
            "hunter2-not-in-the-issue",          # POST field
            "tok-abcdef1234567890",              # Authorization header
            "sekrit-session-value-123",          # session cookie
            settings.SECRET_KEY,                 # frame local
            "sk-super-secret-openai-key",        # frame local
        ):
            with self.subTest(secret=secret[:16]):
                self.assertNotIn(secret, body)

    def test_allowlisted_header_is_present(self):
        """Proves the allowlist actually transmits — that the test above is not
        passing merely because nothing is ever included."""
        body = self._body_for_sensitive_request(
            ALLOWED_REQUEST_HEADERS=("Accept",)
        )
        self.assertIn("text/html", body)

    def test_allowlisted_field_is_present_and_others_are_not(self):
        body = self._body_for_sensitive_request(ALLOWED_REQUEST_FIELDS=("note",))
        self.assertIn("safe-note", body)
        self.assertNotIn("hunter2-not-in-the-issue", body)

    def test_query_string_is_never_collected(self):
        request = RequestFactory().get("/search?token=leaky-query-token")
        data = redact_request(request, error_reporting.get_config(BASE_CONFIG))
        self.assertEqual(data["path"], "/search")
        self.assertNotIn("leaky-query-token", str(data))

    def test_unknown_header_is_excluded_without_being_named(self):
        """The point of an allowlist: a header nobody has thought of is safe."""
        request = RequestFactory().get("/", HTTP_X_INTERNAL_TOKEN="brand-new-secret")
        data = redact_request(request, error_reporting.get_config(BASE_CONFIG))
        self.assertNotIn("brand-new-secret", str(data))

    def test_traceback_is_included_so_the_issue_is_useful(self):
        body = self._body_for_sensitive_request()
        self.assertIn("ValueError", body)
        self.assertIn("raise_with_secret_in_locals", body)


# --------------------------------------------------------------------------- #
# 4. deduplication
# --------------------------------------------------------------------------- #
class DeduplicationTests(SimpleTestCase):
    def test_one_hundred_identical_exceptions_produce_one_issue(self):
        reporter, repo = make_reporter()
        numbers = set()
        for _ in range(100):
            try:
                raise_with_secret_in_locals()
            except ValueError:
                exc_info = sys.exc_info()
            record = logging.LogRecord(
                "django.request", logging.ERROR, __file__, 1, "boom", (), exc_info
            )
            numbers.add(reporter.report(record))
        self.assertEqual(repo.create_calls, 1)
        self.assertEqual(len(numbers), 1)

    def test_distinct_defects_get_distinct_issues(self):
        reporter, repo = make_reporter()
        reporter.report(record_from_exception(ValueError("a")))
        reporter.report(record_from_exception(KeyError("b")))
        self.assertEqual(repo.create_calls, 2)

    def test_the_message_does_not_affect_the_fingerprint(self):
        """Volatile values in the message must not fork the fingerprint —
        otherwise every occurrence carrying a row id files a new issue."""
        def boom(value):
            raise ValueError(f"row {value} exploded")

        prints = set()
        for value in (1, 2, 3):
            try:
                boom(value)
            except ValueError:
                prints.add(fingerprint_exception(sys.exc_info()))
        self.assertEqual(len(prints), 1)

    def test_an_issue_filed_by_a_previous_process_is_reused(self):
        """The in-memory cache dies with the worker; a restart must not re-file."""
        fingerprint = fingerprint_exception(
            record_from_exception(ValueError("x")).exc_info
        )
        seeded = FakeIssue(
            7, "old", error_reporting.MARKER_TEMPLATE.format(fingerprint=fingerprint), []
        )
        reporter, repo = make_reporter(repo=FakeRepo(private=True, seed_issues=[seeded]))
        self.assertEqual(reporter.report(record_from_exception(ValueError("x"))), 7)
        self.assertEqual(repo.create_calls, 0)

    def test_repeat_outside_the_window_comments_rather_than_refiling(self):
        reporter, repo = make_reporter(DEDUPE_WINDOW_SECONDS=0)
        reporter.report(record_from_exception(ValueError("x")))
        reporter.report(record_from_exception(ValueError("x")))
        self.assertEqual(repo.create_calls, 1)
        self.assertEqual(len(repo.issues[0].comments), 1)


# --------------------------------------------------------------------------- #
# 5. rate limiting
# --------------------------------------------------------------------------- #
class RateLimitTests(SimpleTestCase):
    def test_rolling_window_allows_then_blocks(self):
        limiter = RateLimiter(max_events=2, window_seconds=100)
        self.assertTrue(limiter.allow(now=0))
        self.assertTrue(limiter.allow(now=1))
        self.assertFalse(limiter.allow(now=2))
        # …and recovers once the window has passed.
        self.assertTrue(limiter.allow(now=200))

    def test_ceiling_stops_issue_creation_and_says_so(self):
        # DISTINCT exception types, so each is a distinct fingerprint. Ten
        # ValueErrors raised from the same line would dedupe to one issue and
        # never reach the limiter at all.
        distinct = [
            ValueError, KeyError, TypeError, IndexError, AttributeError,
            RuntimeError, OSError, ZeroDivisionError, NotImplementedError,
            ArithmeticError,
        ]
        reporter, repo = make_reporter(RATE_LIMIT_MAX_ISSUES=3)
        with self.assertLogs("parodynews.utils.error_reporting", "ERROR") as logs:
            for exc_type in distinct:
                reporter.report(record_from_exception(exc_type("boom")))
        self.assertEqual(repo.create_calls, 3)
        # Falling back to local logging must itself be recorded — a silent
        # ceiling is indistinguishable from a broken reporter.
        self.assertIn("rate limit reached", "\n".join(logs.output))

    def test_repeats_do_not_consume_the_budget(self):
        """A single error storming a thousand times must cost ONE slot."""
        reporter, repo = make_reporter(RATE_LIMIT_MAX_ISSUES=2)
        for _ in range(50):
            reporter.report(record_from_exception(ValueError("same")))
        reporter.report(record_from_exception(KeyError("other")))
        self.assertEqual(repo.create_calls, 2)


# --------------------------------------------------------------------------- #
# 6. failure of the reporter is never failure of the app
# --------------------------------------------------------------------------- #
class ApiFailureTests(SimpleTestCase):
    def test_create_issue_failure_is_swallowed_and_logged(self):
        reporter, repo = make_reporter(
            repo=FakeRepo(private=True, fail_on_create=RuntimeError("502 from GitHub"))
        )
        with self.assertLogs("parodynews.utils.error_reporting", "ERROR") as logs:
            self.assertIsNone(reporter.report(record_from_exception(ValueError("x"))))
        self.assertIn("failed to file issue", "\n".join(logs.output))

    def test_unreachable_github_is_swallowed(self):
        def exploding_factory():
            raise OSError("Name or service not known")

        reporter = GitHubIssueReporter(
            config=dict(BASE_CONFIG), client_factory=exploding_factory
        )
        with self.assertLogs("parodynews.utils.error_reporting", "ERROR"):
            self.assertIsNone(reporter.report(record_from_exception(ValueError("x"))))

    def test_handler_emit_never_raises(self):
        def exploding_factory():
            raise OSError("down")

        handler = GitHubIssueHandler(
            config=dict(BASE_CONFIG), client_factory=exploding_factory
        )
        try:
            with self.assertLogs("parodynews.utils.error_reporting", "ERROR"):
                handler.emit(record_from_exception(ValueError("x")))
        finally:
            handler.close()


# --------------------------------------------------------------------------- #
# 7. off the request path
# --------------------------------------------------------------------------- #
class RequestPathTests(SimpleTestCase):
    def test_emit_returns_immediately_when_the_api_hangs(self):
        """A GitHub outage must not become an application outage.

        With the client stubbed to hang for 5s, `emit` must still return
        promptly — the response is already on its way out.
        """
        started = []

        def hanging_factory():
            started.append(True)
            time.sleep(5)
            raise AssertionError("unreachable in this test")

        handler = GitHubIssueHandler(
            config=dict(BASE_CONFIG, ASYNC=True), client_factory=hanging_factory
        )
        try:
            begin = time.monotonic()
            handler.emit(record_from_exception(ValueError("x")))
            elapsed = time.monotonic() - begin
        finally:
            handler.close()
        self.assertLess(elapsed, 0.5, f"emit blocked for {elapsed:.2f}s")

    def test_synchronous_mode_is_opt_in(self):
        self.assertTrue(DEFAULTS["ASYNC"])


# --------------------------------------------------------------------------- #
# 8. no network, ever
# --------------------------------------------------------------------------- #
class NoNetworkTests(SimpleTestCase):
    def test_no_network_client_is_ever_constructed(self):
        """The real PyGithub client must never be built.

        `github` is replaced with a module whose `Github` raises, so if
        `_get_repo` ever falls through to the real client instead of using the
        injected factory, this test fails loudly rather than making a request.
        """
        booby_trap = mock.MagicMock()
        booby_trap.Github.side_effect = AssertionError(
            "a real GitHub client was constructed in a test"
        )
        with mock.patch.dict(sys.modules, {"github": booby_trap}):
            reporter, repo = make_reporter()
            reporter.report(record_from_exception(ValueError("x")))
        self.assertEqual(repo.create_calls, 1)
        booby_trap.Github.assert_not_called()

    def test_body_carries_the_dedupe_marker(self):
        reporter, repo = make_reporter()
        reporter.report(record_from_exception(ValueError("x")))
        self.assertRegex(repo.issues[0].body, error_reporting.MARKER_RE)


# --------------------------------------------------------------------------- #
# 9. the startup-ordering invariant this handler depends on
# --------------------------------------------------------------------------- #
class ImportSafetyTests(SimpleTestCase):
    """`settings.LOGGING` names this handler by dotted path, and Django
    configures logging inside `django.setup()` BEFORE `apps.populate()`.

    Importing the handler therefore imports `parodynews.utils.__init__` while
    the app registry is still empty. If any module in that package ever grows a
    module-level model import, the application stops booting with
    `AppRegistryNotReady` — an error that points nowhere near its cause. This
    test turns that latent coupling into a guarded invariant.
    """

    def test_utils_package_imports_no_models_at_module_level(self):
        import ast
        import pathlib

        def is_app_models(module, level):
            """An APP's models module — not `django.db.models`, which is just
            the ORM machinery and is safe to import before apps are populated."""
            if module.startswith("django."):
                return False
            if level > 0:  # relative: ..models, .models
                return module in ("models", "admin") or module.startswith("models.")
            return module.startswith("parodynews.models") or module == "parodynews.admin"

        package = pathlib.Path(error_reporting.__file__).parent
        offenders = []
        for path in sorted(package.glob("*.py")):
            tree = ast.parse(path.read_text(), filename=str(path))
            for node in tree.body:  # TOP LEVEL ONLY — nested imports are fine
                if isinstance(node, ast.ImportFrom):
                    if is_app_models(node.module or "", node.level):
                        offenders.append(
                            f"{path.name}: from {'.' * node.level}"
                            f"{node.module or ''} import ..."
                        )
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if is_app_models(alias.name, 0):
                            offenders.append(f"{path.name}: import {alias.name}")
        self.assertEqual(
            offenders,
            [],
            "module-level model import under parodynews/utils/ — this breaks "
            f"startup, because LOGGING imports this package: {offenders}",
        )

    def test_reporter_module_itself_has_no_heavy_imports(self):
        """PyGithub must not load in a process with the reporter switched off."""
        import ast
        import pathlib

        tree = ast.parse(pathlib.Path(error_reporting.__file__).read_text())
        top_level = set()
        for node in tree.body:
            if isinstance(node, ast.Import):
                top_level.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                top_level.add((node.module or "").split(".")[0])
        self.assertNotIn("github", top_level)
