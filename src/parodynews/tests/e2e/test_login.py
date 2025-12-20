"""
File: test_login.py
Description: Minimal Playwright smoke test for E2E login in CI
Author: Barodybroject Team <team@example.com>
Created: 2025-12-19
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- pytest
- pytest-playwright

Usage:
  pytest -m e2e
"""

import pytest


@pytest.mark.e2e
def test_login_smoke(logged_in_page):
    page = logged_in_page
    page.goto("/")
    page.wait_for_timeout(250)
    assert "Barody" in page.content()
