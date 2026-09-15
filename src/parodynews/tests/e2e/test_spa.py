"""
File: test_spa.py
Description: Playwright smoke tests for the React application
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 1.0.0

Dependencies:
- pytest
- pytest-playwright

Usage:
  pytest -m e2e --browser chromium

These run against a real server with the frontend built, so they cover the
seam the unit suites cannot: Django serving the hashed bundle, the SPA booting,
and the session cookie carrying through to the API. Component behaviour is
covered by the Vitest suite in `src/frontend`.
"""

import pytest


@pytest.mark.e2e
def test_the_app_boots_and_renders_the_shell(logged_in_page):
    page = logged_in_page
    page.goto("/")
    page.wait_for_selector("nav.navbar", timeout=15000)

    assert page.locator("#root").count() == 1
    assert "Barody Broject" in page.locator("nav.navbar").inner_text()


@pytest.mark.e2e
def test_the_bundle_loads_without_console_errors(logged_in_page):
    """A missing or stale hashed asset shows up here and nowhere else."""
    errors: list[str] = []
    page = logged_in_page
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on(
        "console",
        lambda msg: errors.append(msg.text) if msg.type == "error" else None,
    )

    page.goto("/")
    page.wait_for_selector("nav.navbar", timeout=15000)
    page.wait_for_timeout(500)

    assert errors == []


@pytest.mark.e2e
def test_client_side_routing_reaches_every_section(logged_in_page):
    page = logged_in_page
    page.goto("/")
    page.wait_for_selector("nav.navbar", timeout=15000)

    for label, heading in [
        ("Content", "Content"),
        ("Threads", "Threads"),
        ("Assistants", "Assistants"),
        ("Settings", "AI providers"),
    ]:
        page.click(f"nav >> text={label}")
        page.wait_for_selector(f"h1:has-text('{heading}')", timeout=10000)


@pytest.mark.e2e
def test_a_deep_link_is_served_by_django_and_routed_by_react(logged_in_page):
    """Reloading on a client-side route must not 404: Django hands every
    unclaimed path to the SPA, which then routes it."""
    page = logged_in_page
    response = page.goto("/settings")
    assert response is not None and response.status == 200
    page.wait_for_selector("h1:has-text('AI providers')", timeout=15000)


@pytest.mark.e2e
def test_the_settings_screen_lists_every_provider(logged_in_page):
    page = logged_in_page
    page.goto("/settings")
    page.wait_for_selector(".card h2", timeout=15000)

    text = page.locator("main").inner_text()
    for provider in ("Claude Code", "Anthropic", "OpenAI"):
        assert provider in text


@pytest.mark.e2e
def test_the_theme_toggle_persists_across_a_reload(logged_in_page):
    page = logged_in_page
    page.goto("/")
    page.wait_for_selector("nav.navbar", timeout=15000)

    page.get_by_title("Dark").click()
    assert (
        page.evaluate("document.documentElement.getAttribute('data-bs-theme')")
        == "dark"
    )

    page.reload()
    page.wait_for_selector("nav.navbar", timeout=15000)
    assert (
        page.evaluate("document.documentElement.getAttribute('data-bs-theme')")
        == "dark"
    )


@pytest.mark.e2e
def test_signing_out_returns_to_the_django_auth_flow(logged_in_page):
    """Authentication stayed server-side, so the sign-out link is a real
    navigation rather than a client-side route."""
    page = logged_in_page
    page.goto("/")
    page.wait_for_selector("nav.navbar", timeout=15000)

    page.click("nav >> text=Sign out")
    page.wait_for_load_state("networkidle")
    assert "/accounts/" in page.url
