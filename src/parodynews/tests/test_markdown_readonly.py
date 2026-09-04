"""
File: test_markdown_readonly.py
Description: Tests for read-only Markdown rendering on the content detail view
Author: Barodybroject Team
Created: 2026-09-04
Version: 1.0.0

Dependencies:
- django
- django-markdownify

Usage: python -m pytest parodynews/tests/test_markdown_readonly.py

Background: assistant `instructions` were displayed inside a readonly
<textarea>, a widget that renders its content as text by specification, so
Markdown was always shown as raw source. The field is display-only (it is not a
ContentItem model field; ContentItemForm populates it from the selected
assistant), so content_detail.html now renders it through `|markdownify` and
carries the raw value in a hidden input to keep the submitted payload
identical. These tests pin all three halves of that: the rendering, the
sanitisation, and the unchanged payload.
"""

import re

from django import forms
from django.template.loader import render_to_string
from django.test import SimpleTestCase, TestCase
from markdownify.templatetags.markdownify import markdownify

from parodynews.models import Assistant

MARKDOWN_SAMPLE = """## Heading

- item one
- item two

Some **bold** text.

```
fenced = "code"
```
"""

HOSTILE_MARKDOWN = "<script>alert(1)</script>\n\n<img src=x onerror=alert(1)>"


class ReadonlyMarkdownProfileTests(SimpleTestCase):
    """The `readonly` django-markdownify profile used by read-only displays.

    django-markdownify falls back to bleach.sanitizer.ALLOWED_TAGS when no
    matching MARKDOWNIFY profile exists, and that default set is only
    {a, abbr, acronym, b, blockquote, code, em, i, li, ol, strong, ul} -- it
    contains no heading, paragraph or <pre> tag. A bare `|markdownify` would
    therefore strip `## Heading` down to the bare word. These tests assert the
    profile is configured, not merely that the filter was called.
    """

    def setUp(self):
        self.html = markdownify(MARKDOWN_SAMPLE, "readonly")

    def test_headings_render_as_headings(self):
        self.assertIn("<h2>Heading</h2>", self.html)

    def test_raw_markdown_syntax_is_not_shown(self):
        self.assertNotIn("## Heading", self.html)

    def test_lists_render_as_lists(self):
        self.assertIn("<ul>", self.html)
        self.assertIn("<li>item one</li>", self.html)

    def test_emphasis_renders_as_strong(self):
        self.assertIn("<strong>bold</strong>", self.html)

    def test_fenced_code_blocks_render_as_preformatted_code(self):
        # Requires markdown.extensions.fenced_code; without it a fenced block
        # collapses to an inline <code> inside a paragraph.
        self.assertIn("<pre><code>", self.html)

    def test_script_tags_are_neutralised(self):
        html = markdownify(HOSTILE_MARKDOWN, "readonly")
        self.assertNotIn("<script", html)

    def test_event_handler_attributes_are_stripped(self):
        html = markdownify(HOSTILE_MARKDOWN, "readonly")
        self.assertNotIn("onerror", html)
        # `img` is deliberately absent from the profile's allowlist, so the
        # element goes with the attribute rather than being kept unarmed.
        self.assertNotIn("<img", html)


class _StubForm(forms.Form):
    """Stands in for ContentItemForm so the template renders without the DB.

    ContentItemForm.__init__ queries Assistant, which content_detail.html does
    not need in order to exercise the instructions block.
    """

    instructions = forms.CharField(
        widget=forms.Textarea(attrs={"readonly": "readonly"}),
        required=False,
    )


def render_content_detail(instructions):
    """Render content_detail.html in create mode (no content_detail_id)."""
    return render_to_string(
        "parodynews/content_detail.html",
        {
            "content_form": _StubForm(initial={"instructions": instructions}),
            "content_detail_form": _StubForm(),
            "content_detail_info": [],
            "fields": [],
            "display_fields": [],
        },
    )


# The two halves of the block: what the reader sees, and what the form posts.
# The opening tag is split over several lines, hence DOTALL.
RENDERED_BLOCK_RE = re.compile(
    r'<div id="instructions-rendered".*?>(.*?)</div>', flags=re.DOTALL
)
HIDDEN_INPUT_RE = re.compile(
    r'<input type="hidden"[^>]*name="instructions".*?>', flags=re.DOTALL
)


def rendered_block(html):
    """The HTML shown to the reader, without the surrounding page."""
    match = RENDERED_BLOCK_RE.search(html)
    if match is None:
        raise AssertionError("no #instructions-rendered block in the page")
    return match.group(1)


def hidden_input(html):
    """The hidden <input> tag that carries the submitted value."""
    match = HIDDEN_INPUT_RE.search(html)
    if match is None:
        raise AssertionError("no hidden instructions input in the page")
    return match.group(0)


class ContentDetailInstructionsRenderingTests(SimpleTestCase):
    """content_detail.html must display instructions as HTML, not as source."""

    def setUp(self):
        self.html = render_content_detail(MARKDOWN_SAMPLE)
        self.block = rendered_block(self.html)

    def test_instructions_heading_renders_as_html(self):
        # The regression: this was `## Heading` inside a <textarea>.
        self.assertIn("<h2>Heading</h2>", self.block)

    def test_instructions_list_renders_as_html(self):
        self.assertIn("<li>item one</li>", self.block)

    def test_instructions_emphasis_renders_as_html(self):
        self.assertIn("<strong>bold</strong>", self.block)

    def test_instructions_fenced_code_renders_as_html(self):
        self.assertIn("<pre><code>", self.block)

    def test_raw_markdown_source_is_not_displayed(self):
        # Scoped to the displayed block: the hidden input legitimately still
        # carries the raw source, because that is what the form submits.
        self.assertNotIn("## Heading", self.block)
        self.assertNotIn("**bold**", self.block)

    def test_instructions_are_no_longer_rendered_in_a_textarea(self):
        # A <textarea> shows its content as text by specification, so no filter
        # applied to the value can render it. `exclude="instructions"` on the
        # bootstrap_form call is what keeps that widget off the page.
        self.assertNotIn(
            "<textarea", self.html[: self.html.index("Content Detail Form")]
        )

    def test_rendered_block_has_a_stable_hook_for_the_ajax_handler(self):
        # content_detail.js writes data.instructions_html into this element when
        # the selected assistant changes.
        self.assertIn('id="instructions-rendered"', self.html)

    def test_submitted_payload_is_unchanged(self):
        # The form still posts `instructions` with the raw Markdown value, so
        # ContentItemForm.Meta.fields keeps working exactly as before.
        tag = hidden_input(self.html)
        self.assertIn('id="id_instructions"', tag)
        self.assertIn("## Heading", tag)
        self.assertIn("**bold**", tag)

    def test_hostile_instructions_are_neutralised_in_the_rendered_block(self):
        block = rendered_block(render_content_detail(HOSTILE_MARKDOWN))
        self.assertNotIn("<script", block)
        self.assertNotIn("<img", block)
        self.assertNotIn("onerror", block)

    def test_hostile_instructions_are_escaped_in_the_hidden_input(self):
        # The raw value must survive round-tripping, so it is escaped rather
        # than sanitised: no tag can be formed out of an escaped attribute.
        tag = hidden_input(render_content_detail(HOSTILE_MARKDOWN))
        self.assertIn("&lt;script&gt;", tag)
        self.assertNotIn("<script", tag)
        self.assertNotIn("<img", tag)


class AssistantDetailsEndpointTests(TestCase):
    """Changing the assistant must re-render without a page reload.

    content_detail.js swaps in `instructions_html`; the endpoint renders it
    server-side through the same profile so the browser never needs a second
    Markdown implementation, and the HTML it inserts is already sanitised.
    """

    def setUp(self):
        self.assistant = Assistant.objects.create(
            id="asst_markdown_test",
            name="Markdown Test Assistant",
            instructions=MARKDOWN_SAMPLE,
        )

    def test_endpoint_returns_the_raw_instructions(self):
        response = self.client.get(
            f"/get_assistant_details/{self.assistant.id}/",
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["instructions"], MARKDOWN_SAMPLE)

    def test_endpoint_returns_rendered_html_alongside_the_raw_value(self):
        response = self.client.get(
            f"/get_assistant_details/{self.assistant.id}/",
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        html = response.json()["instructions_html"]
        self.assertIn("<h2>Heading</h2>", html)
        self.assertIn("<strong>bold</strong>", html)
        self.assertNotIn("## Heading", html)

    def test_endpoint_sanitises_hostile_instructions(self):
        self.assistant.instructions = HOSTILE_MARKDOWN
        self.assistant.save()
        response = self.client.get(
            f"/get_assistant_details/{self.assistant.id}/",
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        html = response.json()["instructions_html"]
        self.assertNotIn("<script", html)
        self.assertNotIn("onerror", html)

    def test_missing_assistant_still_404s(self):
        response = self.client.get("/get_assistant_details/nope/")
        self.assertEqual(response.status_code, 404)
