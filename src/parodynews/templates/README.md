
# templates Directory

## Purpose
This directory contains Django HTML templates that define the user interface and presentation layer for the parody news generator application. It includes templates for authentication, content management, navigation, and various user interface components using Django's template system.

## Contents
- `429.html`: Rate limiting error page template
- `account/`: Django Allauth account management templates (login, signup, profile)
- `admin/`: Custom Django admin interface templates
- `allauth/`: Django Allauth authentication system templates and layouts
- `base.html`: Base template that other templates extend, includes common HTML structure
- `chatbox.html`: Template for chat/messaging interface components
- `footer.html`: Footer component template used across the site
- `includes/`: Reusable template fragments and components
- `index.html`: Main landing page template
- `menu/`: Navigation menu templates
- `mfa/`: Multi-factor authentication templates (TOTP, WebAuthn, recovery codes)
- `object_template.html`: Generic object display template
- `parodynews/`: Application-specific templates for parody news functionality
- `profile.html`: User profile display template
- `registration/`: User registration and password reset templates
- `socialaccount/`: Social media authentication templates
- `usersessions/`: User session management templates

## Usage
Templates are rendered by Django views and follow Django template conventions:

```python
# In views.py
from django.shortcuts import render

def home_view(request):
    return render(request, 'index.html', context)

def content_view(request):
    return render(request, 'parodynews/content_detail.html', context)
```

```html
<!-- Template inheritance -->
{% extends 'base.html' %}
{% load static %}

{% block content %}
<!-- Page-specific content -->
{% endblock %}
```

Template features:
- Django template inheritance with `base.html`
- Integration with Django Allauth for authentication
- Multi-factor authentication support
- Social media login integration
- Responsive design components
- Static file integration

## Container Configuration
Templates are served through Django's template system:
- Located in Django's `TEMPLATES` setting configuration
- Processed by Django template engine during request handling
- Static assets referenced via `{% static %}` template tags
- Automatically reloaded in development mode

## Related Paths
- Incoming: Rendered by Django views in response to HTTP requests
- Outgoing: Generates HTML responses sent to web browsers, includes static assets
