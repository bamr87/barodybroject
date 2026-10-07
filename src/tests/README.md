# tests Directory

## Purpose

Project-level tests — the ones that describe the repository's own configuration rather than the behaviour of the `parodynews` Django application. Application tests live in `src/parodynews/tests/`.

This directory exists because `src/pytest.ini` already lists `tests` in its `testpaths`, and CI runs pytest from `src/` (`.github/scripts/run-pytest.sh`). A test placed here is therefore executed by the `Tests (Python 3.10/3.11/3.12)` jobs. A test placed in the repository-root `test/` tree is **not** — that path is only reachable through the root `pyproject.toml`, which no workflow uses.

## Contents

- `test_dependency_scan_scope.py`: CI contract for the `Quality and Security` dependency gate (issue #176) — asserts that `quality.sh dependency-scan` passes `-r requirements.txt` to both `safety` and `pip-audit`, that the gating (non-report) invocations are not silenced with `|| true`, that the `Run dependency scans` step has no `continue-on-error`, and that the obsolete runtime `setuptools` upgrade is gone. Pure stdlib, so it runs even where the application's dependencies are absent.

- `test_auth_stack_pins.py`: dependency contract for the auth stack (bamr87/bamr87#326) — asserts that `src/requirements.txt` floors `oauthlib` at 4.0.0 (the PYSEC-2026-4114 fix) and pins a `django-allauth` new enough to accept it, with all four extras kept. Pure stdlib.

## Usage

These tests run as part of the normal suite:

```bash
# from src/ — the same working directory CI uses
python -m pytest

# just this directory
python -m pytest tests/
```

## Notes

Keep tests here free of Django and database dependencies. They are meant to stay green in a bare interpreter so that a configuration regression is reported as a configuration failure, not as a collection error.
