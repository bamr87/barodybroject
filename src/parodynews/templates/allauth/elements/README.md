
# elements Directory

## Purpose
This directory contains Django-Allauth template element components that provide reusable UI building blocks for authentication forms and interfaces. These elements follow a component-based approach, allowing for consistent styling and behavior across all authentication pages while maintaining customization flexibility.

## Contents
- `alert.html`: Alert message component for displaying notifications and feedback
- `badge.html`: Badge component for status indicators and labels
- `button.html`: Button component with various styles and states for form actions
- `button__entrance.html`: Specialized button styling for entrance/login pages
- `button_group.html`: Button group component for related action buttons
- `field.html`: Form field wrapper component with error handling and styling
- `fields.html`: Multiple form fields container with consistent spacing
- `form.html`: Form wrapper component with CSRF protection and validation
- `form__entrance.html`: Specialized form styling for entrance/login forms
- `h1.html`, `h2.html`: Header components with consistent typography
- `h1__entrance.html`, `h2__entrance.html`: Specialized headers for entrance pages
- `hr.html`: Horizontal rule component for visual separation
- `img.html`: Image component with responsive styling
- `p.html`: Paragraph component with consistent text styling
- `panel.html`: Panel container component for grouped content
- `provider.html`: Social authentication provider button component
- `provider_list.html`: Container for multiple social provider buttons
- `table.html`, `tbody.html`, `td.html`, `th.html`, `thead.html`, `tr.html`: Table components for tabular data display

## Usage
Elements are imported and used within Allauth templates:

```html
<!-- Example usage in authentication templates -->
{% load allauth_elements %}

{% element "form" form=form %}
  {% element "fields" fields=form.visible_fields %}
  {% element "button" type="submit" %}
    Sign In
  {% endelement %}
{% endelement %}

{% element "panel" %}
  {% element "provider_list" providers=socialaccount_providers %}
{% endelement %}
```

Component features:
- **Consistent Styling**: Bootstrap-based styling with custom theme integration
- **Accessibility**: ARIA labels and semantic HTML structure
- **Responsive Design**: Mobile-first responsive behavior
- **Form Validation**: Error display and validation state styling
- **Social Authentication**: Provider-specific styling and icons

## Container Configuration
Elements are rendered server-side within Django templates:
- CSS and JavaScript assets served from static files
- Responsive design adapts to container viewport
- Form elements include CSRF protection and validation
- Error handling integrated with Django's form validation system

## Related Paths
- Incoming: Used by Django-Allauth authentication templates and forms
- Outgoing: Renders HTML components for authentication user interfaces
