"""CI contract: the dependency gate audits this project's declared dependencies.

Regression guard for #176. `quality.sh dependency-scan` used to run
`safety check` and `pip-audit --desc` with no `-r`, which makes both of them
whole-interpreter audits. In the `quality` job that interpreter holds only the
lint and audit tools at scan time -- `src/requirements.txt` is installed three
steps later -- so the gate could never report an advisory against Django,
openai, boto3 or psycopg2, and it failed every PR on `nltk`, a transitive
dependency of `safety` itself, for an advisory with no patched version.

These assertions are pure stdlib on purpose: they describe the shape of the CI
configuration, so they must run even where the application's own dependencies
are not installed.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
QUALITY_SH = REPO_ROOT / ".github" / "scripts" / "quality.sh"
CI_YML = REPO_ROOT / ".github" / "workflows" / "ci.yml"
REQUIREMENTS = REPO_ROOT / "src" / "requirements.txt"

SCANNERS = ("safety", "pip-audit")


def dependency_scan_branch() -> list[str]:
    """The body of the ``dependency-scan)`` case branch in quality.sh."""
    lines = QUALITY_SH.read_text(encoding="utf-8").splitlines()
    start = next(
        (
            i
            for i, line in enumerate(lines)
            if re.fullmatch(r"\s*dependency-scan\)\s*", line)
        ),
        None,
    )
    assert start is not None, "quality.sh no longer has a dependency-scan) branch"

    body: list[str] = []
    for line in lines[start + 1 :]:
        if line.strip() == ";;":
            return body
        body.append(line)
    raise AssertionError("the dependency-scan) branch is not terminated by ';;'")


def commands() -> list[str]:
    """Executable lines of the branch, comments and blanks removed."""
    return [
        stripped
        for line in dependency_scan_branch()
        if (stripped := line.strip()) and not stripped.startswith("#")
    ]


def scanner_calls(scanner: str) -> list[str]:
    return [c for c in commands() if c.startswith(f"{scanner} ")]


def is_report_call(call: str) -> bool:
    """Report-writing invocations produce the upload artifacts, not the verdict."""
    return "--output" in call or "--json" in call


def test_branch_runs_from_src_so_requirements_txt_resolves():
    """`-r requirements.txt` is only correct because the branch cds into src/."""
    assert "cd src" in commands(), "dependency-scan no longer cds into src/"
    assert REQUIREMENTS.is_file(), "src/requirements.txt is missing"


def test_every_scanner_call_is_scoped_to_the_declared_requirements():
    for scanner in SCANNERS:
        calls = scanner_calls(scanner)
        assert calls, f"the dependency-scan branch no longer invokes {scanner}"
        for call in calls:
            assert "-r requirements.txt" in call, (
                f"{scanner} is invoked without '-r requirements.txt', so it audits the "
                f"whole interpreter rather than this project's dependencies: {call}"
            )


def test_the_gating_calls_keep_their_teeth():
    """Report calls may swallow their exit code; the calls that gate may not."""
    for scanner in SCANNERS:
        gating = [c for c in scanner_calls(scanner) if not is_report_call(c)]
        assert gating, (
            f"{scanner} has no blocking invocation left -- every call writes a report, "
            f"so a real advisory would no longer fail the build"
        )
        for call in gating:
            assert (
                "|| true" not in call
            ), f"the gating {scanner} call is silenced: {call}"


def test_dependency_scan_step_is_not_continue_on_error():
    text = CI_YML.read_text(encoding="utf-8")
    match = re.search(
        r"^\s*- name: Run dependency scans\s*$(?P<body>.*?)(?=^\s*- name: )",
        text,
        re.MULTILINE | re.DOTALL,
    )
    assert match, "ci.yml has no 'Run dependency scans' step"
    assert "continue-on-error" not in match.group("body"), (
        "'Run dependency scans' was made non-blocking, which would make the gate "
        "permanently silent instead of correctly scoped"
    )


def test_setuptools_workaround_is_gone():
    """The env-level setuptools patch was a symptom of the unscoped audit."""
    body = "\n".join(dependency_scan_branch())
    assert "setuptools" not in body, (
        "the setuptools workaround is redundant once the audit is scoped to "
        "src/requirements.txt, which pins setuptools itself"
    )
    assert "setuptools==83.0.0" in REQUIREMENTS.read_text(encoding="utf-8"), (
        "src/requirements.txt no longer pins setuptools, so removing the runtime "
        "upgrade from quality.sh needs rethinking"
    )
