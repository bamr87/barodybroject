
# Account Email Templates Directory

## Purpose
Contains email template files for Django allauth account-related email notifications. These templates define the subject lines and message content for automated emails sent during user registration, password management, email verification, and other account operations.

## Contents

### Email Verification Templates
- `email_confirmation_signup_message.txt`: Welcome email content for new user email verification
- `email_confirmation_signup_subject.txt`: Subject line for signup email confirmation
- `email_confirmation_message.txt`: Standard email verification message content
- `email_confirmation_subject.txt`: Subject line for email verification
- `email_confirmation_message.html`: HTML version of email confirmation message
- `email_confirm_message.txt`: Alternative email confirmation content
- `email_confirm_subject.txt`: Alternative email confirmation subject

### Password Management Templates
- `password_reset_key_message.txt`: Password reset email with secure reset link
- `password_reset_key_subject.txt`: Subject line for password reset emails
- `password_reset_message.txt`: General password reset notification
- `password_reset_subject.txt`: Subject line for password reset notifications
- `password_changed_message.txt`: Notification when password is successfully changed
- `password_changed_subject.txt`: Subject line for password change confirmation
- `password_set_message.txt`: Notification when password is initially set
- `password_set_subject.txt`: Subject line for password set confirmation

### Account Management Templates
- `account_already_exists_message.txt`: Message when attempting to create duplicate account
- `account_already_exists_subject.txt`: Subject for duplicate account notifications
- `email_deleted_message.txt`: Notification when email address is removed
- `email_deleted_subject.txt`: Subject line for email deletion notifications
- `email_changed_message.txt`: Notification when primary email is changed
- `email_changed_subject.txt`: Subject line for email change notifications

### Authentication Templates
- `login_code_message.txt`: Message containing temporary login code
- `login_code_subject.txt`: Subject line for login code emails
- `unknown_account_message.txt`: Response for password reset on non-existent accounts
- `unknown_account_subject.txt`: Subject for unknown account notifications

### Base Templates
- `base_message.txt`: Base template for common email formatting
- `base_notification.txt`: Base template for notification-style emails

## Usage

### Email Template Configuration
```python
# In Django settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'Barody Broject <noreply@barodybroject.com>'

# Allauth email settings
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
```

### Custom Email Template Example
```text
# password_reset_key_message.txt
Hello {{ user.get_full_name|default:user.username }},

You requested a password reset for your Barody Broject account.

Click the link below to reset your password:
{{ password_reset_url }}

This link will expire in 24 hours.

If you didn't request this reset, please ignore this email.

Best regards,
The Barody Broject Team
```

### HTML Email Template
```html
<!-- email_confirmation_message.html -->
<html>
<head>
    <title>Confirm Your Email - Barody Broject</title>
</head>
<body>
    <h2>Welcome to Barody Broject!</h2>
    <p>Hello {{ user.get_full_name|default:user.username }},</p>
    
    <p>Please confirm your email address by clicking the link below:</p>
    <a href="{{ activate_url }}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
        Confirm Email Address
    </a>
    
    <p>If the button doesn't work, copy and paste this link into your browser:</p>
    <p>{{ activate_url }}</p>
</body>
</html>
```

## Container Configuration
- **Runtime**: Django email backend integration
- **Dependencies**: 
  - SMTP server configuration
  - Django allauth email settings
  - Template rendering engine
- **Environment Variables**:
  - `EMAIL_HOST`: SMTP server hostname
  - `EMAIL_PORT`: SMTP server port
  - `EMAIL_USE_TLS`: Enable TLS encryption
  - `DEFAULT_FROM_EMAIL`: Sender email address
- **Assets**: HTML email styling, inline CSS support

## Related Paths
- **Incoming**: 
  - Django allauth authentication workflows
  - User registration and login views
  - Password reset and email management views
  - Account settings and profile updates
- **Outgoing**: 
  - SMTP email delivery system
  - Email tracking and analytics
  - User notification preferences
  - Email bounce and unsubscribe handling
