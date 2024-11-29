from django import forms
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
    OpenAIModel
    )
from django.db.models import Count
# from martor.fields import MartorFormField
from cms.models.fields import PlaceholderField


print("Loading forms...")

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



class ContentItemForm(forms.ModelForm):

    assistant = forms.ModelChoiceField(
        queryset=Assistant.objects.all(),
        label="Assistant Name",
        widget=forms.Select(attrs={'class': 'form-select'}),
        to_field_name="id"  # This will display the 'name' field in the dropdown

    )
    
    instructions = forms.CharField(
        widget=forms.Textarea(
            attrs={'class': 'form-control',
                   'readonly': 'readonly'}), 
        required=False)

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

# Fetch all Assistant objects and create a list of tuples for the dropdown choices

from django import forms
from .models import Assistant

class AssistantForm(forms.ModelForm):

    class Meta:
        model = Assistant
        fields = ['name', 'description', 'model', 'instructions', 'json_schema', 'assistant_groups']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_name'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_assist_description'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'id': 'id_instructions'}),
            'model': forms.Select(attrs={'class': 'form-select', 'id': 'id_model'}),
            'json_schema': forms.Select(attrs={'class': 'form-control', 'id': 'id_json_schema'}),
            'assistant_groups': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super(AssistantForm, self).__init__(*args, **kwargs)

        if 'instance' in kwargs and kwargs['instance']:
            assistant = kwargs['instance']
            self.fields['assistant_groups'].queryset = AssistantGroup.objects.all()
            self.fields['assistant_groups'].initial = assistant.assistant_groups.all()
        else:
            self.fields['assistant_groups'].queryset = AssistantGroup.objects.all()

class AssistantGroupForm(forms.ModelForm):
    class Meta:
        model = AssistantGroup
        fields = ['name', 'assistants', 'group_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_group_name'}),
            'assistants': forms.CheckboxSelectMultiple(),
            'group_type': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_group_type'}),
        }

    def __init__(self, *args, **kwargs):
        super(AssistantGroupForm, self).__init__(*args, **kwargs)
        self.fields['assistants'].queryset = Assistant.objects.all()

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
    
from django import forms

# Post form 
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'id', 'content_detail', 'thread', 'message', 'assistant',
            'created_at', 'filename', 'status'  # Added 'status' field
        ]
        widgets = {
            'content_detail': forms.Select(attrs={'class': 'form-control'}),
            'thread': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Select(attrs={'class': 'form-control'}),
            'assistant': forms.Select(attrs={'class': 'form-control'}),
            'created_at': forms.DateTimeInput(attrs={'class': 'form-control'}),
            'filename': forms.TextInput(attrs={'class': 'form-control'}),
        }
        exclude = ['updated_at']
    # content = MartorFormField()

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

from django_json_widget.widgets import JSONEditorWidget
import re
from django.core.exceptions import ValidationError

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

