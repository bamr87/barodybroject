import pytest

def test_content_create(ensure_logged_in):
    page = ensure_logged_in
    page.goto('http://localhost:8000/content/')
    page.wait_for_selector("#content-form")
    page.fill("input[name='title']", "My Test Title")
    page.fill("textarea[name='description']", "Test description text.")
    page.fill("input[name='author']", "TestAuthor")
    page.fill("input[name='slug']", "test-slug")
    # Wait for "Save" button to become enabled
    page.wait_for_timeout(1000)  # or wait for condition
    # Automatically handle the confirmation dialog on button click
    page.once("dialog", lambda dialog: dialog.accept())
    
    page.click("button#create-button")
    page.wait_for_timeout(1000)  # or wait for condition
    page.wait_for_timeout(1000)  # or wait for condition
    page.click("button#create-button")

    page.wait_for_selector("text=Content and its details saved successfully!")
    assert 'Content and its details saved successfully!' in page.content()

def test_fill_and_save_content(page):
    page.goto("http://localhost:8000/content/")
    # Fill out the new content form
    page.fill("input[name='title']", "My Test Title")
    page.fill("textarea[name='description']", "Test description text.")
    page.fill("input[name='author']", "TestAuthor")
    page.fill("input[name='slug']", "test-slug")
    # Wait for "Save" button to become enabled
    page.wait_for_timeout(1000)  # or wait for condition
    # Click the "Save" button
    page.click("button#save-btn")
