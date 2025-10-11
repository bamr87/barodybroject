
# Social Account Messages Directory

## Purpose
Contains message templates for social authentication events using django-allauth. These templates provide user feedback messages when connecting, disconnecting, or updating social media accounts like Google, GitHub, Facebook, and other OAuth providers.

## Contents
- `account_connected_other.txt`: Message when user connects an additional social account
- `account_disconnected.txt`: Confirmation message when social account is disconnected
- `account_connected.txt`: Success message when first social account is connected
- `account_connected_updated.txt`: Message when existing social account information is updated

## Usage

### Social Account Integration
```python
# In Django views with social authentication
from django.contrib import messages
from allauth.socialaccount.models import SocialAccount

def connect_social_account(request):
    # After successful OAuth flow
    messages.success(request, 'Your Google account has been connected successfully.')
    
def disconnect_social_account(request, provider):
    # After disconnecting social account
    messages.info(request, f'Your {provider} account has been disconnected.')
```

### Message Display in Templates
```django
<!-- Social account management page -->
{% if messages %}
    <div class="messages">
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
                {{ message }}
                <button type="button" class="close" data-dismiss="alert">
                    <span>&times;</span>
                </button>
            </div>
        {% endfor %}
    </div>
{% endif %}

<div class="social-accounts">
    <h3>Connected Accounts</h3>
    {% for account in user.socialaccount_set.all %}
        <div class="social-account-item">
            <img src="{{ account.get_avatar_url }}" alt="{{ account.provider }}">
            <span>{{ account.provider|title }}: {{ account.extra_data.name }}</span>
            <a href="{% url 'socialaccount_disconnect' account.id %}" 
               class="btn btn-sm btn-outline-danger">
                Disconnect
            </a>
        </div>
    {% endfor %}
</div>
```

### Custom Message Templates
```text
# account_connected.txt
Your {{ provider }} account has been successfully connected to your Barody Broject profile. You can now sign in using {{ provider }} authentication.

# account_disconnected.txt  
Your {{ provider }} account has been disconnected from your Barody Broject profile. You can reconnect it anytime from your account settings.

# account_connected_other.txt
An additional {{ provider }} account has been connected to your profile. You now have multiple social login options available.

# account_connected_updated.txt
Your {{ provider }} account information has been updated with the latest data from {{ provider }}.
```

### JavaScript Integration
```javascript
// Handle social account actions
document.addEventListener('DOMContentLoaded', function() {
    // Confirm before disconnecting social accounts
    document.querySelectorAll('.disconnect-social').forEach(link => {
        link.addEventListener('click', function(e) {
            const provider = this.dataset.provider;
            if (!confirm(`Are you sure you want to disconnect your ${provider} account?`)) {
                e.preventDefault();
            }
        });
    });
    
    // Auto-hide success messages
    setTimeout(() => {
        document.querySelectorAll('.alert-success').forEach(alert => {
            alert.classList.remove('show');
        });
    }, 5000);
});
```

## Container Configuration
- **Runtime**: Django allauth social authentication framework
- **Dependencies**: 
  - django-allauth with social account providers
  - OAuth provider configurations (Google, GitHub, etc.)
  - Django message framework
- **Environment Variables**:
  - `GOOGLE_OAUTH2_CLIENT_ID`: Google OAuth client ID
  - `GITHUB_CLIENT_ID`: GitHub OAuth application ID
  - `FACEBOOK_APP_ID`: Facebook application ID
- **Security**: OAuth callback URLs and CSRF protection

## Related Paths
- **Incoming**: 
  - Social authentication workflows
  - OAuth provider callbacks
  - User account management views
  - Social account connection/disconnection actions
- **Outgoing**: 
  - User profile and settings pages
  - Authentication state management
  - Social provider API integrations
  - User notification systems
