
# layouts Directory

## Purpose
This directory contains Django-Allauth base layout templates that define the overall structure and design framework for authentication pages. These layouts provide consistent page structure, navigation, and styling foundation that all authentication templates inherit from.

## Contents
- `base.html`: Base layout template for all authentication pages with common HTML structure, head elements, and navigation
- `entrance.html`: Specialized layout for entrance pages (login, signup, password reset) with focused, minimal design
- `manage.html`: Layout template for account management pages (profile, email settings, password change) with full navigation

## Usage
Layouts are extended by specific authentication templates:

```html
<!-- Example template extending base layout -->
{% extends "allauth/layouts/base.html" %}
{% load i18n %}

{% block head_title %}
  {% trans "Sign In" %} {{ block.super }}
{% endblock %}

{% block content %}
  <div class="auth-container">
    <!-- Authentication form content -->
  </div>
{% endblock %}

<!-- Example entrance layout usage -->
{% extends "allauth/layouts/entrance.html" %}
<!-- Simplified layout for login/signup -->
```

Layout features:
- **Base Layout**: Common HTML structure with meta tags, CSS, and JavaScript includes
- **Entrance Layout**: Minimalist design for login/registration flows with centered content
- **Management Layout**: Full-featured layout for account management with sidebar navigation
- **Responsive Design**: Mobile-first approach with responsive breakpoints
- **Brand Integration**: Consistent branding and styling with main application
- **Block Structure**: Flexible block system for content customization

## Container Configuration
Layouts provide structure for containerized authentication:
- Static assets served efficiently in container environments
- Responsive design adapts to various container viewport sizes
- CSS and JavaScript bundling for optimal container performance
- Consistent navigation and branding across authentication flows

## Related Paths
- Incoming: Extended by specific Django-Allauth authentication templates
- Outgoing: Provides HTML structure foundation for all authentication user interfaces
