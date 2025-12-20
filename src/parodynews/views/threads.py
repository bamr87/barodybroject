"""
File: threads.py
Description: Views for thread and message management in AI conversations
Author: Barodybroject Team <team@example.com>
Created: 2025-12-19
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- django: >=5.1

Usage: Included via parodynews URL routing.
"""

import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from openai import OpenAI

from ..forms import ThreadForm
from ..mixins import AppConfigClientMixin, ModelFieldsMixin
from ..models import (
    Assistant,
    AssistantGroupMembership,
    ContentDetail,
    ContentItem,
    Message,
    Post,
    PostFrontMatter,
    Thread,
)
from ..utils import create_run, generate_content_detail, openai_delete_message


class ProcessContentView(LoginRequiredMixin, ModelFieldsMixin, View):
    """
    Content processing view for managing threads, messages, and AI operations.

    Manages thread/message handling, running assistants or assistant groups,
    creating content and posts from conversation messages.
    """

    model = Thread
    template_name = "parodynews/content_processing.html"

    def get(self, request, message_id=None, thread_id=None, assistant_group_id=None):
        """Handle GET requests for content processing interface."""
        if not thread_id and request.GET.get("thread_id"):
            thread_id = request.GET.get("thread_id")

        if thread_id:
            current_thread = Thread.objects.get(pk=thread_id)
            thread_messages = Message.objects.filter(thread_id=thread_id)
            thread_form = ThreadForm(instance=current_thread)
            current_message = None
            assistant_group_id = current_thread.assistant_group_id
        else:
            current_thread = None
            current_message = None
            thread_messages = None
            thread_form = ThreadForm()
            assistant_group_id = None

        if message_id:
            current_message = Message.objects.get(pk=message_id)

        threads = Thread.objects.all()
        fields, display_fields = self.get_model_fields()

        message_list = Message.objects.all()
        assistants = Assistant.objects.all()

        context = {
            "message_list": message_list,
            "current_thread": current_thread,
            "thread_form": thread_form,
            "threads": threads,
            "assistants": assistants,
            "assistant_group_id": assistant_group_id,
            "thread_messages": thread_messages,
            "current_message": current_message,
            "fields": fields,
            "display_fields": display_fields,
        }

        return render(request, self.template_name, context)

    def post(self, request, thread_id=None, message_id=None):
        """Handle POST requests for content processing operations."""
        if request.POST.get("_method") == "delete":
            return self.delete_thread(request, thread_id)

        if request.POST.get("_method") == "delete_thread_message":
            return self.delete_thread_message(request, message_id, thread_id)

        if request.POST.get("_method") == "create_content":
            return self.create_content(request)

        if request.POST.get("_method") == "run_assistant_group":
            return self.run_assistant_group(request)

        if request.POST.get("_method") == "run_assistant_message":
            return self.run_assistant_message(request)

        if request.POST.get("_method") == "create_post":
            return self.create_post(request)

        if request.POST.get("_method") == "save":
            return self.save(request, thread_id)

    def delete_thread(self, request, thread_id=None):
        """Delete a conversation thread and clean up OpenAI resources."""
        thread = Thread.objects.get(pk=thread_id)
        thread.delete()
        client = OpenAI()
        client.beta.threads.delete(thread_id)
        messages.success(request, "Thread deleted successfully.")
        return redirect("process_content")

    def delete_thread_message(self, request, message_id, thread_id):
        """Delete a specific message from a thread."""
        message = Message.objects.get(id=message_id)
        message.delete()
        client = AppConfigClientMixin.get_client(self)
        openai_delete_message(client, message_id, thread_id)
        messages.success(request, "Message deleted successfully.")
        return redirect("thread_detail", thread_id=thread_id)

    def create_content(self, request, thread_id=None, message_id=None):
        """Create structured content from a thread message."""
        client = AppConfigClientMixin.get_client(self)

        message_id = request.POST.get("message_id")
        message = Message.objects.get(id=message_id)
        message_content = message.contentitem.content_text
        assistant_id = message.assistant_id

        generated_content_detail = json.loads(
            generate_content_detail(client, message_content)
        )

        title = (generated_content_detail["Header"]["title"],)
        description = (generated_content_detail["Metadata"]["description"],)
        author = (generated_content_detail["Header"]["author"]["name"],)
        published_at = (datetime.now().isoformat(),)
        slug = generated_content_detail["Metadata"]["slug"]

        content_detail = ContentDetail.objects.create(
            title=title[0],
            description=description[0],
            author=author[0],
            published_at=published_at[0],
            slug=slug[0],
        )
        content_detail_instance = ContentDetail.objects.get(id=content_detail.id)

        contentitem, _ = ContentItem.objects.update_or_create(
            prompt=message_content,
            assistant=(
                Assistant.objects.get(id=assistant_id) if assistant_id else None
            ),
            detail=content_detail_instance,
        )

        content_detail.contentitem.set([contentitem])
        content_detail.save()

        messages.success(request, "Message and content created successfully.")
        return redirect("content_detail", content_detail_id=content_detail.id)

    def run_assistant_group(self, request, thread_id=None, assistant_group_id=None):
        """Execute all assistants in a group sequentially on a thread."""
        client = AppConfigClientMixin.get_client(self)

        thread_id = request.POST.get("thread_id")
        thread = Thread.objects.get(pk=thread_id)

        assistant_group = thread.assistant_group

        assistant_ids = (
            AssistantGroupMembership.objects.filter(assistantgroup=assistant_group)
            .values_list("assistants_id", flat=True)
            .order_by("position")
        )

        for assistant_id in assistant_ids:
            run, run_status, run_response = create_run(client, thread_id, assistant_id)

        messages.success(request, "Assistant group run successfully.")
        return redirect("thread_detail", thread_id=thread.id)

    def run_assistant_message(
        self, request, thread_id=None, message_id=None, assistant_id=None
    ):
        """Run a specific assistant on a message within a thread."""
        client = AppConfigClientMixin.get_client(self)

        thread_id = request.POST.get("thread_id")
        message_id = request.POST.get("message_id")
        assistant_id = request.POST.get("assistant_id")

        run, run_status, run_response = create_run(client, thread_id, assistant_id)

        messages.success(request, "Message run successfully.")
        return redirect(
            "thread_message_detail", message_id=message_id, thread_id=thread_id
        )

    def create_post(self, request):
        """Create a publishable post from a thread message."""
        client = AppConfigClientMixin.get_client(self)

        message_id = request.POST.get("message_id")
        message = Message.objects.get(id=message_id)
        message_content = message.contentitem.content_text
        thread_id = request.POST.get("thread_id")
        assistant_id = message.assistant_id
        assistant = (
            Assistant.objects.get(id=assistant_id) if assistant_id else None
        )

        generated_content_detail = json.loads(
            generate_content_detail(client, message_content)
        )

        title = (generated_content_detail["Header"]["title"],)
        description = (generated_content_detail["Metadata"]["description"],)
        author = (generated_content_detail["Header"]["author"]["name"],)
        published_at = (datetime.now().isoformat(),)
        slug = generated_content_detail["Metadata"]["slug"]

        content_detail = ContentDetail.objects.create(
            title=title[0],
            description=description[0],
            author=author[0],
            published_at=published_at[0],
            slug=slug[0],
        )
        content_detail_instance = ContentDetail.objects.get(id=content_detail.id)

        contentitem, _ = ContentItem.objects.update_or_create(
            prompt=message_content,
            assistant=(
                Assistant.objects.get(id=assistant_id) if assistant_id else None
            ),
            detail=content_detail_instance,
        )

        content_detail.contentitem.set([contentitem])
        content_detail.save()

        messages.success(request, "Message and content created successfully.")

        post = Post.objects.create(
            thread=Thread.objects.get(id=thread_id),
            message=Message.objects.get(id=message_id),
            assistant=assistant,
            content_detail=content_detail,
            post_content=message_content,
            user=request.user,
        )

        post_frontmatter = PostFrontMatter.objects.create(
            post_id=post.id,
            title=message.contentitem.detail.title,
            description=message.contentitem.detail.description,
            author=message.contentitem.detail.author,
            published_at=message.contentitem.detail.published_at,
            slug=message.contentitem.detail.slug,
        )

        post.save()
        post_frontmatter.save()

        messages.success(request, "Post created successfully.")
        return redirect("post_detail", post_id=post.id)

    def save(self, request, thread_id=None):
        """Save modifications to thread properties."""
        thread_id = request.POST.get("thread_id")
        thread_form = ThreadForm(
            request.POST, instance=Thread.objects.get(pk=thread_id)
        )
        if thread_form.is_valid():
            thread = thread_form.save(commit=False)
            thread.save()

        messages.success(request, "Thread saved successfully.")
        return redirect("thread_detail", thread_id=thread_id)


class ManageMessageView(LoginRequiredMixin, View):
    """Message management view for handling individual messages."""

    template_name = "parodynews/message_detail.html"

    def get(self, request, message_id=None):
        """Handle GET requests for message management interface."""
        message_list = Message.objects.all()
        assistants = Assistant.objects.all()
        current_message = None

        if message_id:
            current_message = Message.objects.get(pk=message_id)

        return render(
            request,
            "parodynews/message_detail.html",
            {
                "message_list": message_list,
                "current_message": current_message,
                "assistants": assistants,
            },
        )

    def post(
        self, request, message_id=None, thread_id=None, assigned_assistant_id=None
    ):
        """Handle POST requests for message management operations."""
        if request.POST.get("_method") == "create_message":
            return self.create_message(request)

        if request.POST.get("_method") == "delete_message":
            return self.delete_message(request, message_id, thread_id)

        if request.POST.get("_method") == "assign_assistant_to_message":
            return self.assign_assistant_to_message(request, message_id)

    def delete_message(self, request, message_id, thread_id):
        """Delete a message from the system."""
        message = Message.objects.get(id=message_id)
        message.delete()
        messages.success(request, "Message deleted successfully.")
        return redirect("manage_message")

    def assign_assistant_to_message(self, request, message_id, thread_id=None):
        """Assign an assistant to a message for processing."""
        assigned_assistant_id = request.POST.get("assigned_assistant_id")
        thread_id = request.POST.get("thread_id")

        message = Message.objects.get(pk=message_id)
        assistant = Assistant.objects.get(pk=assigned_assistant_id)
        message.assistant_id = assistant

        message.save()

        messages.success(request, "Message Assigned successfully.")

        if thread_id:
            return redirect(
                "thread_message_detail", thread_id=thread_id, message_id=message_id
            )
        return redirect("message_detail", message_id=message_id)

