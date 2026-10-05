"""
File: threads.py
Description: Thread and message workflows (create, replay, run assistants)
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 0.6.0

Dependencies:
- django: >=5.1

Usage:
    from parodynews.services import threads
    thread, first_message = threads.create_thread_from_content(detail, user)
    reply = threads.run_assistant(thread, assistant)

A thread is replayed to the provider on every run: the provider receives the
assistant's instructions as the system prompt and the thread's messages as
alternating user/assistant turns. No provider-side conversation state is
required, which is what lets the same thread be continued by any provider.
"""

from __future__ import annotations

import logging

from django.db import transaction

from parodynews.ai import AIError, ChatMessage
from parodynews.models import (
    Assistant,
    AssistantGroup,
    ContentDetail,
    ContentItem,
    Message,
    Thread,
)
from parodynews.models.base import generate_prefixed_id

from .content import provider_for, request_for_assistant, result_text

logger = logging.getLogger(__name__)


def thread_detail(thread: Thread) -> ContentDetail | None:
    """The ``ContentDetail`` the thread's messages hang off, if any."""
    first = (
        thread.messages.filter(contentitem__isnull=False)
        .select_related("contentitem__detail")
        .order_by("created_at", "id")
        .first()
    )
    return first.contentitem.detail if first is not None else None


def _ensure_detail(thread: Thread) -> ContentDetail:
    detail = thread_detail(thread)
    if detail is None:
        detail = ContentDetail.objects.create(
            title=thread.name[:255], description=thread.description, user=thread.user
        )
    return detail


def build_history(thread: Thread) -> list[ChatMessage]:
    """The thread as provider-agnostic chat turns, oldest first."""
    history: list[ChatMessage] = []
    for message in thread.ordered_messages():
        text = message.text
        if not text.strip():
            continue  # failed runs and empty placeholders carry no turn
        role = (
            message.role if message.role in ("user", "assistant", "system") else "user"
        )
        history.append(ChatMessage(role, text))
    return history


# ---------------------------------------------------------------- creation
@transaction.atomic
def create_thread_from_content(
    content_detail: ContentDetail,
    user=None,
    *,
    assistant_group: AssistantGroup | None = None,
    name: str = "",
) -> tuple[Thread, Message]:
    """Start a thread whose first user turn is the content item's text.

    The prompt is used when the item has no generated text yet, so a thread
    can be started straight from a prompt.
    """
    item = content_detail.contentitem.order_by("line_number", "id").first()
    if item is None:
        raise ValueError("content detail has no content items to start a thread from")
    if not (item.content_text or "").strip():
        item.content_text = item.prompt
        item.save(update_fields=["content_text"])
    thread = Thread.objects.create(
        name=(name or content_detail.title or "New Thread")[:100],
        description=content_detail.description,
        assistant_group=assistant_group,
        user=user,
    )
    message = Message.objects.create(
        thread=thread,
        role=Message.ROLE_USER,
        contentitem=item,
        assistant=item.assistant,
    )
    return thread, message


@transaction.atomic
def add_user_message(
    thread: Thread, text: str, *, assistant: Assistant | None = None
) -> Message:
    """Append a user turn to the thread."""
    detail = _ensure_detail(thread)
    item = ContentItem.objects.create(
        detail=detail,
        assistant=assistant,
        prompt=text,
        content_text=text,
        content_type="message",
    )
    return Message.objects.create(
        thread=thread, role=Message.ROLE_USER, contentitem=item, assistant=assistant
    )


def assign_assistant(message: Message, assistant: Assistant | None) -> Message:
    message.assistant = assistant
    message.save(update_fields=["assistant"])
    return message


# --------------------------------------------------------------------- runs
def run_assistant(
    thread: Thread, assistant: Assistant, *, provider_slug: str | None = None
) -> Message:
    """Run ``assistant`` on the thread and append its reply as a message.

    On failure a ``failed`` message carrying the error is recorded (with no
    content, so it never becomes part of the replayed history) and the
    ``AIError`` is re-raised for the caller to report.
    """
    provider = provider_for(assistant, provider_slug)
    history = build_history(thread)
    if not history:
        raise AIError("the thread has no messages to run an assistant on")
    request = request_for_assistant(
        assistant,
        history,
        provider=provider,
        metadata={"thread_id": thread.id},
    )
    run_id = generate_prefixed_id("run")
    try:
        result = provider.generate(request)
    except AIError as exc:
        Message.objects.create(
            thread=thread,
            role=Message.ROLE_ASSISTANT,
            assistant=assistant,
            status=Message.STATUS_FAILED,
            run_id=run_id,
            provider=provider.slug,
            error=str(exc),
        )
        logger.warning(
            "assistant %s failed on thread %s: %s", assistant.id, thread.id, exc
        )
        raise

    text = result_text(result)
    with transaction.atomic():
        detail = _ensure_detail(thread)
        item = ContentItem.objects.create(
            detail=detail,
            assistant=assistant,
            prompt=history[-1].content,
            content_text=text,
            content_type="message",
        )
        message = Message.objects.create(
            thread=thread,
            role=Message.ROLE_ASSISTANT,
            contentitem=item,
            assistant=assistant,
            status=Message.STATUS_COMPLETED,
            run_id=run_id,
            provider=result.provider,
            model_id=result.model,
            remote_id=result.remote_id,
            usage=result.usage,
        )
        if thread.provider != result.provider:
            thread.provider = result.provider
            thread.save(update_fields=["provider"])
    return message


def run_assistant_group(
    thread: Thread,
    *,
    group: AssistantGroup | None = None,
    provider_slug: str | None = None,
) -> list[Message]:
    """Run every assistant of the group in position order, each seeing the last."""
    group = group or thread.assistant_group
    if group is None:
        raise AIError("the thread has no assistant group to run")
    assistants = group.ordered_assistants()
    if not assistants:
        raise AIError(f"assistant group {group.name!r} has no assistants")
    replies: list[Message] = []
    for assistant in assistants:
        replies.append(run_assistant(thread, assistant, provider_slug=provider_slug))
    return replies
