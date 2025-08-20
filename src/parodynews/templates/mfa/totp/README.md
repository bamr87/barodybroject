
# TOTP Authentication Templates Directory

## Purpose
Contains templates for Time-based One-Time Password (TOTP) authentication setup and management. These templates guide users through configuring authenticator apps like Google Authenticator, Authy, or Microsoft Authenticator for two-factor authentication.

## Contents
- `activate_form.html`: TOTP setup form with QR code and manual entry key
- `base.html`: Base template for TOTP-related pages with consistent styling
- `deactivate_form.html`: Form to disable TOTP authentication with confirmation

## Usage

### TOTP Activation Form
```django
<!-- activate_form.html -->
{% extends "mfa/totp/base.html" %}
{% load qr_code %}

{% block head_title %}Setup Authenticator App{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h3>
                    <i class="fas fa-mobile-alt"></i>
                    Setup Two-Factor Authentication
                </h3>
            </div>
            <div class="card-body">
                <div class="setup-steps">
                    <div class="step">
                        <h5>Step 1: Install an Authenticator App</h5>
                        <p>Download one of these apps on your mobile device:</p>
                        <div class="app-recommendations">
                            <div class="app-option">
                                <i class="fab fa-google"></i>
                                <strong>Google Authenticator</strong>
                                <div class="app-links">
                                    <a href="https://apps.apple.com/app/google-authenticator/id388497605" target="_blank">iOS</a>
                                    <a href="https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2" target="_blank">Android</a>
                                </div>
                            </div>
                            <div class="app-option">
                                <i class="fas fa-shield-alt"></i>
                                <strong>Authy</strong>
                                <div class="app-links">
                                    <a href="https://apps.apple.com/app/authy/id494168017" target="_blank">iOS</a>
                                    <a href="https://play.google.com/store/apps/details?id=com.authy.authy" target="_blank">Android</a>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="step">
                        <h5>Step 2: Scan QR Code or Enter Key Manually</h5>
                        <div class="setup-methods">
                            <div class="qr-method">
                                <h6>Option A: Scan QR Code</h6>
                                <div class="qr-code-container">
                                    {% qr_from_text qr_code_url size="200x200" %}
                                </div>
                                <p class="text-muted">Scan this code with your authenticator app</p>
                            </div>
                            
                            <div class="manual-method">
                                <h6>Option B: Enter Key Manually</h6>
                                <div class="manual-key">
                                    <label>Account:</label>
                                    <code>{{ user.email }}</code>
                                </div>
                                <div class="manual-key">
                                    <label>Key:</label>
                                    <div class="key-display">
                                        <code id="secret-key">{{ secret_key }}</code>
                                        <button type="button" class="btn btn-sm btn-outline-secondary" onclick="copyToClipboard('secret-key')">
                                            <i class="fas fa-copy"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="step">
                        <h5>Step 3: Verify Setup</h5>
                        <form method="post">
                            {% csrf_token %}
                            <div class="form-group">
                                <label for="id_token">Enter the 6-digit code from your app:</label>
                                <input type="text" 
                                       name="token" 
                                       id="id_token" 
                                       class="form-control form-control-lg text-center" 
                                       placeholder="000000"
                                       maxlength="6"
                                       pattern="[0-9]{6}"
                                       required
                                       autocomplete="off">
                                <small class="form-text text-muted">
                                    The code refreshes every 30 seconds
                                </small>
                            </div>
                            
                            <button type="submit" class="btn btn-primary btn-lg btn-block">
                                <i class="fas fa-check"></i>
                                Activate Two-Factor Authentication
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    const text = element.textContent;
    navigator.clipboard.writeText(text).then(() => {
        // Visual feedback
        const button = element.nextElementSibling;
        const originalContent = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i>';
        setTimeout(() => {
            button.innerHTML = originalContent;
        }, 2000);
    });
}

// Auto-focus and format TOTP input
document.getElementById('id_token').addEventListener('input', function() {
    this.value = this.value.replace(/\D/g, '');
    
    // Auto-submit when 6 digits entered
    if (this.value.length === 6) {
        this.form.submit();
    }
});
</script>
{% endblock %}
```

### TOTP Deactivation Form
```django
<!-- deactivate_form.html -->
{% extends "mfa/totp/base.html" %}

{% block head_title %}Disable Two-Factor Authentication{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card border-warning">
            <div class="card-header bg-warning text-dark">
                <h3>
                    <i class="fas fa-exclamation-triangle"></i>
                    Disable Two-Factor Authentication
                </h3>
            </div>
            <div class="card-body">
                <div class="alert alert-warning">
                    <strong>Security Warning:</strong>
                    <p>Disabling two-factor authentication will reduce your account security. You will no longer need your authenticator app to sign in.</p>
                </div>
                
                <h5>Confirm Deactivation</h5>
                <p>To disable two-factor authentication, please:</p>
                
                <form method="post">
                    {% csrf_token %}
                    
                    <div class="form-group">
                        <label for="id_password">Enter your password:</label>
                        <input type="password" 
                               name="password" 
                               id="id_password" 
                               class="form-control" 
                               required>
                    </div>
                    
                    <div class="form-group">
                        <label for="id_token">Enter current 6-digit code:</label>
                        <input type="text" 
                               name="token" 
                               id="id_token" 
                               class="form-control" 
                               placeholder="000000"
                               maxlength="6"
                               pattern="[0-9]{6}"
                               required>
                        <small class="form-text text-muted">
                            Code from your authenticator app
                        </small>
                    </div>
                    
                    <div class="form-check mb-3">
                        <input type="checkbox" 
                               class="form-check-input" 
                               id="id_confirm" 
                               name="confirm"
                               required>
                        <label class="form-check-label" for="id_confirm">
                            I understand that disabling two-factor authentication reduces my account security
                        </label>
                    </div>
                    
                    <div class="button-group">
                        <button type="submit" class="btn btn-danger">
                            <i class="fas fa-times"></i>
                            Disable Two-Factor Authentication
                        </button>
                        <a href="{% url 'mfa_dashboard' %}" class="btn btn-secondary">
                            Cancel
                        </a>
                    </div>
                </form>
            </div>
        </div>
        
        <div class="mt-3">
            <div class="card">
                <div class="card-body">
                    <h6>Alternative Security Options</h6>
                    <p>Instead of disabling, consider:</p>
                    <ul>
                        <li>Adding a backup security key</li>
                        <li>Generating recovery codes</li>
                        <li>Setting up email-based authentication</li>
                    </ul>
                    <a href="{% url 'mfa_dashboard' %}" class="btn btn-outline-primary btn-sm">
                        Explore Security Options
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### TOTP Base Template
```django
<!-- base.html -->
{% extends "mfa/base_manage.html" %}
{% load static %}

{% block extra_head %}
{{ block.super }}
<link rel="stylesheet" href="{% static 'css/mfa-totp.css' %}">
<style>
.setup-steps .step {
    margin-bottom: 2rem;
    padding: 1.5rem;
    border: 1px solid #dee2e6;
    border-radius: 0.5rem;
}

.setup-steps .step h5 {
    color: #007bff;
    margin-bottom: 1rem;
}

.app-recommendations {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}

.app-option {
    flex: 1;
    min-width: 200px;
    padding: 1rem;
    border: 1px solid #e9ecef;
    border-radius: 0.375rem;
    text-align: center;
}

.app-option i {
    font-size: 2rem;
    color: #007bff;
    margin-bottom: 0.5rem;
}

.app-links a {
    display: inline-block;
    margin: 0 0.5rem;
    padding: 0.25rem 0.5rem;
    background-color: #f8f9fa;
    border-radius: 0.25rem;
    text-decoration: none;
    color: #495057;
    font-size: 0.875rem;
}

.setup-methods {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    margin: 1rem 0;
}

.qr-code-container {
    text-align: center;
    padding: 1rem;
    background-color: #f8f9fa;
    border-radius: 0.5rem;
}

.manual-key {
    margin-bottom: 1rem;
}

.key-display {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.key-display code {
    flex: 1;
    padding: 0.5rem;
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 0.375rem;
    font-family: 'Courier New', monospace;
    letter-spacing: 2px;
}

@media (max-width: 768px) {
    .setup-methods {
        grid-template-columns: 1fr;
    }
    
    .app-recommendations {
        flex-direction: column;
    }
}
</style>
{% endblock %}

{% block breadcrumb %}
{{ block.super }}
<li class="breadcrumb-item">
    <a href="{% url 'mfa_dashboard' %}">Security</a>
</li>
<li class="breadcrumb-item active">
    Authenticator App
</li>
{% endblock %}
```

### TOTP Management Logic
```python
# In Django views for TOTP management
import pyotp
import qrcode
from io import BytesIO
import base64

def setup_totp(request):
    """Setup TOTP for user"""
    if request.method == 'POST':
        token = request.POST.get('token')
        secret = request.session.get('totp_secret')
        
        if pyotp.TOTP(secret).verify(token, valid_window=1):
            # Save TOTP device
            device = request.user.totpdevice_set.create(
                name='Authenticator App',
                secret=secret
            )
            messages.success(request, 'Two-factor authentication has been successfully activated.')
            return redirect('mfa_dashboard')
        else:
            messages.error(request, 'Invalid code. Please try again.')
    
    # Generate new secret for setup
    secret = pyotp.random_base32()
    request.session['totp_secret'] = secret
    
    # Generate QR code
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=request.user.email,
        issuer_name='Barody Broject'
    )
    
    return render(request, 'mfa/totp/activate_form.html', {
        'secret_key': secret,
        'qr_code_url': totp_uri,
    })
```

## Container Configuration
- **Runtime**: Django with TOTP cryptographic libraries
- **Dependencies**: 
  - pyotp for TOTP generation and verification
  - qrcode library for QR code generation
  - PIL/Pillow for image processing
  - django-qr-code for template integration
- **Environment**: 
  - Secret key management for TOTP seeds
  - Session storage for setup workflows
  - Time synchronization for accurate TOTP validation
- **Security**: Secure random number generation, time-based validation windows

## Related Paths
- **Incoming**: 
  - MFA dashboard and security settings
  - User authentication and setup workflows
  - Account verification and re-authentication
  - Mobile authenticator app integration
- **Outgoing**: 
  - TOTP token validation and verification
  - User session management and authentication state
  - Security audit logging and monitoring
  - Backup recovery code generation
