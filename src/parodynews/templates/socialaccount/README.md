
# Social Account Templates Directory

## Purpose
Contains Django allauth social authentication templates for OAuth-based login with providers like Google, GitHub, Facebook, and Twitter. These templates handle the complete social authentication workflow including login, signup, account connections, and error handling.

## Contents
- **snippets/**: Reusable social authentication UI components
- **messages/**: User feedback messages for social account operations
- **email/**: Email templates for social account notifications
- `base_entrance.html`: Base template for social authentication entry points
- `login_redirect.html`: Template displayed during OAuth redirect process
- `login.html`: Social login page with provider selection buttons
- `base_manage.html`: Base template for social account management pages
- `login_cancelled.html`: Page shown when user cancels social authentication
- `connections.html`: Social account management and connection interface
- `signup.html`: Social signup page for new users via OAuth providers
- `authentication_error.html`: Error page for failed social authentication attempts

## Usage

### Social Login Integration
```django
<!-- login.html -->
{% extends "socialaccount/base_entrance.html" %}
{% load socialaccount %}

{% block head_title %}Sign In - Barody Broject{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h3>Sign In with Social Account</h3>
            </div>
            <div class="card-body">
                {% get_providers as socialaccount_providers %}
                {% for provider in socialaccount_providers %}
                    <a href="{% provider_login_url provider.id %}" 
                       class="btn btn-{{ provider.id }} btn-block mb-2">
                        <i class="fab fa-{{ provider.id }}"></i>
                        Sign in with {{ provider.name }}
                    </a>
                {% endfor %}
                
                <hr>
                <div class="text-center">
                    <a href="{% url 'account_login' %}">
                        Sign in with email instead
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Social Account Connections Management
```django
<!-- connections.html -->
{% extends "socialaccount/base_manage.html" %}
{% load socialaccount %}

{% block content %}
<h2>Manage Social Accounts</h2>

<div class="social-accounts-list">
    {% get_social_accounts user as accounts %}
    {% if accounts %}
        <h4>Connected Accounts</h4>
        {% for account in accounts %}
            <div class="connected-account">
                <img src="{{ account.get_avatar_url }}" alt="{{ account.provider }}">
                <div class="account-info">
                    <strong>{{ account.provider|title }}</strong>
                    <p>{{ account.extra_data.name|default:account.uid }}</p>
                </div>
                
                <form method="post" action="{% url 'socialaccount_disconnect' account.id %}">
                    {% csrf_token %}
                    <button type="submit" class="btn btn-sm btn-outline-danger">
                        Disconnect
                    </button>
                </form>
            </div>
        {% endfor %}
    {% endif %}
    
    <h4>Available Providers</h4>
    {% get_providers as socialaccount_providers %}
    {% for provider in socialaccount_providers %}
        {% if provider.id not in connected_accounts %}
            <a href="{% provider_login_url provider.id process='connect' %}" 
               class="btn btn-outline-primary">
                <i class="fab fa-{{ provider.id }}"></i>
                Connect {{ provider.name }}
            </a>
        {% endif %}
    {% endfor %}
</div>
{% endblock %}
```

### OAuth Error Handling
```django
<!-- authentication_error.html -->
{% extends "socialaccount/base_entrance.html" %}

{% block head_title %}Authentication Error{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="alert alert-danger">
            <h4>Authentication Failed</h4>
            <p>We encountered an error while trying to authenticate your account.</p>
            
            {% if error %}
                <p><strong>Error:</strong> {{ error }}</p>
            {% endif %}
            
            <hr>
            <p>Please try again or contact support if the problem persists.</p>
            
            <a href="{% url 'socialaccount_login' %}" class="btn btn-primary">
                Try Again
            </a>
            <a href="{% url 'account_login' %}" class="btn btn-secondary">
                Sign In with Email
            </a>
        </div>
    </div>
</div>
{% endblock %}
```

### Provider Configuration
```python
# In Django settings.py
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    'github': {
        'SCOPE': [
            'user:email',
        ],
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
        ],
    }
}
```

### Custom Social Account Adapter
```python
# Custom adapter for social account handling
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed
        """
        # Custom logic for handling social login
        user = sociallogin.user
        if user.email:
            # Check if user exists with this email
            try:
                existing_user = User.objects.get(email=user.email)
                sociallogin.connect(request, existing_user)
            except User.DoesNotExist:
                pass
```

## Container Configuration
- **Runtime**: Django allauth social authentication framework
- **Dependencies**: 
  - django-allauth with social providers
  - OAuth provider configurations
  - Frontend framework (Bootstrap)
  - FontAwesome icons for provider buttons
- **Environment Variables**:
  - `SOCIALACCOUNT_PROVIDERS`: Provider configurations
  - Provider-specific client IDs and secrets
  - OAuth callback URLs
- **Security**: CSRF protection, OAuth state validation

## Related Paths
- **Incoming**: 
  - OAuth provider authentication flows
  - User registration and login workflows
  - Account management and settings pages
  - Email verification and confirmation processes
- **Outgoing**: 
  - User profile creation and updates
  - Session management and authentication state
  - Provider API integrations for user data
  - Account linking and social graph connections
