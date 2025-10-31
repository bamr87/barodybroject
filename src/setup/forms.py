"""
File: forms.py
Description: Django forms for installation wizard
Author: Barodybroject Team <team@example.com>
Created: 2025-10-30
Last Modified: 2025-10-30
Version: 1.0.0

Dependencies:
- django.forms: Form classes and fields
- django.contrib.auth: User model

Usage: Forms for web-based admin user creation during setup
"""

import re

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class AdminUserForm(forms.Form):
    """
    Form for creating admin user during setup wizard
    
    Includes validation for secure passwords and unique usernames
    """
    
    username = forms.CharField(
        max_length=150,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'admin',
            'autocomplete': 'username'
        })
    )
    
    email = forms.EmailField(
        help_text='Required. Enter a valid email address.',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'admin@example.com',
            'autocomplete': 'email'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        help_text='Optional. First name for display purposes.',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'John',
            'autocomplete': 'given-name'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        help_text='Optional. Last name for display purposes.',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Doe',
            'autocomplete': 'family-name'
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a secure password',
            'autocomplete': 'new-password'
        }),
        help_text='Password must be at least 8 characters with letters and numbers.'
    )
    
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'autocomplete': 'new-password'
        }),
        help_text='Enter the same password for verification.'
    )
    
    def clean_username(self):
        """Validate username uniqueness and format"""
        username = self.cleaned_data['username']
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            raise ValidationError('A user with this username already exists.')
        
        # Validate username format
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError(
                'Username may only contain letters, digits and @/./+/-/_ characters.'
            )
        
        return username
    
    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data['email']
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        
        return email
    
    def clean_password(self):
        """Validate password strength"""
        password = self.cleaned_data['password']
        
        # Minimum length check
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        
        # Check for at least one letter and one number
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError('Password must contain at least one letter.')
        
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one number.')
        
        # Check for common passwords (basic check)
        common_passwords = [
            'password', '12345678', 'qwerty', 'abc123', 'admin123',
            'password123', 'welcome123', 'letmein', 'monkey123'
        ]
        
        if password.lower() in common_passwords:
            raise ValidationError('This password is too common. Please choose a more secure password.')
        
        return password
    
    def clean(self):
        """Validate password confirmation"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError({
                    'password_confirm': 'Password confirmation does not match.'
                })
        
        return cleaned_data


class SetupTokenForm(forms.Form):
    """
    Form for entering setup token
    """
    
    token = forms.CharField(
        max_length=100,
        help_text='Enter the setup token provided by the installation command.',
        widget=forms.TextInput(attrs={
            'class': 'form-control font-monospace',
            'placeholder': 'Enter setup token...',
            'autocomplete': 'off'
        })
    )
    
    def clean_token(self):
        """Basic token format validation"""
        token = self.cleaned_data['token'].strip()
        
        if not token:
            raise ValidationError('Setup token is required.')
        
        # Basic format check (should be URL-safe base64)
        if not re.match(r'^[A-Za-z0-9_-]+$', token):
            raise ValidationError('Invalid token format.')
        
        return token


class SetupConfigForm(forms.Form):
    """
    Form for basic setup configuration options
    """
    
    site_name = forms.CharField(
        max_length=100,
        initial='Barodybroject',
        help_text='Name of your parody news site.',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'My Parody News Site'
        })
    )
    
    site_description = forms.CharField(
        max_length=255,
        initial='AI-powered parody news generator',
        required=False,
        help_text='Brief description of your site.',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Generate hilarious satirical news with AI'
        })
    )
    
    enable_registration = forms.BooleanField(
        initial=True,
        required=False,
        help_text='Allow new users to register accounts.',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    enable_comments = forms.BooleanField(
        initial=True,
        required=False,
        help_text='Enable comments on articles.',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    default_language = forms.ChoiceField(
        choices=[
            ('en', 'English'),
            ('es', 'Spanish'),
            ('fr', 'French'),
            ('de', 'German'),
        ],
        initial='en',
        help_text='Default language for the site.',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )