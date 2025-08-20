
# Social Account Snippets Directory

## Purpose
Contains reusable template snippets for social authentication UI components. These modular templates provide consistent social login buttons, provider lists, and authentication elements that can be included across multiple pages and authentication flows.

## Contents
- `login.html`: Social login button snippet for individual providers
- `login_extra.html`: Additional login options and alternative authentication methods
- `provider_list.html`: Complete list of available social authentication providers

## Usage

### Social Login Button Snippet
```django
<!-- snippets/login.html -->
<a href="{% provider_login_url provider.id %}" 
   class="btn btn-social btn-{{ provider.id }}">
    <i class="fab fa-{{ provider.id }}"></i>
    Sign in with {{ provider.name }}
</a>
```

### Provider List Integration
```django
<!-- Including provider list in any template -->
{% load socialaccount %}

<div class="social-login-section">
    <h4>Quick Login</h4>
    {% include "socialaccount/snippets/provider_list.html" %}
</div>

<!-- Or include individual provider buttons -->
{% get_providers as socialaccount_providers %}
{% for provider in socialaccount_providers %}
    <div class="provider-option">
        {% include "socialaccount/snippets/login.html" with provider=provider %}
    </div>
{% endfor %}
```

### Enhanced Provider List Template
```django
<!-- snippets/provider_list.html -->
{% load socialaccount %}
{% get_providers as socialaccount_providers %}

{% if socialaccount_providers %}
    <div class="social-providers">
        {% for provider in socialaccount_providers %}
            <div class="provider-button-wrapper">
                <button type="button" 
                        class="btn btn-outline-{{ provider.id }} btn-social"
                        onclick="window.location.href='{% provider_login_url provider.id %}'">
                    <i class="fab fa-{{ provider.id }}"></i>
                    <span class="provider-name">{{ provider.name }}</span>
                </button>
            </div>
        {% endfor %}
    </div>
    
    <div class="provider-divider">
        <span>or</span>
    </div>
{% endif %}
```

### Custom Login Extra Options
```django
<!-- snippets/login_extra.html -->
<div class="alternative-login-options">
    <div class="login-help">
        <h5>Need Help?</h5>
        <ul class="list-unstyled">
            <li>
                <a href="{% url 'account_reset_password' %}">
                    <i class="fas fa-key"></i> Forgot your password?
                </a>
            </li>
            <li>
                <a href="{% url 'account_email' %}">
                    <i class="fas fa-envelope"></i> Resend confirmation email
                </a>
            </li>
            <li>
                <a href="{% url 'contact' %}">
                    <i class="fas fa-question-circle"></i> Contact support
                </a>
            </li>
        </ul>
    </div>
    
    <div class="signup-prompt">
        <p>Don't have an account?</p>
        <a href="{% url 'account_signup' %}" class="btn btn-link">
            Create New Account
        </a>
    </div>
</div>
```

### JavaScript Enhanced Snippets
```javascript
// Enhanced social login functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add loading states to social login buttons
    document.querySelectorAll('.btn-social').forEach(button => {
        button.addEventListener('click', function() {
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Connecting...';
            this.disabled = true;
        });
    });
    
    // Track social login attempts
    document.querySelectorAll('[data-provider]').forEach(button => {
        button.addEventListener('click', function() {
            const provider = this.dataset.provider;
            gtag('event', 'social_login_attempt', {
                'provider': provider,
                'method': 'button_click'
            });
        });
    });
});
```

### CSS Styling for Social Providers
```css
/* Social provider button styling */
.btn-social {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    padding: 12px 20px;
    margin-bottom: 10px;
    width: 100%;
    text-align: left;
    border-radius: 6px;
    transition: all 0.3s ease;
}

.btn-social i {
    margin-right: 12px;
    width: 20px;
    text-align: center;
}

/* Provider-specific colors */
.btn-google { 
    background-color: #dc4e41; 
    border-color: #dc4e41; 
    color: white; 
}

.btn-github { 
    background-color: #333; 
    border-color: #333; 
    color: white; 
}

.btn-facebook { 
    background-color: #3b5998; 
    border-color: #3b5998; 
    color: white; 
}

.provider-divider {
    text-align: center;
    margin: 20px 0;
    position: relative;
}

.provider-divider:before {
    content: '';
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 1px;
    background-color: #ddd;
}

.provider-divider span {
    background-color: white;
    padding: 0 15px;
    color: #666;
}
```

## Container Configuration
- **Runtime**: Django template rendering with social authentication context
- **Dependencies**: 
  - django-allauth template tags
  - FontAwesome icons for provider branding
  - Bootstrap CSS framework
  - Custom social authentication styling
- **Assets**: Provider logos, custom CSS, JavaScript enhancements
- **Environment**: Social provider configurations and OAuth settings

## Related Paths
- **Incoming**: 
  - Main social authentication pages
  - User registration and login forms
  - Account connection management interfaces
  - Mobile and responsive authentication views
- **Outgoing**: 
  - OAuth provider authentication flows
  - User session creation and management
  - Analytics and tracking systems
  - Social provider API integrations
