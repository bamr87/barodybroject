"""
File: test_services_threads.py
Description: Tests for parodynews.services.threads — replay, runs, and failure handling
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 1.0.0

Dependencies:
- django
- pytest-django

Usage: python -m pytest parodynews/tests/test_services_threads.py (run from src/)
"""

import pytest

from parodynews.ai import AIError, AIProviderError
from parodynews.models import (
    Assistant,
    AssistantGroupMembership,
    ContentItem,
    Message,
    Thread,
)
from parodynews.services import threads as thread_services

pytestmark = pytest.mark.django_db


# --------------------------------------------------------------------------- #
# create_thread_from_content
# --------------------------------------------------------------------------- #
def test_create_thread_seeds_the_first_user_turn(content_detail, content_item, user):
    thread, message = thread_services.create_thread_from_content(content_detail, user)

    assert thread.user == user
    assert thread.name == content_detail.title
    assert message.role == Message.ROLE_USER
    assert message.contentitem == content_item


def test_create_thread_uses_the_prompt_when_nothing_is_generated_yet(
    content_detail, user
):
    """A thread can be started straight from a prompt, before any generation."""
    item = ContentItem.objects.create(
        detail=content_detail, prompt="Write about cats", content_text=""
    )
    thread, _message = thread_services.create_thread_from_content(content_detail, user)

    item.refresh_from_db()
    assert item.content_text == "Write about cats"
    assert thread_services.build_history(thread)[0].content == "Write about cats"


def test_create_thread_needs_a_content_item(content_detail, user):
    with pytest.raises(ValueError, match="no content items"):
        thread_services.create_thread_from_content(content_detail, user)


# --------------------------------------------------------------------------- #
# build_history — what gets replayed to the provider
# --------------------------------------------------------------------------- #
def test_history_is_oldest_first_with_roles(thread, content_item, assistant):
    first = Message.objects.create(
        thread=thread, contentitem=content_item, role=Message.ROLE_USER
    )
    reply_item = ContentItem.objects.create(
        detail=content_item.detail, prompt="p", content_text="the reply"
    )
    second = Message.objects.create(
        thread=thread, contentitem=reply_item, role=Message.ROLE_ASSISTANT
    )
    Message.objects.filter(pk=first.pk).update(
        created_at=second.created_at.replace(year=second.created_at.year - 1)
    )

    history = thread_services.build_history(thread)
    assert [(m.role, m.content) for m in history] == [
        ("user", content_item.content_text),
        ("assistant", "the reply"),
    ]


def test_history_skips_messages_with_no_text(thread, content_item):
    """A failed run leaves a message with an error and no content; replaying it
    would send an empty turn the provider rejects."""
    Message.objects.create(thread=thread, contentitem=content_item)
    Message.objects.create(thread=thread, status="failed", error="boom")

    assert len(thread_services.build_history(thread)) == 1


# --------------------------------------------------------------------------- #
# run_assistant
# --------------------------------------------------------------------------- #
def test_run_assistant_appends_a_completed_reply(thread, content_item, assistant):
    Message.objects.create(thread=thread, contentitem=content_item)

    reply = thread_services.run_assistant(thread, assistant)

    assert reply.role == Message.ROLE_ASSISTANT
    assert reply.status == Message.STATUS_COMPLETED
    assert reply.provider == "mock"
    assert reply.model_id == "mock-1"
    assert reply.text
    assert reply.usage


def test_run_assistant_records_the_provider_on_the_thread(
    thread, content_item, assistant
):
    Message.objects.create(thread=thread, contentitem=content_item)
    thread_services.run_assistant(thread, assistant)

    thread.refresh_from_db()
    assert thread.provider == "mock"


def test_run_assistant_replays_the_whole_conversation(
    thread, content_item, assistant, mock_provider
):
    Message.objects.create(thread=thread, contentitem=content_item)
    thread_services.run_assistant(thread, assistant)
    thread_services.run_assistant(thread, assistant)

    # The second run sees the first turn and the reply it produced.
    assert len(mock_provider.calls[1].messages) == 2


def test_run_assistant_sends_the_assistants_instructions_as_the_system_prompt(
    thread, content_item, assistant, mock_provider
):
    Message.objects.create(thread=thread, contentitem=content_item)
    thread_services.run_assistant(thread, assistant)

    assert mock_provider.calls[0].system == assistant.instructions


def test_run_assistant_needs_something_to_reply_to(thread, assistant):
    with pytest.raises(AIError, match="no messages"):
        thread_services.run_assistant(thread, assistant)


def test_a_failed_run_is_recorded_and_re_raised(
    thread, content_item, assistant, mock_provider
):
    """The operator has to be able to see what went wrong, and the error has to
    reach the API so the UI can report it."""
    Message.objects.create(thread=thread, contentitem=content_item)
    mock_provider.queue_response(AIProviderError("provider exploded", provider="mock"))

    with pytest.raises(AIProviderError):
        thread_services.run_assistant(thread, assistant)

    failure = thread.messages.filter(status=Message.STATUS_FAILED).get()
    assert "provider exploded" in failure.error
    assert failure.role == Message.ROLE_ASSISTANT


def test_a_failed_run_does_not_pollute_the_replayed_history(
    thread, content_item, assistant, mock_provider
):
    Message.objects.create(thread=thread, contentitem=content_item)
    mock_provider.queue_response(AIProviderError("boom", provider="mock"))
    with pytest.raises(AIProviderError):
        thread_services.run_assistant(thread, assistant)

    # One turn still: the failure carries no content.
    assert len(thread_services.build_history(thread)) == 1


def test_run_assistant_can_be_pointed_at_another_provider(
    thread, content_item, assistant, mock_provider
):
    """The same thread can be continued by a different provider — that is the
    whole point of storing the conversation locally."""
    Message.objects.create(thread=thread, contentitem=content_item)
    reply = thread_services.run_assistant(thread, assistant, provider_slug="mock")
    assert reply.provider == "mock"


# --------------------------------------------------------------------------- #
# run_assistant_group
# --------------------------------------------------------------------------- #
def test_a_group_runs_every_member_in_position_order(
    thread, content_item, assistant, assistant_group, ai_model, mock_provider
):
    second = Assistant.objects.create(
        name="Editor", model=ai_model, instructions="Edit it."
    )
    AssistantGroupMembership.objects.create(
        assistantgroup=assistant_group, assistant=assistant, position=1
    )
    AssistantGroupMembership.objects.create(
        assistantgroup=assistant_group, assistant=second, position=2
    )
    Message.objects.create(thread=thread, contentitem=content_item)

    replies = thread_services.run_assistant_group(thread)

    assert [reply.assistant for reply in replies] == [assistant, second]
    # Each member sees everything before it, so the prompts grow.
    assert len(mock_provider.calls[1].messages) > len(mock_provider.calls[0].messages)


def test_a_group_run_needs_a_group(thread, content_item):
    thread.assistant_group = None
    thread.save()
    Message.objects.create(thread=thread, contentitem=content_item)

    with pytest.raises(AIError, match="no assistant group"):
        thread_services.run_assistant_group(thread)


def test_an_empty_group_is_an_error(thread, content_item, assistant_group):
    Message.objects.create(thread=thread, contentitem=content_item)
    with pytest.raises(AIError, match="no assistants"):
        thread_services.run_assistant_group(thread)


# --------------------------------------------------------------------------- #
# add_user_message / assign_assistant
# --------------------------------------------------------------------------- #
def test_adding_a_user_message_extends_the_history(thread, content_item):
    Message.objects.create(thread=thread, contentitem=content_item)
    thread_services.add_user_message(thread, "one more thing")

    history = thread_services.build_history(thread)
    assert history[-1].role == "user"
    assert history[-1].content == "one more thing"


def test_adding_a_message_to_a_bare_thread_creates_a_content_detail(user):
    """A thread started outside the content screen still needs somewhere to
    hang its items."""
    thread = Thread.objects.create(name="Bare", user=user)
    message = thread_services.add_user_message(thread, "hello")
    assert message.contentitem is not None


def test_assigning_an_assistant_updates_the_message(message, plain_assistant):
    thread_services.assign_assistant(message, plain_assistant)
    message.refresh_from_db()
    assert message.assistant == plain_assistant


def test_an_assistant_can_be_unassigned(message):
    thread_services.assign_assistant(message, None)
    message.refresh_from_db()
    assert message.assistant is None
