"""
File: conversation.py
Description: Locally stored conversation threads and messages
Author: Barodybroject Team <team@example.com>
Created: 2025-11-30
Last Modified: 2026-09-14
Version: 0.6.0

Dependencies:
- django: >=5.1

Usage: from parodynews.models.conversation import Thread, Message

Threads and messages are the application's own record of a conversation.
Running an assistant replays the thread's messages to whichever provider is
configured, so nothing depends on a provider keeping state for us.
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from .base import generate_prefixed_id


class Thread(models.Model):
    """Conversation thread for multi-turn content generation.

    Attributes:
        id (str): Locally generated primary key (``thread_...``)
        name (str): Human-readable thread name
        description (str): Text description of thread purpose
        assistant_group (AssistantGroup): Group run by "Run assistant group"
        provider (str): Provider slug that last ran on this thread (informational)
        remote_id (str): Provider-side conversation id, when a provider keeps one
        user (User): Owner
    """

    id = models.CharField(max_length=255, primary_key=True, blank=True)
    name = models.CharField(max_length=100, default="New Thread")
    description = models.TextField(blank=True)
    assistant_group = models.ForeignKey(
        "parodynews.AssistantGroup",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="threads",
    )
    provider = models.CharField(max_length=50, blank=True, default="")
    remote_id = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="threads"
    )

    class Meta:
        app_label = "parodynews"
        verbose_name = "Thread"
        verbose_name_plural = "Threads"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_prefixed_id("thread")
        super().save(*args, **kwargs)

    def get_display_fields(self):
        return ["name", "description", "assistant_group", "created_at"]

    def ordered_messages(self):
        """Messages oldest first: the order they are replayed to a provider."""
        return self.messages.select_related("contentitem", "assistant").order_by(
            "created_at", "id"
        )


class Message(models.Model):
    """Individual message in a conversation thread.

    The text lives on the linked :class:`~parodynews.models.ContentItem`;
    the message records who said it (``role``), which assistant and provider
    produced it, and how the run went.

    Status values:
        - initial: created, not yet processed
        - queued / in_progress: a run is pending or executing
        - completed: an assistant run finished successfully
        - failed: the last run raised an error (see ``error``)
    """

    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"
    ROLE_SYSTEM = "system"
    ROLE_CHOICES = [
        (ROLE_USER, "User"),
        (ROLE_ASSISTANT, "Assistant"),
        (ROLE_SYSTEM, "System"),
    ]

    STATUS_INITIAL = "initial"
    STATUS_QUEUED = "queued"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    id = models.CharField(max_length=255, primary_key=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_USER)
    created_at = models.DateTimeField(default=timezone.now)
    contentitem = models.ForeignKey(
        "parodynews.ContentItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages",
    )
    thread = models.ForeignKey(
        Thread, on_delete=models.SET_NULL, null=True, related_name="messages"
    )
    assistant = models.ForeignKey(
        "parodynews.Assistant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages",
    )
    status = models.CharField(max_length=100, default=STATUS_INITIAL)
    run_id = models.CharField(max_length=255, blank=True, default="")
    provider = models.CharField(max_length=50, blank=True, default="")
    model_id = models.CharField(max_length=255, blank=True, default="")
    remote_id = models.CharField(max_length=255, blank=True, default="")
    usage = models.JSONField(default=dict, blank=True)
    error = models.TextField(blank=True, default="")

    class Meta:
        app_label = "parodynews"
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["thread", "-created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.id

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_prefixed_id("msg")
        super().save(*args, **kwargs)

    @property
    def text(self) -> str:
        return self.contentitem.content_text if self.contentitem_id else ""

    def get_display_fields(self):
        return ["contentitem", "assistant", "role", "created_at", "status"]
