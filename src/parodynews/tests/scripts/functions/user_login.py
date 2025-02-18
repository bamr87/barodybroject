from playwright.sync_api import Page

def login_user(page: Page, username: str, password: str) -> bool:
    """
    Performs the login process using Playwright.
    Returns True if the login was successful, False otherwise.
    """
    login_url = 'http://localhost:8000/accounts/login/'
    page.goto(login_url)
    try:
        page.locator("#id_login").fill(username)
        page.locator("#id_password").fill(password)
        page.locator("form").press("Enter")
        if page.url != login_url:
            print("Login successful")
            return True
        else:
            print("Login failed")
            return False
    except Exception as e:
        print("Login failed:", e)
        return False
