from django import forms
from .models import Assistant, Content, ContentDetail, MyObject, JSONSchema
import json

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


# Load model choices from the JSON file
try:
    with open('model_choices.json', 'r') as f:
        MODEL_CHOICES = [(model, model) for model in json.load(f)]
except FileNotFoundError:
    MODEL_CHOICES = []

class ContentForm(forms.ModelForm):

    assistant = forms.ModelChoiceField(
        queryset=Assistant.objects.all(),
        label="Assistant Name",
        widget=forms.Select(attrs={'class': 'form-select'}),
        to_field_name="name"  # This will display the 'name' field in the dropdown
    )
    
    instructions = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'readonly': 'readonly'}), required=False)

    class Meta:
        model = Content
        fields = [ 'assistant', 'instructions', 'prompt']
        widgets = {
            'prompt': forms.Textarea(attrs={'class': 'form-control'}),
        }
        labels = {
            'prompt': 'Prompt',
        }
        field_order = ['prompt']  # Specify the order of fields

# Fetch all Assistant objects and create a list of tuples for the dropdown choices

class AssistantForm(forms.ModelForm):

    class Meta:
        model = Assistant
        fields = ['name', 'description', 'model', 'instructions', 'json_schema']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_name'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_assist_description'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'id': 'id_instructions'}),
            'model': forms.Select(attrs={'class': 'form-select', 'id': 'id_model'}),
            'json_schema': forms.Select(attrs={'class': 'form-control', 'id': 'id_json_schema'}),
        }


    def __init__(self, *args, **kwargs):
        super(AssistantForm, self).__init__(*args, **kwargs)
        self.fields['model'].choices = MODEL_CHOICES
        self.fields['model'].initial = Assistant._meta.get_field('model').default

class MyObjectForm(forms.ModelForm):
    class Meta:
        model = MyObject
        fields = ['name', 'description']

# JSON Schema model form

from django_json_widget.widgets import JSONEditorWidget

class JSONSchemaForm(forms.ModelForm):
    class Meta:
        model = JSONSchema
        fields = ['name', 'schema']
        widgets = {
            'schema': JSONEditorWidget
        }
        