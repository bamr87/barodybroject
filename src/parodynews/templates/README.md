
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
- Environment treatment in `base.html` (see below)

## Environment treatment

`base.html` gives non-production deployments a colour treatment so an operator
with several tabs open can tell production from test from development before
clicking a destructive control.

The environment name comes from `settings.ENVIRONMENT` (see
[docs/configuration/environment-config.md](../../../docs/configuration/environment-config.md)),
and reaches templates through the `parodynews.context_processors.environment`
context processor, which supplies:

| Context variable | Meaning |
| --- | --- |
| `environment` | The raw name — `production`, `test`, or `development` |
| `show_environment_badge` | Whether to render the treatment at all |
| `environment_label` | The text shown in the badge, e.g. `TEST` |
| `environment_badge_class` | Bootstrap badge class, e.g. `text-bg-warning` |
| `environment_border_class` | Bootstrap border class, e.g. `border-warning` |

The colour map:

| Environment | Label | Badge | Navbar border |
| --- | --- | --- | --- |
| `production` | *(none)* | *(none — unstyled baseline)* | *(none)* |
| `test` | `TEST` | `text-bg-warning` | `border-warning` |
| `development` | `DEV` | `text-bg-info` | `border-info` |

Three rules this treatment is built to keep:

1. **Production is the unstyled baseline.** Colouring the normal case too would
   train everyone to ignore the signal. Production renders today's exact markup.
2. **The label is text, never colour alone.** Colour by itself fails for
   colour-blind users and in greyscale (WCAG 2.1 SC 1.4.1).
3. **It must not fight the light/dark switcher.** The treatment uses Bootstrap
   5.3 semantic classes (`text-bg-*`, `border-*`), which are colour-mode aware,
   and never touches `data-bs-theme` or the stored theme preference. The two
   signals compose.

**Adding a fourth environment (e.g. `staging`) is a one-line change**: add the
name to `ENVIRONMENTS` in `settings/base.py`, and add one row to
`ENVIRONMENT_TREATMENTS` in `parodynews/context_processors.py`. `base.html`
needs no change — it branches on `show_environment_badge`, not on the name. An
environment with no row simply renders no badge.

Covered by `parodynews/tests/test_environment_theme.py`.

## Container Configuration
Templates are served through Django's template system:
- Located in Django's `TEMPLATES` setting configuration
- Processed by Django template engine during request handling
- Static assets referenced via `{% static %}` template tags
- Automatically reloaded in development mode

## Related Paths
- Incoming: Rendered by Django views in response to HTTP requests
- Outgoing: Generates HTML responses sent to web browsers, includes static assets
