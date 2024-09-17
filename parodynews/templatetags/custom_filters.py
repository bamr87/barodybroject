from django import template

register = template.Library()

# Custom filter to get the value of a field from an instance
@register.filter
def get_field_value(instance, field_name):
    return getattr(instance, field_name, None)

# truncate_chars filter
@register.filter
def truncate_chars(value, max_length):
    if isinstance(value, str) and len(value) > max_length:
        return value[:max_length] + '...'
    return value