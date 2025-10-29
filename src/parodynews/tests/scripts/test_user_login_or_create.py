import pytest  # noqa: F401
from selenium.webdriver.common.by import By


def test_login_or_create(ensure_logged_in):
    driver = ensure_logged_in
    # Navigate to a post‑login page (adjust URL and condition as needed)
    alerts = driver.find_elements(By.CSS_SELECTOR, ".alert.alert-success")
    assert alerts, "Login or account creation failed"
