from django import template
import ast

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

# render dict as text list
@register.filter
def dict_to_text_list(value):
    if isinstance(value, str):
        try:
            value = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value  # Return the original string if it's not a valid dictionary

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