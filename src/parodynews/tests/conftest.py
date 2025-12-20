import os

import pytest
from playwright.sync_api import Page

from parodynews.tests.scripts.functions.user_login import login_user


@pytest.fixture(scope="session")
def e2e_base_url() -> str:
    return os.environ.get("E2E_BASE_URL", "http://localhost:8000").rstrip("/")


@pytest.fixture(scope="session")
def e2e_credentials() -> dict[str, str]:
    username = os.environ.get("E2E_USERNAME", "e2e_user")
    password = os.environ.get("E2E_PASSWORD", "e2e_password")
    email = os.environ.get("E2E_EMAIL", f"{username}@example.com")
    return {"username": username, "password": password, "email": email}


@pytest.fixture(scope="session")
def browser_name() -> str:
    # Enforce Chromium-only for CI determinism.
    return "chromium"


@pytest.fixture(scope="session")
def browser_context_args(e2e_base_url: str) -> dict:
    # pytest-playwright will pass these args to `browser.new_context()`.
    return {"base_url": e2e_base_url}


@pytest.fixture
def logged_in_page(page: Page, e2e_base_url: str, e2e_credentials: dict[str, str]) -> Page:
    # Allauth is configured for email-based authentication.
    ok = login_user(page, e2e_credentials["email"], e2e_credentials["password"], base_url=e2e_base_url)
    assert ok, (
        "E2E login failed. Ensure the user exists (recommended: run "
        "`python src/manage.py ensure_e2e_user`)."
    )
    return page
