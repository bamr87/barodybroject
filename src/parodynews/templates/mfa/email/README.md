
# MFA Email Templates Directory

## Purpose
Contains email notification templates for multi-factor authentication events. These templates provide security notifications when users make changes to their MFA settings, ensuring users are informed of important security changes to their accounts.

## Contents
- `webauthn_added_subject.txt`: Subject line for WebAuthn security key addition notifications
- `webauthn_added_message.txt`: Email content when security key is added to account
- `totp_deactivated_message.txt`: Email content when TOTP authenticator is disabled
- `recovery_codes_generated_message.txt`: Email content when new recovery codes are generated
- `totp_activated_subject.txt`: Subject line for TOTP authenticator activation notifications
- `totp_deactivated_subject.txt`: Subject line for TOTP authenticator deactivation notifications
- `recovery_codes_generated_subject.txt`: Subject line for recovery code generation notifications
- `totp_activated_message.txt`: Email content when TOTP authenticator is enabled
- `webauthn_removed_message.txt`: Email content when security key is removed from account
- `webauthn_removed_subject.txt`: Subject line for WebAuthn security key removal notifications

## Usage

### TOTP Authentication Email Templates
```text
# totp_activated_subject.txt
Security Update - Two-Factor Authentication Enabled

# totp_activated_message.txt
Hello {{ user.get_full_name|default:user.username }},

Two-factor authentication using an authenticator app has been successfully enabled on your Barody Broject account.

Security Details:
- Authentication Method: TOTP (Time-based One-Time Password)
- Activated On: {{ activation_date|date:"F j, Y \a\t g:i A T" }}
- Device/Browser: {{ user_agent }}
- IP Address: {{ ip_address }}

Your account is now more secure with two-factor authentication. You'll need your authenticator app to sign in from now on.

Important Security Tips:
- Keep your device with the authenticator app secure
- Consider generating backup recovery codes
- Contact support if you lose access to your authenticator

If you did not enable this feature, please contact our security team immediately.

Manage Security Settings: {{ security_settings_url }}

Best regards,
Barody Broject Security Team
```

### WebAuthn Security Key Email Templates
```text
# webauthn_added_subject.txt
Security Key Added to Your Account

# webauthn_added_message.txt
Hello {{ user.get_full_name|default:user.username }},

A new security key has been successfully added to your Barody Broject account.

Security Key Details:
- Key Name: {{ key_name }}
- Added On: {{ addition_date|date:"F j, Y \a\t g:i A T" }}
- Key Type: {{ key_type|default:"Hardware Security Key" }}
- Browser: {{ user_agent }}
- IP Address: {{ ip_address }}

You can now use this security key to sign in to your account for enhanced security.

Security Key Benefits:
- Phishing-resistant authentication
- Works across devices and platforms
- No need to enter codes manually
- Hardware-backed security

If you did not add this security key, please:
1. Log into your account immediately
2. Remove the unauthorized key
3. Review your security settings
4. Contact our support team

Manage Security Keys: {{ security_settings_url }}

Stay secure,
Barody Broject Security Team
```

### Recovery Codes Email Template
```text
# recovery_codes_generated_subject.txt
New Recovery Codes Generated for Your Account

# recovery_codes_generated_message.txt
Hello {{ user.get_full_name|default:user.username }},

New backup recovery codes have been generated for your Barody Broject account.

Generation Details:
- Generated On: {{ generation_date|date:"F j, Y \a\t g:i A T" }}
- Number of Codes: {{ code_count }}
- Browser: {{ user_agent }}
- IP Address: {{ ip_address }}

Important Information:
- Previous recovery codes are now invalid
- Each new code can only be used once
- Store these codes in a secure location
- Use recovery codes when other MFA methods are unavailable

Security Recommendations:
- Save codes in a password manager
- Print codes and store in a safe place
- Don't store codes on the same device as your authenticator
- Generate new codes if you suspect they've been compromised

If you did not generate these recovery codes, please secure your account immediately.

View Recovery Codes: {{ recovery_codes_url }}

Best regards,
Barody Broject Security Team
```

### Email Configuration
```python
# In Django views for sending MFA notifications
from django.core.mail import send_mail
from django.template.loader import render_to_string

def send_mfa_notification(user, event_type, context):
    """Send MFA-related email notification"""
    
    email_templates = {
        'totp_activated': {
            'subject': 'mfa/email/totp_activated_subject.txt',
            'message': 'mfa/email/totp_activated_message.txt',
        },
        'webauthn_added': {
            'subject': 'mfa/email/webauthn_added_subject.txt',
            'message': 'mfa/email/webauthn_added_message.txt',
        },
        'recovery_codes_generated': {
            'subject': 'mfa/email/recovery_codes_generated_subject.txt',
            'message': 'mfa/email/recovery_codes_generated_message.txt',
        },
    }
    
    templates = email_templates.get(event_type)
    if not templates:
        return
    
    # Prepare email context
    email_context = {
        'user': user,
        'site_url': settings.SITE_URL,
        'security_settings_url': f"{settings.SITE_URL}/accounts/security/",
        'support_email': settings.SUPPORT_EMAIL,
        **context
    }
    
    # Render email content
    subject = render_to_string(templates['subject'], email_context).strip()
    message = render_to_string(templates['message'], email_context)
    
    # Send email
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.SECURITY_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )
```

## Container Configuration
- **Runtime**: Django email backend with MFA event integration
- **Dependencies**: 
  - Django email system and SMTP configuration
  - MFA event tracking and logging
  - Template rendering with security context
- **Environment**: 
  - Email delivery configuration
  - Security monitoring and alerting systems
  - User notification preferences
- **Security**: Security event notifications, audit logging, user awareness

## Related Paths
- **Incoming**: 
  - MFA activation and deactivation events
  - Security key registration and removal
  - Recovery code generation workflows
  - Account security changes and updates
- **Outgoing**: 
  - Email delivery and notification systems
  - Security monitoring and audit trails
  - User security awareness and education
  - Support and incident response workflows
