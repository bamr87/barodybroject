"""
File: assistants.py
Description: Views for creating and managing OpenAI assistants
Author: Barodybroject Team <team@example.com>
Created: 2025-12-19
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- django: >=5.1
- openai: >=1.57.0

Usage: Included via parodynews URL routing.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from ..forms import AssistantForm, AssistantGroupForm, AssistantGroupMembershipFormSet
from ..mixins import AppConfigClientMixin, ModelFieldsMixin
from ..models import Assistant, AssistantGroup, AssistantGroupMembership
from ..utils import delete_assistant, get_openai_client, save_assistant


class ManageAssistantsView(
    LoginRequiredMixin, ModelFieldsMixin, AppConfigClientMixin, View
):
    """
    Assistant management view for creating and managing AI assistants.

    Provides interface for managing OpenAI assistants, including creating,
    editing, and synchronizing with OpenAI's assistant API.
    """

    model = Assistant
    template_name = "parodynews/assistant_detail.html"

    def get(self, request, assistant_id=None):
        """Handle GET requests for assistant management interface."""
        if assistant_id:
            assistant = Assistant.objects.get(pk=assistant_id)
            is_edit = True
        else:
            assistant = None
            is_edit = False

        assistant_form = AssistantForm(instance=assistant)
        assistants_info = Assistant.objects.all()
        fields, display_fields = self.get_model_fields()

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
        """Handle POST requests for assistant management operations."""
        if request.POST.get("_method") == "delete":
            return self.delete(request, assistant_id)
        elif request.POST.get("_method") == "save":
            return self.save(request, assistant_id)

        return redirect("assistant_detail", assistant_id=assistant_id)

    def save(self, request, assistant_id=None):
        """Save assistant configuration with OpenAI synchronization."""
        assistant_id = request.POST.get("assistant_id")
        save_form = request.POST.get("save_form")

        assistant_form = AssistantForm(request.POST)

        if assistant_id:
            assistant = Assistant.objects.get(pk=assistant_id)
            assistant_form = AssistantForm(request.POST, instance=assistant)

        if save_form == "assistant_form":
            if assistant_form.is_valid():
                assistant = assistant_form.save(commit=False)

                try:
                    client = AppConfigClientMixin.get_client(self)
                    assistant_ai = save_assistant(
                        client,
                        assistant.name,
                        assistant.description,
                        assistant.instructions,
                        assistant.model,
                        assistant.json_schema,
                        assistant.id,
                    )
                except Exception as e:
                    messages.error(request, f"Error creating assistant: {e}")
                    return self.render_form(request, assistant_form, assistant_id)

                assistant.id = assistant_ai.id
                assistant.save()

                assistant_form.save_m2m()

                messages.success(request, "Assistant created successfully.")
                return redirect("assistant_detail", assistant_id=assistant.id)
            else:
                messages.error(request, "Error creating assistant.")
                return self.render_form(request, assistant_form, assistant_id)

        else:
            messages.error(request, "Error creating assistant.")
            return self.render_form(request, assistant_form, assistant_id)

        return self.render_form(request, assistant_form, assistant_id)

    def render_form(self, request, assistant_form, assistant_id=None):
        """Render assistant form state with the list view context."""
        assistants_info = Assistant.objects.all()
        fields, display_fields = self.get_model_fields()
        return render(
            request,
            self.template_name,
            {
                "assistant_form": assistant_form,
                "assistants_info": assistants_info,
                "assistant_id": assistant_id,
                "is_edit": bool(assistant_id),
                "fields": fields,
                "display_fields": display_fields,
            },
        )

    def delete(self, request, assistant_id=None):
        """Delete assistant from both local database and OpenAI."""
        try:
            client = get_openai_client()
            delete_assistant(client, assistant_id)
            messages.success(request, "Assistant deleted successfully.")
        except Exception as e:
            messages.error(request, f"Error deleting assistant: {e}")
        return redirect("manage_assistants")


def get_assistant_details(request, assistant_id):
    """AJAX endpoint for retrieving assistant details."""
    try:
        assistant = Assistant.objects.get(id=assistant_id)
        instructions = assistant.instructions

        data = {
            "assistant_id": assistant.id,
            "instructions": instructions,
        }
        return JsonResponse(data)
    except Assistant.DoesNotExist:
        return JsonResponse({"error": "Assistant not found"}, status=404)


class ManageAssistantGroupsView(LoginRequiredMixin, ModelFieldsMixin, View):
    """
    Assistant group management view for organizing assistants into workflows.

    Provides functionality for creating and managing groups of assistants
    that work together in coordinated workflows.
    """

    model = AssistantGroup
    template_name = "parodynews/assistant_group_detail.html"

    def get(self, request, assistant_group_id=None):
        """Handle GET requests for assistant group management interface."""
        if assistant_group_id:
            assistant_group = get_object_or_404(AssistantGroup, pk=assistant_group_id)
            assistant_group_form = AssistantGroupForm(instance=assistant_group)
        else:
            assistant_group = None
            assistant_group_form = AssistantGroupForm()

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
        """Handle POST requests for assistant group management operations."""
        if request.POST.get("_method") == "delete":
            return self.delete(request, assistant_group_id)
        if request.POST.get("_method") == "save":
            return self.save(request, assistant_group_id)

        return redirect("manage_assistant_groups")

    def save(self, request, assistant_group_id=None):
        """Save assistant group configuration and membership."""
        assistant_group_id = request.POST.get("assistant_group_id")

        assistant_group_form = AssistantGroupForm(request.POST)
        assistant_group_formset = AssistantGroupMembershipFormSet(request.POST)

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
            assistant_group = assistant_group_form.save()

            if assistant_group_formset.is_valid():
                assistant_group_formset.instance = assistant_group
                assistant_group_formset.save()

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
        """Delete assistant group and all associated memberships."""
        assistant_group = AssistantGroup.objects.get(pk=assistant_group_id)
        assistant_group.delete()
        messages.success(request, "Assistant Group deleted successfully.")
        return redirect("manage_assistant_groups")

