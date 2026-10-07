"""Dependency contract: the auth stack resolves to a patched oauthlib.

Regression guard for bamr87/bamr87#326. oauthlib 3.3.1 carries
PYSEC-2026-4114 (fixed in 4.0.0), and the `Quality and Security` dependency
gate failed every run on it. The advisory is transitive: oauthlib reaches the
tree only through django-allauth's `socialaccount` extra, and allauth 65.14.1
capped it at `<4`. Pinning oauthlib alone would move the failure from
`pip-audit` to `pip install`, so the floor and the allauth bump must travel
together.

Pure stdlib, like the rest of this directory, so it runs where the
application's dependencies are not installed.
"""

from __future__ import annotations

import re
from pathlib import Path

REQUIREMENTS = Path(__file__).resolve().parents[1] / "requirements.txt"


def requirement(name: str) -> str:
    """The requirement line for ``name``, extras and version spec included."""
    pattern = re.compile(rf"^{re.escape(name)}(\[[^\]]*\])?\s*[=<>!~]", re.IGNORECASE)
    for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        if pattern.match(line.strip()):
            return line.strip()
    raise AssertionError(f"src/requirements.txt does not declare {name}")


def release(spec: str, operator: str) -> tuple[int, ...]:
    match = re.search(rf"{re.escape(operator)}\s*([0-9][0-9.]*)", spec)
    assert match, f"expected a '{operator}' version in: {spec}"
    return tuple(int(part) for part in match.group(1).split("."))


def test_oauthlib_has_a_patched_floor():
    spec = requirement("oauthlib")
    floor = release(spec, ">=")
    assert floor >= (4, 0, 0), f"oauthlib must be floored at 4.0.0: {spec}"


def test_allauth_is_new_enough_to_accept_oauthlib_4():
    spec = requirement("django-allauth")
    assert release(spec, "==") >= (65, 19, 7), (
        "django-allauth 65.14.1 requires oauthlib<4 for its socialaccount extra, "
        f"which makes the oauthlib floor unresolvable: {spec}"
    )


def test_allauth_keeps_its_extras():
    spec = requirement("django-allauth")
    for extra in ("mfa", "saml", "socialaccount", "steam"):
        assert re.search(
            rf"[\[,]{extra}[,\]]", spec
        ), f"django-allauth lost its '{extra}' extra: {spec}"
