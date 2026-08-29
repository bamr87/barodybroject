"""
File: test_markdown_rendering.py
Description: Markdown display tests — rendered HTML in read-only views, raw
             source only while editing, and one sanitized renderer everywhere.
Author: Barodybroject Team
Created: 2026-08-29
Version: 1.0.0

Dependencies:
- django
- pytest (optional)

Usage: python manage.py test parodynews.tests.test_markdown_rendering

Covers the regression in #57: `content_detail.html` loaded the `markdownify`
filter library and never applied it, so fields — including a read-only one —
displayed raw Markdown in form widgets while four other templates rendered the
same content correctly.

The security assertions here are the load-bearing ones. This app's content is
AI-generated and user-editable and the repository is public, so "renders
Markdown" must never become "renders whatever HTML the content contains".
"""

import re
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.template import Context, Template
from django.template.loader import render_to_string
from django.test import Client, SimpleTestCase, TestCase
from django.urls import Resolver404, resolve, reverse

from parodynews.utils.markdown import render_markdown

SRC_ROOT = Path(settings.BASE_DIR)


def markdownify_via_template(text):
    """Render `text` exactly as the four already-correct templates do."""
    return Template("{% load markdownify %}{{ text|markdownify }}").render(
        Context({"text": text})
    )


class RenderMarkdownTests(SimpleTestCase):
    """The one renderer: correctness, sanitization, graceful degradation."""

    def test_renders_markdown_to_html(self):
        html = render_markdown("# Heading\n\nSome **bold** text.")
        self.assertIn("<h1", html)
        self.assertIn("<strong>bold</strong>", html)
        self.assertNotIn("**bold**", html)

    def test_empty_and_none_render_empty(self):
        # A blank field must render blank, not "None" and not a crash.
        self.assertEqual(render_markdown(""), "")
        self.assertEqual(render_markdown(None), "")

    def test_script_tag_is_inert(self):
        html = render_markdown("Hello <script>alert(1)</script> world")
        self.assertNotIn("<script>", html)
        self.assertNotIn("</script>", html)
        # The text may survive as escaped content; the executable tag may not.
        self.assertIn("&lt;script&gt;", html)

    def test_event_handler_attribute_is_inert(self):
        html = render_markdown('An image: <img src=x onerror="alert(1)">')
        self.assertNotIn("<img", html)
        self.assertNotIn("onerror=", html.lower())

    def test_javascript_url_is_not_emitted_as_a_live_link(self):
        html = render_markdown("[click me](javascript:alert(1))")
        self.assertNotIn('href="javascript:', html.lower())

    def test_malformed_markdown_degrades_without_a_traceback(self):
        # Unbalanced constructs must render *something* readable — never a
        # traceback, never a silently blanked field.
        for broken in (
            "[unclosed link](http://example.com",
            "```\nunterminated fence",
            "| broken | table\n| --- |",
            "**unclosed bold",
        ):
            with self.subTest(broken=broken):
                html = render_markdown(broken)
                self.assertNotEqual(html.strip(), "")
                self.assertNotIn("Traceback", html)

    def test_output_matches_the_filter_the_other_templates_use(self):
        """One renderer, one result — the acceptance criterion, asserted.

        `message_detail.html` and `thread_detail.html` render content through
        `|markdownify`. If the Python-side renderer ever diverges from the
        template filter, the same content renders two different ways depending
        on which page you are looking at.
        """
        for source in (
            "# Title\n\n* one\n* two",
            "Some `code` and a [link](https://example.com).",
            "<script>alert(1)</script>",
        ):
            with self.subTest(source=source):
                self.assertEqual(
                    str(render_markdown(source)), markdownify_via_template(source)
                )


class MarkdownPreviewEndpointTests(TestCase):
    """The blur round trip: the endpoint the editor calls to re-render."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="mduser", password="mdpass123", email="md@example.com"
        )
        self.url = reverse("markdown_preview")

    def test_requires_authentication(self):
        response = self.client.post(self.url, {"text": "# hi"})
        self.assertIn(response.status_code, (302, 403))

    def test_renders_posted_markdown(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {"text": "# Heading"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("<h1", response.content.decode())

    def test_rejects_get(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_response_is_sanitized(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.url, {"text": '<script>alert(1)</script><img src=x onerror=alert(1)>'}
        )
        body = response.content.decode()
        self.assertNotIn("<script>", body)
        self.assertNotIn("onerror=", body.lower())

    def test_missing_text_is_not_an_error(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)

    def test_martor_markdownify_endpoint_is_routed(self):
        """`MARTOR_MARKDOWNIFY_URL` must resolve, not 404.

        Recorded as a regression because #57 reported this endpoint as unrouted.
        It is in fact routed — `parodynews/urls.py` includes `martor.urls`, and
        `barodybroject/urls.py` includes `parodynews.urls` at the root — so the
        setting at `settings/base.py` points at a live view. This test fails if
        either include is ever removed.
        """
        try:
            match = resolve(settings.MARTOR_MARKDOWNIFY_URL)
        except Resolver404:  # pragma: no cover - only on a routing regression
            self.fail(
                f"MARTOR_MARKDOWNIFY_URL ({settings.MARTOR_MARKDOWNIFY_URL}) "
                "does not resolve; martor.urls is no longer included."
            )
        self.assertTrue(match.func)


class MarkdownFieldTemplateTests(TestCase):
    """The partial: rendered by default, raw only where editing is possible."""

    MARKDOWN = "# Heading\n\nSome **bold** text."

    def _render_field(self, field_name, initial):
        from parodynews.forms import ContentItemForm

        form = ContentItemForm(initial={field_name: initial})
        form.fields[field_name].initial = initial
        return render_to_string(
            "parodynews/_markdown_field.html", {"field": form[field_name]}
        )

    def test_readonly_field_is_rendered_as_html(self):
        html = self._render_field("instructions", self.MARKDOWN)
        self.assertIn("<strong>bold</strong>", html)
        self.assertNotIn("**bold**", html)

    def test_readonly_field_has_no_editor_to_reveal_raw_source(self):
        """A read-only field must never expose its Markdown source.

        There is no textarea in the DOM at all, so this holds regardless of what
        the user clicks or what JavaScript does.
        """
        html = self._render_field("instructions", self.MARKDOWN)
        self.assertIn("data-markdown-readonly", html)
        self.assertNotIn("<textarea", html)
        # …but the value still submits, exactly as a readonly textarea did.
        self.assertIn('type="hidden"', html)
        self.assertIn('name="instructions"', html)

    def test_editable_field_keeps_its_editor_for_raw_on_focus(self):
        html = self._render_field("content_text", self.MARKDOWN)
        self.assertIn("data-markdown-rendered", html)
        self.assertIn("data-markdown-source", html)
        self.assertIn("<textarea", html)
        self.assertIn("<strong>bold</strong>", html)

    def test_editor_is_visible_without_javascript(self):
        """Progressive enhancement: content_detail.js hides the editor, not the
        template. With JS off the field stays editable rather than invisible.

        The partial must therefore emit no `d-none` anywhere — the class is
        added at runtime by `initMarkdownFields`.
        """
        html = self._render_field("content_text", self.MARKDOWN)
        self.assertNotIn("d-none", html)

    def test_script_payload_in_a_field_value_is_inert(self):
        html = self._render_field(
            "content_text", "<script>alert(1)</script><img src=x onerror=alert(1)>"
        )
        self.assertNotIn("<script>", html)
        self.assertNotIn("onerror=", html.lower())


class MarkdownSourceHygieneTests(SimpleTestCase):
    """Static guarantees about how rendering is wired, per #57's criteria."""

    def test_content_detail_has_no_unused_markdownify_load(self):
        """The bug's fingerprint: the library loaded, the filter never called."""
        template = (
            SRC_ROOT
            / "parodynews/templates/parodynews/content_detail.html"
        ).read_text()
        # Ignore the explanatory {% comment %} block, which names the library.
        body = re.sub(
            r"{%\s*comment\s*%}.*?{%\s*endcomment\s*%}", "", template, flags=re.DOTALL
        )
        loads_library = "{% load markdownify %}" in body
        uses_filter = "|markdownify" in body
        self.assertFalse(
            loads_library and not uses_filter,
            "content_detail.html loads the markdownify library without applying "
            "the filter — the exact state that produced #57.",
        )

    def test_no_client_side_markdown_renderer_was_introduced(self):
        """Rendering stays server-side, behind the one sanitizer.

        A browser-side renderer (marked.js, showdown.js) would inject
        unsanitized HTML into the DOM — a stored-XSS path in an app whose
        content is AI-generated and user-editable, in a public repository.
        """
        offenders = []
        for path in SRC_ROOT.rglob("*.js"):
            if "node_modules" in path.parts or "static" in path.parts:
                continue
            text = path.read_text(errors="ignore")
            for lib in ("marked.min.js", "showdown.min.js", "from 'marked'",
                        'require("marked")', "new showdown."):
                if lib in text:
                    offenders.append(f"{path}: {lib}")
        self.assertEqual(offenders, [], f"client-side Markdown renderer found: {offenders}")
