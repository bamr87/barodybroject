
# WebAuthn Snippets Directory

## Purpose
Contains reusable WebAuthn/FIDO2 template components and JavaScript modules for security key authentication. These snippets provide modular UI elements and functionality that can be included across multiple WebAuthn-related pages.

## Contents
- `scripts.html`: Core WebAuthn JavaScript utilities and helper functions
- `login_script.html`: WebAuthn authentication flow JavaScript for login pages

## Usage

### Core WebAuthn Scripts
```django
<!-- scripts.html -->
<script>
// Core WebAuthn utility functions
class WebAuthnHelper {
    static base64urlToArrayBuffer(base64url) {
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
    
    static arrayBufferToBase64url(buffer) {
        const bytes = new Uint8Array(buffer);
        let binaryString = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binaryString += String.fromCharCode(bytes[i]);
        }
        const base64 = window.btoa(binaryString);
        return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
    }
    
    static async isSupported() {
        return window.PublicKeyCredential && 
               await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
    }
}

// Global WebAuthn event handlers
window.webauthnHelper = WebAuthnHelper;
</script>
```

### Login Authentication Script
```django
<!-- login_script.html -->
<script>
async function authenticateWithWebAuthn() {
    try {
        // Get authentication options from server
        const response = await fetch('{% url "webauthn_begin_auth" %}', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
        });
        
        const options = await response.json();
        
        if (!response.ok) {
            throw new Error(options.error || 'Failed to get authentication options');
        }
        
        // Convert base64url to ArrayBuffer
        options.challenge = WebAuthnHelper.base64urlToArrayBuffer(options.challenge);
        
        if (options.allowCredentials) {
            options.allowCredentials.forEach(cred => {
                cred.id = WebAuthnHelper.base64urlToArrayBuffer(cred.id);
            });
        }
        
        // Get credential from authenticator
        const credential = await navigator.credentials.get({
            publicKey: options
        });
        
        // Send credential to server for verification
        const authResponse = await fetch('{% url "webauthn_complete_auth" %}', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                id: credential.id,
                rawId: WebAuthnHelper.arrayBufferToBase64url(credential.rawId),
                response: {
                    authenticatorData: WebAuthnHelper.arrayBufferToBase64url(credential.response.authenticatorData),
                    clientDataJSON: WebAuthnHelper.arrayBufferToBase64url(credential.response.clientDataJSON),
                    signature: WebAuthnHelper.arrayBufferToBase64url(credential.response.signature),
                    userHandle: credential.response.userHandle ? 
                        WebAuthnHelper.arrayBufferToBase64url(credential.response.userHandle) : null
                },
                type: credential.type
            })
        });
        
        const result = await authResponse.json();
        
        if (authResponse.ok) {
            // Redirect on successful authentication
            window.location.href = result.redirect_url || '{% url "dashboard" %}';
        } else {
            throw new Error(result.error || 'Authentication failed');
        }
        
    } catch (error) {
        console.error('WebAuthn authentication failed:', error);
        alert('Security key authentication failed: ' + error.message);
    }
}

// Add event listeners when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const webauthnButtons = document.querySelectorAll('.btn-webauthn');
    webauthnButtons.forEach(button => {
        button.addEventListener('click', authenticateWithWebAuthn);
    });
});
</script>
```

## Container Configuration
- **Runtime**: WebAuthn JavaScript API integration
- **Dependencies**: 
  - Modern browser with FIDO2/WebAuthn support
  - HTTPS/TLS for secure credential transmission
  - Base64url encoding/decoding utilities
- **Environment**: HTTPS-only for security requirements
- **Security**: Cross-origin and anti-phishing protections

## Related Paths
- **Incoming**: 
  - WebAuthn authentication workflows and security pages
  - Login and registration forms requiring security key authentication
  - MFA setup and management interfaces
- **Outgoing**: 
  - Security key verification and credential management
  - Authentication state management and session creation
  - User authentication success/failure handling
