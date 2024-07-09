from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['role', 'prompt']

class AssistantForm(forms.Form):
    assistant_name = forms.CharField(label='Assistant Name', max_length=100)
    instructions = forms.CharField(label='Instructions', widget=forms.Textarea)