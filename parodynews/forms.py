from django import forms
from .models import Assistant, Content, ContentDetail
import json

print("Loading forms...")

class ContentDetailForm(forms.ModelForm):
    class Meta:
        model = ContentDetail
        fields = ['title', 'description', 'author', 'published_at', 'slug']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'published_at': forms.DateInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def save(self, commit=True):
        # Call the parent class's save method
        instance = super().save(commit=False)
        # Add any additional processing here if needed
        if commit:
            instance.save()
        return instance

# Load model choices from the JSON file
try:
    with open('model_choices.json', 'r') as f:
        MODEL_CHOICES = [(model, model) for model in json.load(f)]
except FileNotFoundError:
    MODEL_CHOICES = []


class ContentForm(forms.ModelForm):

    class Meta:
        model = Content
        fields = [ 'prompt']
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

    def save(self, request):
        assistant_id = self.cleaned_data.get('assistant')
        if assistant_id:
            try:
                assistant = Assistant.objects.get(pk=assistant_id)
                json_schema = assistant.json_schema
                instructions = assistant.instructions
                # Store json_schema in the session
                request.session['json_schema'] = json_schema
                
                # Redirect to the view with the prompt
            except Assistant.DoesNotExist:
                raise forms.ValidationError("Assistant not found")
    

# Other form classes remain unchanged
from django import forms
from .models import Assistant, MODEL_CHOICES  # Import MODEL_CHOICES

# Fetch all Assistant objects and create a list of tuples for the dropdown choices
ASSISTANT_CHOICES = [(assistant.assistant_id, assistant.name) for assistant in Assistant.objects.all()]

class AssistantForm(forms.ModelForm):
    name_list = forms.ChoiceField(choices=ASSISTANT_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Assistant
        fields = ['name_list', 'assistant_id', 'name', 'description', 'model', 'instructions', 'json_schema']
        widgets = {
            'name_list': forms.TextInput(attrs={'class': 'form-control'}),
            'assistant_id': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control'}),
            'model': forms.Select(attrs={'class': 'form-select'}),
            'json_schema': forms.Select(attrs={'class': 'form-control'}),
        }
        initial = {
            'model': 'gpt-3.5-turbo'
        }

    def __init__(self, *args, **kwargs):
        super(AssistantForm, self).__init__(*args, **kwargs)
        self.fields['model'].choices = MODEL_CHOICES
        self.fields['model'].initial = MODEL_CHOICES[0][0] if MODEL_CHOICES else None
        self.fields['name_list'].choices = ASSISTANT_CHOICES

        # Set the initial value of name_list to the assistant_id of the instance
        if 'instance' in kwargs and kwargs['instance']:
            self.fields['name_list'].initial = kwargs['instance'].assistant_id

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
        