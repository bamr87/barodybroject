"""
File: test_thread_message_delete.py
Description: Regression tests for deleting a message from a thread (issue #30)
Author: Barodybroject Team <team@example.com>
Created: 2026-08-13
Version: 1.0.0

Dependencies:
- django
- pytest-django

Usage: python -m pytest parodynews/tests/test_thread_message_delete.py (run from src/)
"""

from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from parodynews.mixins import AppConfigClientMixin
from parodynews.models import Message, Thread

VIEW_HELPER = "parodynews.views.threads.openai_delete_message"


class DeleteThreadMessageTests(TestCase):
    """Cover POST /threads/<thread_id>/messages/delete/<message_id>/.

    Issue #30 reported `TypeError: openai_delete_message() missing 1 required
    positional argument: 'thread_id'` from the delete-message route. The call
    site now passes all three arguments, and these tests pin both the arity and
    the ordering of the local/remote deletes so neither can regress silently.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="thread_deleter",
            password="testpass123",
            email="thread_deleter@example.com",
        )
        self.client.force_login(self.user)

        self.thread = Thread.objects.create(
            id="thread_issue30", name="Issue 30 thread", user=self.user
        )
        self.message = Message.objects.create(id="msg_issue30", thread=self.thread)

        self.url = reverse(
            "delete_thread_message",
            kwargs={"thread_id": self.thread.id, "message_id": self.message.id},
        )

    def _post_delete(self):
        """POST the delete-message form the thread template submits."""
        return self.client.post(self.url, {"_method": "delete_thread_message"})

    @patch(VIEW_HELPER, autospec=True)
    def test_delete_passes_client_message_and_thread(self, mock_delete):
        """`openai_delete_message` receives (client, message_id, thread_id).

        `autospec=True` binds the mock to the real signature, so the
        two-argument form from issue #30 raises `TypeError` here instead of
        passing.
        """
        with patch.object(AppConfigClientMixin, "get_client") as mock_get_client:
            openai_client = mock_get_client.return_value
            response = self._post_delete()

        mock_delete.assert_called_once_with(
            openai_client, self.message.id, self.thread.id
        )
        self.assertRedirects(
            response,
            reverse("thread_detail", kwargs={"thread_id": self.thread.id}),
            fetch_redirect_response=False,
        )
        self.assertFalse(Message.objects.filter(pk=self.message.id).exists())

    @patch.object(AppConfigClientMixin, "get_client")
    def test_openai_delete_runs_before_local_row_is_removed(self, mock_get_client):
        """The remote delete must happen while the local row still exists."""
        observed = {}

        def record_local_row(client, message_id, thread_id):
            observed["row_present"] = Message.objects.filter(pk=message_id).exists()

        with patch(VIEW_HELPER, autospec=True, side_effect=record_local_row):
            self._post_delete()

        self.assertTrue(
            observed.get("row_present"),
            "openai_delete_message must be called before the local Message row "
            "is deleted, so an upstream failure leaves the two stores in sync.",
        )

    @patch.object(AppConfigClientMixin, "get_client")
    def test_local_row_survives_when_openai_delete_fails(self, mock_get_client):
        """A failing remote delete leaves the local `Message` retryable."""
        with (
            patch(VIEW_HELPER, autospec=True, side_effect=RuntimeError("openai down")),
            self.assertRaises(RuntimeError),
        ):
            self._post_delete()

        self.assertTrue(Message.objects.filter(pk=self.message.id).exists())
