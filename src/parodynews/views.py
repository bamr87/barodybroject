"""
Parody News Django Views Module.

This module contains all the view classes and functions for the Barodybroject Django application.
It provides a comprehensive web interface for managing AI-powered content generation, including:

- Content management and generation using OpenAI
- Assistant and assistant group management
- Thread and message handling for AI conversations
- Post creation and publishing workflows
- JSON schema management for structured content
- Django REST Framework API endpoints
- Integration with Django CMS for publishing

The module follows Django best practices with proper error handling, user authentication,
and form validation. It integrates with OpenAI's API for AI-powered content generation
and provides both web interface and REST API endpoints.

Author: Barodybroject Team <team@example.com>
Created: 2025-01-15
Last Modified: 2025-01-20
Version: 1.2.0

Dependencies:
    - Django 4.x: Web framework
    - OpenAI: AI content generation
    - Django REST Framework: API endpoints
    - Django CMS: Content management
    - PyGithub: GitHub integration
    - PyYAML: YAML processing

Container Requirements:
    - Base Image: python:3.8-slim
    - Exposed Ports: 8000/tcp
    - Volumes: /app/src:rw, /app/static:rw
    - Environment: DJANGO_SETTINGS_MODULE, OPENAI_API_KEY

Usage:
    This module is automatically loaded by Django's URL dispatcher.
    Views are accessed through URL patterns defined in urls.py.
"""

import json
from datetime import datetime

import yaml
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import Resolver404, resolve, reverse_lazy
from django.utils.translation import override
from django.views import View
from django.views.generic import ListView, TemplateView
from github import Github
from openai import OpenAI
from rest_framework import status, viewsets
from rest_framework.response import Response

from . import models
from .forms import (AssistantForm, AssistantGroupForm,
                    AssistantGroupMembershipFormSet, ContentDetailForm,
                    ContentItemForm, JSONSchemaForm, MyObjectForm, PostForm,
                    PostFrontMatterForm, ThreadForm)
from .mixins import AppConfigClientMixin, ModelFieldsMixin
from .models import (AppConfig, Assistant, AssistantGroup,
                     AssistantGroupMembership, ContentDetail, ContentItem,
                     GeneralizedCodes, JSONSchema, Message, MyObject, Post,
                     PostFrontMatter, PostVersion, PoweredBy, Thread)
from .serializers import (AssistantGroupSerializer, AssistantSerializer,
                          ContentDetailSerializer, ContentItemSerializer,
                          GeneralizedCodesSerializer, JSONSchemaSerializer,
                          MessageSerializer, MyObjectSerializer,
                          PostFrontMatterSerializer, PostSerializer,
                          PoweredBySerializer, ThreadSerializer)
from .utils import (create_or_update_assistant, create_run, delete_assistant,
                    generate_content, generate_content_detail,
                    get_openai_client, openai_create_message,
                    openai_delete_message, save_assistant)

print("Loading views.py")


# =============================================================================
# TEMPLATE VIEWS SECTION
# =============================================================================

# TODO: Post Frontmatter needs to be dynamic and populated based on the assistant schema, otherwise the front matter is defaulted
# TODO: Link post to the URL and filename, and github location


class FooterView(TemplateView):
    """
    Footer template view for rendering page footers.

    This view provides context data for footer templates, including
    information about services and tools that power the application.

    Attributes:
        template_name (str): Template file path for footer rendering

    Example:
        .. code-block:: python

            # URL configuration
            path('footer/', FooterView.as_view(), name='footer')
    """

    template_name = "footer.html"

    def get_context_data(self, **kwargs):
        """
        Get context data for footer template.

        Retrieves all PoweredBy objects to display in the footer,
        showing what services and tools power the application.

        Args:
            **kwargs: Additional keyword arguments from parent class

        Returns:
            dict: Context dictionary containing powered_by queryset

        Example:
            .. code-block:: python

                context = {
                    'powered_by': [<PoweredBy: OpenAI>, <PoweredBy: Django>]
                }
        """
        context = super().get_context_data(**kwargs)
        context["powered_by"] = PoweredBy.objects.all()
        return context


class UserLoginView(LoginView):
    """
    Custom user login view extending Django's built-in LoginView.

    Provides a custom template for user authentication while maintaining
    all the security features and functionality of Django's LoginView.

    Attributes:
        template_name (str): Custom login template path

    Example:
        .. code-block:: python

            # URL configuration
            path('login/', UserLoginView.as_view(), name='login')
    """

    template_name = "login.html"


def index(request):
    """
    Home page view function.

    Renders the main index page of the application. This is typically
    the landing page that users see when they first visit the site.

    Args:
        request (HttpRequest): The HTTP request object

    Returns:
        HttpResponse: Rendered index page template

    Example:
        .. code-block:: python

            # URL configuration
            path('', index, name='index')
    """
    # This view will render the root index page
    return render(request, "parodynews/index.html", {})


# =============================================================================
# CONTENT MANAGEMENT VIEWS SECTION
# =============================================================================


class ManageContentView(
    LoginRequiredMixin, ModelFieldsMixin, AppConfigClientMixin, View
):
    """
    Content management view for creating, editing, and generating content.

    This view provides a comprehensive interface for managing content items
    and their details. It supports:

    - Creating new content items and details
    - Editing existing content and metadata
    - AI-powered content generation using OpenAI
    - Creating conversation threads for content
    - Form validation and error handling

    The view integrates with OpenAI's API for automated content generation
    and provides a user-friendly interface for content management workflows.

    Attributes:
        model: Primary model class (ContentDetail)
        template_name (str): Template for content management interface

    Mixins:
        - LoginRequiredMixin: Ensures user authentication
        - ModelFieldsMixin: Provides model field introspection
        - AppConfigClientMixin: Handles OpenAI client configuration

    Example:
        .. code-block:: python

            # URL configuration
            path('content/', ManageContentView.as_view(), name='manage_content')
            path('content/<int:content_detail_id>/',
                 ManageContentView.as_view(), name='content_detail')
    """

    model = ContentDetail
    template_name = "parodynews/content_detail.html"

    def get(self, request, content_detail_id=None, content_item_id=None):
        """
        Handle GET requests for content management interface.

        Displays the content management form with existing data if editing,
        or empty forms for creating new content. Provides context for
        associated assistants and instructions.

        Args:
            request (HttpRequest): The HTTP request object
            content_detail_id (int, optional): ID of content detail to edit
            content_item_id (int, optional): ID of content item to edit

        Returns:
            HttpResponse: Rendered content management template

        Context:
            - content_form: Form for content item data
            - content_detail_form: Form for content metadata
            - assistant: Associated assistant name
            - instructions: Assistant instructions
            - content_detail_info: User's content details
            - fields: Model field information
            - display_fields: Fields for display
        """
        # Check if content_detail_id is provided
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

        # Initialize the forms

        # Get the fields and display fields for the model
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

        # Render the content detail page with the forms and content details
        return render(request, self.template_name, context)

    def post(self, request, content_detail_id=None):
        """
        Handle POST requests for content management operations.

        Routes different operations based on the _method parameter:
        - delete: Delete content and associated data
        - save: Save content and metadata forms
        - generate_content: Generate content using AI
        - create_thread: Create conversation thread

        Args:
            request (HttpRequest): The HTTP request object
            content_detail_id (int, optional): ID of content to operate on

        Returns:
            HttpResponse: Redirect or rendered template based on operation
        """
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
        """
        Save content item and detail forms.

        Validates and saves both content item and content detail forms.
        Handles both creation of new content and updating existing content.
        Provides proper error handling and user feedback.

        Args:
            request (HttpRequest): The HTTP request object containing form data
            content_detail_id (int, optional): ID of existing content to update

        Returns:
            HttpResponse: Redirect to content detail on success,
                         or rendered form with errors on failure

        Raises:
            ValidationError: If form validation fails

        Note:
            Sets request.user as the content owner for new content.
        """
        content_detail_id = request.POST.get("content_detail_id")

        # initialize the forms
        content_form = ContentItemForm(request.POST)
        content_detail_form = ContentDetailForm(request.POST)

        # Get the fields and display fields for the model
        content_detail_info = ContentDetail.objects.all()
        fields, display_fields = self.get_model_fields()

        # Check if content_detail_id is provided
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

        # Save the forms if they are valid
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

            # Pass the forms back to the context to preserve the data
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
        """
        Generate content using OpenAI API.

        Uses the configured OpenAI client to generate content based on
        the content item's prompt. Parses the generated content and
        updates both the content text and metadata fields.

        Args:
            request (HttpRequest): The HTTP request object
            content_detail (ContentDetail, optional): Content detail instance

        Returns:
            HttpResponse: Redirect to content detail page

        Raises:
            json.JSONDecodeError: If generated content is not valid JSON
            OpenAIError: If API call fails

        Note:
            FIXME: Content generation fails if assistant is assigned to schema

        Todo:
            * Improve error handling for schema-assistant conflicts
            * Add retry logic for API failures
        """
        # FIXME: if an assistant is assigned to a schema, generate content fails
        # Retrieve the OpenAI client from the session
        client = AppConfigClientMixin.get_client(self)

        content_detail_id = request.POST.get("content_detail_id")
        content_form = ContentItem.objects.get(detail_id=content_detail_id)
        content_detail = ContentDetail.objects.get(pk=content_detail_id)
        data, content_detail_schema = generate_content(client, content_form)
        json_data = json.loads(content_detail_schema)
        # Check if data is in JSON format
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
        """
        Create a new conversation thread for content.

        Creates an OpenAI conversation thread and associated Django models
        for managing AI-powered conversations about content. Links the
        thread to the content item and creates an initial message.

        Args:
            request (HttpRequest): The HTTP request object

        Returns:
            HttpResponse: Redirect to thread message detail page

        Raises:
            OpenAIError: If thread creation fails
            DoesNotExist: If content item is not found

        Example:
            The created thread enables multi-turn conversations with AI
            assistants about the content, allowing for iterative refinement.
        """
        # Retrieve the OpenAI client from the session
        client = AppConfigClientMixin.get_client(self)

        content_detail_id = request.POST.get("content_detail_id")

        contentitem = ContentItem.objects.get(
            detail_id=content_detail_id, line_number=1
        )
        contentitem_id = contentitem.id

        # Call utils.create_message to get message and thread_id
        message, thread_id = openai_create_message(client, contentitem)

        # Create a new Thread instance and save it
        new_thread = Thread(id=thread_id, name=contentitem.detail.title)
        new_thread.user = request.user
        new_thread.save()
        # new_thread.create_run_queue()

        print(f"New thread created with ID: {contentitem_id}")

        # Create and save the new Message instance with the thread_id
        new_message = Message(
            id=message.id, contentitem_id=contentitem_id, thread_id=new_thread.id
        )
        new_message.save()

        messages.success(request, "Message created successfully.")
        return redirect(
            "thread_message_detail", message_id=new_message.id, thread_id=new_thread.id
        )

    def delete(self, request, content_detail_id=None):
        """
        Delete content detail and associated content items.

        Removes both the content detail record and all associated
        content items. Provides user feedback and redirects to the
        content management page.

        Args:
            request (HttpRequest): The HTTP request object
            content_detail_id (int, optional): ID of content to delete

        Returns:
            HttpResponse: Redirect to manage content page

        Warning:
            This operation is irreversible. All associated content
            items will also be deleted due to foreign key relationships.
        """
        content_detail_id = request.POST.get("content_detail_id")
        content_detail = ContentDetail.objects.get(pk=content_detail_id)
        contentitem = ContentItem.objects.filter(detail_id=content_detail_id)
        content_detail.delete()
        contentitem.delete()
        messages.success(request, "Content and its details deleted successfully!")
        return redirect("manage_content")


class ProcessContentView(LoginRequiredMixin, ModelFieldsMixin, View):
    """
    Content processing view for managing threads, messages, and AI operations.

    This view provides a comprehensive interface for processing content through
    AI-powered workflows. It manages:

    - Thread and message management for AI conversations
    - Running individual assistants or assistant groups
    - Creating content and posts from conversation messages
    - Deleting threads and messages with proper cleanup

    The view serves as the central hub for AI-powered content processing,
    enabling users to orchestrate complex workflows involving multiple
    AI assistants and conversation threads.

    Attributes:
        model: Primary model class (Thread)
        template_name (str): Template for content processing interface

    Mixins:
        - LoginRequiredMixin: Ensures user authentication
        - ModelFieldsMixin: Provides model field introspection

    Example:
        .. code-block:: python

            # URL configuration
            path('process/', ProcessContentView.as_view(), name='process_content')
            path('thread/<str:thread_id>/',
                 ProcessContentView.as_view(), name='thread_detail')
    """

    model = Thread
    template_name = "parodynews/content_processing.html"
    # View to list all threads and messages

    def get(self, request, message_id=None, thread_id=None, assistant_group_id=None):
        """
        Handle GET requests for content processing interface.

        Displays the content processing interface with thread and message
        management capabilities. Supports selecting threads via URL parameters
        or GET parameters for flexible navigation.

        Args:
            request (HttpRequest): The HTTP request object
            message_id (str, optional): ID of specific message to display
            thread_id (str, optional): ID of thread to display
            assistant_group_id (int, optional): ID of assistant group

        Returns:
            HttpResponse: Rendered content processing template

        Context:
            - current_thread: Selected thread object
            - thread_messages: Messages in selected thread
            - threads: All available threads
            - assistants: All available assistants
            - message_list: All messages
            - fields: Model field information

        Note:
            Supports thread selection via both URL path and GET parameter
            for enhanced user experience and deep linking.
        """
        # support selecting a thread via GET param
        if not thread_id and request.GET.get("thread_id"):
            thread_id = request.GET.get("thread_id")
        # Check if thread_id is provided
        if thread_id:
            current_thread = Thread.objects.get(pk=thread_id)
            thread_messages = Message.objects.filter(thread_id=thread_id)
            thread_form = ThreadForm(instance=current_thread)
            thread_messages = Message.objects.filter(thread_id=thread_id)
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

        threads = (
            Thread.objects.all()
        )  # Retrieve all threads regardless of user assignment
        fields, display_fields = self.get_model_fields()

        message_list = Message.objects.all()
        assistants = Assistant.objects.all()  # Fetch all assistants

        context = {
            "message_list": message_list,
            "current_thread": current_thread,
            "thread_form": thread_form,
            "threads": threads,
            "assistants": assistants,
            "assistant_group_id": assistant_group_id,
            "thread_messages": thread_messages,
            "current_message": current_message,
            # 'thread_run_form': ThreadRunFrom(),
            "fields": fields,
            "display_fields": display_fields,
        }

        return render(request, self.template_name, context)

    def post(self, request, thread_id=None, message_id=None):
        """
        Handle POST requests for content processing operations.

        Routes different operations based on the _method parameter:
        - delete: Delete entire thread
        - delete_thread_message: Delete specific message
        - create_content: Create content from message
        - run_assistant_group: Run all assistants in group
        - run_assistant_message: Run single assistant on message
        - create_post: Create publishable post from message
        - save: Save thread modifications

        Args:
            request (HttpRequest): The HTTP request object
            thread_id (str, optional): ID of thread to operate on
            message_id (str, optional): ID of message to operate on

        Returns:
            HttpResponse: Redirect or rendered template based on operation
        """
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
        """
        Delete a conversation thread and clean up OpenAI resources.

        Removes the thread from both the local database and OpenAI's
        servers to ensure complete cleanup and prevent orphaned resources.

        Args:
            request (HttpRequest): The HTTP request object
            thread_id (str, optional): ID of thread to delete

        Returns:
            HttpResponse: Redirect to content processing page

        Raises:
            OpenAIError: If OpenAI thread deletion fails
            DoesNotExist: If thread is not found in database

        Warning:
            This operation permanently deletes the thread and all
            associated messages from both local storage and OpenAI.
        """
        # Fetch the thread from the database
        thread = Thread.objects.get(pk=thread_id)
        # Delete the thread
        thread.delete()
        client = OpenAI()

        client.beta.threads.delete(thread_id)
        messages.success(request, "Thread deleted successfully.")

        # Redirect to a suitable page after deletion, e.g., the threads list page
        return redirect(
            "process_content"
        )  # Replace 'threads_list' with the name of your threads list view

    def delete_thread_message(self, request, message_id, thread_id):
        """
        Delete a specific message from a thread.

        Removes the message from both the local database and OpenAI's
        thread to maintain consistency between local and remote state.

        Args:
            request (HttpRequest): The HTTP request object
            message_id (str): ID of message to delete
            thread_id (str): ID of thread containing the message

        Returns:
            HttpResponse: Redirect to thread detail page

        Raises:
            OpenAIError: If OpenAI message deletion fails
            DoesNotExist: If message is not found in database
        """
        # Retrieve the message instance
        message = Message.objects.get(id=message_id)

        # Delete the message
        message.delete()
        client = AppConfigClientMixin.get_client(self)
        # Delete the message from OpenAI
        openai_delete_message(client, message_id, thread_id)

        messages.success(request, "Message deleted successfully.")
        return redirect("thread_detail", thread_id=thread_id)

    def create_content(self, request, thread_id=None, message_id=None):
        """
        Create structured content from a thread message.

        Processes a message through AI to generate structured content with
        proper metadata including title, description, author, and slug.
        Creates both ContentDetail and ContentItem records for the generated content.

        Args:
            request (HttpRequest): The HTTP request object
            thread_id (str, optional): ID of thread containing message
            message_id (str, optional): ID of message to process

        Returns:
            HttpResponse: Redirect to content detail page

        Raises:
            json.JSONDecodeError: If AI response is not valid JSON
            OpenAIError: If content generation API call fails
            DoesNotExist: If message or assistant is not found

        Note:
            The generated content includes structured metadata extracted
            from AI processing, including header information and SEO metadata.
        """
        # Retrieve the OpenAI client from the session
        client = AppConfigClientMixin.get_client(self)

        message_id = request.POST.get("message_id")
        message = Message.objects.get(id=message_id)
        message_content = message.contentitem.content_text
        assistant_id = message.assistant_id

        generated_content_detail = json.loads(
            generate_content_detail(client, message_content)
        )
        # First, create the ContentDetail object
        title = (
            generated_content_detail["Header"]["title"],
        )  # Placeholder title, adjust as needed
        description = (
            generated_content_detail["Metadata"]["description"],
        )  # Placeholder description, adjust as needed
        author = (
            generated_content_detail["Header"]["author"]["name"],
        )  # Access the nested 'name' key within 'author'
        published_at = (
            datetime.now().isoformat(),
        )  # Use the current time for published_at
        slug = generated_content_detail["Metadata"]["slug"]  # Access the 'slug' key)

        content_detail = ContentDetail.objects.create(
            title=title[0],
            description=description[0],
            author=author[0],
            published_at=published_at[0],
            slug=slug[0],
        )
        # Retrieve the ContentDetail instance using the ID
        content_detail_instance = ContentDetail.objects.get(id=content_detail.id)

        # Then, create or update the Content object with the content_detail instance
        contentitem, _ = ContentItem.objects.update_or_create(
            prompt=message_content,  # Assuming you want to use the message_content as the prompt
            assistant=(
                Assistant.objects.get(id=assistant_id) if assistant_id else None
            ),  # Assuming you want to use the message_content as the prompt
            detail=content_detail_instance,  # Use the ContentDetail instance here
        )

        # Update content_detail to link to the newly created or updated content
        content_detail.contentitem.set([contentitem])
        content_detail.save()

        messages.success(request, "Message and content created successfully.")

        return redirect(
            "content_detail", content_detail_id=content_detail.id
        )  # Redirect back to the thread detail page

    def run_assistant_group(self, request, thread_id=None, assistant_group_id=None):
        """
        Execute all assistants in a group sequentially on a thread.

        Runs each assistant in the specified group in their defined order
        (by position) against the thread. This enables complex multi-step
        processing workflows where different assistants handle different
        aspects of content processing.

        Args:
            request (HttpRequest): The HTTP request object
            thread_id (str, optional): ID of thread to process
            assistant_group_id (int, optional): ID of assistant group

        Returns:
            HttpResponse: Redirect to thread detail page

        Raises:
            OpenAIError: If any assistant run fails
            DoesNotExist: If thread or assistant group is not found

        Example:
            A group might include assistants for content generation,
            fact-checking, and style editing that run in sequence.
        """
        # Retrieve the OpenAI client from the session
        client = AppConfigClientMixin.get_client(self)

        # Retrieve the thread instance
        thread_id = request.POST.get("thread_id")
        thread = Thread.objects.get(pk=thread_id)

        # Retrieve the assistant group for the thread
        assistant_group = thread.assistant_group

        # Retrieve the assistant IDs in the assistant group
        assistant_ids = (
            AssistantGroupMembership.objects.filter(assistantgroup=assistant_group)
            .values_list("assistants_id", flat=True)
            .order_by("position")
        )

        # Iterate over the assistant IDs in the group
        for assistant_id in assistant_ids:
            run, run_status, run_response = create_run(client, thread_id, assistant_id)

        messages.success(request, "Assistant group run successfully.")
        return redirect("thread_detail", thread_id=thread.id)

    def run_assistant_message(
        self, request, thread_id=None, message_id=None, assistant_id=None
    ):
        """
        Run a specific assistant on a message within a thread.

        Executes a single assistant against a specific message in a thread,
        allowing for targeted processing and refinement of content.
        This enables precise control over which assistant processes which content.

        Args:
            request (HttpRequest): The HTTP request object
            thread_id (str, optional): ID of thread containing message
            message_id (str, optional): ID of message to process
            assistant_id (str, optional): ID of assistant to run

        Returns:
            HttpResponse: Redirect to thread message detail page

        Raises:
            OpenAIError: If assistant run fails
            DoesNotExist: If thread, message, or assistant is not found

        Example:
            Running a fact-checking assistant on a specific claim
            or a style assistant on a particular paragraph.
        """
        # Retrieve the OpenAI client from the session
        client = AppConfigClientMixin.get_client(self)

        # retrieve the message instance of the selected message
        thread_id = request.POST.get(
            "thread_id"
        )  # Assuming thread_id is passed in the request
        message_id = request.POST.get(
            "message_id"
        )  # Assuming message_id is passed in the request
        assistant_id = request.POST.get(
            "assistant_id"
        )  # Assuming assistant_id is passed in the request

        # Call the create_run function to create a run for the message
        run, run_status, run_response = create_run(client, thread_id, assistant_id)

        messages.success(request, "Message run successfully.")

        # Redirect to the thread_detail.html of the message
        return redirect(
            "thread_message_detail", message_id=message_id, thread_id=thread_id
        )

    def create_post(self, request):
        """
        Create a publishable post from a thread message.

        Converts a thread message into a full Post object with associated
        front matter for publishing workflows. Generates structured metadata
        and creates all necessary records for publication to various platforms.

        Args:
            request (HttpRequest): The HTTP request object

        Returns:
            HttpResponse: Redirect to post detail page

        Raises:
            json.JSONDecodeError: If AI response is not valid JSON
            OpenAIError: If content generation API call fails
            DoesNotExist: If message, thread, or assistant is not found

        Note:
            Creates both Post and PostFrontMatter records with complete
            metadata for publishing workflows including GitHub integration.

        Example:
            The created post can be published to GitHub Pages, Django CMS,
            or other publishing platforms through the post management interface.
        """
        # Retrieve the OpenAI client from the session
        client = AppConfigClientMixin.get_client(self)

        message_id = request.POST.get("message_id")
        message = Message.objects.get(id=message_id)
        message_content = message.contentitem.content_text
        thread_id = request.POST.get("thread_id")
        assistant_id = message.assistant_id
        assistant = (
            Assistant.objects.get(id=assistant_id) if assistant_id else None
        )  # Assuming you want to use the message_content as the prompt

        generated_content_detail = json.loads(
            generate_content_detail(client, message_content)
        )
        # First, create the ContentDetail object
        title = (
            generated_content_detail["Header"]["title"],
        )  # Placeholder title, adjust as needed
        description = (
            generated_content_detail["Metadata"]["description"],
        )  # Placeholder description, adjust as needed
        author = (
            generated_content_detail["Header"]["author"]["name"],
        )  # Access the nested 'name' key within 'author'
        published_at = (
            datetime.now().isoformat(),
        )  # Use the current time for published_at
        slug = generated_content_detail["Metadata"]["slug"]  # Access the 'slug' key)

        content_detail = ContentDetail.objects.create(
            title=title[0],
            description=description[0],
            author=author[0],
            published_at=published_at[0],
            slug=slug[0],
        )
        # Retrieve the ContentDetail instance using the ID
        content_detail_instance = ContentDetail.objects.get(id=content_detail.id)

        # Then, create or update the Content object with the content_detail instance
        contentitem, _ = ContentItem.objects.update_or_create(
            prompt=message_content,  # Assuming you want to use the message_content as the prompt
            assistant=(
                Assistant.objects.get(id=assistant_id) if assistant_id else None
            ),  # Assuming you want to use the message_content as the prompt
            detail=content_detail_instance,  # Use the ContentDetail instance here
        )

        # Update content_detail to link to the newly created or updated content
        content_detail.contentitem.set([contentitem])
        content_detail.save()

        messages.success(request, "Message and content created successfully.")

        # Create the Placeholder instance
        # placeholder = Placeholder.objects.create(slot='post_content')

        # Add content to the placeholder using a plugin
        # from djangocms_text_ckeditor.cms_plugins import TextPlugin
        # from cms.api import add_plugin

        # add_plugin(placeholder, TextPlugin, language='en', body=message_content)

        # Assign the placeholder using set() for the ManyToMany field
        # post.post_content.set([placeholder])

        # Create the Post without assigning ManyToMany fields directly
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
        """
        Save modifications to thread properties.

        Updates thread metadata and properties based on form input.
        Validates the form data and saves changes to the thread record.

        Args:
            request (HttpRequest): The HTTP request object containing form data
            thread_id (str, optional): ID of thread to update

        Returns:
            HttpResponse: Redirect to thread detail page

        Raises:
            ValidationError: If form validation fails
            DoesNotExist: If thread is not found
        """
        thread_id = request.POST.get("thread_id")
        thread_form = ThreadForm(
            request.POST, instance=Thread.objects.get(pk=thread_id)
        )
        if thread_form.is_valid():
            thread = thread_form.save(commit=False)
            thread.save()

        messages.success(request, "Thread saved successfully.")
        return redirect("thread_detail", thread_id=thread_id)


# =============================================================================
# MESSAGE MANAGEMENT VIEWS SECTION
# =============================================================================


class ManageMessageView(LoginRequiredMixin, View):
    """
    Message management view for handling individual messages.

    This view provides functionality for managing messages within the system,
    including viewing message details, deleting messages, and assigning
    assistants to messages for processing.

    Attributes:
        template_name (str): Template for message management interface

    Mixins:
        - LoginRequiredMixin: Ensures user authentication

    Example:
        .. code-block:: python

            # URL configuration
            path('messages/', ManageMessageView.as_view(), name='manage_message')
            path('messages/<str:message_id>/',
                 ManageMessageView.as_view(), name='message_detail')
    """

    template_name = "parodynews/message_detail.html"

    def get(self, request, message_id=None):
        """
        Handle GET requests for message management interface.

        Displays the message management interface with a list of all messages
        and details for a specific message if provided.

        Args:
            request (HttpRequest): The HTTP request object
            message_id (str, optional): ID of specific message to display

        Returns:
            HttpResponse: Rendered message detail template

        Context:
            - message_list: All available messages
            - current_message: Selected message object (if any)
            - assistants: All available assistants for assignment
        """
        message_list = Message.objects.all()
        assistants = Assistant.objects.all()  # Fetch all assistants
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
        """
        Handle POST requests for message management operations.

        Routes different operations based on the _method parameter:
        - create_message: Create new message
        - delete_message: Delete existing message
        - assign_assistant_to_message: Assign assistant to message

        Args:
            request (HttpRequest): The HTTP request object
            message_id (str, optional): ID of message to operate on
            thread_id (str, optional): ID of associated thread
            assigned_assistant_id (str, optional): ID of assistant to assign

        Returns:
            HttpResponse: Redirect based on operation performed
        """
        if request.POST.get("_method") == "create_message":
            return self.create_message(request)

        if request.POST.get("_method") == "delete_message":
            return self.delete_message(request, message_id, thread_id)

        if request.POST.get("_method") == "assign_assistant_to_message":
            return self.assign_assistant_to_message(request, message_id)

    def delete_message(self, request, message_id, thread_id):
        """
        Delete a message from the system.

        Removes the message from the local database. Note that this
        method doesn't clean up OpenAI resources, which should be
        handled separately.

        Args:
            request (HttpRequest): The HTTP request object
            message_id (str): ID of message to delete
            thread_id (str): ID of associated thread

        Returns:
            HttpResponse: Redirect to message management page

        Raises:
            DoesNotExist: If message is not found

        Todo:
            * Add OpenAI cleanup for consistency
            * Implement soft delete option
        """
        # Retrieve the message instance
        message = Message.objects.get(id=message_id)

        # Delete the message
        message.delete()

        # Delete the message from OpenAI
        messages.success(request, "Message deleted successfully.")
        return redirect(
            "manage_message"
        )  # Redirect to the messages list page or wherever appropriate

    def assign_assistant_to_message(self, request, message_id, thread_id=None):
        """
        Assign an assistant to a message for processing.

        Associates a specific assistant with a message, enabling the assistant
        to process or respond to the message content. This is useful for
        organizing workflows and tracking which assistant should handle
        specific types of content.

        Args:
            request (HttpRequest): The HTTP request object
            message_id (str): ID of message to assign assistant to
            thread_id (str, optional): ID of associated thread

        Returns:
            HttpResponse: Redirect to appropriate detail page

        Raises:
            DoesNotExist: If message or assistant is not found

        Note:
            The assignment enables targeted processing and helps organize
            AI workflows by responsibility and specialization.
        """
        assigned_assistant_id = request.POST.get("assigned_assistant_id")
        thread_id = request.POST.get("thread_id")

        message = Message.objects.get(pk=message_id)
        assistant = Assistant.objects.get(pk=assigned_assistant_id)
        message.assistant_id = (
            assistant  # Assuming your Message model has a ForeignKey to Assistant
        )

        message.save()

        messages.success(request, "Message Assigned successfully.")

        if thread_id:
            return redirect(
                "thread_message_detail", thread_id=thread_id, message_id=message_id
            )
        return redirect(
            "message_detail", message_id=message_id
        )  # Redirect to the messages list page or wherever appropriate


# =============================================================================
# ASSISTANT MANAGEMENT VIEWS SECTION
# =============================================================================


class ManageAssistantsView(
    LoginRequiredMixin, ModelFieldsMixin, AppConfigClientMixin, View
):
    """
    Assistant management view for creating and managing AI assistants.

    This view provides a comprehensive interface for managing OpenAI assistants,
    including creating new assistants, editing existing ones, and maintaining
    synchronization between local database records and OpenAI's assistant API.

    Key features:
    - Create and configure new AI assistants
    - Edit existing assistant properties and instructions
    - Synchronize with OpenAI's assistant API
    - Delete assistants from both local and remote storage
    - Form validation and error handling

    Attributes:
        model: Primary model class (Assistant)
        template_name (str): Template for assistant management interface

    Mixins:
        - LoginRequiredMixin: Ensures user authentication
        - ModelFieldsMixin: Provides model field introspection
        - AppConfigClientMixin: Handles OpenAI client configuration

    Example:
        .. code-block:: python

            # URL configuration
            path('assistants/', ManageAssistantsView.as_view(), name='manage_assistants')
            path('assistants/<str:assistant_id>/',
                 ManageAssistantsView.as_view(), name='assistant_detail')
    """

    model = Assistant
    template_name = "parodynews/assistant_detail.html"

    def get(self, request, assistant_id=None):
        """
        Handle GET requests for assistant management interface.

        Displays the assistant management form with existing data if editing,
        or empty forms for creating new assistants. Provides context for
        all existing assistants and model field information.

        Args:
            request (HttpRequest): The HTTP request object
            assistant_id (str, optional): ID of assistant to edit

        Returns:
            HttpResponse: Rendered assistant management template

        Context:
            - assistant_form: Form for assistant configuration
            - assistants_info: All existing assistants
            - is_edit: Boolean indicating edit vs create mode
            - fields: Model field information
            - display_fields: Fields for display purposes
        """
        # Check if assistant_id is provided
        if assistant_id:
            assistant = Assistant.objects.get(pk=assistant_id)
            is_edit = True
        else:
            assistant = None
            is_edit = False

        # Initialize the form
        assistant_form = AssistantForm(instance=assistant)
        # assistant_group_form = AssistantGroupForm()
        # Get the fields and display fields for the model
        assistants_info = Assistant.objects.all()
        fields, display_fields = self.get_model_fields()

        # Render the assistant detail page with the form and assistant details
        return render(
            request,
            self.template_name,
            {
                "assistant_form": assistant_form,
                "assistants_info": assistants_info,
                "assistant_id": assistant_id,
                "is_edit": is_edit,
                "fields": fields,
                "display_fields": display_fields,
            },
        )

    def post(self, request, assistant_id=None):
        """
        Handle POST requests for assistant management operations.

        Routes different operations based on the _method parameter:
        - delete: Delete assistant from both local and OpenAI storage
        - save: Create or update assistant with OpenAI synchronization

        Args:
            request (HttpRequest): The HTTP request object
            assistant_id (str, optional): ID of assistant to operate on

        Returns:
            HttpResponse: Redirect to assistant detail or error template
        """
        if request.POST.get("_method") == "delete":
            return self.delete(request, assistant_id)
        elif request.POST.get("_method") == "save":
            return self.save(request, assistant_id)

        return redirect("assistant_detail", assistant_id=assistant_id)

    def save(self, request, assistant_id=None):
        """
        Save assistant configuration with OpenAI synchronization.

        Validates the assistant form and synchronizes the assistant with
        OpenAI's API. Handles both creating new assistants and updating
        existing ones. Maintains consistency between local database and
        remote OpenAI assistant configuration.

        Args:
            request (HttpRequest): The HTTP request object containing form data
            assistant_id (str, optional): ID of existing assistant to update

        Returns:
            HttpResponse: Redirect to assistant detail on success,
                         or rendered form with errors on failure

        Raises:
            OpenAIError: If assistant creation/update fails on OpenAI side
            ValidationError: If form validation fails

        Note:
            The OpenAI assistant ID is synchronized with the local record
            to ensure consistency between local and remote state.
        """
        # Retrieve the OpenAI client from the session
        client = AppConfigClientMixin.get_client(self)

        assistant_id = request.POST.get("assistant_id")
        save_form = request.POST.get("save_form")

        assistant_form = AssistantForm(request.POST)

        if assistant_id:
            assistant = Assistant.objects.get(pk=assistant_id)
            assistant_form = AssistantForm(request.POST, instance=assistant)

        if save_form == "assistant_form":
            if assistant_form.is_valid():
                assistant = assistant_form.save(commit=False)

                # Create or update the assistant in OpenAI
                assistant_ai = save_assistant(
                    client,
                    assistant.name,
                    assistant.description,
                    assistant.instructions,
                    assistant.model,
                    assistant.json_schema,
                    assistant.id,
                )
                assistant.id = assistant_ai.id
                assistant.save()

                # Save the many-to-many relationships for the assistant groups
                assistant_form.save_m2m()

                messages.success(request, "Assistant created successfully.")
                return redirect("assistant_detail", assistant_id=assistant.id)
            else:
                messages.error(request, "Error creating assistant.")

        else:
            messages.error(request, "Error creating assistant.")
            assistants_info = Assistant.objects.all()
            fields = Assistant._meta.get_fields()
            display_fields = Assistant().get_display_fields()
            return render(
                request,
                self.template_name,
                {
                    "assistant_form": assistant_form,
                    "assistants_info": assistants_info,
                    "fields": fields,
                    "display_fields": display_fields,
                },
            )

    def delete(self, request, assistant_id=None):
        """
        Delete assistant from both local database and OpenAI.

        Removes the assistant from both the local database and OpenAI's
        servers to ensure complete cleanup and prevent orphaned resources.
        Provides appropriate error handling for API failures.

        Args:
            request (HttpRequest): The HTTP request object
            assistant_id (str, optional): ID of assistant to delete

        Returns:
            HttpResponse: Redirect to assistant management page

        Raises:
            OpenAIError: If OpenAI assistant deletion fails
            DoesNotExist: If assistant is not found in database

        Warning:
            This operation permanently deletes the assistant and cannot
            be undone. All assistant configuration will be lost.
        """
        try:
            client = get_openai_client()
            delete_assistant(client, assistant_id)
            messages.success(request, "Assistant deleted successfully.")
        except Exception as e:
            messages.error(request, f"Error deleting assistant: {e}")
        return redirect("manage_assistants")


def get_assistant_details(request, assistant_id):
    """
    AJAX endpoint for retrieving assistant details.

    Provides assistant information in JSON format for dynamic UI updates.
    This is typically used for AJAX requests to populate forms or display
    assistant information without full page reloads.

    Args:
        request (HttpRequest): The HTTP request object
        assistant_id (str): ID of assistant to retrieve

    Returns:
        JsonResponse: Assistant details in JSON format

    Response Format:
        .. code-block:: json

            {
                "assistant_id": "asst_abc123",
                "instructions": "You are a helpful assistant..."
            }

    Raises:
        Assistant.DoesNotExist: If assistant is not found (returns 404)

    Example:
        .. code-block:: javascript

            fetch('/api/assistant/asst_abc123/details/')
                .then(response => response.json())
                .then(data => console.log(data.instructions));
    """
    try:
        assistant = Assistant.objects.get(id=assistant_id)
        instructions = (
            assistant.instructions
        )  # Assuming 'instructions' is a field in the Assistant model

        data = {
            "assistant_id": assistant.id,
            "instructions": instructions,
        }
        return JsonResponse(data)
    except Assistant.DoesNotExist:
        return JsonResponse({"error": "Assistant not found"}, status=404)


# =============================================================================
# ASSISTANT GROUP MANAGEMENT VIEWS SECTION
# =============================================================================


class ManageAssistantGroupsView(LoginRequiredMixin, ModelFieldsMixin, View):
    """
    Assistant group management view for organizing assistants into workflows.

    This view provides functionality for creating and managing groups of assistants
    that can work together in coordinated workflows. Assistant groups enable
    complex processing pipelines where multiple assistants handle different
    aspects of content processing in a defined sequence.

    Key features:
    - Create and configure assistant groups
    - Manage assistant membership and ordering within groups
    - Define execution order for workflow processing
    - Edit existing group configurations
    - Delete groups and clean up memberships

    Attributes:
        model: Primary model class (AssistantGroup)
        template_name (str): Template for assistant group management

    Mixins:
        - LoginRequiredMixin: Ensures user authentication
        - ModelFieldsMixin: Provides model field introspection

    Example:
        .. code-block:: python

            # URL configuration
            path('assistant-groups/', ManageAssistantGroupsView.as_view(),
                 name='manage_assistant_groups')
            path('assistant-groups/<int:assistant_group_id>/',
                 ManageAssistantGroupsView.as_view(), name='assistant_group_detail')
    """

    model = AssistantGroup
    template_name = "parodynews/assistant_group_detail.html"

    def get(self, request, assistant_group_id=None):
        """
        Handle GET requests for assistant group management interface.

        Displays the assistant group management interface with forms for
        group configuration and assistant membership management using formsets.

        Args:
            request (HttpRequest): The HTTP request object
            assistant_group_id (int, optional): ID of group to edit

        Returns:
            HttpResponse: Rendered assistant group management template

        Context:
            - assistant_group_form: Form for group configuration
            - assistant_group_formset: Formset for managing memberships
            - assistant_group: Current group object (if editing)
            - assistant_groups_info: All existing groups
            - fields: Model field information
            - display_fields: Fields for display purposes
        """
        # Check if assistant_group_id is provided
        if assistant_group_id:
            assistant_group = get_object_or_404(AssistantGroup, pk=assistant_group_id)
            assistant_group_form = AssistantGroupForm(instance=assistant_group)
        else:
            assistant_group = None
            assistant_group_form = AssistantGroupForm()

        # initialize the form
        assistant_group_formset = AssistantGroupMembershipFormSet(
            instance=assistant_group
        )

        assistant_groups_info = AssistantGroup.objects.all()
        fields, display_fields = self.get_model_fields()

        context = {
            "assistant_group_form": assistant_group_form,
            "assistant_group_formset": assistant_group_formset,
            "assistant_group": assistant_group,
            "assistant_group_id": assistant_group_id,
            "assistant_groups_info": assistant_groups_info,
            "fields": fields,
            "display_fields": display_fields,
        }

        return render(request, self.template_name, context)

    def post(self, request, assistant_group_id=None):
        """
        Handle POST requests for assistant group management operations.

        Routes different operations based on the _method parameter:
        - delete: Delete assistant group and memberships
        - save: Save group configuration and membership changes

        Args:
            request (HttpRequest): The HTTP request object
            assistant_group_id (int, optional): ID of group to operate on

        Returns:
            HttpResponse: Redirect to appropriate page or rendered template
        """
        if request.POST.get("_method") == "delete":
            return self.delete(request, assistant_group_id)
        if request.POST.get("_method") == "save":
            return self.save(request, assistant_group_id)

        # Return a default response if no condition is met
        return redirect("manage_assistant_groups")

    def save(self, request, assistant_group_id=None):
        """
        Save assistant group configuration and membership.

        Validates and saves both the assistant group form and the associated
        membership formset. Handles creation of new groups and updating
        existing groups with their assistant memberships and ordering.

        Args:
            request (HttpRequest): The HTTP request object containing form data
            assistant_group_id (int, optional): ID of existing group to update

        Returns:
            HttpResponse: Redirect to group detail on success,
                         or rendered form with errors on failure

        Raises:
            ValidationError: If form or formset validation fails

        Note:
            The membership formset manages the many-to-many relationship
            between assistant groups and assistants, including position ordering
            for workflow execution sequence.
        """
        assistant_group_id = request.POST.get("assistant_group_id")

        # initialize the forms
        assistant_group_form = AssistantGroupForm(request.POST)
        assistant_group_formset = AssistantGroupMembershipFormSet(request.POST)

        # Check if assistant_group_id is provided
        if assistant_group_id:
            assistant_group = AssistantGroup.objects.get(pk=assistant_group_id)
            assistant_group_membership = AssistantGroupMembership.objects.filter(
                assistantgroup=assistant_group
            )
            assistant_group_form = AssistantGroupForm(
                request.POST, instance=assistant_group
            )
            assistant_group_formset = AssistantGroupMembershipFormSet(
                request.POST, instance=assistant_group_form.instance
            )

        if assistant_group_form.is_valid():
            assistant_group = (
                assistant_group_form.save()
            )  # Save the assistant group first

            if assistant_group_formset.is_valid():
                assistant_group_formset.instance = (
                    assistant_group  # Set the instance for the formset
                )
                assistant_group_formset.save()  # Save the formset

                messages.success(
                    request, "Assistant group and members saved successfully."
                )
                return redirect(
                    "assistant_group_detail", assistant_group_id=assistant_group.id
                )
            else:
                error_messages = (
                    f"Group Membership form errors: {assistant_group_formset.errors}"
                )
                messages.error(
                    request, f"Error saving content and its details! {error_messages}"
                )
        else:
            error_messages = f"Group form errors: {assistant_group_form.errors}"
            messages.error(
                request, f"Error saving content and its details! {error_messages}"
            )

        assistant_groups_info = AssistantGroup.objects.all()
        fields, display_fields = self.get_model_fields()
        context = {
            "assistant_group_form": assistant_group_form,
            "assistant_group_formset": assistant_group_formset,
            "assistant_group": assistant_group_form.instance,
            "assistant_group_membership": assistant_group_membership,
            "assistant_groups_info": assistant_groups_info,
            "fields": fields,
            "display_fields": display_fields,
        }
        return render(self.request, self.template_name, context)

    def delete(self, request, assistant_group_id=None):
        """
        Delete assistant group and all associated memberships.

        Removes the assistant group and automatically cascades to delete
        all associated membership records. Provides user feedback on
        successful deletion.

        Args:
            request (HttpRequest): The HTTP request object
            assistant_group_id (int, optional): ID of group to delete

        Returns:
            HttpResponse: Redirect to assistant groups management page

        Raises:
            DoesNotExist: If assistant group is not found

        Warning:
            This operation permanently deletes the group and all membership
            relationships. Individual assistants are not deleted.
        """
        assistant_group = AssistantGroup.objects.get(pk=assistant_group_id)
        assistant_group.delete()
        messages.success(request, "Assistant Group deleted successfully.")
        return redirect("manage_assistant_groups")


# =============================================================================
# UTILITY VIEWS SECTION
# =============================================================================


class MyObjectView(View):
    """
    Generic object management view for demonstration purposes.

    This view provides a basic CRUD interface for MyObject model instances.
    It demonstrates standard Django patterns for handling create, read,
    update, and delete operations with proper form handling and validation.

    Attributes:
        template_name (str): Template for object management
        success_url: URL to redirect to after successful operations

    Example:
        .. code-block:: python

            # URL configuration
            path('objects/', MyObjectView.as_view(), name='object-list')
            path('objects/<int:pk>/', MyObjectView.as_view(), name='object-detail')
            path('objects/<int:pk>/delete/', MyObjectView.as_view(),
                 {'action': 'delete'}, name='object-delete')
    """

    template_name = "object_template.html"
    success_url = reverse_lazy("object-list")

    def get(self, request, pk=None, action=None):
        """
        Handle GET requests for object management operations.

        Provides different views based on the action parameter:
        - delete confirmation view
        - edit form for existing objects
        - create form for new objects

        Args:
            request (HttpRequest): The HTTP request object
            pk (int, optional): Primary key of object to operate on
            action (str, optional): Action to perform ('delete', etc.)

        Returns:
            HttpResponse: Rendered template with appropriate context
        """
        if action == "delete" and pk:
            obj = get_object_or_404(MyObject, pk=pk)
            return render(
                request,
                self.template_name,
                {
                    "object": obj,
                    "object_list": MyObject.objects.all(),
                    "action": "delete",
                },
            )

        if pk:
            obj = get_object_or_404(MyObject, pk=pk)
            form = MyObjectForm(instance=obj)
            action = "update"
        else:
            form = MyObjectForm()
            obj = None
            action = "create"

        objects = MyObject.objects.all()
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "object": obj,
                "object_list": objects,
                "action": action,
            },
        )

    def post(self, request, pk=None, action=None):
        """
        Handle POST requests for object management operations.

        Processes form submissions for create, update, and delete operations.
        Validates form data and handles both success and error cases.

        Args:
            request (HttpRequest): The HTTP request object containing form data
            pk (int, optional): Primary key of object to operate on
            action (str, optional): Action to perform ('delete', etc.)

        Returns:
            HttpResponse: Redirect on success or rendered form with errors
        """
        if action == "delete" and pk:
            obj = get_object_or_404(MyObject, pk=pk)
            obj.delete()
            return redirect(self.success_url)

        if pk:
            obj = get_object_or_404(MyObject, pk=pk)
            form = MyObjectForm(request.POST, instance=obj)
            action = "update"
        else:
            form = MyObjectForm(request.POST)
            obj = None
            action = "create"

        if form.is_valid():
            form.save()
            return redirect(self.success_url)

        objects = MyObject.objects.all()
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "object": obj,
                "object_list": objects,
                "action": action,
            },
        )


# =============================================================================
# JSON SCHEMA MANAGEMENT FUNCTIONS
# =============================================================================


def list_schemas(request):
    """
    Display a list of all JSON schemas.

    Renders a page showing all available JSON schemas in the system.
    These schemas are used to structure AI-generated content and
    ensure consistent output formats.

    Args:
        request (HttpRequest): The HTTP request object

    Returns:
        HttpResponse: Rendered schema list template

    Context:
        - schemas: QuerySet of all JSONSchema objects

    Example:
        .. code-block:: python

            # URL configuration
            path('schemas/', list_schemas, name='list_schemas')
    """
    schemas = JSONSchema.objects.all()
    return render(request, "parodynews/schema_detail.html", {"schemas": schemas})


def create_schema(request):
    """
    Create a new JSON schema.

    Handles both GET and POST requests for creating new JSON schemas.
    GET displays the creation form, POST processes the form submission
    and creates the schema record.

    Args:
        request (HttpRequest): The HTTP request object

    Returns:
        HttpResponse: Rendered form template or redirect to schema list

    Raises:
        ValidationError: If schema validation fails

    Example:
        .. code-block:: python

            # URL configuration
            path('schemas/create/', create_schema, name='create_schema')
    """
    if request.method == "POST":
        form = JSONSchemaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Schema created successfully.")
            return redirect("list_schemas")
    else:
        form = JSONSchemaForm()
    return render(request, "parodynews/schema_form.html", {"form": form})


def edit_schema(request, pk):
    """
    Edit an existing JSON schema.

    Handles both GET and POST requests for editing JSON schemas.
    GET displays the edit form with existing data, POST processes
    the form submission and updates the schema.

    Args:
        request (HttpRequest): The HTTP request object
        pk (int): Primary key of schema to edit

    Returns:
        HttpResponse: Rendered form template or redirect to schema list

    Raises:
        Http404: If schema is not found
        ValidationError: If updated schema validation fails

    Example:
        .. code-block:: python

            # URL configuration
            path('schemas/<int:pk>/edit/', edit_schema, name='edit_schema')
    """
    schema = get_object_or_404(JSONSchema, pk=pk)
    if request.method == "POST":
        form = JSONSchemaForm(request.POST, instance=schema)
        if form.is_valid():
            form.save()
            messages.success(request, "Schema updated successfully.")
            return redirect("list_schemas")
    else:
        form = JSONSchemaForm(instance=schema)
    return render(request, "parodynews/schema_form.html", {"form": form})


def export_schema(request, pk):
    """
    Export a JSON schema as a downloadable file.

    Provides the schema data as a JSON download with appropriate
    Content-Disposition headers for file download. Useful for
    sharing schemas or backing up schema definitions.

    Args:
        request (HttpRequest): The HTTP request object
        pk (int): Primary key of schema to export

    Returns:
        JsonResponse: Schema data with download headers

    Raises:
        Http404: If schema is not found

    Example:
        .. code-block:: python

            # URL configuration
            path('schemas/<int:pk>/export/', export_schema, name='export_schema')
    """
    schema = get_object_or_404(JSONSchema, pk=pk)
    response = JsonResponse(schema.schema)
    response["Content-Disposition"] = f'attachment; filename="{schema.name}.json"'
    return response


def delete_schema(request, pk):
    """
    Delete a JSON schema with proper confirmation.

    Handles both GET (confirmation page) and POST (actual deletion)
    requests. Provides safe deletion workflow with user confirmation
    to prevent accidental loss of schema data.

    Args:
        request (HttpRequest): The HTTP request object
        pk (int): Primary key of schema to delete

    Returns:
        HttpResponse:
            - GET: Confirmation page template
            - POST: Redirect to schema list after deletion

    Raises:
        Http404: If schema is not found

    Example:
        .. code-block:: python

            # URL configuration
            path('schemas/<int:pk>/delete/', delete_schema, name='delete_schema')
    """
    schema = get_object_or_404(JSONSchema, pk=pk)
    if request.method == "POST":
        schema.delete()
        messages.success(request, "Schema deleted successfully.")
        return redirect("list_schemas")
    return redirect("list_schemas")


# ============================================================================
# POST MANAGEMENT VIEWS
# ============================================================================
#
# This section handles the management of blog posts and articles within
# the CMS. It includes functionality for creating, editing, publishing,
# and organizing posts with various content types and metadata.
#
# Key Components:
# - ManagePostView: Main post management interface
# - Post creation and editing workflows
# - Publishing and status management
# - Tag and category management
# - Media attachment handling
#
# The post management system integrates with the AI content generation
# features to allow seamless creation of AI-assisted content.

# parodynews/views.py


class ManagePostView(LoginRequiredMixin, ModelFieldsMixin, TemplateView):
    """
    Comprehensive post management interface for content creators.

    Provides a unified interface for managing blog posts and articles,
    including creation, editing, publishing workflows, and organization
    features. Integrates with AI content generation capabilities.

    The view handles multiple content types including:
    - Regular blog posts
    - AI-generated articles
    - Mixed content (human + AI)
    - Media-rich posts with attachments

    Attributes:
        model: Post model class for ORM operations
        template_name (str): Template for rendering the management interface

    Security:
        - Requires user authentication (LoginRequiredMixin)
        - Includes model field utilities (ModelFieldsMixin)

    Example:
        .. code-block:: python

            # URL configuration
            path('manage/posts/', ManagePostView.as_view(), name='manage_posts')
            path('manage/posts/<int:post_id>/', ManagePostView.as_view(), name='edit_post')
    """

    model = Post
    template_name = "parodynews/pages_post_detail.html"

    def get(self, request, post_id=None):
        """
        Handle GET requests for post management interface.

        Displays either the post creation form (when post_id is None) or
        the post editing form (when post_id is provided). Loads all
        necessary forms, post data, and context for the template.

        Args:
            request (HttpRequest): The HTTP request object
            post_id (int, optional): ID of post to edit. None for new post creation.

        Returns:
            HttpResponse: Rendered template with post management interface

        Context Variables:
            post: Post instance being edited (None for new posts)
            form_post: Form for editing post content
            form_post_frontmatter: Form for editing post metadata
            post_list: List of user's posts for navigation
            fields: Model field information
            display_fields: Fields to display in the interface

        Example:
            .. code-block:: python

                # Create new post
                GET /manage/posts/

                # Edit existing post
                GET /manage/posts/123/
        """
        if post_id:
            post = Post.objects.get(pk=post_id)
            post_frontmatter = PostFrontMatter.objects.get(post_id=post.id)
            form_post = PostForm(instance=post)
            form_post_frontmatter = PostFrontMatterForm(instance=post_frontmatter)

        else:
            post = None
            post_frontmatter = None
            form_post = None
            form_post_frontmatter = None

        # Initialize the form
        form_post = PostForm(instance=post)
        form_post_frontmatter = PostFrontMatterForm(instance=post_frontmatter)

        # Get all posts and fields
        post_list = Post.objects.filter(user=request.user)
        fields, display_fields = self.get_model_fields()

        context = {
            "post": post,
            "form_post": form_post,
            "form_post_frontmatter": form_post_frontmatter,
            "post_list": post_list,
            "fields": fields,
            "display_fields": display_fields,
        }

        return render(request, self.template_name, context)

    def post(self, request, post_id=None):
        """
        Handle POST requests for post management operations.

        Routes different post operations based on the '_method' parameter
        in the POST data. Supports delete, save, publish, and CMS publishing
        operations with appropriate method delegation.

        Args:
            request (HttpRequest): The HTTP request object containing POST data
            post_id (int, optional): ID of post being operated on

        Returns:
            HttpResponse: Redirect to appropriate page after operation

        Supported Operations:
            - delete: Remove a post from the system
            - save: Save post changes without publishing
            - publish: Publish post to GitHub Pages via pull request

        Example:
            .. code-block:: html

                <!-- Delete operation -->
                <form method="post">
                    <input type="hidden" name="_method" value="delete">
                    <input type="hidden" name="post_id" value="123">
                    <button type="submit">Delete Post</button>
                </form>
        """
        if request.POST.get("_method") == "delete":
            return self.delete(request)

        if request.POST.get("_method") == "save":
            return self.save(request, post_id)

        if request.POST.get("_method") == "publish":
            return self.publish(request)

        return redirect("manage_post")

    def delete(self, request, post_id=None):
        """
        Delete a post from the system.

        Removes the specified post from the database and provides
        user feedback through Django messages framework.

        Args:
            request (HttpRequest): The HTTP request object
            post_id (int, optional): ID from URL parameter (unused, gets from POST)

        Returns:
            HttpResponseRedirect: Redirect to post management page

        Side Effects:
            - Deletes post from database
            - Displays success message to user
            - Cascades to related objects (frontmatter, etc.)

        Example:
            .. code-block:: python

                # Called via POST with _method=delete
                # Gets post_id from request.POST data
        """
        post_id = request.POST.get("post_id")
        post = Post.objects.get(id=post_id)
        post.delete()

        messages.success(request, "Post deleted successfully.")

        return redirect("manage_post")

    def save(self, request, post_id=None):
        """
        Save post changes without publishing.

        Handles form validation and saving for both new posts and
        updates to existing posts. Processes both the main post
        content and associated frontmatter metadata.

        Args:
            request (HttpRequest): The HTTP request object with form data
            post_id (int, optional): ID from URL parameter (unused, gets from POST)

        Returns:
            HttpResponseRedirect: Redirect to post management page

        Form Processing:
            - Validates PostForm (main content)
            - Validates PostFrontMatterForm (metadata)
            - Creates or updates post and frontmatter objects
            - Associates post with current user

        Side Effects:
            - Creates/updates Post and PostFrontMatter objects
            - Displays success/error messages

        Example:
            .. code-block:: python

                # Called via POST with _method=save
                # Form data includes title, content, metadata fields
        """
        post_id = request.POST.get("post_id")

        # Initialize the forms
        form_post = PostForm(request.POST)
        form_post_frontmatter = PostFrontMatterForm(request.POST)

        # Get the fields and display fields for the model
        post_list = Post.objects.all()
        fields, display_fields = self.get_model_fields()

        # Check if post_id is provided
        if post_id:
            post = Post.objects.get(pk=post_id)
            post_frontmatter = PostFrontMatter.objects.get(post_id=post.id)

            form_post = PostForm(request.POST, instance=post)
            form_post_frontmatter = PostFrontMatterForm(
                request.POST, instance=post_frontmatter
            )
        else:
            post = form_post.save(commit=False)
            post.user = request.user

        # Save the forms if they are valid
        if form_post.is_valid() and form_post_frontmatter.is_valid():
            post_front_matter = form_post_frontmatter.save(commit=False)
            post_front_matter.save()

            post.save()

            messages.success(request, "Post and front matter saved successfully.")
            return redirect("post_detail", post_id=post.id)
        else:
            if not form_post.is_valid():
                messages.error(request, form_post.errors)
            if not form_post_frontmatter.is_valid():
                messages.error(request, form_post_frontmatter.errors)

            context = {
                "post": post,
                "form_post": form_post,
                "form_post_frontmatter": form_post_frontmatter,
                "post_list": post_list,
                "fields": fields,
                "display_fields": display_fields,
            }

            return render(request, self.template_name, context)

    def publish(self, request, post_id=None):
        """
        Publish post to external blogging platform (GitHub Pages/Jekyll).

        Converts the post and its frontmatter into Jekyll-compatible format
        and publishes to a GitHub repository. Handles file naming, frontmatter
        serialization, and version management.

        Args:
            request (HttpRequest): The HTTP request object
            post_id (int, optional): ID from URL parameter (unused, gets from POST)

        Returns:
            HttpResponseRedirect: Redirect based on publish success/failure

        Process:
            1. Retrieves post and frontmatter data
            2. Converts frontmatter to YAML format
            3. Combines frontmatter and content with Jekyll delimiters
            4. Increments version number for tracking
            5. Publishes to GitHub repository via API

        File Format:
            Creates Jekyll post format with YAML frontmatter:
            ```
            ---
            title: Post Title
            description: Post description
            author: Author Name
            published_at: 2023-01-01
            slug: post-slug
            ---

            Post content here...
            ```

        Side Effects:
            - Creates/updates file in GitHub repository
            - Updates post version number
            - Displays success/error messages
        """
        post_id = request.POST.get("post_id")
        post = Post.objects.get(id=post_id)

        # Fetch the related PostFrontMatter
        post_frontmatter = PostFrontMatter.objects.get(post_id=post.id)

        # Create the frontmatter as a dictionary
        frontmatter = {
            "title": post_frontmatter.title,
            "description": post_frontmatter.description,
            "author": post_frontmatter.author,
            "published_at": post_frontmatter.published_at.strftime("%Y-%m-%d"),
            "slug": post_frontmatter.slug,
        }

        # Convert the frontmatter dictionary to a YAML string
        frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False)

        # Combine the frontmatter and the main content
        data = f"---\n{frontmatter_yaml}---\n\n{post.post_content}"

        # Increment version number
        latest_version = post.versions.order_by("-version_number").first()
        version_number = latest_version.version_number + 1 if latest_version else 1

        # Save the content to PostVersion
        post_version = PostVersion.objects.create(
            post=post,
            version_number=version_number,
            content=data,
            frontmatter=frontmatter_yaml,
        )

        # Fetch GitHub config from AppConfig
        app_config = AppConfig.objects.first()
        if not app_config:
            messages.error(request, "GitHub configuration is missing.")
            return redirect("manage_post")

        # Push to GitHub and create a PR
        github_url = push_to_github_and_create_pr(post, post_version, app_config)

        # Redirect to the GitHub PR URL
        return redirect(github_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_id = self.kwargs.get("post_id")
        post = get_object_or_404(Post, id=post_id)
        context["post"] = post
        # Add other context variables as needed
        return context


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
#
# This section contains utility functions that support the main views
# and provide common functionality across the application. These functions
# handle specific tasks like GitHub integration, content processing,
# and system configuration.


def push_to_github_and_create_pr(post, post_version, app_config):
    """
    Push post content to GitHub repository and create pull request.

    Handles the complete workflow for publishing content to a GitHub
    repository, including branch creation, file updates, and pull
    request generation for review and publishing.

    Args:
        post (Post): The post object being published
        post_version (PostVersion): Specific version of the post content
        app_config (AppConfig): Application configuration with GitHub settings

    Returns:
        str: URL of the created pull request

    Process:
        1. Authenticates with GitHub using configured token
        2. Creates new branch for the post publication
        3. Uploads post content as markdown file
        4. Creates pull request for review
        5. Returns PR URL for redirection

    Configuration Requirements:
        - github_pages_token: GitHub personal access token
        - github_pages_repo: Target repository name (owner/repo)
        - github_pages_branch: Base branch for publishing
        - github_pages_post_dir: Directory for post files

    File Naming:
        Creates files with pattern: slug.md (sanitized from frontmatter)

    Branch Naming:
        Creates branches with pattern: publish/{post_id}-v{version_number}

    Side Effects:
        - Creates GitHub branch if it doesn't exist
        - Uploads/updates file in repository
        - Creates pull request for review

    Raises:
        GithubException: If GitHub API operations fail

    Example:
        .. code-block:: python

            pr_url = push_to_github_and_create_pr(post, version, config)
            # Returns: "https://github.com/owner/repo/pull/123"
    """
    token = app_config.github_pages_token
    repo_name = app_config.github_pages_repo
    base_branch = app_config.github_pages_branch
    post_dir = app_config.github_pages_post_dir.rstrip("/")

    g = Github(token)
    repo = g.get_repo(repo_name)
    main_branch = repo.get_branch(base_branch)
    new_branch_name = f"publish/{post.id}-v{post_version.version_number}"

    # Create a new branch from the base branch
    from github.GithubException import GithubException

    try:
        repo.get_branch(new_branch_name)
        # Branch already exists
    except GithubException:
        # Create branch if it doesn't exist
        repo.create_git_ref(
            ref=f"refs/heads/{new_branch_name}", sha=main_branch.commit.sha
        )
    content = post_version.content

    # Fetch the related PostFrontMatter
    post_frontmatter = PostFrontMatter.objects.get(post_id=post.id)

    # Destination path in the repository
    filename = f"{post_frontmatter.slug.lower().replace(' ', '-')}.md"
    date_str = post_frontmatter.published_at.strftime("%Y-%m-%d")
    formatted_filename = f"{date_str}-{filename}"
    repo_path = f"{post_dir}/{formatted_filename}"

    # Check if file already exists in the branch
    try:
        existing_file = repo.get_contents(repo_path, ref=new_branch_name)
        repo.update_file(
            path=repo_path,
            message=f"Update post {post.content_detail.title}",
            content=content,
            sha=existing_file.sha,
            branch=new_branch_name,
        )
    except Exception:
        repo.create_file(
            path=repo_path,
            message=f"Add post {post.content_detail.title}",
            content=content,
            branch=new_branch_name,
        )

    # Create a pull request
    pr = repo.create_pull(
        title=f"Add post {post.content_detail.title}",
        body="Please review the new post.",
        head=new_branch_name,
        base=base_branch,
    )
    return pr.html_url


# ============================================================================
# REST API VIEWSETS
# ============================================================================
#
# This section contains Django REST Framework ViewSets that provide
# programmatic API access to the application's core models. These
# viewsets enable CRUD operations through standard HTTP methods
# and serve as the foundation for API-driven integrations.
#
# Key Components:
# - AssistantViewSet: Manage AI assistants and their configurations
# - AssistantGroupViewSet: Organize assistants into logical groups
# - ContentItemViewSet: Handle individual content items
# - ContentDetailViewSet: Manage detailed content metadata
# - ThreadViewSet: Conversation thread management
# - MessageViewSet: Individual message operations
# - PostViewSet: Blog post and article API access
#
# All viewsets inherit from ModelViewSet providing full CRUD
# functionality with proper serialization and permissions.


class AssistantViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing AI Assistant configurations.

    Provides full CRUD operations for Assistant objects through
    RESTful API endpoints. Includes custom creation logic for
    handling assistant configuration and updates.

    Endpoints:
        - GET /api/assistants/ - List all assistants
        - POST /api/assistants/ - Create new assistant
        - GET /api/assistants/{id}/ - Retrieve specific assistant
        - PUT /api/assistants/{id}/ - Update assistant
        - DELETE /api/assistants/{id}/ - Delete assistant

    Attributes:
        queryset: All Assistant objects
        serializer_class: AssistantSerializer for data validation

    Custom Methods:
        create: Enhanced creation with assistant configuration logic

    Example:
        .. code-block:: python

            # Create assistant via API
            POST /api/assistants/
            {
                "name": "Content Writer",
                "model": "gpt-4",
                "instructions": "Write engaging blog posts"
            }
    """

    queryset = Assistant.objects.all()
    serializer_class = AssistantSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            assistant = create_or_update_assistant(serializer.validated_data)
            output_serializer = self.get_serializer(assistant)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssistantGroupViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing Assistant Groups.

    Provides RESTful API access to AssistantGroup objects for
    organizing assistants into logical collections. Enables
    grouping assistants by purpose, project, or workflow.

    Endpoints:
        - GET /api/assistant-groups/ - List all groups
        - POST /api/assistant-groups/ - Create new group
        - GET /api/assistant-groups/{id}/ - Retrieve specific group
        - PUT /api/assistant-groups/{id}/ - Update group
        - DELETE /api/assistant-groups/{id}/ - Delete group

    Attributes:
        queryset: All AssistantGroup objects
        serializer_class: AssistantGroupSerializer for validation

    Example:
        .. code-block:: python

            # Create assistant group
            POST /api/assistant-groups/
            {
                "name": "Content Team",
                "description": "Writers and editors"
            }
    """

    queryset = AssistantGroup.objects.all()
    serializer_class = AssistantGroupSerializer


class ContentItemViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing Content Items.

    Provides RESTful API access to ContentItem objects representing
    individual pieces of content in the system. Handles basic
    content metadata and relationships.

    Endpoints:
        - GET /api/content-items/ - List all content items
        - POST /api/content-items/ - Create new content item
        - GET /api/content-items/{id}/ - Retrieve specific item
        - PUT /api/content-items/{id}/ - Update content item
        - DELETE /api/content-items/{id}/ - Delete content item

    Attributes:
        queryset: All ContentItem objects
        serializer_class: ContentItemSerializer for validation

    Example:
        .. code-block:: python

            # Create content item
            POST /api/content-items/
            {
                "title": "Article Title",
                "content_type": "article",
                "status": "draft"
            }
    """

    queryset = ContentItem.objects.all()
    serializer_class = ContentItemSerializer


class ContentDetailViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing Content Details.

    Provides RESTful API access to ContentDetail objects containing
    detailed metadata and configuration for content items. Handles
    rich content properties and relationships.

    Endpoints:
        - GET /api/content-details/ - List all content details
        - POST /api/content-details/ - Create new content detail
        - GET /api/content-details/{id}/ - Retrieve specific detail
        - PUT /api/content-details/{id}/ - Update content detail
        - DELETE /api/content-details/{id}/ - Delete content detail

    Attributes:
        queryset: All ContentDetail objects
        serializer_class: ContentDetailSerializer for validation

    Example:
        .. code-block:: python

            # Create content detail
            POST /api/content-details/
            {
                "content_item": 1,
                "description": "Detailed content metadata",
                "tags": ["tech", "ai"]
            }
    """

    queryset = ContentDetail.objects.all()
    serializer_class = ContentDetailSerializer


class ThreadViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing Conversation Threads.

    Provides RESTful API access to Thread objects representing
    conversation threads for AI assistant interactions. Handles
    thread creation, management, and message organization.

    Endpoints:
        - GET /api/threads/ - List all threads
        - POST /api/threads/ - Create new thread
        - GET /api/threads/{id}/ - Retrieve specific thread
        - PUT /api/threads/{id}/ - Update thread
        - DELETE /api/threads/{id}/ - Delete thread

    Attributes:
        queryset: All Thread objects
        serializer_class: ThreadSerializer for validation

    Example:
        .. code-block:: python

            # Create conversation thread
            POST /api/threads/
            {
                "title": "Content Discussion",
                "assistant": 1,
                "user": 1
            }
    """

    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer


class MessageViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing Messages within Threads.

    Provides RESTful API access to Message objects representing
    individual messages in conversation threads. Handles message
    creation, retrieval, and conversation flow management.

    Endpoints:
        - GET /api/messages/ - List all messages
        - POST /api/messages/ - Create new message
        - GET /api/messages/{id}/ - Retrieve specific message
        - PUT /api/messages/{id}/ - Update message
        - DELETE /api/messages/{id}/ - Delete message

    Attributes:
        queryset: All Message objects
        serializer_class: MessageSerializer for validation

    Example:
        .. code-block:: python

            # Create message in thread
            POST /api/messages/
            {
                "thread": 1,
                "content": "Hello, how can I help?",
                "role": "assistant"
            }
    """

    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class PostViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing Blog Posts.

    Provides RESTful API access to Post objects representing
    blog posts and articles in the system. Enables programmatic
    content management and integration with external systems.

    Endpoints:
        - GET /api/posts/ - List all posts
        - POST /api/posts/ - Create new post
        - GET /api/posts/{id}/ - Retrieve specific post
        - PUT /api/posts/{id}/ - Update post
        - DELETE /api/posts/{id}/ - Delete post

    Attributes:
        queryset: All Post objects
        serializer_class: PostSerializer for validation

    Features:
        - Full CRUD operations for posts
        - Automatic user association
        - Content validation and formatting
        - Integration with frontmatter system

    Example:
        .. code-block:: python

            # Create blog post via API
            POST /api/posts/
            {
                "title": "My Blog Post",
                "content": "This is the post content",
                "status": "draft"
            }
    """

    queryset = Post.objects.all()
    serializer_class = PostSerializer


class PostFrontMatterViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing Post FrontMatter metadata.

    Provides RESTful API access to PostFrontMatter objects containing
    metadata and configuration for blog posts. Handles SEO data,
    publication settings, and content organization metadata.

    Endpoints:
        - GET /api/post-frontmatter/ - List all frontmatter objects
        - POST /api/post-frontmatter/ - Create new frontmatter
        - GET /api/post-frontmatter/{id}/ - Retrieve specific frontmatter
        - PUT /api/post-frontmatter/{id}/ - Update frontmatter
        - DELETE /api/post-frontmatter/{id}/ - Delete frontmatter

    Attributes:
        queryset: All PostFrontMatter objects
        serializer_class: PostFrontMatterSerializer for validation
    """

    queryset = PostFrontMatter.objects.all()
    serializer_class = PostFrontMatterSerializer


class JSONSchemaViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing JSON Schema definitions.

    Provides RESTful API access to JSONSchema objects used for
    structuring and validating AI-generated content. Enables
    programmatic schema management and validation rules.

    Endpoints:
        - GET /api/json-schemas/ - List all schemas
        - POST /api/json-schemas/ - Create new schema
        - GET /api/json-schemas/{id}/ - Retrieve specific schema
        - PUT /api/json-schemas/{id}/ - Update schema
        - DELETE /api/json-schemas/{id}/ - Delete schema

    Attributes:
        queryset: All JSONSchema objects
        serializer_class: JSONSchemaSerializer for validation
    """

    queryset = JSONSchema.objects.all()
    serializer_class = JSONSchemaSerializer


class PoweredByViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing PoweredBy attribution records.

    Provides RESTful API access to PoweredBy objects for tracking
    and managing attribution information for AI-generated content
    and external services used in the platform.

    Endpoints:
        - GET /api/powered-by/ - List all attribution records
        - POST /api/powered-by/ - Create new attribution
        - GET /api/powered-by/{id}/ - Retrieve specific attribution
        - PUT /api/powered-by/{id}/ - Update attribution
        - DELETE /api/powered-by/{id}/ - Delete attribution

    Attributes:
        queryset: All PoweredBy objects
        serializer_class: PoweredBySerializer for validation
    """

    queryset = PoweredBy.objects.all()
    serializer_class = PoweredBySerializer


class MyObjectViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing MyObject instances.

    Provides RESTful API access to MyObject instances used for
    custom object management and data storage within the platform.
    Handles generic object operations and data relationships.

    Endpoints:
        - GET /api/my-objects/ - List all objects
        - POST /api/my-objects/ - Create new object
        - GET /api/my-objects/{id}/ - Retrieve specific object
        - PUT /api/my-objects/{id}/ - Update object
        - DELETE /api/my-objects/{id}/ - Delete object

    Attributes:
        queryset: All MyObject instances
        serializer_class: MyObjectSerializer for validation
    """

    queryset = MyObject.objects.all()
    serializer_class = MyObjectSerializer


class GeneralizedCodesViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing Generalized Code definitions.

    Provides RESTful API access to GeneralizedCodes objects for
    managing code snippets, templates, and reusable code components
    within the content management system.

    Endpoints:
        - GET /api/generalized-codes/ - List all code definitions
        - POST /api/generalized-codes/ - Create new code definition
        - GET /api/generalized-codes/{id}/ - Retrieve specific code
        - PUT /api/generalized-codes/{id}/ - Update code definition
        - DELETE /api/generalized-codes/{id}/ - Delete code definition

    Attributes:
        queryset: All GeneralizedCodes objects
        serializer_class: GeneralizedCodesSerializer for validation
    """

    queryset = GeneralizedCodes.objects.all()
    serializer_class = GeneralizedCodesSerializer


def post_detail(request, post_id):
    """
    Display detailed view of a specific blog post.

    Renders a detailed view of a blog post with all its content,
    metadata, and related information. Serves as the main post
    viewing interface for end users.

    Args:
        request (HttpRequest): The HTTP request object
        post_id (int): Primary key of the post to display

    Returns:
        HttpResponse: Rendered post detail template

    Raises:
        Http404: If post with given ID is not found

    Context Variables:
        post: The Post object being displayed

    Template:
        parodynews/pages_post_detail.html

    Example:
        .. code-block:: python

            # URL configuration
            path('posts/<int:post_id>/', post_detail, name='post_detail')
    """
    post = get_object_or_404(Post, id=post_id)
    context = {
        "post": post,
    }
    return render(request, "parodynews/pages_post_detail.html", context)


def get_app_instance(request):
    """
    Retrieve Django CMS app instance configuration for current request.

    Determines the current CMS application configuration based on the
    request context and page application URLs. Used for multi-app
    configurations and namespace resolution.

    Args:
        request (HttpRequest): The HTTP request object with CMS context

    Returns:
        tuple: (namespace, config) where:
            - namespace (str): Application namespace string
            - config: Application configuration object or None

    Process:
        1. Checks if request has current_page with application_urls
        2. Retrieves app hook from apphook_pool
        3. Attempts to get app configuration
        4. Returns namespace and config tuple

    CMS Integration:
        - Works with django-cms apphook system
        - Handles multi-app configurations
        - Provides namespace isolation

    Example:
        .. code-block:: python

            namespace, config = get_app_instance(request)
            if config:
                # Use app-specific configuration
                pass
    """
    # CMS functionality temporarily disabled - return empty defaults
    # Uncomment the code below when CMS is re-enabled
    return "", None
    
    # Original CMS code (commented out):
    # namespace, config = "", None
    # if getattr(request, "current_page", None) and request.current_page.application_urls:
    #     app = apphook_pool.get_apphook(request.current_page.application_urls)
    #     if app and app.app_config:
    #         try:
    #             config = None
    #             with override(get_language_from_request(request)):
    #                 if hasattr(request, "toolbar") and hasattr(
    #                     request.toolbar, "request_path"
    #                 ):
    #                     path = (
    #                         request.toolbar.request_path
    #                     )  # If v4 endpoint take request_path from toolbar
    #                 else:
    #                     path = request.path_info
    #                 namespace = resolve(path).namespace
    #                 config = app.get_config(namespace)
    #         except Resolver404:
    #             pass
    # return namespace, config


class AppHookConfigMixin:
    """
    Mixin for Django CMS app hook configuration handling.

    Provides common functionality for views that need to work with
    Django CMS app hook configurations. Handles namespace resolution,
    configuration retrieval, and queryset filtering based on app context.

    Attributes:
        namespace (str): Current app namespace from request
        config: App configuration object for current namespace

    Methods:
        dispatch: Intercepts request to set up app context
        get_queryset: Filters queryset based on app configuration

    CMS Integration:
        - Works with django-cms apphook system
        - Provides app-specific context and filtering
        - Handles multi-app namespace isolation

    Usage:
        Inherit from this mixin in views that need app-specific behavior:

        .. code-block:: python

            class MyView(AppHookConfigMixin, ListView):
                model = MyModel
                # Automatically filters by app_config__namespace
    """

    def dispatch(self, request, *args, **kwargs):
        # get namespace and config
        self.namespace, self.config = get_app_instance(request)
        request.current_app = self.namespace
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(app_config__namespace=self.namespace)


# CMS-specific view commented out since Entry model is disabled
# Uncomment when CMS is re-enabled
# class PostPageView(AppHookConfigMixin, ListView):
#     """
#     List view for displaying posts in Django CMS context.
#
#     Displays a paginated list of Entry objects (posts) within
#     a Django CMS application hook context. Provides app-specific
#     filtering and pagination configuration.
#
#     Attributes:
#         model: models.Entry - The model class for posts
#         template_name (str): Template for rendering the post list
#
#     Features:
#         - App-specific post filtering via AppHookConfigMixin
#         - Configurable pagination based on app settings
#         - CMS integration with namespace isolation
#
#     Pagination:
#         Uses app configuration for pagination settings, falls back
#         to default of 10 items per page if not configured.
#
#     Template Context:
#         Provides standard ListView context with Entry objects
#         filtered by current app configuration.
#
#     Example:
#         .. code-block:: python
#
#             # URL configuration in CMS app hook
#             urlpatterns = [
#                 path('', PostPageView.as_view(), name='post_list'),
#             ]
#     """
#
#     model = models.Entry
#     template_name = "index.html"
#
#     def get_paginate_by(self, queryset):
#         try:
#             return self.config.paginate_by
#         except AttributeError:
#             return 10


def send_welcome_email(user_email):
    """
    Send welcome email to new user registrations.

    Sends a standardized welcome email to users who have just
    registered for the Barody Broject platform. Uses Django's
    email framework for reliable delivery.

    Args:
        user_email (str): Email address of the new user

    Returns:
        None

    Email Details:
        - Subject: "Welcome to Barody Broject"
        - From: Configured DEFAULT_FROM_EMAIL setting
        - Content: Simple welcome message

    Configuration Requirements:
        - DEFAULT_FROM_EMAIL: Set in Django settings
        - Email backend configured (SMTP, etc.)

    Side Effects:
        - Sends email via configured email backend
        - May raise SMTPException if email delivery fails

    Example:
        .. code-block:: python

            # Call after user registration
            send_welcome_email(user.email)
    """
    subject = "Welcome to Barody Broject"
    message = "Thank you for signing up for Barody Broject."
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]
    send_mail(subject, message, email_from, recipient_list)
