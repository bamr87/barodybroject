from django import forms
from .models import Content

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['role', 'prompt']

class AssistantForm(forms.Form):
    assistant_name = forms.CharField(label='Assistant Name', max_length=100)
    instructions = forms.CharField(label='Instructions', widget=forms.Textarea)