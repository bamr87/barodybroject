import pytest

def test_assistant_group_create(ensure_logged_in):
    page = ensure_logged_in

    # Create 3 assistants
    for i in range(1, 4):
        page.goto("http://localhost:8000/assistants/")
        page.wait_for_selector("#assistant-form")
        page.fill("input#id_name", f"GroupAssistant{i}")
        page.fill("input#id_assist_description", f"This is test assistant {i}.")
        page.select_option("select#id_model", "gpt-4o-mini")
        page.once("dialog", lambda dialog: dialog.accept())
        page.click("button[type='submit']")
        page.wait_for_timeout(1000)
        assert "Assistant created successfully." in page.content()

    # Create Assistant Group with a membership of the three assistants
    page.goto("http://localhost:8000/assistant-groups/")
    page.wait_for_selector("form")
    page.fill("input[name='name']", "Test Assistant Group")
    page.fill("input[name='group_type']", "default")

    # Fill inline formset fields for membership; using the default formset prefix.
    page.select_option("select[name='assistantgroupmembership_set-0-assistants']", label="GroupAssistant1")
    page.fill("input[name='assistantgroupmembership_set-0-position']", "1")
    page.select_option("select[name='assistantgroupmembership_set-1-assistants']", label="GroupAssistant2")
    page.fill("input[name='assistantgroupmembership_set-1-position']", "2")
    page.select_option("select[name='assistantgroupmembership_set-2-assistants']", label="GroupAssistant3")
    page.fill("input[name='assistantgroupmembership_set-2-position']", "3")

    page.once("dialog", lambda dialog: dialog.accept())
    page.click("button[type='submit']")
    page.wait_for_timeout(1000)
    # Verify that the group list is displayed (template shows 'Assistant Groups')
    assert "Assistant Groups" in page.content()
