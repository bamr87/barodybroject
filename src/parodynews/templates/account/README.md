
# account Directory

## Purpose
This directory contains Django-Allauth account management templates that provide user authentication interfaces including login, signup, password management, email verification, and account security features. These templates create a complete user authentication experience with modern, responsive design and comprehensive security features.

## Contents
- `login.html`: User login form with username/email and password authentication
- `signup.html`: User registration form with account creation and email verification
- `logout.html`: User logout confirmation page with session termination
- `password_change.html`: Password change form for authenticated users
- `password_set.html`: Initial password setup for users who signed up without passwords
- `password_reset.html`: Password reset request form with email-based recovery
- `password_reset_done.html`: Confirmation page after password reset email sent
- `password_reset_from_key.html`: Password reset form accessed via email link
- `password_reset_from_key_done.html`: Confirmation page after successful password reset
- `email.html`: Email address management interface for users
- `email_change.html`: Email address change form with verification
- `email_confirm.html`: Email address confirmation page from verification links
- `verification_sent.html`: Confirmation that email verification was sent
- `verified_email_required.html`: Page prompting users to verify their email address
- `account_inactive.html`: Page shown when user account is inactive or disabled
- `signup_closed.html`: Page shown when user registration is temporarily disabled
- `reauthenticate.html`: Re-authentication form for sensitive operations
- `base_reauthenticate.html`: Base template for re-authentication pages
- `request_login_code.html`: Request login code form for passwordless authentication
- `confirm_login_code.html`: Confirm login code form for passwordless authentication
- `confirm_email_verification_code.html`: Email verification code confirmation form
- `signup_by_passkey.html`: Passkey-based registration form for modern authentication
- `base_entrance.html`: Base template for login/signup entrance pages
- `base_manage.html`: Base template for account management pages
- `base_manage_email.html`: Base template for email management pages
- `base_manage_password.html`: Base template for password management pages
- `snippets/`: Subdirectory containing reusable template components (has its own README)
- `messages/`: Subdirectory containing message templates for notifications (has its own README)
- `email/`: Subdirectory containing email templates for account notifications (has its own README)

## Usage
Templates are rendered by Django-Allauth views and can be customized:

```html
<!-- Example login.html template -->
{% extends "account/base_entrance.html" %}
{% load allauth i18n %}

{% block head_title %}{% trans "Sign In" %}{% endblock %}

{% block content %}
<div class="auth-form">
    <h1>{% trans "Sign In" %}</h1>
    
    <form class="login" method="POST" action="{% url 'account_login' %}">
        {% csrf_token %}
        {{ form.as_p }}
        
        <button type="submit" class="btn btn-primary">
            {% trans "Sign In" %}
        </button>
    </form>
    
    <p class="auth-links">
        <a href="{% url 'account_reset_password' %}">
            {% trans "Forgot Password?" %}
        </a>
    </p>
</div>
{% endblock %}
```

## Container Configuration
Account templates served through Django web container:
- Templates rendered with full Django context and user session data
- Responsive design optimized for mobile and desktop viewing
- Form validation and error handling integrated with Django-Allauth
- CSRF protection and security features enabled for all authentication forms

## Related Paths
- Incoming: Rendered by Django-Allauth views handling user authentication workflows
- Outgoing: Provides complete user account management interface for the parody news generator application
