
# MFA Recovery Codes Templates Directory

## Purpose
Contains templates for managing MFA backup recovery codes. These templates allow users to generate, view, download, and use one-time recovery codes that serve as backup authentication when other MFA methods are unavailable.

## Contents
- `index.html`: Recovery codes display and management interface
- `base.html`: Base template for recovery code pages
- `download.txt`: Plain text template for downloadable recovery codes file
- `generate.html`: Recovery code generation confirmation and display

## Usage

### Recovery Codes Display
```django
<!-- index.html -->
{% extends "mfa/recovery_codes/base.html" %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="alert alert-warning">
            <i class="fas fa-exclamation-triangle"></i>
            <strong>Important:</strong> Save these recovery codes in a secure location. 
            Each code can only be used once.
        </div>
        
        <div class="card">
            <div class="card-header">
                <h3>Your Recovery Codes</h3>
                <small class="text-muted">Generated on {{ codes.created_at|date:"F j, Y" }}</small>
            </div>
            <div class="card-body">
                <div class="recovery-codes-container">
                    <div class="codes-grid">
                        {% for code in recovery_codes %}
                            <div class="recovery-code {% if code.used %}used{% endif %}">
                                <code>{{ code.code }}</code>
                                {% if code.used %}
                                    <small class="used-date">Used {{ code.used_at|date:"M j" }}</small>
                                {% endif %}
                            </div>
                        {% endfor %}
                    </div>
                </div>
                
                <div class="codes-actions mt-4">
                    <button type="button" class="btn btn-primary" onclick="printCodes()">
                        <i class="fas fa-print"></i> Print Codes
                    </button>
                    
                    <button type="button" class="btn btn-outline-secondary" onclick="copyCodes()">
                        <i class="fas fa-copy"></i> Copy to Clipboard
                    </button>
                    
                    <a href="{% url 'mfa_recovery_codes_download' %}" class="btn btn-outline-info">
                        <i class="fas fa-download"></i> Download
                    </a>
                    
                    <form method="post" action="{% url 'mfa_recovery_codes_regenerate' %}" 
                          class="d-inline" onsubmit="return confirm('Generate new codes? Current codes will be invalidated.')">
                        {% csrf_token %}
                        <button type="submit" class="btn btn-outline-warning">
                            <i class="fas fa-sync"></i> Generate New Codes
                        </button>
                    </form>
                </div>
                
                <div class="usage-stats mt-3">
                    <small class="text-muted">
                        {{ codes_used_count }} of {{ total_codes_count }} codes used
                    </small>
                </div>
            </div>
        </div>
        
        <div class="card mt-3">
            <div class="card-body">
                <h5>How to Use Recovery Codes</h5>
                <ol>
                    <li>When prompted for two-factor authentication, click "Use recovery code"</li>
                    <li>Enter one of your unused recovery codes</li>
                    <li>The code will be marked as used and cannot be used again</li>
                    <li>Generate new codes when you have few remaining</li>
                </ol>
                
                <div class="alert alert-info mt-3">
                    <strong>Security Tips:</strong>
                    <ul class="mb-0">
                        <li>Store codes in a secure password manager</li>
                        <li>Print codes and store in a safe location</li>
                        <li>Don't store codes on the same device as your authenticator app</li>
                        <li>Generate new codes if you suspect they've been compromised</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Recovery Code Generation
```django
<!-- generate.html -->
{% extends "mfa/recovery_codes/base.html" %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h3>Generate Recovery Codes</h3>
            </div>
            <div class="card-body">
                <p>Recovery codes are backup authentication codes that allow you to access your account if your other MFA methods are unavailable.</p>
                
                <div class="alert alert-info">
                    <h5>What happens when you generate recovery codes:</h5>
                    <ul>
                        <li>{{ code_count }} new recovery codes will be created</li>
                        <li>Any existing recovery codes will be invalidated</li>
                        <li>Each code can only be used once</li>
                        <li>Codes should be stored securely</li>
                    </ul>
                </div>
                
                {% if existing_codes %}
                    <div class="alert alert-warning">
                        <strong>Warning:</strong> You have existing recovery codes. 
                        Generating new codes will invalidate all {{ existing_codes.count }} existing codes.
                    </div>
                {% endif %}
                
                <form method="post">
                    {% csrf_token %}
                    <div class="form-check mb-3">
                        <input type="checkbox" class="form-check-input" id="understand" required>
                        <label class="form-check-label" for="understand">
                            I understand that generating new recovery codes will invalidate any existing codes
                        </label>
                    </div>
                    
                    <button type="submit" class="btn btn-primary btn-block">
                        <i class="fas fa-key"></i>
                        Generate {{ code_count }} Recovery Codes
                    </button>
                </form>
                
                <div class="mt-3 text-center">
                    <a href="{% url 'mfa_dashboard' %}" class="btn btn-link">
                        Cancel and return to security settings
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Downloadable Recovery Codes
```text
# download.txt
BARODY BROJECT - RECOVERY CODES
Generated: {{ generation_date }}
Account: {{ user.email }}

IMPORTANT: Save these codes in a secure location.
Each code can only be used once as backup authentication.

Recovery Codes:
{% for code in recovery_codes %}
{{ forloop.counter|stringformat:"02d" }}. {{ code.code }}
{% endfor %}

Security Instructions:
- Use these codes when other MFA methods are unavailable
- Each code works only once
- Generate new codes when you have few remaining
- Keep codes secure and private
- Contact support if codes are compromised

For help: support@barodybroject.com
```

### Recovery Code Usage
```python
# In Django views for recovery code handling
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import secrets
import string

@login_required
def generate_recovery_codes(request):
    """Generate new recovery codes for user"""
    if request.method == 'POST':
        # Invalidate existing codes
        request.user.recovery_codes.all().delete()
        
        # Generate new codes
        codes = []
        for _ in range(10):  # Generate 10 codes
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) 
                          for _ in range(8))
            codes.append(request.user.recovery_codes.create(code=code))
        
        messages.success(request, 'New recovery codes have been generated. Please save them securely.')
        return redirect('mfa_recovery_codes_view')
    
    return render(request, 'mfa/recovery_codes/generate.html', {
        'code_count': 10,
        'existing_codes': request.user.recovery_codes.filter(used=False)
    })

@login_required
def download_recovery_codes(request):
    """Download recovery codes as text file"""
    recovery_codes = request.user.recovery_codes.filter(used=False)
    
    response = render(request, 'mfa/recovery_codes/download.txt', {
        'recovery_codes': recovery_codes,
        'generation_date': recovery_codes.first().created_at if recovery_codes else None,
        'user': request.user
    }, content_type='text/plain')
    
    response['Content-Disposition'] = 'attachment; filename="barodybroject-recovery-codes.txt"'
    return response
```

### JavaScript Enhancements
```javascript
// Recovery codes functionality
function copyCodes() {
    const codes = Array.from(document.querySelectorAll('.recovery-code code'))
        .filter(code => !code.closest('.recovery-code').classList.contains('used'))
        .map(code => code.textContent)
        .join('\n');
    
    navigator.clipboard.writeText(codes).then(() => {
        const button = document.querySelector('[onclick="copyCodes()"]');
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i> Copied!';
        setTimeout(() => {
            button.innerHTML = originalText;
        }, 2000);
    });
}

function printCodes() {
    const printWindow = window.open('', '_blank');
    const codes = document.querySelector('.recovery-codes-container').innerHTML;
    
    printWindow.document.write(`
        <html>
        <head>
            <title>Recovery Codes - Barody Broject</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .recovery-code { margin: 10px 0; font-family: monospace; }
                .used { opacity: 0.5; text-decoration: line-through; }
                @media print { body { margin: 0; } }
            </style>
        </head>
        <body>
            <h1>Barody Broject - Recovery Codes</h1>
            <p>Generated: ${new Date().toLocaleDateString()}</p>
            <p><strong>Important:</strong> Store these codes securely. Each can only be used once.</p>
            ${codes}
        </body>
        </html>
    `);
    
    printWindow.document.close();
    printWindow.print();
}
```

## Container Configuration
- **Runtime**: Django with secure random number generation
- **Dependencies**: 
  - Python secrets module for cryptographic randomness
  - Django authentication framework
  - Secure file download handling
  - Print and clipboard JavaScript APIs
- **Environment**: 
  - Secure random seed generation
  - Database storage for recovery codes
  - User session management
- **Security**: Cryptographically secure code generation, one-time use validation

## Related Paths
- **Incoming**: 
  - MFA dashboard and security settings
  - Authentication failure recovery workflows
  - Account lockout and recovery procedures
  - Security incident response protocols
- **Outgoing**: 
  - Authentication bypass for emergency access
  - Security audit logging and monitoring
  - User notification systems for code usage
  - Account security assessment and recommendations
