
# Account Snippets Directory

## Purpose
Contains reusable HTML snippet templates for account-related UI components. These templates provide modular, consistent user interface elements for account warnings, notifications, and state indicators that can be included across multiple account pages.

## Contents
- `warn_no_email.html`: Warning snippet displayed when user has no verified email address
- `already_logged_in.html`: Information snippet shown when user is already authenticated

## Usage

### Template Inclusion
```django
<!-- Include warning snippets in account templates -->
{% include "account/snippets/warn_no_email.html" %}

<!-- Conditional inclusion based on user state -->
{% if user.is_authenticated %}
    {% include "account/snippets/already_logged_in.html" %}
{% endif %}
```

### Custom Snippet Creation
```django
<!-- warn_no_email.html example -->
<div class="alert alert-warning">
    <i class="fas fa-exclamation-triangle"></i>
    <strong>No verified email address</strong>
    <p>Please add and verify an email address to ensure account security.</p>
    <a href="{% url 'account_email' %}" class="btn btn-sm btn-warning">
        Add Email Address
    </a>
</div>
```

### JavaScript Integration
```javascript
// Handle snippet interactions
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide temporary notifications
    setTimeout(() => {
        document.querySelectorAll('.alert-info').forEach(alert => {
            alert.style.opacity = '0';
        });
    }, 5000);
});
```

## Container Configuration
- **Runtime**: Django template engine with HTML rendering
- **Dependencies**: Bootstrap CSS framework for styling
- **Environment**: Integrated with allauth template context
- **Assets**: FontAwesome icons, custom CSS for alert styling

## Related Paths
- **Incoming**: 
  - Account view templates (`login.html`, `signup.html`)
  - User dashboard and profile pages
  - Email management views
- **Outgoing**: 
  - Base template styling systems
  - JavaScript notification handlers
  - Account action redirects and forms
