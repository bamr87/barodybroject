"""
File: custom_filters.py
Description: Custom Django template tags and filters for barodybroject
Author: Barodybroject Team
Created: 2024-01-01
Last Modified: 2025-11-25
Version: 2.0.0

Dependencies:
- django

Usage: {% load custom_filters %}
"""

from django import template
import ast
import json

register = template.Library()


# Custom filter to get the value of a field from an instance
@register.filter
def get_field_value(instance, field_name):
    """
    Dynamically access a field value from a model instance
    
    Usage: {{ object|get_field_value:"field_name" }}
    """
    try:
        return getattr(instance, field_name, None)
    except AttributeError:
        return None


# truncate_chars filter
@register.filter
def truncate_chars(value, max_length):
    """
    Truncate string to specified length with ellipsis
    
    Usage: {{ text|truncate_chars:100 }}
    Note: Django provides built-in truncatechars filter - consider using that instead
    """
    if isinstance(value, str) and len(value) > max_length:
        return value[:max_length] + "..."
    return value


# render dict as text list
@register.filter
def dict_to_text_list(value):
    """
    Convert dictionary or JSON string to formatted text list
    
    Usage: {{ data|dict_to_text_list }}
    Security: Fixed to use json.loads instead of ast.literal_eval
    """
    if isinstance(value, str):
        try:
            # Use json.loads instead of ast.literal_eval for security
            value = json.loads(value)
        except (ValueError, json.JSONDecodeError):
            return value  # Return the original string if it's not valid JSON

    if isinstance(value, dict):
        result = []
        for key, val in value.items():
            if isinstance(val, list):
                result.append(f"{key}:")
                for item in val:
                    result.append(f"  - {item}")
            else:
                result.append(f"{key}: {val}")
        return "\n".join(result)
    return value


@register.inclusion_tag('includes/status_badge.html')
def status_badge(status, label=None):
    """
    Render a status badge with appropriate styling
    
    Usage: {% status_badge object.status "Custom Label" %}
    """
    return {
        'status': status,
        'label': label or status,
    }


@register.inclusion_tag('includes/model_table.html')
def render_model_table(objects, fields, display_fields, detail_url, table_label=None):
    """
    Render a sortable, filterable table for any model listing
    
    Usage: {% render_model_table objects fields display_fields 'edit_content' 'Content List' %}
    
    Parameters:
        objects: QuerySet of model instances
        fields: List of model field objects from model._meta.get_fields()
        display_fields: List of field names to display (e.g., ['title', 'author', 'created_at'])
        detail_url: URL name for detail view (will be passed object.id)
        table_label: Optional ARIA label for accessibility
    """
    return {
        'objects': objects,
        'fields': fields,
        'display_fields': display_fields,
        'detail_url': detail_url,
        'table_label': table_label or 'Data table',
    }


@register.inclusion_tag('includes/crud_buttons.html')
def crud_buttons(object_id=None, save_url=None, delete_url=None, create_url=None):
    """
    Render standard CRUD button group (Save/Delete/Create)
    
    Usage: {% crud_buttons object.id 'edit_content' 'delete_content' 'manage_content' %}
    
    Parameters:
        object_id: ID of object being edited (None for create mode)
        save_url: URL name for save/update action
        delete_url: URL name for delete action
        create_url: URL name for create action
    """
    return {
        'object_id': object_id,
        'save_url': save_url,
        'delete_url': delete_url,
        'create_url': create_url,
    }


@register.simple_tag
def get_field_display(instance, field_name):
    """
    Get the display value for a field (useful for choices fields)
    
    Usage: {% get_field_display object 'status' %}
    """
    get_display_method = f'get_{field_name}_display'
    if hasattr(instance, get_display_method):
        return getattr(instance, get_display_method)()
    return getattr(instance, field_name, None)


@register.filter
def add_class(field, css_class):
    """
    Add CSS class to form field widget
    
    Usage: {{ form.field|add_class:"form-control" }}
    """
    return field.as_widget(attrs={'class': css_class})


@register.filter
def field_type(field):
    """
    Get the type of a form field widget
    
    Usage: {% if form.field|field_type == 'textarea' %}
    """
    return field.field.widget.__class__.__name__.lower()

