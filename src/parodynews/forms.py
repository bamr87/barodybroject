import re
from django_json_widget.widgets import JSONEditorWidget
from django.core.exceptions import ValidationError
from django import forms
from django.db.models import Count
from .models import (
    Assistant,
    AssistantGroup,
    ContentItem,
    ContentDetail,
    MyObject,
    JSONSchema,
    Thread,
    Post,
    PostFrontMatter,
    )

# from martor.fields import MartorFormField
from cms.models.fields import PlaceholderField
from django.forms import inlineformset_factory
from .models import AssistantGroup, AssistantGroupMembership

print("Loading forms...")

# Content detail form that contains the main content details and metadata. Converted to post front matter form for the blog
class ContentDetailForm(forms.ModelForm):
    class Meta:
        model = ContentDetail
        fields = ['id', 'title', 'description', 'author', 'published_at', 'slug']
        widgets = {
            'id': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'published_at': forms.DateInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }

# Content item form that contains the main content details and metadata. Converted to post form for the blog

class ContentItemForm(forms.ModelForm):

    # Define the form fields for the assistant to be displayed in the form
    assistant = forms.ModelChoiceField(
        queryset=Assistant.objects.all(),
        label="Assistant Name",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    # Define the form field for the instructions to be displayed in the form
    instructions = forms.CharField(
        widget=forms.Textarea(
            attrs={'class': 'form-control',
                   'readonly': 'readonly'}), 
        required=False
    )

    # Meta class to define the model and fields to be displayed in the form
    class Meta:
        model = ContentItem
        fields = [ 'assistant', 'instructions', 'prompt', 'content_text']
        widgets = {
            'prompt': forms.Textarea(attrs={'class': 'form-control'}),
            'content_text': forms.Textarea(attrs={'class': 'form-control'}),
        }
        labels = {
            'prompt': 'Prompt',
        }
        field_order = ['prompt']  # Specify the order of fields

    # Set the assistant field choices to the names of all Assistant objects. Needed for AJAX request
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assistant'].widget.choices = [
            (assistant.id, assistant.name) for assistant in Assistant.objects.all()
        ]

        self.fields['content_text'].required = False  # Make content field optional

        # Only set the assistant field to a random record if the form is new
        if not self.initial.get('assistant'):
            random_assistant = Assistant.objects.annotate(num=Count('id')).order_by('?').first()
            if random_assistant:
                self.fields['assistant'].initial = random_assistant.id
                self.fields['instructions'].initial = random_assistant.instructions
        else:
            # Populate the instructions field based on the selected assistant
            assistant_id = self.initial.get('assistant')
            try:
                assistant = Assistant.objects.get(id=assistant_id)
                self.fields['instructions'].initial = assistant.instructions
            except Assistant.DoesNotExist:
                self.fields['instructions'].initial = ''

# Assistant form that contains the main assistant details and metadata
class AssistantForm(forms.ModelForm):
    # Define the form fields for the assistant to be displayed in the form
    class Meta:
        model = Assistant
        fields = ['name', 'description', 'model', 'instructions', 'json_schema', 'assistant_group_memberships']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_name'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_assist_description'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'id': 'id_instructions'}),
            'model': forms.Select(attrs={'class': 'form-select', 'id': 'id_model'}),
            'json_schema': forms.Select(attrs={'class': 'form-control', 'id': 'id_json_schema'}),
            'assistant_group_memberships': forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'id_assistant_group_memberships'}),
        }

    # Set the assistant field choices to the names of all Assistant objects. Needed for AJAX request
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # Filter to assistant groups the assistant is a member of
            memberships = AssistantGroupMembership.objects.filter(assistants=self.instance)
            # self.fields['assistant_group_memberships'].queryset = memberships
            self.fields['assistant_group_memberships'].queryset = AssistantGroup.objects.filter(assistantgroupmembership__assistants=self.instance)

        else:
            # No memberships for new assistants
            self.fields['assistant_group_memberships'].queryset = AssistantGroup.objects.all()

# Assistant group form that contains the main assistant group details and metadata. Used to group assistants into a workflow.
class AssistantGroupMembershipForm(forms.ModelForm):
    class Meta:
        model = AssistantGroupMembership
        fields = ['assistants', 'position']  # Updated field name
        widgets = {
            'assistants': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

AssistantGroupMembershipFormSet = inlineformset_factory(
    AssistantGroup,
    AssistantGroupMembership,
    form=AssistantGroupMembershipForm,
    extra=1,
    can_delete=True
)

class AssistantGroupForm(forms.ModelForm):
    class Meta:
        model = AssistantGroup
        fields = ['name', 'group_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'group_type': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ContentProcessingForm(forms.Form):
    thread_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    assistant_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    content_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    prompt = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ThreadRunFrom(forms.Form):
    thread_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    assistant_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    content_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    prompt = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    


# Post form 
class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = [
            'id', 'content_detail', 'thread', 'message', 'assistant',
            'created_at', 'filename', 'status', 'post_content'  # Added 'status' field
        ]
        widgets = {
            'content_detail': forms.Select(attrs={'class': 'form-control'}),
            'thread': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Select(attrs={'class': 'form-control'}),
            'assistant': forms.Select(attrs={'class': 'form-control'}),
            'created_at': forms.DateTimeInput(attrs={'class': 'form-control'}),
            'filename': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.TextInput(attrs={'class': 'form-control'}),
            'post_content': forms.Textarea(attrs={'class': 'form-control'}),
        }
        exclude = ['updated_at']


class PostFrontMatterForm(forms.ModelForm):
    class Meta:
        model = PostFrontMatter
        fields = ['id', 'title', 'description', 'author', 'published_at', 'slug']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'published_at': forms.DateTimeInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }


class MyObjectForm(forms.ModelForm):
    class Meta:
        model = MyObject
        fields = ['name', 'description']

# JSON Schema model form


class JSONSchemaForm(forms.ModelForm):
    class Meta:
        model = JSONSchema
        fields = ['name', 'description', 'schema']
        widgets = {
            'schema': JSONEditorWidget
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            raise ValidationError('Name can only contain letters, numbers, underscores, and hyphens.')
        return name

