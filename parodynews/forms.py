from django import forms
from .models import Assistant, Content, ContentDetail
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
        empty_label="Select an Assistant",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    instructions = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'readonly': 'readonly'}), required=False)

    class Meta:
        model = Content
        fields = [ 'assistant', 'prompt']
        widgets = {
            'prompt': forms.Textarea(attrs={'class': 'form-control'}),
        }
        labels = {
            'prompt': 'Prompt',
        }
        field_order = ['prompt']  # Specify the order of fields


    def __init__(self, *args, **kwargs):
        assistant_id = kwargs.pop('assistant_id', None)
        super(ContentForm, self).__init__(*args, **kwargs)
        
        if assistant_id:
            try:
                assistant = Assistant.objects.get(pk=assistant_id)
                self.fields['assistant'].initial = assistant.assistant_id
                self.fields['instructions'].initial = assistant.instructions
                self.fields['assistant_id'].initial = assistant_id

            except Assistant.DoesNotExist:
                pass

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
        initial = {
            'model': 'gpt-3.5-turbo'
        }

    def __init__(self, *args, **kwargs):
        super(AssistantForm, self).__init__(*args, **kwargs)
        self.fields['model'].choices = MODEL_CHOICES
        self.fields['model'].initial = MODEL_CHOICES[0][0] if MODEL_CHOICES else None


from django import forms
from .models import MyObject

class MyObjectForm(forms.ModelForm):
    class Meta:
        model = MyObject
        fields = ['name', 'description']


# JSON Schema model form

# forms.py
from django import forms
from django_json_widget.widgets import JSONEditorWidget
from .models import JSONSchema

class JSONSchemaForm(forms.ModelForm):
    class Meta:
        model = JSONSchema
        fields = ['name', 'schema']
        widgets = {
            'schema': JSONEditorWidget
        }
        