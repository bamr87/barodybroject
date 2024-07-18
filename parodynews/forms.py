from django import forms
from .models import SystemRole, Content

class ContentForm(forms.ModelForm):
    instructions = forms.CharField(widget=forms.Textarea(attrs={'readonly': 'readonly'}), required=False, label='Instructions')
    def __init__(self, *args, **kwargs):
        super(ContentForm, self).__init__(*args, **kwargs)
        # Fetch role names from SystemRole objects
        system_roles = SystemRole.objects.all().values_list('id', 'role_name')
        # Create choices list with role names and an option to create a new role
        choices = [('', 'Select Role')]  # Default choice added here
        choices += [(role[0], role[1]) for role in system_roles]
        # Set choices for the role_name field
        self.fields['role_name'] = forms.ChoiceField(choices=choices, required=False)
        self.fields['instructions'].initial = 'Select a role to see instructions.'

    class Meta:
        model = Content
        fields = ['system_role', 'instructions', 'prompt']

class RoleForm(forms.ModelForm):
    class Meta:
        model = SystemRole
        fields = ['role_name', 'role_type', 'instructions']

# Other form classes remain unchanged
class AssistantForm(forms.Form):
    assistant_name = forms.CharField(label='Assistant Name', max_length=100)
    instructions = forms.CharField(label='Instructions', widget=forms.Textarea)