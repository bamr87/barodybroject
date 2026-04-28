"""
File: conversation.py
Description: Django models for assistant threads and messages
Author: Barodybroject Team <team@example.com>
Created: 2025-11-30
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- django: >=5.1

Usage: from parodynews.models.conversation import Thread, Message

See Also:
- https://platform.openai.com/docs/api-reference/messages
- https://platform.openai.com/docs/api-reference/threads
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Thread(models.Model):
    """Conversation thread for multi-turn content generation.

    Represents a persistent conversation context for interacting with
    assistant groups. Threads maintain conversation history and can be
    associated with users and assistant groups.

    Attributes:
        id (str): Unique thread identifier (primary key, max 255 chars)
        name (str): Human-readable thread name (default: 'New Thread', max 100 chars)
        description (str): Text description of thread purpose
        assistant_group (AssistantGroup): Group of assistants used in this thread
        created_at (datetime): Timestamp when thread was created
        user (User): User who owns this thread
        messages (RelatedManager): Messages in this thread (reverse relation)
        posts (RelatedManager): Posts generated from this thread (reverse relation)

    Examples:
        >>> from parodynews.models import Thread, AssistantGroup
        >>> from django.contrib.auth.models import User
        >>> user = User.objects.first()
        >>> group = AssistantGroup.objects.get(name="Content Pipeline")
        >>> thread = Thread.objects.create(
        ...     id="thread_news_article_123",
        ...     name="Cat Independence Article",
        ...     description="Multi-assistant thread for generating satirical news",
        ...     assistant_group=group,
        ...     user=user
        ... )
        >>> print(thread.get_display_fields())
        ['name', 'description', 'assistant_group', 'created_at']

    Note:
        Thread IDs should be unique and descriptive. Consider using prefixes
        like 'thread_' for clarity.
    """

    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=100, default="New Thread")
    description = models.TextField(blank=True)

    assistant_group = models.ForeignKey(
        "parodynews.AssistantGroup",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="threads",
    )
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

    def get_display_fields(self):
        """Return list of fields to display in admin and list views.

        Returns:
            list: Field names ['name', 'description', 'assistant_group', 'created_at']
        """
        return ["name", "description", "assistant_group", "created_at"]

    def __str__(self):
        """Return the thread name.

        Returns:
            str: The name field value
        """
        return self.name


class Message(models.Model):
    """Individual message in a conversation thread.

    Represents a single message exchange in an OpenAI conversation thread.
    Messages track the assistant used, content generated, and processing status.

    Attributes:
        id (str): Unique message identifier (primary key, max 255 chars)
        created_at (datetime): Timestamp when message was created
        contentitem (ContentItem): Associated content item for this message
        thread (Thread): Parent conversation thread
        assistant (Assistant): Assistant that generated or processed this message
        status (str): Processing status (default: 'initial', max 100 chars)
        run_id (str): OpenAI run ID for tracking API execution (max 255 chars)
        posts (RelatedManager): Posts created from this message (reverse relation)

    Examples:
        >>> from parodynews.models import Message, Thread, Assistant, ContentItem
        >>> thread = Thread.objects.get(name="Cat Independence Article")
        >>> assistant = Assistant.objects.get(name="News Writer")
        >>> contentitem = ContentItem.objects.first()
        >>> message = Message.objects.create(
        ...     id="msg_abc123xyz",
        ...     thread=thread,
        ...     assistant=assistant,
        ...     contentitem=contentitem,
        ...     status="completed",
        ...     run_id="run_def456uvw"
        ... )
        >>> print(message.status)
        completed
        >>> print(message.get_display_fields())
        ['contentitem', 'assistant', 'created_at', 'status']

    Status Values:
        - initial: Message created but not processed
        - queued: Message queued for processing
        - in_progress: Currently being processed
        - completed: Successfully processed
        - failed: Processing failed

    See Also:
        https://platform.openai.com/docs/api-reference/messages
    """

    id = models.CharField(max_length=255, primary_key=True)

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
    status = models.CharField(max_length=100, default="initial")
    run_id = models.CharField(max_length=255, null=True, blank=True)

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

    def get_display_fields(self):
        """Return list of fields to display in admin and list views.

        Returns:
            list: Field names ['contentitem', 'assistant', 'created_at', 'status']
        """
        return ["contentitem", "assistant", "created_at", "status"]

    def __str__(self):
        """Return the message ID.

        Returns:
            str: The id field value
        """
        return self.id
