
# Registration Templates Directory

## Purpose
Contains Django authentication templates for user registration and login workflows. These templates provide the user interface for standard Django authentication views including login forms and logout confirmation pages.

## Contents
- `login.html`: Login form template with username/password fields
- `logged_out.html`: Logout confirmation page displayed after successful logout

## Usage

### Login Template Implementation
```django
<!-- login.html -->
{% extends "base.html" %}
{% load crispy_forms_tags %}

{% block title %}Login - Barody Broject{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h3>Login to Your Account</h3>
            </div>
            <div class="card-body">
                <form method="post">
                    {% csrf_token %}
                    {{ form|crispy }}
                    
                    <button type="submit" class="btn btn-primary btn-block">
                        Sign In
                    </button>
                </form>
                
                <div class="mt-3 text-center">
                    <a href="{% url 'password_reset' %}">Forgot Password?</a>
                    <br>
                    <a href="{% url 'account_signup' %}">Create New Account</a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Logout Confirmation
```django
<!-- logged_out.html -->
{% extends "base.html" %}

{% block title %}Logged Out - Barody Broject{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="alert alert-success text-center">
            <h4>You have been successfully logged out</h4>
            <p>Thank you for using Barody Broject!</p>
            
            <a href="{% url 'account_login' %}" class="btn btn-primary">
                Log In Again
            </a>
            <a href="{% url 'home' %}" class="btn btn-secondary">
                Return to Home
            </a>
        </div>
    </div>
</div>
{% endblock %}
```

### URL Configuration
```python
# In urls.py
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(
        template_name='registration/logged_out.html'
    ), name='logout'),
]
```

### Form Customization
```python
# Custom login form
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
```

## Container Configuration
- **Runtime**: Django template engine with form rendering
- **Dependencies**: 
  - Django authentication system
  - django-crispy-forms for form styling
  - Bootstrap CSS framework
- **Environment**: Integrated with Django user authentication
- **Session Management**: Handles user session creation and cleanup

## Related Paths
- **Incoming**: 
  - Django authentication middleware
  - User registration and account views
  - Password reset workflows
  - Social authentication (allauth)
- **Outgoing**: 
  - User session management
  - Account dashboard and profile pages
  - Protected application areas
  - Authentication decorators and mixins
