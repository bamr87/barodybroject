import os
import time

import pytest  # noqa: F401
from playwright.sync_api import sync_playwright

from parodynews.tests.scripts.functions.user_create import create_new_account
from parodynews.tests.scripts.functions.user_login import login_user

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ['DJANGO_SETTINGS_MODULE'] = 'barodybroject.settings'


@pytest.fixture(scope="session")
def browser_context():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        context = browser.new_context()
        yield context
        context.close()

@pytest.fixture
def page(browser_context):
    page = browser_context.new_page()
    yield page
    page.close()

@pytest.fixture(scope="session")
def ensure_logged_in(browser_context):
    page = browser_context.new_page()
    username = 'bamr87'
    password = 'amr123'
    email = username + "@barodybroject.com"
    if not login_user(page, username, password):
        create_new_account(page, username, email, password)
        time.sleep(5)  # wait for account creation
        assert login_user(page, username, password), "Login failed after account creation"
    return page