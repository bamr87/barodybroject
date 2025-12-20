"""
File: user_login.py
Description: Playwright helper for logging into the Django Allauth sign-in flow
Author: Barodybroject Team <team@example.com>
Created: 2025-12-19
Last Modified: 2025-12-19
Version: 1.0.1

Dependencies:
- playwright: sync_api

Usage: from parodynews.tests.scripts.functions.user_login import login_user
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

from playwright.sync_api import Page


def login_user(page: Page, username: str, password: str, *, base_url: str = "http://localhost:8000") -> bool:
    """
    Performs the login process using Playwright.
    Returns True if the login was successful, False otherwise.
    """
    login_url = f"{base_url.rstrip('/')}/accounts/login/"
    page.goto(login_url, wait_until="domcontentloaded")
    try:
        page.locator("#id_login").fill(username)
        page.locator("#id_password").fill(password)

        page.get_by_role("button", name=re.compile(r"^sign in$", re.IGNORECASE)).click()
        page.wait_for_load_state("networkidle")

        # Allauth redirects away from the login page on success.
        if urlparse(page.url).path.rstrip("/") != "/accounts/login":
            print("Login successful")
            return True
        else:
            print("Login failed")
            return False
    except Exception as e:
        print("Login failed:", e)
        return False
