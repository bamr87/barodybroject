
# Account Messages Directory

## Purpose
Contains Django allauth message templates for user account-related notifications and feedback. These text templates provide user-friendly messages for various account operations like email verification, password changes, and authentication events.

## Contents
- `email_deleted.txt`: Message displayed when user deletes an email address
- `password_set.txt`: Confirmation message when password is initially set
- `password_changed.txt`: Notification when password is successfully changed
- `primary_email_set.txt`: Message when user sets a primary email address
- `email_confirmed.txt`: Success message after email address verification
- `logged_in.txt`: Welcome message displayed upon successful login
- `unverified_primary_email.txt`: Warning when primary email is unverified
- `cannot_delete_primary_email.txt`: Error message preventing primary email deletion
- `email_confirmation_failed.txt`: Error message for failed email verification
- `email_confirmation_sent.txt`: Confirmation that verification email was sent
- `logged_out.txt`: Message displayed after successful logout
- `login_code_sent.txt`: Notification that login code was sent to user

## Usage

### Message Display Example
```python
# In Django views, messages are automatically displayed
from django.contrib import messages

# Custom message usage
messages.success(request, 'Your email has been confirmed successfully.')
messages.error(request, 'Cannot delete primary email address.')
```

### Template Integration
```django
<!-- In base templates -->
{% if messages %}
    <div class="messages">
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }}">
                {{ message }}
            </div>
        {% endfor %}
    </div>
{% endif %}
```

## Container Configuration
- **Runtime**: Django template rendering engine
- **Dependencies**: django-allauth message framework
- **Environment**: Integrated with Django settings and message backends
- **Localization**: Supports internationalization through Django's i18n framework

## Related Paths
- **Incoming**: 
  - `parodynews/views.py` - Account view operations
  - `allauth` authentication workflows
  - Django message framework
- **Outgoing**: 
  - Base templates for message display
  - Frontend JavaScript for message handling
  - User notification systems
