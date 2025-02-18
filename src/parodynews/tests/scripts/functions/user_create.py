from playwright.sync_api import Page

def create_new_account(page: Page, username, email, password):
    """
    Navigates to the signup page, fills out the form fields, and submits the form.
    
    :param page: An instance of Playwright Page.
    :param username: The desired username.
    :param email: The user's email address.
    :param password: The user's password (used for both password fields).
    """
    # Open the signup page
    page.goto("https://barodybroject.com/accounts/signup/")
    
    # Wait until the signup form loads (assuming the username field has id 'id_username')
    page.wait_for_selector("#id_username")
    
    # Fill in the signup form fields.
    page.locator("#id_username").fill(username)
    page.locator("#id_email").fill(email)
    page.locator("#id_password1").fill(password)
    page.locator("#id_password2").fill(password)
    
    # Click the submit button (assumed to be a <button> with type 'submit')
    page.locator("button[type='submit']").click()
    
    # Optionally, wait for a confirmation element that signals successful account creation.
    # This may need adjustment based on your site's actual response.
    page.wait_for_selector("text=Welcome, text=account created")
    print(f"Account created: {username}")