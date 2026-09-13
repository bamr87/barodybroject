"""
Forms for parodynews application.

Organized by model category matching the new models package structure.
"""

import re

from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django_json_widget.widgets import JSONEditorWidget

from .mixins import DefaultFormFieldsMixin
from .models import (  # AI models; Content models; Publishing models; Conversation models
    Assistant,
    AssistantGroup,
    AssistantGroupMembership,
    ContentDetail,
    ContentItem,
    JSONSchema,
    Post,
    PostFrontMatter,
    Thread,
)

# TODO: Add additional fields to Post frontmatter to handle dynamic fields (i.e., based on JSON schema)


# =============================================================================
# CONTENT FORMS
# =============================================================================


class ContentDetailForm(DefaultFormFieldsMixin, forms.ModelForm):
    class Meta:
        model = ContentDetail
        fields = ["id", "title", "description", "author", "published_at", "slug"]


# Content item form that contains the main content details and metadata. Converted to post form for the blog


class ContentItemForm(DefaultFormFieldsMixin, forms.ModelForm):
    # Define the form fields for the assistant to be displayed in the form
    # `ContentItem.assistant` is `null=True, blank=True`, so the form field is
    # optional too -- an item with no assistant must stay saveable as one.
    assistant = forms.ModelChoiceField(
        queryset=Assistant.objects.all(),
        label="Assistant Name",
        required=False,
    )

    # Define the form field for the instructions to be displayed in the form
    instructions = forms.CharField(
        widget=forms.Textarea(attrs={"readonly": "readonly"}),
        required=False,
    )

    # Meta class to define the model and fields to be displayed in the form
    class Meta:
        model = ContentItem
        fields = ["assistant", "instructions", "prompt", "content_text"]
        labels = {
            "prompt": "Prompt",
        }
        field_order = ["prompt"]  # Specify the order of fields

    # Set the assistant field choices to the names of all Assistant objects. Needed for AJAX request
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assistant"].widget.choices = [
            # The blank choice must survive this override: without it the
            # browser silently selects the first assistant for an item that
            # has none, and saving the form then persists that choice.
            ("", self.fields["assistant"].empty_label),
            *((assistant.id, assistant.name) for assistant in Assistant.objects.all()),
        ]

        self.fields["content_text"].required = False  # Make content field optional

        # Seed a default assistant only when the form is genuinely new.
        #
        # `self.initial` comes from `model_to_dict(instance)`, which reports
        # `assistant: None` for BOTH a brand-new form AND a saved ContentItem
        # whose nullable `assistant` FK is NULL -- so `self.initial` cannot
        # tell them apart. Whether the instance has been saved can (issue #3).
        assistant_id = self.initial.get("assistant")
        if assistant_id:
            # Populate the instructions field based on the selected assistant
            try:
                assistant = Assistant.objects.get(id=assistant_id)
                self.fields["instructions"].initial = assistant.instructions
            except Assistant.DoesNotExist:
                self.fields["instructions"].initial = ""
        elif self.instance.pk is None:
            default_assistant = Assistant.objects.order_by("?").first()
            if default_assistant:
                self.fields["assistant"].initial = default_assistant.id
                self.fields["instructions"].initial = default_assistant.instructions
        else:
            # A saved item with no assistant: pre-select nothing, and show no
            # other assistant's instructions.
            self.fields["instructions"].initial = ""


# =============================================================================
# AI FORMS
# =============================================================================


class AssistantForm(forms.ModelForm):
    # Define the form fields for the assistant to be displayed in the form
    class Meta:
        model = Assistant
        fields = [
            "name",
            "description",
            "model",
            "instructions",
            "json_schema",
            "assistant_group_memberships",
        ]

    # Set the assistant field choices to the names of all Assistant objects. Needed for AJAX request
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # self.fields['assistant_group_memberships'].queryset = memberships
            self.fields["assistant_group_memberships"].queryset = (
                AssistantGroup.objects.filter(
                    assistantgroupmembership__assistants=self.instance
                )
            )

        else:
            # No memberships for new assistants
            self.fields["assistant_group_memberships"].queryset = (
                AssistantGroup.objects.all()
            )


class AssistantGroupMembershipForm(forms.ModelForm):
    class Meta:
        model = AssistantGroupMembership
        fields = ["assistants", "position"]  # Updated field name


AssistantGroupMembershipFormSet = inlineformset_factory(
    AssistantGroup,
    AssistantGroupMembership,
    form=AssistantGroupMembershipForm,
    extra=3,
    can_delete=True,
)


class AssistantGroupForm(forms.ModelForm):
    class Meta:
        model = AssistantGroup
        fields = ["name", "group_type"]


# =============================================================================
# CONVERSATION FORMS
# =============================================================================


class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = [
            "name",
            "description",
            "assistant_group",
        ]


# =============================================================================
# PUBLISHING FORMS
# =============================================================================


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "id",
            "content_detail",
            "thread",
            "message",
            "assistant",
            "created_at",
            "filename",
            "status",
            "post_content",  # Added 'status' field
        ]
        exclude = ["updated_at"]


class PostFrontMatterForm(forms.ModelForm):
    class Meta:
        model = PostFrontMatter
        fields = ["id", "title", "description", "author", "published_at", "slug"]


class JSONSchemaForm(forms.ModelForm):
    class Meta:
        model = JSONSchema
        fields = ["name", "description", "schema"]
        widgets = {"schema": JSONEditorWidget}

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not re.match(r"^[a-zA-Z0-9_-]+$", name):
            raise ValidationError(
                "Name can only contain letters, numbers, underscores, and hyphens."
            )
        return name
