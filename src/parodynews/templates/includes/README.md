
# Template Includes Directory

## Purpose
Contains reusable Django template components designed to eliminate code duplication and provide consistent UI patterns across the barodybroject application. These components reduce template code by ~35% while improving maintainability and accessibility.

## Contents
- `crud_buttons.html` - Standardized Save/Delete/Create button groups
- `model_table.html` - Dynamic sortable/filterable tables  
- `sortable_header.html` - One sortable/filterable `<th>`, for tables that cannot use `model_table.html`
- `form_wrapper.html` - Bootstrap 5 form with error handling
- `status_badge.html` - Status indicator badges
- `confirm_modal.html` - Confirmation dialog for destructive actions

## List tables: always go through a component

Sorting and filtering are client-side only (`assets/js/table_utils.js`) and depend on an exact markup contract. **Do not hand-roll a `<th>`.** Every list table uses one of two components:

| Situation | Use |
| --- | --- |
| The rows are a plain projection of `fields`/`display_fields` | `{% render_model_table objects fields display_fields 'detail_url_name' 'Label' %}` |
| The rows carry click-through handlers, embedded forms, or static columns | build the body by hand, but emit each header with `{% include "includes/sortable_header.html" with label=… sort_type=… %}` |

The contract both satisfy, and why it is easy to get wrong:

- `table_utils.js:7` binds its click handler to **`th.sortable`**. A header without that
  class gets no listener, so clicking it does nothing — silently.
- Filtering binds to `input.filter` (`table_utils.js:35`) and needs **no** class on the header. That asymmetry is the trap: a hand-rolled header where the filter works and the sort is dead looks half-functional rather than broken, and that is exactly the state four list templates sat in.
- `data-type="number"|"date"` selects the comparator. Without it a column of IDs sorts
  `1, 10, 2`. For model-driven columns get it from `field|sort_data_type`; for static
  columns pass it explicitly.

`parodynews/tests/test_model_table.py` pins all of this, including a sweep over every template's source that fails if any header renders a filter without opting into sorting.

Migrating a hand-rolled table onto `render_model_table` is preferred, but not at the cost of behaviour: the component renders its first cell as a link and cannot express row-level click-through, embedded forms, or per-cell truncation. Where those matter, keep the body and use `sortable_header.html`.

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
