
# js Directory

## Purpose
This directory contains client-side JavaScript files that provide interactive functionality for the parody news generator's user interface. These scripts enhance the user experience with dynamic form handling, table utilities, UI frameworks, and content management features.

## Contents
- `content_detail.js`: JavaScript for dynamic content detail forms, handles assistant selection and auto-populates instructions fields via AJAX
- `halfmoon.js`: UI framework library for enhanced interface components and styling
- `issue_submission.js`: Handles form submission functionality for issue reporting and content creation
- `table_utils.js`: Provides sorting and filtering functionality for data tables throughout the application

## Usage
These JavaScript files are included in Django templates:

```html
<!-- In Django templates -->
{% load static %}
<script src="{% static 'js/content_detail.js' %}"></script>
<script src="{% static 'js/table_utils.js' %}"></script>
<script src="{% static 'js/halfmoon.js' %}"></script>
<script src="{% static 'js/issue_submission.js' %}"></script>
```

Key functionality:
- **content_detail.js**: Dynamic form field population based on assistant selection
- **table_utils.js**: Interactive table sorting and filtering for data management
- **halfmoon.js**: UI component library for consistent interface styling
- **issue_submission.js**: Form validation and submission handling

## Container Configuration
JavaScript files are served as static assets:
- Collected with `python manage.py collectstatic`
- Served through Django's static file configuration
- Cached by web browsers for performance
- Minified in production deployments

## Related Paths
- Incoming: Loaded by Django templates in web browser clients
- Outgoing: Makes AJAX requests to Django views, manipulates DOM elements
