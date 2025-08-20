
# templatetags Directory

## Purpose
This directory contains Django custom template tags and filters that extend Django's template system with application-specific functionality. These custom filters provide specialized data processing and formatting capabilities for the parody news generator templates.

## Contents
- `__init__.py`: Python package initialization file making this directory a Python package
- `custom_filters.py`: Custom Django template filters for field access, text truncation, and dictionary formatting

## Usage
Template tags and filters are loaded and used in Django templates:

```html
<!-- Load custom filters in templates -->
{% load custom_filters %}

<!-- Use custom filters -->
{{ instance|get_field_value:"field_name" }}
{{ long_text|truncate_chars:100 }}
{{ dictionary_data|dict_to_text_list }}
```

Available custom filters:
- **`get_field_value`**: Dynamically access field values from model instances using field name strings
- **`truncate_chars`**: Truncate text to specified maximum length with ellipsis
- **`dict_to_text_list`**: Convert dictionary data to formatted text lists for display

Example usage in templates:
```html
<!-- Dynamic field access -->
{% for field_name in dynamic_fields %}
    <p>{{ object|get_field_value:field_name }}</p>
{% endfor %}

<!-- Text truncation -->
<p>{{ article.content|truncate_chars:150 }}</p>

<!-- Dictionary formatting -->
<pre>{{ metadata|dict_to_text_list }}</pre>
```

## Container Configuration
Template tags are loaded as part of the Django application:
- Registered with Django's template system at startup
- Available across all templates in the application
- Cached for performance in production environments

## Related Paths
- Incoming: Used by Django templates during rendering
- Outgoing: Processes template data for display in HTML responses
