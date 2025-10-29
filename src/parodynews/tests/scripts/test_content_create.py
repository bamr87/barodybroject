import pytest  # noqa: F401


def test_content_create(ensure_logged_in):
    page = ensure_logged_in
    page.goto("http://localhost:8000/content/")
    page.wait_for_selector("#content-form")
    page.fill("input[name='title']", "My Test Title")
    page.fill("textarea[name='description']", "Test description text.")
    page.fill("input[name='author']", "TestAuthor")
    page.fill("input[name='slug']", "test-slug")
    page.fill("textarea[name='prompt']", "Test prompt text.")

    # Wait for "Save" button to become enabled
    page.wait_for_timeout(1000)  # or wait for condition
    # Automatically handle the confirmation dialog on button click
    page.once("dialog", lambda dialog: dialog.accept())

    page.click("button#create-button")
    page.wait_for_timeout(1000)  # or wait for condition

    page.click("button#generate-btn")
    page.wait_for_timeout(1000)  # or wait for condition

    current_content = page.input_value("textarea[name='content_text']")
    page.fill("textarea[name='content_text']", f"TEST CONTENT: {current_content}")
    page.wait_for_timeout(1000)  # or wait for condition

    page.once("dialog", lambda dialog: dialog.accept())
    page.click("button#save-btn")
    page.wait_for_timeout(1000)  # or wait for condition

    page.click("button#thread-btn")
    page.wait_for_timeout(1000)  # or wait for condition

    page.wait_for_selector("text=Message created successfully.")
    assert "Message created successfully." in page.content()
