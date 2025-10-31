
# Social Account Email Templates Directory

## Purpose
Contains email templates for social authentication notifications sent when users connect or disconnect social media accounts from their Barody Broject profile. These templates provide professional email communication for social account management events.

## Contents
- `account_disconnected_subject.txt`: Email subject line for social account disconnection notifications
- `account_disconnected_message.txt`: Email content when user disconnects a social account
- `account_connected_subject.txt`: Email subject line for social account connection confirmations
- `account_connected_message.txt`: Email content when user connects a new social account

## Usage

### Social Account Email Templates
```text
# account_connected_subject.txt
Social Account Connected - {{ provider }} linked to your Barody Broject account

# account_connected_message.txt
Hello {{ user.get_full_name|default:user.username }},

Your {{ provider }} account has been successfully connected to your Barody Broject profile.

Account Details:
- Provider: {{ provider }}
- Connected Account: {{ socialaccount.extra_data.name|default:socialaccount.uid }}
- Connection Date: {{ socialaccount.date_joined|date:"F j, Y at g:i A" }}

You can now sign in to Barody Broject using your {{ provider }} credentials, making access to your account faster and more convenient.

To manage your connected social accounts, visit your account settings:
{{ account_settings_url }}

If you did not connect this account, please contact our support team immediately.

Best regards,
The Barody Broject Team
```

### Disconnection Email Template
```text
# account_disconnected_subject.txt
Social Account Disconnected - {{ provider }} removed from your account

# account_disconnected_message.txt
Hello {{ user.get_full_name|default:user.username }},

Your {{ provider }} account has been disconnected from your Barody Broject profile.

Disconnected Account Details:
- Provider: {{ provider }}
- Account: {{ socialaccount.extra_data.name|default:socialaccount.uid }}
- Disconnection Date: {{ disconnect_date|date:"F j, Y at g:i A" }}

You will no longer be able to sign in using this {{ provider }} account. You can still access your Barody Broject account using:
{% if user.has_usable_password %}
- Your email and password
{% endif %}
{% for account in user.socialaccount_set.all %}
- Your {{ account.provider }} account
{% endfor %}

To reconnect this or other social accounts, visit your account settings:
{{ account_settings_url }}

If you did not disconnect this account, please contact our support team immediately.

Best regards,
The Barody Broject Team
```

### Email Configuration
```python
# In Django settings.py for social account emails
SOCIALACCOUNT_EMAIL_VERIFICATION = 'optional'
SOCIALACCOUNT_EMAIL_REQUIRED = False

# Custom email context processor
def social_account_email_context(user, socialaccount, provider):
    return {
        'user': user,
        'socialaccount': socialaccount,
        'provider': provider.title(),
        'account_settings_url': 'https://barodybroject.com/accounts/settings/',
        'support_email': 'support@barodybroject.com',
        'site_name': 'Barody Broject',
    }
```

### HTML Email Versions
```html
<!-- account_connected_message.html -->
<html>
<head>
    <title>Social Account Connected - Barody Broject</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .header { background-color: #007bff; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .provider-info { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .button { background-color: #007bff; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Social Account Connected</h1>
    </div>
    
    <div class="content">
        <p>Hello {{ user.get_full_name|default:user.username }},</p>
        
        <p>Great news! Your {{ provider }} account has been successfully connected to your Barody Broject profile.</p>
        
        <div class="provider-info">
            <strong>Connection Details:</strong><br>
            Provider: {{ provider }}<br>
            Account: {{ socialaccount.extra_data.name|default:socialaccount.uid }}<br>
            Connected: {{ socialaccount.date_joined|date:"F j, Y" }}
        </div>
        
        <p>You can now enjoy faster sign-ins using your {{ provider }} credentials!</p>
        
        <a href="{{ account_settings_url }}" class="button">
            Manage Social Accounts
        </a>
        
        <p><small>If you didn't connect this account, please contact our support team immediately at {{ support_email }}.</small></p>
    </div>
</body>
</html>
```

### Email Sending Logic
```python
# Custom social account email sender
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_social_account_notification(user, socialaccount, action):
    """Send email notification for social account actions"""
    
    provider = socialaccount.provider.title()
    context = {
        'user': user,
        'socialaccount': socialaccount,
        'provider': provider,
        'site_name': settings.SITE_NAME,
        'account_settings_url': f"{settings.SITE_URL}/accounts/social/",
    }
    
    if action == 'connected':
        subject_template = 'socialaccount/email/account_connected_subject.txt'
        message_template = 'socialaccount/email/account_connected_message.txt'
        html_template = 'socialaccount/email/account_connected_message.html'
    elif action == 'disconnected':
        subject_template = 'socialaccount/email/account_disconnected_subject.txt'
        message_template = 'socialaccount/email/account_disconnected_message.txt'
        html_template = 'socialaccount/email/account_disconnected_message.html'
    
    subject = render_to_string(subject_template, context).strip()
    message = render_to_string(message_template, context)
    html_message = render_to_string(html_template, context)
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False
    )
```

## Container Configuration
- **Runtime**: Django email backend with template rendering
- **Dependencies**: 
  - Django email system
  - django-allauth social account models
  - Email template rendering engine
  - SMTP configuration
- **Environment Variables**:
  - `EMAIL_HOST`: SMTP server configuration
  - `DEFAULT_FROM_EMAIL`: Sender email address
  - `SITE_URL`: Base URL for account links
  - `SITE_NAME`: Application name for emails
- **Security**: Email content sanitization and CSRF protection

## Related Paths
- **Incoming**: 
  - Social account connection/disconnection events
  - User social authentication workflows
  - Account management and settings pages
  - OAuth provider integration callbacks
- **Outgoing**: 
  - SMTP email delivery system
  - User notification preferences
  - Email tracking and analytics
  - Account security monitoring
