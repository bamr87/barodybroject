import json
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView
from django.views import View
from datetime import datetime

from django.urls import reverse_lazy
from .models import MyObject
from .forms import MyObjectForm
from .forms import PostForm, PostFrontMatterForm
import yaml

from django.views.generic import ListView
from django.urls import Resolver404, resolve
from django.utils.translation import override

from cms.apphook_pool import apphook_pool
from cms.utils import get_language_from_request

from . import models

from django.contrib.auth import authenticate, login
from .utils import get_openai_client, delete_assistant

from django.shortcuts import render, get_object_or_404


from .models import JSONSchema
from .forms import JSONSchemaForm

from rest_framework import viewsets, status
from rest_framework.response import Response

from .forms import (
    AssistantForm,
    ContentItemForm,
    ContentDetailForm,
    ThreadForm,
    AssistantGroupForm,
    AssistantGroupMembershipForm,
    AssistantGroupMembershipFormSet,
)
from .models import (
    Assistant,
    AssistantGroup,
    AssistantGroupMembership,
    ContentItem,
    ContentDetail,
    Message,
    Thread,
    PoweredBy,
    Post,
    MyObject,
    GeneralizedCodes,
    PostFrontMatter,
    AppConfig,
    PostVersion,
)
from .utils import (
    save_assistant,
    openai_delete_assistant,
    create_run,
    generate_content,
    openai_create_message,
    openai_delete_message,
    generate_content_detail,
    create_or_update_assistant,
)
from .serializers import (
    AssistantSerializer,
    AssistantGroupSerializer,
    ContentItemSerializer,
    ContentDetailSerializer,
    ThreadSerializer,
    MessageSerializer,
    PostSerializer,
    PostFrontMatterSerializer,
    JSONSchemaSerializer,
    PoweredBySerializer,
    MyObjectSerializer,
    GeneralizedCodesSerializer,
)
from .mixins import ModelFieldsMixin, AppConfigClientMixin

from openai import OpenAI
from github import Github
from django.conf import settings

from django.core.mail import send_mail
print("Loading views.py")

# TODO: Post Frontmatter needs to be dynamic and populated based on the assistant schema, otherwise the front matter is defaulted
# TODO: Link post to the URL and filename, and github location
class FooterView(TemplateView):
    template_name = "footer.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["powered_by"] = PoweredBy.objects.all()
        return context


# Custom LoginView to render a custom login page
class UserLoginView(LoginView):
    template_name = "login.html"


# View to render the index page
def index(request):
    # This view will render the root index page
    return render(request, "parodynews/index.html", {})


# View to manage content creation and deletion


class ManageContentView(
    LoginRequiredMixin, ModelFieldsMixin, AppConfigClientMixin, View
):
    model = ContentDetail
    template_name = "parodynews/content_detail.html"

    def get(self, request, content_detail_id=None, content_item_id=None):
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
        content_detail_info = ContentDetail.objects.all()
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

        # Save the forms if they are valid
        if content_form.is_valid() and content_detail_form.is_valid():
            content_detail = content_detail_form.save(commit=False)
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
        content_detail_id = request.POST.get("content_detail_id")
        content_detail = ContentDetail.objects.get(pk=content_detail_id)
        contentitem = ContentItem.objects.filter(detail_id=content_detail_id)
        content_detail.delete()
        contentitem.delete()
        messages.success(request, "Content and its details deleted successfully!")
        return redirect("manage_content")


class ProcessContentView(LoginRequiredMixin, ModelFieldsMixin, View):
    model = Thread
    template_name = "parodynews/content_processing.html"
    # View to list all threads and messages

    def get(self, request, message_id=None, thread_id=None, assistant_group_id=None):
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

        threads = Thread.objects.all()  # Retrieve all threads
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

    # View to delete a thread

    def delete_thread(self, request, thread_id=None):
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
        # Retrieve the OpenAI client from the session
        client = AppConfigClientMixin.get_client(self)

        message_id = request.POST.get("message_id")
        message = Message.objects.get(id=message_id)
        message_content = message.contentitem.content_text
        thread_id = request.POST.get("thread_id")
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
            assistant=Assistant.objects.get(id=assistant_id)
            if assistant_id
            else None,  # Assuming you want to use the message_content as the prompt
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
        # Retrieve the OpenAI client from the session
        client = AppConfigClientMixin.get_client(self)

        # Retrieve the thread instance
        thread_id = request.POST.get("thread_id")
        thread = Thread.objects.get(pk=thread_id)

        # Retrieve the assistant group for the thread
        assistant_group_id = request.POST.get("assistant_group_id")
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

    # View to run individual messages

    def run_assistant_message(
        self, request, thread_id=None, message_id=None, assistant_id=None
    ):
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

    # View to create a post

    def create_post(self, request):
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
            assistant=Assistant.objects.get(id=assistant_id)
            if assistant_id
            else None,  # Assuming you want to use the message_content as the prompt
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
    template_name = "parodynews/message_detail.html"

    def get(self, request, message_id=None):
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
        if request.POST.get("_method") == "create_message":
            return self.create_message(request)

        if request.POST.get("_method") == "delete_message":
            return self.delete_message(request, message_id, thread_id)

        if request.POST.get("_method") == "assign_assistant_to_message":
            return self.assign_assistant_to_message(request, message_id)

    def delete_message(self, request, message_id, thread_id):
        # Retrieve the message instance
        message = Message.objects.get(id=message_id)

        # Delete the message
        message.delete()

        # Delete the message from OpenAI
        messages.success(request, "Message deleted successfully.")
        return redirect(
            "manage_message"
        )  # Redirect to the messages list page or wherever appropriate

    # View to assign an assistant to a message

    def assign_assistant_to_message(self, request, message_id, thread_id=None):
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


from django.forms import inlineformset_factory


class ManageAssistantsView(
    LoginRequiredMixin, ModelFieldsMixin, AppConfigClientMixin, View
):
    model = Assistant
    template_name = "parodynews/assistant_detail.html"

    def get(self, request, assistant_id=None):
        # Check if assistant_id is provided
        if assistant_id:
            assistant = Assistant.objects.get(pk=assistant_id)
            is_edit = True
        else:
            assistant = None
            is_edit = False

        # Initialize the form
        assistant_form = AssistantForm(instance=assistant)
        assistant_group_form = AssistantGroupForm()
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
        if request.POST.get("_method") == "delete":
            return self.delete(request, assistant_id)
        elif request.POST.get("_method") == "save":
            return self.save(request, assistant_id)

        return redirect("assistant_detail", assistant_id=assistant_id)

    def save(self, request, assistant_id=None):
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
        try:
            client = get_openai_client()
            delete_assistant(client, assistant_id)
            messages.success(request, "Assistant deleted successfully.")
        except Exception as e:
            messages.error(request, f"Error deleting assistant: {e}")
        return redirect("manage_assistants")


def get_assistant_details(request, assistant_id):
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


class ManageAssistantGroupsView(LoginRequiredMixin, ModelFieldsMixin, View):
    model = AssistantGroup
    template_name = "parodynews/assistant_group_detail.html"

    def get(self, request, assistant_group_id=None):
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
        if request.POST.get("_method") == "delete":
            return self.delete(request, assistant_group_id)
        if request.POST.get("_method") == "save":
            return self.save(request, assistant_group_id)

        # Return a default response if no condition is met
        return redirect("manage_assistant_groups")

    def save(self, request, assistant_group_id=None):
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
        assistant_group = AssistantGroup.objects.get(pk=assistant_group_id)
        assistant_group.delete()
        messages.success(request, "Assistant Group deleted successfully.")
        return redirect("manage_assistant_groups")


class MyObjectView(View):
    template_name = "object_template.html"
    success_url = reverse_lazy("object-list")

    def get(self, request, pk=None, action=None):
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


def list_schemas(request):
    schemas = JSONSchema.objects.all()
    return render(request, "parodynews/schema_detail.html", {"schemas": schemas})


def create_schema(request):
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
    schema = get_object_or_404(JSONSchema, pk=pk)
    response = JsonResponse(schema.schema)
    response["Content-Disposition"] = f'attachment; filename="{schema.name}.json"'
    return response


def delete_schema(request, pk):
    schema = get_object_or_404(JSONSchema, pk=pk)
    if request.method == "POST":
        schema.delete()
        messages.success(request, "Schema deleted successfully.")
        return redirect("list_schemas")
    return redirect("list_schemas")


# parodynews/views.py


class ManagePostView(LoginRequiredMixin, ModelFieldsMixin, TemplateView):
    model = Post
    template_name = "parodynews/pages_post_detail.html"

    def get(self, request, post_id=None):
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
        post_list = Post.objects.all()
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
        if request.POST.get("_method") == "delete":
            return self.delete(request)

        if request.POST.get("_method") == "save":
            return self.save(request, post_id)

        if request.POST.get("_method") == "publish":
            return self.publish(request)

        return redirect("manage_post")

    def delete(self, request, post_id=None):
        post_id = request.POST.get("post_id")
        post = Post.objects.get(id=post_id)
        post.delete()

        messages.success(request, "Post deleted successfully.")

        return redirect("manage_post")

    def save(self, request, post_id=None):
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

        # Save the forms if they are valid
        if form_post.is_valid() and form_post_frontmatter.is_valid():
            post_front_matter = form_post_frontmatter.save(commit=False)
            post_front_matter.save()

            post = form_post.save(commit=False)
            post.frontmatter = post_front_matter
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
        post_id = request.POST.get('post_id')
        post = Post.objects.get(id=post_id)

        # Fetch the related PostFrontMatter
        post_frontmatter = PostFrontMatter.objects.get(post_id=post.id)

        # Create the frontmatter as a dictionary
        frontmatter = {
            'title': post_frontmatter.title,
            'description': post_frontmatter.description,
            'author': post_frontmatter.author,
            'published_at': post_frontmatter.published_at.strftime("%Y-%m-%d"),
            'slug': post_frontmatter.slug,
        }

        # Convert the frontmatter dictionary to a YAML string
        frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False)

        # Combine the frontmatter and the main content
        data = f"---\n{frontmatter_yaml}---\n\n{post.post_content}"

        # Increment version number
        latest_version = post.versions.order_by('-version_number').first()
        version_number = latest_version.version_number + 1 if latest_version else 1

        # Save the content to PostVersion
        post_version = PostVersion.objects.create(
            post=post,
            version_number=version_number,
            content=data,
            frontmatter=frontmatter_yaml
        )

        # Fetch GitHub config from AppConfig
        app_config = AppConfig.objects.first()
        if not app_config:
            messages.error(request, "GitHub configuration is missing.")
            return redirect('manage_post')

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


def push_to_github_and_create_pr(post, post_version, app_config):

    token = app_config.github_pages_token
    repo_name = app_config.github_pages_repo
    base_branch = app_config.github_pages_branch
    post_dir = app_config.github_pages_post_dir.rstrip('/')

    g = Github(token)
    repo = g.get_repo(repo_name)
    main_branch = repo.get_branch(base_branch)
    new_branch_name = f'publish/{post.id}-v{post_version.version_number}'

    # Create a new branch from the base branch
    from github.GithubException import GithubException
    
    try:
        repo.get_branch(new_branch_name)
        # Branch already exists
    except GithubException: 
        # Create branch if it doesn't exist
        repo.create_git_ref(ref=f"refs/heads/{new_branch_name}", sha=main_branch.commit.sha)
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
            message=f'Update post {post.content_detail.title}',
            content=content,
            sha=existing_file.sha,
            branch=new_branch_name
        )
    except Exception:
        repo.create_file(
            path=repo_path,
            message=f'Add post {post.content_detail.title}',
            content=content,
            branch=new_branch_name
        )

    # Create a pull request
    pr = repo.create_pull(
        title=f'Add post {post.content_detail.title}',
        body='Please review the new post.',
        head=new_branch_name,
        base=base_branch
    )
    return pr.html_url


class AssistantViewSet(viewsets.ModelViewSet):
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
    queryset = AssistantGroup.objects.all()
    serializer_class = AssistantGroupSerializer


class ContentItemViewSet(viewsets.ModelViewSet):
    queryset = ContentItem.objects.all()
    serializer_class = ContentItemSerializer


class ContentDetailViewSet(viewsets.ModelViewSet):
    queryset = ContentDetail.objects.all()
    serializer_class = ContentDetailSerializer


class ThreadViewSet(viewsets.ModelViewSet):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class PostFrontMatterViewSet(viewsets.ModelViewSet):
    queryset = PostFrontMatter.objects.all()
    serializer_class = PostFrontMatterSerializer


class JSONSchemaViewSet(viewsets.ModelViewSet):
    queryset = JSONSchema.objects.all()
    serializer_class = JSONSchemaSerializer


class PoweredByViewSet(viewsets.ModelViewSet):
    queryset = PoweredBy.objects.all()
    serializer_class = PoweredBySerializer


class MyObjectViewSet(viewsets.ModelViewSet):
    queryset = MyObject.objects.all()
    serializer_class = MyObjectSerializer


class GeneralizedCodesViewSet(viewsets.ModelViewSet):
    queryset = GeneralizedCodes.objects.all()
    serializer_class = GeneralizedCodesSerializer


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    context = {
        "post": post,
    }
    return render(request, "parodynews/pages_post_detail.html", context)


def get_app_instance(request):
    namespace, config = "", None
    if getattr(request, "current_page", None) and request.current_page.application_urls:
        app = apphook_pool.get_apphook(request.current_page.application_urls)
        if app and app.app_config:
            try:
                config = None
                with override(get_language_from_request(request)):
                    if hasattr(request, "toolbar") and hasattr(
                        request.toolbar, "request_path"
                    ):
                        path = (
                            request.toolbar.request_path
                        )  # If v4 endpoint take request_path from toolbar
                    else:
                        path = request.path_info
                    namespace = resolve(path).namespace
                    config = app.get_config(namespace)
            except Resolver404:
                pass
    return namespace, config


class AppHookConfigMixin:
    def dispatch(self, request, *args, **kwargs):
        # get namespace and config
        self.namespace, self.config = get_app_instance(request)
        request.current_app = self.namespace
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(app_config__namespace=self.namespace)


class PostPageView(AppHookConfigMixin, ListView):
    model = models.Entry
    template_name = "index.html"

    def get_paginate_by(self, queryset):
        try:
            return self.config.paginate_by
        except AttributeError:
            return 10


def send_welcome_email(user_email):
    subject = 'Welcome to Barody Broject'
    message = 'Thank you for signing up for Barody Broject.'
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]
    send_mail(subject, message, email_from, recipient_list)
