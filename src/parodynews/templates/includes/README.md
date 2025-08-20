
# Template Includes Directory

## Purpose
Contains reusable Django template components and partial templates that can be included across multiple pages. This directory houses modular template snippets for common UI elements, form components, and shared functionality to promote DRY (Don't Repeat Yourself) principles in template design.

## Contents
*Currently empty - directory prepared for future template includes*

## Usage

### Common Include Patterns
```django
<!-- Navigation include -->
{% include "includes/navigation.html" %}

<!-- Breadcrumb include -->
{% include "includes/breadcrumb.html" with page_title="Current Page" %}

<!-- Form field includes -->
{% include "includes/form_field.html" with field=form.title %}

<!-- Alert message includes -->
{% include "includes/alert.html" with message="Success!" type="success" %}
```

### Typical Include Templates
```django
<!-- includes/navigation.html -->
<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
        <a class="navbar-brand" href="{% url 'home' %}">
            Barody Broject
        </a>
        
        {% if user.is_authenticated %}
            <ul class="navbar-nav ml-auto">
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'profile' %}">
                        {{ user.username }}
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'logout' %}">
                        Logout
                    </a>
                </li>
            </ul>
        {% endif %}
    </div>
</nav>

<!-- includes/form_field.html -->
<div class="form-group">
    {{ field.label_tag }}
    {{ field }}
    {% if field.errors %}
        <div class="text-danger">
            {{ field.errors }}
        </div>
    {% endif %}
    {% if field.help_text %}
        <small class="form-text text-muted">
            {{ field.help_text }}
        </small>
    {% endif %}
</div>
```

### JavaScript Includes
```django
<!-- includes/analytics.html -->
{% if not debug %}
<script>
    // Google Analytics or other tracking code
    gtag('config', 'GA_TRACKING_ID');
</script>
{% endif %}

<!-- includes/common_scripts.html -->
<script src="{% static 'js/jquery.min.js' %}"></script>
<script src="{% static 'js/bootstrap.bundle.min.js' %}"></script>
<script src="{% static 'js/common.js' %}"></script>
```

### Advanced Include Techniques
```django
<!-- Dynamic includes based on context -->
{% if article.category == 'news' %}
    {% include "includes/news_sidebar.html" %}
{% elif article.category == 'opinion' %}
    {% include "includes/opinion_sidebar.html" %}
{% endif %}

<!-- Include with conditional rendering -->
{% include "includes/advertisement.html" only %}

<!-- Include with isolated context -->
{% with custom_var="custom_value" %}
    {% include "includes/custom_component.html" %}
{% endwith %}
```

## Container Configuration
- **Runtime**: Django template engine with include resolution
- **Dependencies**: 
  - Django template system
  - Static file handling
  - Template context processors
- **Performance**: Template caching for frequently used includes
- **Environment**: Supports template inheritance and composition

## Related Paths
- **Incoming**: 
  - Base templates (`base.html`, `layout.html`)
  - Page-specific templates across the application
  - Form templates and wizard steps
  - Email templates requiring common elements
- **Outgoing**: 
  - Static CSS and JavaScript files
  - Template context variables and filters
  - URL routing and reverse lookups
  - Database models for dynamic content
