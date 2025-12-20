"""
File: content.py
Description: Content management views (create/edit/generate content)
Author: Barodybroject Team <team@example.com>
Created: 2025-12-19
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- django: >=5.1
- openai: >=1.57.0

Usage: Included via parodynews URL routing.
"""

import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from ..forms import ContentDetailForm, ContentItemForm
from ..mixins import AppConfigClientMixin, ModelFieldsMixin
from ..models import ContentDetail, ContentItem, Message, Thread
from ..utils import generate_content, openai_create_message


class ManageContentView(
    LoginRequiredMixin, ModelFieldsMixin, AppConfigClientMixin, View
):
    """
    Content management view for creating, editing, and generating content.

    Supports creating/editing content items and details, AI-powered content
    generation using OpenAI, and creating conversation threads.
    """

    model = ContentDetail
    template_name = "parodynews/content_detail.html"

    def get(self, request, content_detail_id=None, content_item_id=None):
        """Handle GET requests for content management interface."""
        if content_detail_id:
            content_detail = ContentDetail.objects.get(pk=content_detail_id)
            content_item = ContentItem.objects.get(
                detail_id=content_detail_id, line_number=1
            )
            content_item_id = content_item.id
            assistant = content_item.assistant.name if content_item.assistant else None
            instructions = (
                content_item.assistant.instructions if content_item.assistant else None
            )
            content_form = ContentItemForm(instance=content_item)
            content_detail_form = ContentDetailForm(instance=content_detail)
        else:
            content_item = None
            content_detail = None
            assistant = None
            instructions = None
            content_form = ContentItemForm()
            content_detail_form = ContentDetailForm()

        content_detail_info = ContentDetail.objects.filter(user=request.user)
        fields, display_fields = self.get_model_fields()

        context = {
            "content_form": content_form,
            "content_detail_form": content_detail_form,
            "content_item_id": content_item_id,
            "content_detail_id": content_detail_id,
            "assistant": assistant,
            "instructions": instructions,
            "content_detail_info": content_detail_info,
            "fields": fields,
            "display_fields": display_fields,
        }

        return render(request, self.template_name, context)

    def post(self, request, content_detail_id=None):
        """Handle POST requests for content management operations."""
        if request.POST.get("_method") == "delete":
            return self.delete(request)

        if request.POST.get("_method") == "save":
            return self.save(request, content_detail_id)

        if request.POST.get("_method") == "generate_content":
            return self.generate_content(request)

        if request.POST.get("_method") == "create_thread":
            return self.create_thread(request)

        return redirect("manage_content")

    def save(self, request, content_detail_id=None):
        """Save content item and detail forms."""
        content_detail_id = request.POST.get("content_detail_id")

        content_form = ContentItemForm(request.POST)
        content_detail_form = ContentDetailForm(request.POST)

        content_detail_info = ContentDetail.objects.all()
        fields, display_fields = self.get_model_fields()

        if content_detail_id:
            content_detail = ContentDetail.objects.get(pk=content_detail_id)
            content = ContentItem.objects.get(detail_id=content_detail, line_number=1)

            content_form = ContentItemForm(request.POST, instance=content)
            content_detail_form = ContentDetailForm(
                request.POST, instance=content_detail
            )
        else:
            content_detail = content_detail_form.save(commit=False)
            content_detail.user = request.user

        if content_form.is_valid() and content_detail_form.is_valid():
            content_detail.save()

            content = content_form.save(commit=False)
            content.detail = content_detail
            content.save()

            messages.success(request, "Content and its details saved successfully!")
            return redirect("content_detail", content_detail_id=content_detail.id)
        else:
            error_messages = f"Content form errors: {content_form.errors}, Content detail form errors: {content_detail_form.errors}"
            messages.error(
                request, f"Error saving content and its details! {error_messages}"
            )

            context = {
                "content_form": content_form,
                "content_detail_form": content_detail_form,
                "content_detail_info": content_detail_info,
                "fields": fields,
                "display_fields": display_fields,
            }

            return render(self.request, self.template_name, context)

        return self.get(request)

    def generate_content(self, request, content_detail=None):
        """Generate content using OpenAI API."""
        client = AppConfigClientMixin.get_client(self)

        content_detail_id = request.POST.get("content_detail_id")
        content_form = ContentItem.objects.get(detail_id=content_detail_id)
        content_detail = ContentDetail.objects.get(pk=content_detail_id)
        data, content_detail_schema = generate_content(client, content_form)
        json_data = json.loads(content_detail_schema)

        try:
            content_data = json.loads(data)
        except json.JSONDecodeError:
            content_data = data

        content_section = (
            content_data["Content"]["body"]
            if isinstance(content_data, dict)
            else content_data
        )

        content_form.content_text = content_section
        content_form.save()

        content_detail_section = json_data["Header"]
        content_detail.title = content_detail_section["title"]
        content_detail.author = content_detail_section["author"]["name"]
        content_detail.published_at = datetime.now()

        content_detail_metadata = json_data["Metadata"]
        content_detail.description = content_detail_metadata["description"]
        content_detail.slug = content_detail_metadata["slug"]

        content_detail.save()

        messages.success(request, "Content generated successfully")

        return redirect("content_detail", content_detail_id=content_detail_id)

    def create_thread(self, request):
        """Create a new conversation thread for content."""
        client = AppConfigClientMixin.get_client(self)

        content_detail_id = request.POST.get("content_detail_id")

        contentitem = ContentItem.objects.get(
            detail_id=content_detail_id, line_number=1
        )
        contentitem_id = contentitem.id

        message, thread_id = openai_create_message(client, contentitem)

        new_thread = Thread(id=thread_id, name=contentitem.detail.title)
        new_thread.user = request.user
        new_thread.save()

        new_message = Message(
            id=message.id, contentitem_id=contentitem_id, thread_id=new_thread.id
        )
        new_message.save()

        messages.success(request, "Message created successfully.")
        return redirect(
            "thread_message_detail", message_id=new_message.id, thread_id=new_thread.id
        )

    def delete(self, request, content_detail_id=None):
        """Delete content detail and associated content items."""
        content_detail_id = request.POST.get("content_detail_id")
        content_detail = ContentDetail.objects.get(pk=content_detail_id)
        contentitem = ContentItem.objects.filter(detail_id=content_detail_id)
        content_detail.delete()
        contentitem.delete()
        messages.success(request, "Content and its details deleted successfully!")
        return redirect("manage_content")

