---
title: "[Bug Fix] Scope the dependency gate to src/requirements.txt, and patch what it found"
type: "bugfix"
version: "0.4.0"
date: "2026-09-11"
author: "Barodybroject Team <team@example.com>"
reviewers: []
related_issues: ["#176"]
related_prs: ["#177"]
impact: "high"
breaking: false
severity: "high"
affected_versions: ["0.4.0"]
---

# Bug Fix: the dependency gate audited the scanners instead of the application

> **Summary**: `quality.sh dependency-scan` now passes `-r requirements.txt` to
> both `safety` and `pip-audit`. Making the gate real immediately surfaced
> advisories against four packages in this project's own dependency tree, so
> this change also patches them.

## 🐛 Problem Description

### Issue Summary

`.github/scripts/quality.sh dependency-scan` ran `safety check` and `pip-audit --desc` with **no `-r`**, which makes both of them whole-interpreter audits. In the `quality` job that interpreter holds only the lint and audit tools at scan time — `src/requirements.txt` is installed three steps later, by `Install quality analysis tools` — so the gate could never report an advisory against Django, djangorestframework, openai, boto3 or psycopg2.

Two consequences, and the quiet one is worse:

1. **It blocked merges.** `safety` pulls in `nltk`, which carries an advisory with no patched version. `pip-audit` flagged it and exited 1, failing every open PR since ~2026-09-03 on a package this repository does not depend on.
2. **It had never protected anything.** The gate was green-by-vacuum for its whole life, then red-by-accident.

### Affected Components

- **`.github/scripts/quality.sh`** — the `dependency-scan)` branch.
- **`src/requirements.txt`** — the file that should have been the audit's input, and which turned out to be carrying real advisories.
- **`.github/workflows/ci.yml`** — the `quality` job's `Run dependency scans` step (unchanged; it stays blocking).

## 🔧 Solution

### The scope fix

Both scanners are now invoked as `-r requirements.txt` from `src/`. The audited set is a declared artifact rather than a side effect of step ordering, so it stays correct if the job is ever reordered. The gating (non-report) invocations keep their teeth — no `continue-on-error`, no `|| true`.

The runtime `pip install --upgrade "setuptools>=83.0.0"` workaround is removed. It existed only to stop an environment-level advisory from masking project findings, which is precisely the bug being fixed, and `src/requirements.txt` pins `setuptools==83.0.0` itself.

### What the corrected gate found

Scoping the scan turned it red for the right reason. `safety` reported seven advisories against `Django` and `Markdown`; `pip-audit`, which also resolves the transitive tree, reported two more against `djangorestframework` and six against `cryptography`. All are patched here.

| Package | Was | Now | Why |
| --- | --- | --- | --- |
| `Django` | 5.1.15 | 5.2.17 | CVE-2026-48587, CVE-2026-6873, CVE-2026-8404 (fixed 5.2.15); CVE-2026-53877, CVE-2026-53878, CVE-2026-48588 (fixed 5.2.16). 5.2 is the current LTS. |
| `djangorestframework` | 3.15.2 | 3.18.1 | PYSEC-2026-3827, PYSEC-2026-3828 (fixed 3.17.2). 3.15 also predates official Django 5.2 support. |
| `Markdown` | 3.5.2 | 3.8.2 | CVE-2025-69534 — uncaught exception on malformed HTML (fixed 3.8.1). |
| `martor` | 1.6.44 | 1.8.2 | Not itself vulnerable: `martor <1.7` declares `Markdown<3.6`, so the Markdown patch is unreachable without it. |
| `fido2` | 1.2.0 | 2.2.1 | Not itself vulnerable: `fido2 1.2.0` declares `cryptography<45`, which pinned the transitive tree to 44.0.3 and its six open advisories (PYSEC-2026-2141, PYSEC-2026-35, PYSEC-2026-3552/3553/3554, GHSA-537c-gmf6-5ccf). |

The last two rows are the part worth reviewing: two packages are upgraded not for their own advisories but because their version caps made a patched dependency unreachable.

## 🧪 Verification

- `src/tests/test_dependency_scan_scope.py` asserts the CI contract: both scanners receive `-r requirements.txt`, the gating invocations are not silenced, `Run dependency scans` has no `continue-on-error`, and the `setuptools` workaround is gone. It fails on the pre-fix `quality.sh` and passes after.
- The test lives under `src/tests/` rather than the repository-root `test/` tree deliberately: CI runs pytest from `src/` against `src/pytest.ini`, whose `testpaths` are `parodynews/tests` and `tests`. A test in root `test/` is never collected by any workflow.
- Both scanners were run against the patched `src/requirements.txt` in a clean `python:3.11-slim` container — the same shape as the CI step. `pip-audit`: *No known vulnerabilities found*. `safety`: *0 vulnerabilities reported*.
- Full suite green on the upgraded dependency set (61 passed, 9 e2e deselected), and `manage.py check --deploy` reports the same seven pre-existing warnings as before the upgrade — no new errors.

## 📎 Related

- Issue #176 — the root cause behind the blocked-CI comments on #173, #174 and #175.
- `docs/ci-cd-pipeline.md` — documents the gate's new scope.
