
# WebAuthn Templates Directory

## Purpose
Contains templates for WebAuthn/FIDO2 hardware security key authentication. These templates provide interfaces for registering, managing, and authenticating with hardware security keys, biometric authenticators, and platform authenticators like Windows Hello or TouchID.

## Contents
- **snippets/**: Reusable WebAuthn UI components and JavaScript modules
- `signup_form.html`: WebAuthn registration during account signup process
- `edit_form.html`: Form to edit existing WebAuthn authenticator settings
- `base.html`: Base template for WebAuthn-related pages with required JavaScript
- `reauthenticate.html`: WebAuthn re-authentication for sensitive operations
- `authenticator_list.html`: List of registered WebAuthn devices with management options
- `authenticator_confirm_delete.html`: Confirmation page for removing WebAuthn authenticators
- `add_form.html`: Form to register new WebAuthn security keys or biometric authenticators

## Usage

### WebAuthn Registration Form
```django
<!-- add_form.html -->
{% extends "mfa/webauthn/base.html" %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h3>
                    <i class="fas fa-key"></i>
                    Add Security Key
                </h3>
            </div>
            <div class="card-body">
                <p>Add a hardware security key or use your device's built-in authenticator for enhanced security.</p>
                
                <div class="webauthn-info">
                    <h5>Supported Authenticators:</h5>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="authenticator-type">
                                <i class="fas fa-usb"></i>
                                <strong>Hardware Keys</strong>
                                <ul>
                                    <li>YubiKey 5 Series</li>
                                    <li>Google Titan Security Key</li>
                                    <li>SoloKeys</li>
                                    <li>Any FIDO2 certified key</li>
                                </ul>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="authenticator-type">
                                <i class="fas fa-fingerprint"></i>
                                <strong>Built-in Authenticators</strong>
                                <ul>
                                    <li>Windows Hello</li>
                                    <li>TouchID / FaceID</li>
                                    <li>Android Fingerprint</li>
                                    <li>Platform TPM</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                
                <form id="webauthn-form" method="post">
                    {% csrf_token %}
                    <div class="form-group">
                        <label for="id_name">Authenticator Name</label>
                        <input type="text" 
                               name="name" 
                               id="id_name" 
                               class="form-control" 
                               placeholder="e.g., My YubiKey"
                               required>
                        <small class="form-text text-muted">
                            Give your authenticator a memorable name
                        </small>
                    </div>
                    
                    <div class="registration-area">
                        <button type="button" 
                                id="register-button" 
                                class="btn btn-primary btn-lg btn-block">
                            <i class="fas fa-plus"></i>
                            Register Security Key
                        </button>
                        
                        <div id="registration-status" class="mt-3 d-none">
                            <div class="alert alert-info">
                                <i class="fas fa-spinner fa-spin"></i>
                                <span id="status-message">Preparing registration...</span>
                            </div>
                        </div>
                    </div>
                </form>
                
                <div class="browser-compatibility mt-4">
                    <h6>Browser Compatibility</h6>
                    <div id="compatibility-check">
                        <div class="compatibility-item">
                            <i class="fas fa-check text-success" id="webauthn-support"></i>
                            WebAuthn API Support
                        </div>
                        <div class="compatibility-item">
                            <i class="fas fa-check text-success" id="platform-support"></i>
                            Platform Authenticator Available
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    checkWebAuthnSupport();
    
    document.getElementById('register-button').addEventListener('click', function() {
        startWebAuthnRegistration();
    });
});

function checkWebAuthnSupport() {
    const webauthnSupport = document.getElementById('webauthn-support');
    const platformSupport = document.getElementById('platform-support');
    
    if (!window.PublicKeyCredential) {
        webauthnSupport.className = 'fas fa-times text-danger';
        document.getElementById('register-button').disabled = true;
        document.getElementById('register-button').innerHTML = 
            '<i class="fas fa-exclamation-triangle"></i> WebAuthn Not Supported';
        return;
    }
    
    // Check for platform authenticator
    PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable()
        .then(available => {
            if (!available) {
                platformSupport.className = 'fas fa-times text-warning';
            }
        });
}

async function startWebAuthnRegistration() {
    const statusDiv = document.getElementById('registration-status');
    const statusMessage = document.getElementById('status-message');
    const registerButton = document.getElementById('register-button');
    
    statusDiv.classList.remove('d-none');
    registerButton.disabled = true;
    
    try {
        // Get registration options from server
        statusMessage.textContent = 'Getting registration challenge...';
        
        const response = await fetch('{% url "webauthn_begin_registration" %}', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
        });
        
        const options = await response.json();
        
        if (!response.ok) {
            throw new Error(options.error || 'Failed to get registration options');
        }
        
        // Convert base64url to ArrayBuffer
        options.challenge = base64urlToArrayBuffer(options.challenge);
        options.user.id = base64urlToArrayBuffer(options.user.id);
        
        if (options.excludeCredentials) {
            options.excludeCredentials.forEach(cred => {
                cred.id = base64urlToArrayBuffer(cred.id);
            });
        }
        
        statusMessage.textContent = 'Please interact with your authenticator...';
        
        // Create credential
        const credential = await navigator.credentials.create({
            publicKey: options
        });
        
        statusMessage.textContent = 'Completing registration...';
        
        // Send credential to server
        const registrationResponse = await fetch('{% url "webauthn_complete_registration" %}', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                id: credential.id,
                rawId: arrayBufferToBase64url(credential.rawId),
                response: {
                    attestationObject: arrayBufferToBase64url(credential.response.attestationObject),
                    clientDataJSON: arrayBufferToBase64url(credential.response.clientDataJSON),
                },
                type: credential.type,
                name: document.getElementById('id_name').value
            })
        });
        
        const result = await registrationResponse.json();
        
        if (registrationResponse.ok) {
            statusDiv.className = 'mt-3 alert alert-success';
            statusMessage.innerHTML = '<i class="fas fa-check"></i> Security key registered successfully!';
            
            setTimeout(() => {
                window.location.href = '{% url "mfa_dashboard" %}';
            }, 2000);
        } else {
            throw new Error(result.error || 'Registration failed');
        }
        
    } catch (error) {
        statusDiv.className = 'mt-3 alert alert-danger';
        statusMessage.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${error.message}`;
        registerButton.disabled = false;
    }
}

// Base64url encoding/decoding utilities
function base64urlToArrayBuffer(base64url) {
    const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
    const padLength = (4 - (base64.length % 4)) % 4;
    const paddedBase64 = base64 + '='.repeat(padLength);
    const binaryString = window.atob(paddedBase64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
}

function arrayBufferToBase64url(buffer) {
    const bytes = new Uint8Array(buffer);
    let binaryString = '';
    for (let i = 0; i < bytes.byteLength; i++) {
        binaryString += String.fromCharCode(bytes[i]);
    }
    const base64 = window.btoa(binaryString);
    return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}
</script>
{% endblock %}
```

### Authenticator Management
```django
<!-- authenticator_list.html -->
{% extends "mfa/webauthn/base.html" %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-10">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2>Security Keys</h2>
            <a href="{% url 'webauthn_add' %}" class="btn btn-primary">
                <i class="fas fa-plus"></i> Add Security Key
            </a>
        </div>
        
        {% if authenticators %}
            <div class="authenticators-grid">
                {% for authenticator in authenticators %}
                    <div class="card mb-3">
                        <div class="card-body">
                            <div class="row align-items-center">
                                <div class="col-md-8">
                                    <h5 class="card-title">
                                        <i class="fas fa-key text-primary"></i>
                                        {{ authenticator.name }}
                                    </h5>
                                    <div class="authenticator-details">
                                        <small class="text-muted">
                                            <strong>Added:</strong> {{ authenticator.created_at|date:"F j, Y" }}
                                        </small>
                                        <br>
                                        <small class="text-muted">
                                            <strong>Last Used:</strong> 
                                            {% if authenticator.last_used_at %}
                                                {{ authenticator.last_used_at|timesince }} ago
                                            {% else %}
                                                Never
                                            {% endif %}
                                        </small>
                                        <br>
                                        <small class="text-muted">
                                            <strong>Type:</strong> 
                                            {% if authenticator.is_platform %}
                                                <span class="badge badge-info">Platform</span>
                                            {% else %}
                                                <span class="badge badge-secondary">Cross-platform</span>
                                            {% endif %}
                                        </small>
                                    </div>
                                </div>
                                <div class="col-md-4 text-right">
                                    <div class="btn-group">
                                        <a href="{% url 'webauthn_edit' authenticator.id %}" 
                                           class="btn btn-sm btn-outline-primary">
                                            <i class="fas fa-edit"></i> Edit
                                        </a>
                                        <button type="button" 
                                                class="btn btn-sm btn-outline-danger"
                                                onclick="testAuthenticator('{{ authenticator.id }}')">
                                            <i class="fas fa-vial"></i> Test
                                        </button>
                                        <a href="{% url 'webauthn_delete' authenticator.id %}" 
                                           class="btn btn-sm btn-outline-danger">
                                            <i class="fas fa-trash"></i> Remove
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                {% endfor %}
            </div>
        {% else %}
            <div class="empty-state text-center py-5">
                <i class="fas fa-key fa-3x text-muted mb-3"></i>
                <h4>No Security Keys Registered</h4>
                <p class="text-muted">Add a hardware security key or use your device's built-in authenticator for enhanced security.</p>
                <a href="{% url 'webauthn_add' %}" class="btn btn-primary">
                    <i class="fas fa-plus"></i> Add Your First Security Key
                </a>
            </div>
        {% endif %}
    </div>
</div>
{% endblock %}
```

## Container Configuration
- **Runtime**: Django with WebAuthn library and cryptographic support
- **Dependencies**: 
  - webauthn Python library for FIDO2/WebAuthn protocol
  - Cryptographic libraries for credential verification
  - Modern browser with WebAuthn API support
  - HTTPS/TLS for secure credential transmission
- **Environment**: 
  - Relying Party (RP) configuration for domain validation
  - HTTPS-only deployment for WebAuthn security requirements
  - Database storage for credential data and metadata
- **Security**: Public key cryptography, challenge-response authentication, anti-phishing protection

## Related Paths
- **Incoming**: 
  - MFA dashboard and security settings
  - User authentication and registration workflows
  - Device and browser compatibility checks
  - FIDO2/WebAuthn protocol implementations
- **Outgoing**: 
  - Hardware security key validation and verification
  - Biometric authentication systems integration
  - Platform authenticator APIs (Windows Hello, TouchID)
  - Security audit logging and credential management
