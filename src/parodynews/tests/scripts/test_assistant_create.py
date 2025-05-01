import pytest  # noqa: F401


def test_assistant_create(ensure_logged_in):
    page = ensure_logged_in

    page.goto("http://localhost:8000/assistants/")
    page.wait_for_selector("#assistant-form")

    # Fill out Assistant fields (reference assistant_detail.html)
    page.fill("input#id_name", "MyTestAssistant")
    page.fill("input#id_assist_description", "This is a test assistant.")
    page.select_option("select#id_model", "gpt-4o-mini")  # Example selection

    page.once("dialog", lambda dialog: dialog.accept())
    page.click("button[type='submit']")  # The 'Create' button

    page.wait_for_timeout(1000)


    # Check for success message or confirm creation
    assert "Assistant created successfully." in page.content()
