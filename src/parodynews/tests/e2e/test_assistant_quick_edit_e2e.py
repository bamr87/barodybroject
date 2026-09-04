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

# The dialog has finished its open animation: `show` is on, the modal has faded
# fully in, and the dialog has finished sliding down. Bootstrap fades `.modal`
# opacity 0 -> 1 and translates `.modal-dialog` -50px -> 0 over 300ms, and the
# fetch stub resolves in a microtask, so `#assistant-quick-edit-fields` can
# appear while all of that is still running.
DIALOG_IS_SETTLED = """
() => {
    const m = document.getElementById('assistantEditModal');
    if (!m || !m.classList.contains('show')) { return false; }
    if (getComputedStyle(m).opacity !== '1') { return false; }
    const d = m.querySelector('.modal-dialog');
    if (!d) { return true; }
    const t = getComputedStyle(d).transform;
    return t === 'none' || t === 'matrix(1, 0, 0, 1, 0, 0)';
}
"""

# The fragment the quick-edit endpoint returns; `fetch` is stubbed to serve it.
#
# Field ids are namespaced `id_quick_*`, matching QUICK_EDIT_AUTO_ID in
# views/assistants.py. AssistantForm shares the names `instructions` and
# `description` with the two forms the content page already renders, so the
# default `id_%s` would put duplicate active ids on the page the moment the
# dialog opens. `AssistantQuickEditViewTests.test_fragment_ids_are_namespaced`
# pins the real endpoint to this shape, so the fixture cannot drift from it.
# The field NAMES are deliberately unprefixed here, exactly as the endpoint
# renders them.
FORM_FRAGMENT = (
    '<div id="assistant-quick-edit-fields" data-assistant-id="%s">'
    '<div class="mb-3">'
    '<label class="form-label" for="id_quick_name">Name</label>'
    '<input type="text" class="form-control" id="id_quick_name" name="name" '
    'value="Original name">'
    "</div>"
    '<div class="mb-3">'
    '<label class="form-label" for="id_quick_instructions">Instructions</label>'
    '<textarea class="form-control" id="id_quick_instructions" '
    'name="instructions">'
    "Original instructions.</textarea>"
    "</div>"
    "</div>" % ASSISTANT_ID
)

# The markup this change adds. The live content page also carries base.html's
# navbar and footer, which this change does not touch.
FEATURE_ROOTS = ("#assistant-field-group", "#assistantEditModal")

# Does any of an axe node's target selectors resolve inside the feature markup?
NODE_IS_IN_FEATURE = """
([targets, roots]) => targets.some(selector => {
    const el = document.querySelector(selector);
    if (!el) { return false; }
    return roots.some(rootSelector => {
        const root = document.querySelector(rootSelector);
        return Boolean(root) && root.contains(el);
    });
})
"""


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


# `set_content` would be the obvious way to load this, and is what
# `test_model_table_e2e.py` does — but that leaves the document on an opaque
# origin, where reading `document.cookie` raises
#   SecurityError: Failed to read the 'cookie' property from 'Document'
# `content_detail.js` reads it via `getCookie('csrftoken')` while assembling the
# save request's headers, so under `set_content` the submit handler dies THERE —
# synchronously, before `fetch` is called, and outside the promise chain, so the
# handler's own `.catch` never runs and the dialog just hangs open. That is an
# artifact of the harness, not of the app: Django serves this page over http,
# where the cookie read is fine. Serve the harness from a real origin so the
# save path under test is the one that actually ships.
HARNESS_ORIGIN = "http://assistant-quick-edit.harness"


def load_harness(page):
    html = harness_html()
    page.route(
        f"{HARNESS_ORIGIN}/**",
        lambda route: route.fulfill(content_type="text/html", body=html),
    )
    page.goto(f"{HARNESS_ORIGIN}/content/")
    page.wait_for_function("() => window.bootstrap && window.bootstrap.Modal")
    return page


def axe_violations(page):
    """Every WCAG 2.1 A/AA violation on the current page, at any impact."""
    from axe_playwright_python.sync_playwright import Axe

    results = Axe().run(
        page, options={"runOnly": {"type": "tag", "values": ["wcag2a", "wcag2aa"]}}
    )
    return results.response["violations"]


def violations_in_feature_markup(page, violations):
    """Keep only violations with at least one node inside FEATURE_ROOTS.

    The criterion is "no *new* accessibility violations", and the live content
    page renders base.html's navbar and footer, which this change does not
    touch. Rather than filter by impact — which lets a pre-existing serious
    violation fail this feature's test while hiding a moderate one the feature
    itself introduced — this asks the page directly which nodes are inside the
    markup the change adds, and holds that markup to ZERO violations at ANY
    impact. Pre-existing problems elsewhere on the page stay visible as their
    own defects instead of being silently absorbed here.
    """
    attributable = []
    for violation in violations:
        nodes = []
        for node in violation.get("nodes", []):
            targets = node.get("target") or []
            # axe nests targets inside iframes; this page has none, so a flat
            # list of selector strings is what we expect. Anything else is not
            # something this helper can attribute, so leave it out.
            if not targets or not all(isinstance(t, str) for t in targets):
                continue
            if page.evaluate(NODE_IS_IN_FEATURE, [targets, list(FEATURE_ROOTS)]):
                nodes.append(node)
        if nodes:
            attributable.append(violation)
    return attributable


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
        """No violation on the live page is attributable to this change.

        Scoped to the markup the change adds. base.html's navbar already fails
        `color-contrast` on `main` — the "Theme", "Settings" and "Report Issue"
        labels (`span.d-none.d-lg-inline.ms-1`) — and neither base.html nor
        footer.html is touched by this PR. That is a real, separate defect in
        pre-existing markup; it is reported on the PR rather than fixed or
        suppressed here.
        """
        page = logged_in_page
        page.goto(f"{e2e_base_url}/content/")
        page.locator("#edit-assistant-btn").wait_for(state="attached")

        violations = violations_in_feature_markup(page, axe_violations(page))
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
        # A distinct element from the content form's same-named `instructions`
        # field, which is why the endpoint namespaces the dialog's ids.
        assert (
            page.locator("#id_quick_instructions").input_value()
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
        """The ordinary save: the dialog closes and the content form catches up."""
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

    def test_saving_closes_a_dialog_that_is_still_opening(self, page):
        """Bootstrap's `hide()` is a no-op while the dialog is still animating
        open, so a save that resolves faster than that animation used to leave
        the dialog stuck open. `hideModal` records the request and the
        `shown.bs.modal` handler re-issues it; this pins that.

        `page.click` cannot express this case: Playwright's actionability check
        waits for the element to be STABLE, i.e. for the very animation whose
        mid-flight state is the bug, so a clicked save always lands after
        `shown.bs.modal` has already fired. The submit is therefore dispatched
        from script — and the assertion below fails loudly if the dialog turns
        out to have settled first, rather than passing while covering nothing.
        """
        load_harness(page)
        page.select_option("#id_assistant", ASSISTANT_ID)
        page.click("#edit-assistant-btn")
        page.wait_for_selector("#assistant-quick-edit-fields")

        # Read the transition state and submit in the SAME JS turn, so the
        # dialog cannot finish opening in between and turn this into the
        # already-covered settled case.
        was_settled = page.evaluate("""() => {
                const m = document.getElementById('assistantEditModal');
                const settled = m.classList.contains('show')
                    && getComputedStyle(m).opacity === '1';
                document.getElementById('assistantEditForm').requestSubmit();
                return settled;
            }""")
        assert not was_settled, (
            "the dialog had already finished opening, so this run did not "
            "exercise the hide()-while-opening race"
        )

        page.wait_for_selector("#assistantEditModal.show", state="detached")
        assert page.locator("#id_instructions").input_value() == "Saved instructions."

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
        # Audit the settled dialog. Mid-fade the modal's opacity is below 1, so
        # every colour inside it composites against the page behind and axe
        # scores the ANIMATION rather than the UI — reporting `color-contrast`
        # on the title, the labels and the inputs alike. Waiting is not a
        # relaxation of the assertion: the transient state being measured is one
        # no user can read or interact with.
        page.wait_for_function(DIALOG_IS_SETTLED)

        opened = axe_violations(page)
        assert opened == [], [v["id"] for v in opened]
