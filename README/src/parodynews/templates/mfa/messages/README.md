
# MFA Messages Directory

## Purpose
Contains user notification messages for multi-factor authentication events. These text templates provide clear feedback to users when they activate, deactivate, or modify their MFA settings, ensuring users understand the security implications of their actions.

## Contents
- `totp_activated.txt`: Success message when TOTP authenticator is successfully set up
- `webauthn_removed.txt`: Confirmation message when WebAuthn security key is removed
- `recovery_codes_generated.txt`: Notification when new backup recovery codes are created
- `webauthn_added.txt`: Success message when WebAuthn security key is added
- `totp_deactivated.txt`: Confirmation message when TOTP authenticator is disabled

## Usage

### MFA Message Templates
```text
# totp_activated.txt
Two-factor authentication has been successfully activated using your authenticator app. Your account is now more secure. Keep your device safe and consider generating recovery codes as a backup.

# totp_deactivated.txt
Two-factor authentication has been disabled. Your account security has been reduced. We recommend re-enabling MFA to protect your account from unauthorized access.

# webauthn_added.txt
Security key has been successfully registered to your account. You can now use this hardware key for secure authentication. Remember to keep your key in a safe place.

# webauthn_removed.txt
Security key has been removed from your account. If you have no other MFA methods enabled, your account security may be reduced. Consider adding another authentication method.

# recovery_codes_generated.txt
New recovery codes have been generated for your account. Save these codes in a secure location - they can be used to access your account if other MFA methods are unavailable. Previous recovery codes are no longer valid.
```

### Message Display Integration
```django
<!-- In MFA setup/management templates -->
{% if messages %}
    <div class="mfa-messages">
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
                {% if message.tags == 'success' %}
                    <i class="fas fa-check-circle"></i>
                {% elif message.tags == 'warning' %}
                    <i class="fas fa-exclamation-triangle"></i>
                {% elif message.tags == 'error' %}
                    <i class="fas fa-times-circle"></i>
                {% else %}
                    <i class="fas fa-info-circle"></i>
                {% endif %}
                
                <strong>Security Update:</strong> {{ message }}
                
                <button type="button" class="close" data-dismiss="alert">
                    <span>&times;</span>
                </button>
            </div>
        {% endfor %}
    </div>
{% endif %}
```

### Django View Integration
```python
# In MFA management views
from django.contrib import messages

def activate_totp(request):
    # TOTP activation logic
    if totp_device.activate():
        messages.success(request, 'Two-factor authentication has been successfully activated using your authenticator app. Your account is now more secure.')
        return redirect('mfa_dashboard')

def add_webauthn_key(request):
    # WebAuthn key registration logic
    if credential.save():
        messages.success(request, 'Security key has been successfully registered to your account. You can now use this hardware key for secure authentication.')
        return redirect('mfa_webauthn_manage')

def generate_recovery_codes(request):
    # Recovery code generation logic
    codes = user.generate_recovery_codes()
    messages.info(request, 'New recovery codes have been generated for your account. Save these codes in a secure location.')
    return render(request, 'mfa/recovery_codes/view.html', {'codes': codes})
```

### Custom Message Categories
```python
# Custom message tags for MFA operations
from django.contrib.messages import constants as messages

# In Django settings.py
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
    50: 'security',  # Custom security message level
}

# Usage in views
messages.add_message(request, 50, 'Critical security setting changed. Please review your account immediately.')
```

### JavaScript Message Enhancements
```javascript
// Enhanced MFA message handling
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide info messages after delay
    setTimeout(() => {
        document.querySelectorAll('.alert-info').forEach(alert => {
            alert.classList.add('fade-out');
            setTimeout(() => alert.remove(), 500);
        });
    }, 10000);
    
    // Emphasize security-related messages
    document.querySelectorAll('.alert').forEach(alert => {
        if (alert.textContent.toLowerCase().includes('security')) {
            alert.classList.add('security-message');
            
            // Add security icon animation
            const icon = alert.querySelector('i');
            if (icon) {
                icon.classList.add('pulse-animation');
            }
        }
    });
    
    // Track MFA message interactions
    document.querySelectorAll('.mfa-messages .alert').forEach(alert => {
        alert.addEventListener('click', function() {
            gtag('event', 'mfa_message_interaction', {
                'message_type': this.classList.contains('alert-success') ? 'success' : 'info',
                'mfa_action': 'message_acknowledged'
            });
        });
    });
});
```

### Localization Support
```text
# For internationalization
# locale/en/LC_MESSAGES/django.po

msgid "totp_activated"
msgstr "Two-factor authentication has been successfully activated using your authenticator app."

msgid "webauthn_added"
msgstr "Security key has been successfully registered to your account."

# locale/es/LC_MESSAGES/django.po
msgid "totp_activated"
msgstr "La autenticación de dos factores se ha activado exitosamente usando tu aplicación autenticadora."

msgid "webauthn_added"
msgstr "La llave de seguridad se ha registrado exitosamente en tu cuenta."
```

### Email Notification Integration
```python
# Send email notifications for critical MFA changes
from django.core.mail import send_mail

def notify_mfa_change(user, action, method):
    """Send email notification for MFA changes"""
    
    subject_map = {
        'activated': f'Two-Factor Authentication Enabled - {method}',
        'deactivated': f'Two-Factor Authentication Disabled - {method}',
        'added': f'New Security Method Added - {method}',
        'removed': f'Security Method Removed - {method}',
    }
    
    message = f"""
    Hello {user.get_full_name() or user.username},
    
    A security setting on your Barody Broject account has been changed:
    
    Action: {action.title()}
    Method: {method}
    Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
    IP Address: {get_client_ip(request)}
    
    If you did not make this change, please contact support immediately.
    
    Best regards,
    Barody Broject Security Team
    """
    
    send_mail(
        subject=subject_map.get(action, 'Security Setting Changed'),
        message=message,
        from_email=settings.SECURITY_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )
```

## Container Configuration
- **Runtime**: Django message framework with MFA integration
- **Dependencies**: 
  - Django allauth MFA system
  - Message display templates
  - Bootstrap alert styling
  - FontAwesome icons for message types
- **Environment**: Integrated with Django settings and user sessions
- **Localization**: Supports multiple languages through Django i18n

## Related Paths
- **Incoming**: 
  - MFA setup and configuration workflows
  - Security key registration and removal
  - TOTP authenticator activation/deactivation
  - Recovery code generation and usage
- **Outgoing**: 
  - User interface message display
  - Email notification systems
  - Security audit logging
  - User dashboard and settings pages
