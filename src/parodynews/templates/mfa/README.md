
# Multi-Factor Authentication (MFA) Templates Directory

## Purpose
Contains Django allauth MFA templates for implementing multi-factor authentication including TOTP (Time-based One-Time Passwords), WebAuthn (hardware keys), email-based authentication, and recovery codes. These templates provide a comprehensive security framework for user account protection.

## Contents
- **recovery_codes/**: Backup recovery code management templates
- **messages/**: MFA-related user notification messages
- **webauthn/**: WebAuthn/FIDO2 hardware key authentication templates
- **totp/**: TOTP authenticator app setup and verification templates
- **email/**: Email-based two-factor authentication templates
- `index.html`: MFA management dashboard and settings overview
- `base_entrance.html`: Base template for MFA authentication entry points
- `reauthenticate.html`: Re-authentication page for sensitive operations
- `base_manage.html`: Base template for MFA management interfaces
- `authenticate.html`: Multi-factor authentication challenge page

## Usage

### MFA Dashboard Integration
```django
<!-- index.html -->
{% extends "mfa/base_manage.html" %}
{% load mfa %}

{% block head_title %}Security Settings{% endblock %}

{% block content %}
<div class="mfa-dashboard">
    <h2>Multi-Factor Authentication</h2>
    <p class="lead">Secure your account with additional authentication methods.</p>
    
    <div class="security-overview">
        <div class="security-status">
            {% if user.mfa_methods.exists %}
                <div class="alert alert-success">
                    <i class="fas fa-shield-alt"></i>
                    <strong>Protected</strong> - MFA is enabled on your account
                </div>
            {% else %}
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle"></i>
                    <strong>Vulnerable</strong> - Enable MFA to secure your account
                </div>
            {% endif %}
        </div>
        
        <div class="mfa-methods">
            <h4>Available Methods</h4>
            
            <!-- TOTP Authenticator Apps -->
            <div class="method-card">
                <div class="method-icon">
                    <i class="fas fa-mobile-alt"></i>
                </div>
                <div class="method-info">
                    <h5>Authenticator App</h5>
                    <p>Use Google Authenticator, Authy, or similar apps</p>
                    {% if user.totp_devices.exists %}
                        <span class="badge badge-success">Enabled</span>
                        <a href="{% url 'mfa_totp_remove' %}" class="btn btn-sm btn-outline-danger">Remove</a>
                    {% else %}
                        <a href="{% url 'mfa_totp_setup' %}" class="btn btn-sm btn-primary">Setup</a>
                    {% endif %}
                </div>
            </div>
            
            <!-- WebAuthn Hardware Keys -->
            <div class="method-card">
                <div class="method-icon">
                    <i class="fas fa-key"></i>
                </div>
                <div class="method-info">
                    <h5>Security Key</h5>
                    <p>YubiKey, Windows Hello, TouchID, or other FIDO2 devices</p>
                    {% get_webauthn_keys user as webauthn_keys %}
                    {% if webauthn_keys %}
                        <span class="badge badge-success">{{ webauthn_keys|length }} key(s)</span>
                        <a href="{% url 'mfa_webauthn_manage' %}" class="btn btn-sm btn-outline-primary">Manage</a>
                    {% else %}
                        <a href="{% url 'mfa_webauthn_add' %}" class="btn btn-sm btn-primary">Add Key</a>
                    {% endif %}
                </div>
            </div>
            
            <!-- Recovery Codes -->
            <div class="method-card">
                <div class="method-icon">
                    <i class="fas fa-list-ol"></i>
                </div>
                <div class="method-info">
                    <h5>Recovery Codes</h5>
                    <p>Backup codes for when other methods aren't available</p>
                    {% if user.recovery_codes.exists %}
                        <span class="badge badge-info">Generated</span>
                        <a href="{% url 'mfa_recovery_codes_view' %}" class="btn btn-sm btn-outline-info">View</a>
                    {% else %}
                        <a href="{% url 'mfa_recovery_codes_generate' %}" class="btn btn-sm btn-secondary">Generate</a>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### MFA Authentication Challenge
```django
<!-- authenticate.html -->
{% extends "mfa/base_entrance.html" %}
{% load mfa %}

{% block head_title %}Two-Factor Authentication Required{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h3>
                    <i class="fas fa-shield-alt"></i>
                    Two-Factor Authentication
                </h3>
            </div>
            <div class="card-body">
                <p>Please verify your identity using one of your configured methods:</p>
                
                {% get_available_methods user as methods %}
                <div class="mfa-methods-list">
                    {% for method in methods %}
                        <div class="mfa-method-option">
                            <form method="post" action="{% url 'mfa_authenticate' method.id %}">
                                {% csrf_token %}
                                
                                {% if method.type == 'totp' %}
                                    <button type="submit" class="btn btn-outline-primary btn-block">
                                        <i class="fas fa-mobile-alt"></i>
                                        Use Authenticator App
                                    </button>
                                {% elif method.type == 'webauthn' %}
                                    <button type="submit" class="btn btn-outline-success btn-block">
                                        <i class="fas fa-key"></i>
                                        Use Security Key
                                    </button>
                                {% elif method.type == 'email' %}
                                    <button type="submit" class="btn btn-outline-info btn-block">
                                        <i class="fas fa-envelope"></i>
                                        Send Email Code
                                    </button>
                                {% endif %}
                            </form>
                        </div>
                    {% endfor %}
                </div>
                
                <hr>
                <div class="text-center">
                    <a href="{% url 'mfa_recovery_codes_use' %}" class="btn btn-link btn-sm">
                        Use Recovery Code Instead
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Re-authentication for Sensitive Operations
```django
<!-- reauthenticate.html -->
{% extends "mfa/base_entrance.html" %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="alert alert-info">
            <h4>Security Verification Required</h4>
            <p>This action requires additional verification to protect your account.</p>
        </div>
        
        <div class="card">
            <div class="card-body">
                <form method="post">
                    {% csrf_token %}
                    
                    <div class="form-group">
                        <label for="id_password">Confirm Your Password</label>
                        <input type="password" 
                               name="password" 
                               id="id_password" 
                               class="form-control" 
                               required>
                    </div>
                    
                    {% if user.mfa_methods.exists %}
                        <div class="form-group">
                            <label for="id_mfa_code">Two-Factor Code</label>
                            <input type="text" 
                                   name="mfa_code" 
                                   id="id_mfa_code" 
                                   class="form-control" 
                                   placeholder="000000"
                                   required>
                            <small class="form-text text-muted">
                                Enter code from your authenticator app
                            </small>
                        </div>
                    {% endif %}
                    
                    <button type="submit" class="btn btn-primary btn-block">
                        Verify and Continue
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### MFA Settings Configuration
```python
# In Django settings.py
MFA_TOTP_ISSUER = 'Barody Broject'
MFA_RECOVERY_CODE_COUNT = 10
MFA_FORMS = {
    'authenticate': 'myapp.forms.MFAAuthenticateForm',
    'setup_totp': 'myapp.forms.TOTPSetupForm',
}

# WebAuthn configuration
MFA_WEBAUTHN = {
    'RP_ID': 'barodybroject.com',
    'RP_NAME': 'Barody Broject',
}
```

### JavaScript MFA Enhancements
```javascript
// MFA user interface enhancements
document.addEventListener('DOMContentLoaded', function() {
    // Auto-focus on MFA code input
    const mfaInput = document.getElementById('id_mfa_code');
    if (mfaInput) {
        mfaInput.focus();
        
        // Auto-submit when 6 digits entered
        mfaInput.addEventListener('input', function() {
            if (this.value.length === 6 && /^\d{6}$/.test(this.value)) {
                this.form.submit();
            }
        });
    }
    
    // WebAuthn support detection
    if (!window.PublicKeyCredential) {
        document.querySelectorAll('.webauthn-method').forEach(el => {
            el.style.display = 'none';
        });
    }
    
    // Copy recovery codes functionality
    document.getElementById('copy-recovery-codes')?.addEventListener('click', function() {
        const codes = document.getElementById('recovery-codes-list').textContent;
        navigator.clipboard.writeText(codes).then(() => {
            this.textContent = 'Copied!';
            setTimeout(() => {
                this.textContent = 'Copy Codes';
            }, 2000);
        });
    });
});
```

## Container Configuration
- **Runtime**: Django allauth MFA framework with cryptographic libraries
- **Dependencies**: 
  - django-allauth[mfa] with MFA support
  - pyotp for TOTP generation
  - webauthn library for FIDO2 support
  - qrcode library for QR code generation
- **Environment Variables**:
  - `MFA_TOTP_ISSUER`: Application name for authenticator apps
  - `MFA_RECOVERY_CODE_COUNT`: Number of backup codes to generate
  - `SECRET_KEY`: Django secret for cryptographic operations
- **Security**: CSRF protection, rate limiting, secure random generation

## Related Paths
- **Incoming**: 
  - User authentication and login workflows
  - Account security settings and management
  - Sensitive operation triggers (password change, etc.)
  - Administrative account access
- **Outgoing**: 
  - Cryptographic token generation and validation
  - WebAuthn credential management
  - Email notification systems
  - Security audit logging and monitoring
