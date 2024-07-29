from django import forms
from .models import Assistant, Content
import json

# Load model choices from the JSON file
try:
    with open('model_choices.json', 'r') as f:
        MODEL_CHOICES = [(model, model) for model in json.load(f)]
except FileNotFoundError:
    MODEL_CHOICES = []

class ContentForm(forms.ModelForm):
    instructions = forms.CharField(widget=forms.Textarea(attrs={'readonly': 'readonly'}), required=False, label='Instructions')
    
    def __init__(self, *args, **kwargs):
        super(ContentForm, self).__init__(*args, **kwargs)
        # Fetch Assistant objects
        assistants = Assistant.objects.all().values_list('assistant_id', 'name')
        # Create choices list with assistant names and an option to create a new assistant
        choices = [('', 'Select Assistant')]  # Default choice added here
        choices += [(assistant[0], assistant[1]) for assistant in assistants]
        # Set choices for the assistant_name field
        self.fields['name'] = forms.ChoiceField(choices=choices, required=False)
        self.fields['assistant'] = forms.ChoiceField(choices=choices, required=False)
        self.fields['instructions'].initial = 'Select an assistant to see instructions.'

    def clean_assistant(self):
        assistant_id = self.cleaned_data.get('assistant')
        if assistant_id:
            try:
                return Assistant.objects.get(assistant_id=assistant_id)
            except Assistant.DoesNotExist:
                raise forms.ValidationError("Invalid assistant selected.")
        return None

    class Meta:
        model = Content
        fields = ['assistant', 'instructions', 'prompt']

# Other form classes remain unchanged
class AssistantForm(forms.Form):
    name = forms.CharField(label='Assistant Name', max_length=100)
    description = forms.CharField(label='Description', max_length=512, required=False)
    instructions = forms.CharField(label='Instructions', widget=forms.Textarea)
    model = forms.ChoiceField(label='Model', choices=MODEL_CHOICES, initial=MODEL_CHOICES[3][0] if MODEL_CHOICES else None)