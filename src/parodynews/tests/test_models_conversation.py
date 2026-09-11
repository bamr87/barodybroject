"""
File: test_models_conversation.py
Description: Unit tests for parodynews.models.conversation — Thread and Message
Author: Barodybroject Team <team@example.com>
Created: 2026-09-11
Version: 1.0.0

Dependencies:
- django
- pytest-django

Usage: python -m pytest parodynews/tests/test_models_conversation.py (run from src/)

Note: `test_thread_message_delete.py` already covers the delete ROUTE for these
two models (issue #30). This module covers their model semantics — defaults,
`__str__`, and the on_delete behaviour of every relation — and deliberately does
not duplicate the route tests.
"""

import pytest

from parodynews.models import Message, Thread

pytestmark = pytest.mark.django_db


# --------------------------------------------------------------------------- #
# Thread
# --------------------------------------------------------------------------- #
def test_thread_round_trips(thread, assistant_group, user):
    stored = Thread.objects.get(pk=thread.pk)
    assert stored.pk == "thread_model_tests"
    assert stored.name == "Cat Independence Article"
    assert stored.assistant_group == assistant_group
    assert stored.user == user


def test_thread_str_is_the_name(thread):
    assert str(thread) == "Cat Independence Article"


def test_thread_display_fields(thread):
    assert thread.get_display_fields() == [
        "name",
        "description",
        "assistant_group",
        "created_at",
    ]


def test_thread_primary_key_is_the_supplied_id():
    """A CharField pk — the OpenAI thread id, not an AutoField."""
    assert Thread._meta.pk.name == "id"
    thread = Thread.objects.create(id="thread_explicit")
    assert thread.pk == "thread_explicit"


def test_thread_defaults():
    bare = Thread.objects.create(id="thread_defaults")
    assert bare.name == "New Thread"
    assert bare.description == ""
    assert bare.assistant_group is None
    assert bare.user is None
    assert bare.created_at is not None


def test_deleting_the_user_deletes_their_threads(thread, user):
    user.delete()
    assert not Thread.objects.filter(pk=thread.pk).exists()


def test_deleting_the_assistant_group_deletes_its_threads(thread, assistant_group):
    """CASCADE, unlike every other assistant-side relation in the tree — worth
    pinning precisely because it is the exception."""
    assistant_group.delete()
    assert not Thread.objects.filter(pk=thread.pk).exists()


def test_threads_are_newest_first():
    older = Thread.objects.create(id="thread_older", name="Older")
    newer = Thread.objects.create(id="thread_newer", name="Newer")
    Thread.objects.filter(pk=older.pk).update(
        created_at=newer.created_at.replace(year=newer.created_at.year - 1)
    )
    assert list(Thread.objects.values_list("name", flat=True)) == ["Newer", "Older"]


def test_the_user_reaches_their_threads_by_related_name(thread, user):
    assert list(user.threads.all()) == [thread]


# --------------------------------------------------------------------------- #
# Message
# --------------------------------------------------------------------------- #
def test_message_round_trips(message, thread, assistant, content_item):
    stored = Message.objects.get(pk=message.pk)
    assert stored.thread == thread
    assert stored.assistant == assistant
    assert stored.contentitem == content_item
    assert stored.status == "completed"
    assert stored.run_id == "run_model_tests"


def test_message_str_is_the_id(message):
    assert str(message) == "msg_model_tests"


def test_message_display_fields(message):
    assert message.get_display_fields() == [
        "contentitem",
        "assistant",
        "created_at",
        "status",
    ]


def test_message_defaults():
    bare = Message.objects.create(id="msg_defaults")
    assert bare.status == "initial"
    assert bare.run_id is None
    assert bare.thread is None
    assert bare.created_at is not None


def test_deleting_the_thread_keeps_the_message(message, thread):
    """SET_NULL on all three FKs — a message survives every parent it points at,
    which is what makes an orphaned row possible and worth asserting."""
    thread.delete()
    message.refresh_from_db()
    assert message.thread is None
    assert Message.objects.filter(pk=message.pk).exists()


def test_deleting_the_content_item_keeps_the_message(message, content_item):
    content_item.delete()
    message.refresh_from_db()
    assert message.contentitem is None


def test_deleting_the_assistant_keeps_the_message(message, assistant):
    assistant.delete()
    message.refresh_from_db()
    assert message.assistant is None


def test_messages_are_newest_first(thread):
    older = Message.objects.create(id="msg_older", thread=thread)
    newer = Message.objects.create(id="msg_newer", thread=thread)
    Message.objects.filter(pk=older.pk).update(
        created_at=newer.created_at.replace(year=newer.created_at.year - 1)
    )
    assert list(Message.objects.values_list("id", flat=True)) == [
        "msg_newer",
        "msg_older",
    ]


def test_the_thread_reaches_its_messages_by_related_name(message, thread):
    assert list(thread.messages.all()) == [message]
