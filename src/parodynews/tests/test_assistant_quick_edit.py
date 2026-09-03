"""
File: test_assistant_quick_edit.py
Description: Coverage for the assistant quick-edit endpoint (issue #105)
Author: Barodybroject Team <team@example.com>
Created: 2026-09-02
Version: 1.0.0

Dependencies:
- django
- pytest-django

Usage: python -m pytest parodynews/tests/test_assistant_quick_edit.py (run from src/)

The endpoint backs the Edit button beside the assistant selector on the content
detail form. Saving an assistant necessarily talks to OpenAI — the same call the
existing full-page edit makes — so `save_assistant` and the client factory are
patched here, following the pattern established in test_thread_message_delete.py.
"""

import re
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from parodynews.mixins import AppConfigClientMixin
from parodynews.models import Assistant, OpenAIModel

SAVE_ASSISTANT = "parodynews.views.assistants.save_assistant"


class AssistantQuickEditViewTests(TestCase):
    """GET renders the form fragment; POST saves without a page navigation."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="quickeditor",
            password="testpass123",
            email="quickeditor@example.com",
        )
        self.client.force_login(self.user)

        self.model = OpenAIModel.objects.create(
            model_id="gpt-4o-test", description="Test model"
        )
        self.assistant = Assistant.objects.create(
            id="asst_issue105",
            name="Original name",
            description="Original description",
            instructions="Original instructions.",
            model=self.model,
        )
        self.url = reverse("assistant_quick_edit", args=[self.assistant.pk])

    def _valid_payload(self, **overrides):
        payload = {
            "name": "Updated name",
            "description": "Updated description",
            "instructions": "Updated instructions.",
            "model": self.model.pk,
        }
        payload.update(overrides)
        return payload

    # ------------------------------------------------------------------ GET

    def test_get_returns_form_fragment_not_a_full_page(self):
        """The fragment is injected into an open dialog, so it must not carry
        base.html's chrome — or the page would render inside the modal."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "parodynews/assistant_quick_edit_form.html")
        self.assertTemplateNotUsed(response, "base.html")

        body = response.content.decode("utf-8")
        self.assertNotIn("<!DOCTYPE html>", body)
        self.assertNotIn("<body", body)

    def test_get_is_populated_with_the_current_values(self):
        response = self.client.get(self.url)
        body = response.content.decode("utf-8")

        self.assertIn("Original instructions.", body)
        self.assertIn("Original name", body)

    def test_fragment_ids_are_namespaced(self):
        """The fragment is injected into the content detail page, which already
        renders ContentItemForm (`instructions`) and ContentDetailForm
        (`description`). AssistantForm carries both names, so Django's default
        `id_%s` would put two `id_instructions` and two `id_description`
        elements on one page as soon as the dialog opened — duplicate active
        ids, <label for> binding to whichever came first in document order, and
        an ambiguous getElementById('id_instructions') in content_detail.js.
        """
        body = self.client.get(self.url).content.decode("utf-8")

        for field in ("name", "description", "instructions", "model"):
            self.assertIn(f'id="id_quick_{field}"', body)
            self.assertNotIn(
                f'id="id_{field}"',
                body,
                f"'{field}' still renders an un-namespaced id and would collide "
                f"with the content detail page",
            )

    def test_fragment_ids_do_not_collide_with_the_content_page(self):
        """The collision, asserted directly against the ids the content page
        actually renders rather than against a hand-listed set."""
        from parodynews.forms import ContentDetailForm, ContentItemForm

        page_ids = {
            field.auto_id
            for form in (ContentItemForm(), ContentDetailForm())
            for field in form
            if field.auto_id
        }
        fragment_ids = set(
            re.findall(r'id="([^"]+)"', self.client.get(self.url).content.decode())
        )

        self.assertTrue(page_ids, "expected the content page forms to have ids")
        self.assertEqual(
            fragment_ids & page_ids,
            set(),
            "quick-edit fragment reuses element ids the content page already "
            "renders; the dialog would produce duplicate active ids",
        )

    def test_fragment_labels_point_at_their_own_controls(self):
        """A namespaced id is only a fix if the labels moved with it."""
        body = self.client.get(self.url).content.decode("utf-8")

        for label_for in re.findall(r'<label[^>]*for="([^"]+)"', body):
            self.assertIn(
                f'id="{label_for}"',
                body,
                f"<label for=\"{label_for}\"> has no matching control in the "
                f"fragment, so it binds to whatever owns that id on the page",
            )

    @patch(SAVE_ASSISTANT, autospec=True)
    def test_namespaced_ids_do_not_change_the_post_payload(
        self, mock_save_assistant
    ):
        """Only `auto_id` is overridden, so field NAMES — and therefore the
        payload the browser submits — are unchanged."""
        with patch.object(AppConfigClientMixin, "get_client"):
            response = self.client.post(self.url, self._valid_payload())

        self.assertEqual(response.status_code, 200)
        self.assistant.refresh_from_db()
        self.assertEqual(self.assistant.name, "Updated name")

        body = self.client.get(self.url).content.decode("utf-8")
        for field in ("name", "description", "instructions", "model"):
            self.assertIn(f'name="{field}"', body)

    def test_get_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url.lower())

    def test_get_unknown_assistant_is_404(self):
        response = self.client.get(
            reverse("assistant_quick_edit", args=["asst_does_not_exist"])
        )
        self.assertEqual(response.status_code, 404)

    # ----------------------------------------------------------------- POST

    @patch(SAVE_ASSISTANT, autospec=True)
    def test_post_persists_the_change(self, mock_save_assistant):
        with patch.object(AppConfigClientMixin, "get_client"):
            response = self.client.post(self.url, self._valid_payload())

        self.assertEqual(response.status_code, 200)

        self.assistant.refresh_from_db()
        self.assertEqual(self.assistant.name, "Updated name")
        self.assertEqual(self.assistant.instructions, "Updated instructions.")
        mock_save_assistant.assert_called_once()

    @patch(SAVE_ASSISTANT, autospec=True)
    def test_post_returns_the_fields_the_content_form_mirrors(
        self, mock_save_assistant
    ):
        """content_detail.js writes `instructions` straight into #id_instructions,
        the same field the select's change handler maintains."""
        with patch.object(AppConfigClientMixin, "get_client"):
            response = self.client.post(self.url, self._valid_payload())

        payload = response.json()
        self.assertEqual(payload["assistant_id"], self.assistant.pk)
        self.assertEqual(payload["name"], "Updated name")
        self.assertEqual(payload["instructions"], "Updated instructions.")

    @patch(SAVE_ASSISTANT, autospec=True)
    def test_post_does_not_redirect(self, mock_save_assistant):
        """Not navigating away is the entire point of the feature."""
        with patch.object(AppConfigClientMixin, "get_client"):
            response = self.client.post(self.url, self._valid_payload())

        self.assertNotIn(response.status_code, (301, 302, 303, 307, 308))
        self.assertEqual(response["Content-Type"], "application/json")

    @patch(SAVE_ASSISTANT, autospec=True)
    def test_post_keeps_the_primary_key_stable(self, mock_save_assistant):
        """The PK is the OpenAI assistant id. Rewriting it on an existing
        instance would insert a second row instead of updating this one."""
        with patch.object(AppConfigClientMixin, "get_client"):
            self.client.post(self.url, self._valid_payload())

        self.assertEqual(Assistant.objects.count(), 1)
        self.assertTrue(Assistant.objects.filter(pk="asst_issue105").exists())

    @patch(SAVE_ASSISTANT, autospec=True)
    def test_invalid_form_returns_422_and_does_not_save(self, mock_save_assistant):
        with patch.object(AppConfigClientMixin, "get_client"):
            response = self.client.post(self.url, self._valid_payload(model=""))

        self.assertEqual(response.status_code, 422)
        self.assertTemplateUsed(response, "parodynews/assistant_quick_edit_form.html")

        self.assistant.refresh_from_db()
        self.assertEqual(self.assistant.name, "Original name")
        mock_save_assistant.assert_not_called()

    @patch(SAVE_ASSISTANT, autospec=True)
    def test_openai_failure_leaves_the_local_row_untouched(self, mock_save_assistant):
        """Matches ManageAssistantsView.save: a rejected sync must not persist
        locally, or the two stores silently diverge."""
        mock_save_assistant.side_effect = RuntimeError("OpenAI is down")

        with patch.object(AppConfigClientMixin, "get_client"):
            response = self.client.post(self.url, self._valid_payload())

        self.assertEqual(response.status_code, 502)
        self.assertIn("error", response.json())

        self.assistant.refresh_from_db()
        self.assertEqual(self.assistant.name, "Original name")
        self.assertEqual(self.assistant.instructions, "Original instructions.")

    def test_post_requires_login(self):
        self.client.logout()
        response = self.client.post(self.url, self._valid_payload())
        self.assertEqual(response.status_code, 302)

    def test_unsupported_method_is_rejected(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)

    def test_existing_details_endpoint_is_unchanged(self):
        """content_detail.js still depends on this exact shape; the new endpoint
        was added as a sibling rather than by extending it."""
        response = self.client.get(
            reverse("get_assistant_details", args=[self.assistant.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()), {"assistant_id", "instructions"})
