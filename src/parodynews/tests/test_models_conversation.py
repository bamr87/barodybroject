"""
File: test_models_conversation.py
Description: Unit tests for parodynews.models.conversation — Thread and Message
Author: Barodybroject Team <team@example.com>
Created: 2026-09-11
Last Modified: 2026-09-14
Version: 2.0.0

Dependencies:
- django
- pytest-django

Usage: python -m pytest parodynews/tests/test_models_conversation.py (run from src/)

These cover model semantics — defaults, `__str__`, ids, and the on_delete
behaviour of every relation. The workflows that read and write them (running
an assistant, replaying a thread) are covered by `test_services_threads.py`.
"""

import pytest

from parodynews.models import ContentItem, Message, Thread

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


def test_thread_mints_its_own_id():
    """Thread ids used to come from the OpenAI Threads API; conversations are
    now stored locally, so the key is generated here."""
    created = Thread.objects.create(name="Local thread")
    assert created.pk.startswith("thread_")


def test_thread_keeps_an_id_it_was_given():
    assert Thread.objects.create(id="thread_explicit").pk == "thread_explicit"


def test_thread_defaults():
    bare = Thread.objects.create(id="thread_defaults")
    assert bare.name == "New Thread"
    assert bare.description == ""
    assert bare.assistant_group is None
    assert bare.user is None
    assert bare.provider == ""
    assert bare.remote_id == ""
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


def test_ordered_messages_is_oldest_first(thread, content_item):
    """The replay order sent to a provider, so it is the reverse of the list
    ordering used in the UI."""
    first = Message.objects.create(id="msg_a", thread=thread, contentitem=content_item)
    second = Message.objects.create(id="msg_b", thread=thread, contentitem=content_item)
    Message.objects.filter(pk=first.pk).update(
        created_at=second.created_at.replace(year=second.created_at.year - 1)
    )
    assert [m.pk for m in thread.ordered_messages()] == ["msg_a", "msg_b"]


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
        "role",
        "created_at",
        "status",
    ]


def test_message_mints_its_own_id():
    assert Message.objects.create().pk.startswith("msg_")


def test_message_defaults():
    bare = Message.objects.create(id="msg_defaults")
    assert bare.role == Message.ROLE_USER
    assert bare.status == Message.STATUS_INITIAL
    assert bare.run_id == ""
    assert bare.thread is None
    assert bare.provider == ""
    assert bare.model_id == ""
    assert bare.usage == {}
    assert bare.error == ""
    assert bare.created_at is not None


def test_message_text_comes_from_its_content_item(message, content_item):
    assert message.text == content_item.content_text


def test_message_text_is_empty_without_a_content_item():
    """A failed run records a message with no content, and the replay code
    reads `.text` on every message — it must not raise."""
    assert Message.objects.create(id="msg_failed", status="failed").text == ""


def test_message_records_which_provider_answered(thread, content_item):
    """The same thread can be continued by a different provider, so the model
    that produced a turn is recorded per message, not per thread."""
    reply = Message.objects.create(
        thread=thread,
        contentitem=content_item,
        role=Message.ROLE_ASSISTANT,
        provider="anthropic",
        model_id="claude-opus-5",
        usage={"output_tokens": 42},
    )
    stored = Message.objects.get(pk=reply.pk)
    assert (stored.provider, stored.model_id) == ("anthropic", "claude-opus-5")
    assert stored.usage["output_tokens"] == 42


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


def test_role_choices_cover_the_three_chat_roles():
    """`build_history` maps these straight onto provider chat turns."""
    assert {value for value, _label in Message.ROLE_CHOICES} == {
        "user",
        "assistant",
        "system",
    }


def test_deleting_a_message_keeps_its_content_item(message, content_item):
    """Deleting a turn must not take the generated text with it: the same
    ContentItem can be the basis of a published post."""
    message.delete()
    assert ContentItem.objects.filter(pk=content_item.pk).exists()
