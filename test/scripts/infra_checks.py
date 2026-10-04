"""Django-level checks for scripts/test-infrastructure.sh.

Run inside the dev container (Django settings already configured):

    python test/scripts/infra_checks.py admin-exists
    python test/scripts/infra_checks.py password-strength

Exits non-zero (AssertionError) when a check fails.
"""

import sys
import time

import django

django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.contrib.auth.password_validation import (  # noqa: E402
    get_password_validators,
    validate_password,
)
from django.core.exceptions import ValidationError  # noqa: E402

WEAK_PASSWORDS = {
    "weak": "shorter than 8 characters",
    "abcdefghij": "no digit",
    "1234567890": "no letter",
    "password123": "common password",
}
STRONG_PASSWORD = "Tr1cky-Ferret-82"


def admin_exists():
    """The dev container's startup creates an admin; a second one is refused."""
    from setup.services import InstallationService

    User = get_user_model()
    # The container runs migrate + ensure_admin after its pip installs, so give
    # that a moment to finish rather than racing it.
    for _ in range(60):
        if User.objects.filter(is_superuser=True).exists():
            break
        time.sleep(2)
    assert User.objects.filter(is_superuser=True).exists(), "no admin user exists"

    try:
        InstallationService().create_admin_user(
            username="infra-duplicate-admin",
            email="infra-duplicate@example.com",
            password="DuplicatePass123",
        )
    except ValidationError as exc:
        assert "already exists" in str(exc), f"unexpected error: {exc}"
    else:
        raise AssertionError("a second admin user was created")
    assert not User.objects.filter(username="infra-duplicate-admin").exists()
    print("Admin exists; duplicate admin refused")


def password_strength():
    """Weak passwords are rejected by the wizard form and the production validators."""
    from setup.forms import AdminUserForm

    def form_errors(password):
        form = AdminUserForm(
            data={
                "username": "infra-pw-check",
                "email": "infra-pw-check@example.com",
                "password": password,
                "password_confirm": password,
            }
        )
        form.is_valid()
        return form.errors

    # The testing settings disable AUTH_PASSWORD_VALIDATORS, so check the
    # validators the base (production) settings configure.
    import barodybroject.settings.base as base_settings

    validators = get_password_validators(base_settings.AUTH_PASSWORD_VALIDATORS)
    assert validators, "base settings configure no password validators"

    for password, why in WEAK_PASSWORDS.items():
        assert "password" in form_errors(password), f"form accepted {why}: {password!r}"
        try:
            validate_password(password, password_validators=validators)
        except ValidationError:
            pass
        else:
            raise AssertionError(f"validators accepted {why}: {password!r}")

    assert "password" not in form_errors(STRONG_PASSWORD), "form rejected a strong password"
    validate_password(STRONG_PASSWORD, password_validators=validators)
    print("Weak passwords rejected; strong password accepted")


CHECKS = {"admin-exists": admin_exists, "password-strength": password_strength}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in CHECKS:
        sys.exit(f"usage: {sys.argv[0]} {{{'|'.join(CHECKS)}}}")
    CHECKS[sys.argv[1]]()
