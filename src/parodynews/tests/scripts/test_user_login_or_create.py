import pytest


@pytest.mark.e2e
def test_login_smoke(logged_in_page):
    page = logged_in_page
    page.goto("/")
    page.wait_for_timeout(250)
    assert "Barody" in page.content()
