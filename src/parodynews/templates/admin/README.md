
# Django Admin Templates Directory

## Purpose
Contains custom Django admin interface templates for overriding and extending the default admin functionality. This directory allows customization of the admin interface appearance, layout, and behavior to match the Barody Broject branding and provide enhanced administrative capabilities.

## Contents
*Currently empty - directory prepared for admin template customizations*

## Usage

### Common Admin Template Overrides
```django
<!-- admin/base_site.html - Custom admin header -->
{% extends "admin/base.html" %}

{% block title %}{{ title }} | Barody Broject Admin{% endblock %}

{% block branding %}
<h1 id="site-name">
    <a href="{% url 'admin:index' %}">
        Barody Broject Administration
    </a>
</h1>
{% endblock %}

{% block nav-global %}{% endblock %}
```

### Model-Specific Admin Templates
```django
<!-- admin/parodynews/article/change_list.html -->
{% extends "admin/change_list.html" %}

{% block content_title %}
    <h1>Parody Articles Management</h1>
    <div class="admin-stats">
        <span class="badge badge-primary">
            Total: {{ cl.result_count }}
        </span>
        <span class="badge badge-success">
            Published: {{ published_count }}
        </span>
    </div>
{% endblock %}

{% block extrahead %}
{{ block.super }}
<style>
    .admin-stats {
        margin: 10px 0;
    }
    .admin-stats .badge {
        margin-right: 10px;
    }
</style>
{% endblock %}
```

### Custom Admin Actions
```django
<!-- admin/parodynews/article/actions.html -->
{% load i18n %}
<div class="actions">
    <label>{% trans 'Action:' %}</label>
    <select name="action" required>
        <option value="" selected>---------</option>
        <option value="publish_articles">Publish selected articles</option>
        <option value="unpublish_articles">Unpublish selected articles</option>
        <option value="generate_ai_content">Generate AI content</option>
    </select>
    
    <button type="submit" class="button" title="{% trans 'Run the selected action' %}" name="index" value="{{ action_index|default:0 }}">
        {% trans "Go" %}
    </button>
</div>
```

### Enhanced Admin Dashboard
```django
<!-- admin/index.html - Custom admin dashboard -->
{% extends "admin/index.html" %}
{% load static %}

{% block extrahead %}
{{ block.super }}
<link rel="stylesheet" type="text/css" href="{% static 'admin/css/dashboard.css' %}">
{% endblock %}

{% block content %}
<div class="dashboard-stats">
    <div class="stat-card">
        <h3>{{ total_articles }}</h3>
        <p>Total Articles</p>
    </div>
    <div class="stat-card">
        <h3>{{ ai_generated_today }}</h3>
        <p>AI Generated Today</p>
    </div>
    <div class="stat-card">
        <h3>{{ active_users }}</h3>
        <p>Active Users</p>
    </div>
</div>

{{ block.super }}
{% endblock %}
```

### Admin Form Customizations
```django
<!-- admin/parodynews/article/change_form.html -->
{% extends "admin/change_form.html" %}

{% block submit_buttons_bottom %}
{{ block.super }}
<div class="submit-row">
    <input type="submit" value="Save and Generate AI Content" 
           class="default" name="_save_and_generate">
    <input type="submit" value="Save and Publish" 
           class="default" name="_save_and_publish">
</div>
{% endblock %}

{% block admin_change_form_document_ready %}
{{ block.super }}
<script>
(function($) {
    // Custom admin JavaScript
    $('#id_category').change(function() {
        var category = $(this).val();
        if (category === 'news') {
            $('#id_ai_tone').val('serious');
        } else if (category === 'comedy') {
            $('#id_ai_tone').val('humorous');
        }
    });
})(django.jQuery);
</script>
{% endblock %}
```

## Container Configuration
- **Runtime**: Django admin interface framework
- **Dependencies**: 
  - Django admin system
  - Custom CSS and JavaScript assets
  - Authentication and permissions system
- **Environment**: 
  - Integrated with Django settings
  - Admin media files and static assets
  - Custom admin context processors
- **Security**: Admin-specific authentication and CSRF protection

## Related Paths
- **Incoming**: 
  - Django admin configuration (`admin.py` files)
  - Custom admin forms and widgets
  - Admin URL patterns and routing
  - User authentication and permissions
- **Outgoing**: 
  - Model management interfaces
  - Database operations and queries
  - Static admin assets (CSS, JS, images)
  - Admin logging and audit trails
