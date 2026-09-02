"""
File: test_assistant_quick_edit_e2e.py
Description: Playwright + axe coverage for the assistant quick-edit control (#105)
Author: Barodybroject Team
Created: 2026-09-02
Version: 1.0.0

Dependencies:
- pytest
- pytest-playwright
- axe-playwright-python
- django (template rendering only; no database access)

Usage:
  pytest -m e2e --browser chromium

Two layers, following the pattern established in test_model_table_e2e.py:

1. `TestLivePage` drives the real running server and asserts what the server
   actually sends for the content page. `.github/scripts/e2e-tests.sh` seeds only
   an e2e user, so there are no assistants to select there — which is exactly the
   empty-selection state criterion 2 calls for.

2. `TestInteraction` builds a harness page from the **real**
   `includes/assistant_edit_modal.html` template and the **real**
   `assets/js/content_detail.js`, with `fetch` stubbed, so the interactive
   criteria (enable-on-select, open without navigation, cancel preserving the
   draft, keyboard, touch) are deterministic without seeded assistants.

   The harness reproduces the select/button markup rather than rendering
   `content_detail.html` (which extends `base.html` and needs a request, a user
   and model-table context). `AssistantQuickEditTemplateTests` in
   `../test_templates.py` pins that markup in the real template — ids,
   `aria-label`, `aria-controls`, the `assistant-field-group` wrapper and the
   initial `disabled` — so the harness cannot drift from the app unnoticed.

The save round trip is covered server-side in `../test_assistant_quick_edit.py`;
it needs an OpenAI call that is patched there rather than driven through a browser.
"""

from pathlib import Path

import pytest
from django.template.loader import render_to_string

# src/parodynews/tests/e2e/ -> src/
SRC_ROOT = Path(__file__).resolve().parents[3]
CONTENT_DETAIL_JS = SRC_ROOT / "assets" / "js" / "content_detail.js"

BOOTSTRAP_JS = (
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
)
BOOTSTRAP_CSS = (
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
)

ASSISTANT_ID = "asst_e2e_105"

FOCUS_IS_INSIDE_MODAL = (
    "() => { const m = document.getElementById('assistantEditModal');"
    " return m && document.activeElement && m.contains(document.activeElement); }"
)

# The fragment the quick-edit endpoint returns; `fetch` is stubbed to serve it.
FORM_FRAGMENT = (
    '<div id="assistant-quick-edit-fields" data-assistant-id="%s">'
    '<div class="mb-3">'
    '<label class="form-label" for="id_name">Name</label>'
    '<input type="text" class="form-control" id="id_name" name="name" '
    'value="Original name">'
    "</div>"
    '<div class="mb-3">'
    '<label class="form-label" for="id_instructions">Instructions</label>'
    '<textarea class="form-control" id="id_instructions_modal" name="instructions">'
    "Original instructions.</textarea>"
    "</div>"
    "</div>" % ASSISTANT_ID
)


def harness_html():
    """Real modal template + real script, wrapped in the field-group markup."""
    modal = render_to_string("includes/assistant_edit_modal.html", {})
    script = CONTENT_DETAIL_JS.read_text(encoding="utf-8")

    return f"""<!DOCTYPE html>
<html lang="en" data-bs-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Assistant quick edit harness</title>
  <link rel="stylesheet" href="{BOOTSTRAP_CSS}">
</head>
<body>
  <main>
    <h1>Content Prompt and Detail</h1>
    <form id="content-form-el">
      <div class="mb-3">
        <label class="form-label" for="id_content_text">Content</label>
        <textarea class="form-control" id="id_content_text"
                  name="content_text"></textarea>
      </div>
      <div class="d-flex align-items-end gap-2 mb-3" id="assistant-field-group">
        <div class="flex-grow-1">
          <label class="form-label" for="id_assistant">Assistant Name</label>
          <select class="form-select" id="id_assistant" name="assistant">
            <option value="">---------</option>
            <option value="{ASSISTANT_ID}">Original name</option>
          </select>
        </div>
        <button type="button" class="btn btn-outline-secondary flex-shrink-0"
                id="edit-assistant-btn"
                aria-label="Edit selected assistant"
                aria-controls="assistantEditModal"
                aria-haspopup="dialog"
                title="Edit selected assistant" disabled>
          <span>Edit</span>
        </button>
      </div>
      <div class="mb-3">
        <label class="form-label" for="id_instructions">Instructions</label>
        <textarea class="form-control" id="id_instructions"
                  name="instructions" readonly></textarea>
      </div>
    </form>
  </main>
  {modal}
  <script src="{BOOTSTRAP_JS}"></script>
  <script>
    // Serve the form fragment and the save response without a server. Also
    // neutralises the existing /get_assistant_details/ call the change handler
    // makes, which is not what these tests are about.
    window.__saveCalls = [];
    window.fetch = function (url, options) {{
      options = options || {{}};
      if (url.indexOf('/get_assistant_details/') !== -1) {{
        return Promise.resolve({{
          ok: true, status: 200,
          json: function () {{
            return Promise.resolve({{
              assistant_id: '{ASSISTANT_ID}',
              instructions: 'Original instructions.'
            }});
          }}
        }});
      }}
      if (url.indexOf('/quick-edit/') !== -1 && options.method === 'POST') {{
        window.__saveCalls.push(url);
        return Promise.resolve({{
          ok: true, status: 200,
          json: function () {{
            return Promise.resolve({{
              assistant_id: '{ASSISTANT_ID}',
              name: 'Renamed assistant',
              instructions: 'Saved instructions.'
            }});
          }}
        }});
      }}
      return Promise.resolve({{
        ok: true, status: 200,
        text: function () {{ return Promise.resolve({FORM_FRAGMENT!r}); }}
      }});
    }};
  </script>
  <script>{script}</script>
</body>
</html>"""


def load_harness(page):
    page.set_content(harness_html())
    page.wait_for_function("() => window.bootstrap && window.bootstrap.Modal")
    return page


def axe_violations(page, impacts=None):
    """WCAG 2.1 A/AA violations on the current page.

    `impacts=None` means every violation counts, which is what the harness page
    is held to — all of its markup is new in this change. The live content page
    is filtered to serious/critical because it carries pre-existing markup this
    change does not touch, and the criterion is "no *new* violations"; tightening
    that to zero is a worthwhile follow-up but would fail here for reasons
    unrelated to this feature.
    """
    from axe_playwright_python.sync_playwright import Axe

    results = Axe().run(
        page, options={"runOnly": {"type": "tag", "values": ["wcag2a", "wcag2aa"]}}
    )
    violations = results.response["violations"]
    if impacts is None:
        return violations
    return [v for v in violations if v.get("impact") in impacts]


@pytest.mark.e2e
class TestLivePage:
    """What the real server sends for the content detail page."""

    def test_edit_button_is_rendered_and_disabled_without_a_selection(
        self, logged_in_page, e2e_base_url
    ):
        page = logged_in_page
        page.goto(f"{e2e_base_url}/content/")

        button = page.locator("#edit-assistant-btn")
        button.wait_for(state="attached")

        assert button.get_attribute("aria-label") == "Edit selected assistant"
        assert button.get_attribute("aria-controls") == "assistantEditModal"
        # No assistants are seeded for E2E, so nothing can be selected yet.
        assert page.locator("#id_assistant").input_value() == ""
        assert button.is_disabled()

    def test_modal_markup_is_present_and_hidden(self, logged_in_page, e2e_base_url):
        page = logged_in_page
        page.goto(f"{e2e_base_url}/content/")

        modal = page.locator("#assistantEditModal")
        modal.wait_for(state="attached")
        assert not modal.is_visible()

    def test_no_new_accessibility_violations_on_the_content_page(
        self, logged_in_page, e2e_base_url
    ):
        page = logged_in_page
        page.goto(f"{e2e_base_url}/content/")
        page.locator("#edit-assistant-btn").wait_for(state="attached")

        violations = axe_violations(page, impacts=("serious", "critical"))
        assert violations == [], [v["id"] for v in violations]


@pytest.mark.e2e
class TestInteraction:
    """Behaviour, driven against the real modal template and the real script."""

    def test_button_enables_only_once_an_assistant_is_selected(self, page):
        load_harness(page)

        button = page.locator("#edit-assistant-btn")
        assert button.is_disabled()

        page.select_option("#id_assistant", ASSISTANT_ID)
        assert button.is_enabled()

        page.select_option("#id_assistant", "")
        assert button.is_disabled()

    def test_opening_the_modal_does_not_navigate(self, page):
        load_harness(page)
        url_before = page.url

        page.select_option("#id_assistant", ASSISTANT_ID)
        page.click("#edit-assistant-btn")

        page.wait_for_selector("#assistantEditModal.show")
        assert page.locator("#assistantEditModal").is_visible()
        assert page.url == url_before

    def test_modal_is_populated_from_the_endpoint(self, page):
        load_harness(page)
        page.select_option("#id_assistant", ASSISTANT_ID)
        page.click("#edit-assistant-btn")

        page.wait_for_selector("#assistant-quick-edit-fields")
        assert (
            page.locator("#id_instructions_modal").input_value()
            == "Original instructions."
        )

    def test_cancelling_preserves_the_unsaved_draft(self, page):
        """The whole point of the feature: the draft must survive the detour."""
        load_harness(page)
        page.fill("#id_content_text", "a draft I have not saved yet")

        page.select_option("#id_assistant", ASSISTANT_ID)
        page.click("#edit-assistant-btn")
        page.wait_for_selector("#assistantEditModal.show")

        page.click("#assistantEditModal .btn-secondary")
        page.wait_for_selector("#assistantEditModal.show", state="detached")

        assert (
            page.locator("#id_content_text").input_value()
            == "a draft I have not saved yet"
        )

    def test_saving_updates_the_content_form_instructions(self, page):
        load_harness(page)
        page.select_option("#id_assistant", ASSISTANT_ID)
        page.click("#edit-assistant-btn")
        page.wait_for_selector("#assistant-quick-edit-fields")

        page.click("#assistantEditSave")
        page.wait_for_selector("#assistantEditModal.show", state="detached")

        assert page.locator("#id_instructions").input_value() == "Saved instructions."
        # A renamed assistant is reflected in the selector it was opened from.
        option = page.locator(f'#id_assistant option[value="{ASSISTANT_ID}"]')
        assert option.text_content() == "Renamed assistant"

    def test_operable_by_keyboard_alone(self, page):
        """Criterion 7: reachable by Tab from the select, activates with Enter
        and Space, and focus returns to the button when the dialog closes."""
        load_harness(page)
        page.select_option("#id_assistant", ASSISTANT_ID)

        page.focus("#id_assistant")
        page.keyboard.press("Tab")
        assert page.evaluate("() => document.activeElement.id") == "edit-assistant-btn"

        page.keyboard.press("Enter")
        page.wait_for_selector("#assistant-quick-edit-fields")
        # Escape only closes the dialog if focus is inside it, so wait for the
        # focus trap rather than racing it.
        page.wait_for_function(FOCUS_IS_INSIDE_MODAL)

        page.keyboard.press("Escape")
        page.wait_for_selector("#assistantEditModal.show", state="detached")
        # Focus is restored on `hidden.bs.modal`, which fires after the hide
        # transition — later than the class removal above.
        page.wait_for_function(
            "() => document.activeElement"
            " && document.activeElement.id === 'edit-assistant-btn'"
        )

        page.keyboard.press(" ")
        page.wait_for_selector("#assistantEditModal.show")
        assert page.locator("#assistantEditModal").is_visible()

    def test_focus_moves_into_the_dialog_on_open(self, page):
        load_harness(page)
        page.select_option("#id_assistant", ASSISTANT_ID)
        page.click("#edit-assistant-btn")
        page.wait_for_selector("#assistant-quick-edit-fields")

        page.wait_for_function(FOCUS_IS_INSIDE_MODAL)

    def test_usable_at_a_mobile_viewport_without_hover(self, browser):
        """Criterion 9: :hover does not exist on touch, so the control must be
        tappable while always visible."""
        context = browser.new_context(
            viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True
        )
        page = context.new_page()
        try:
            load_harness(page)
            page.select_option("#id_assistant", ASSISTANT_ID)

            button = page.locator("#edit-assistant-btn")
            assert button.is_visible(), "control must not be hover-revealed"
            button.tap()

            page.wait_for_selector("#assistantEditModal.show")
            assert page.locator("#assistantEditModal").is_visible()
        finally:
            context.close()

    def test_no_accessibility_violations_with_the_dialog_open(self, page):
        load_harness(page)

        closed = axe_violations(page)
        assert closed == [], [v["id"] for v in closed]

        page.select_option("#id_assistant", ASSISTANT_ID)
        page.click("#edit-assistant-btn")
        page.wait_for_selector("#assistant-quick-edit-fields")

        opened = axe_violations(page)
        assert opened == [], [v["id"] for v in opened]
