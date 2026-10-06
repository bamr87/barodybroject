
# utils Directory

## Purpose
Small, dependency-light helpers for the parodynews Django application. Anything that talks to an AI provider belongs in [`../ai/`](../ai/README.md) and anything that is a use case belongs in [`../services/`](../services/README.md); what is left here is genuinely generic.

## Contents
- `dkim_backend.py`: Django email backend that adds DKIM signatures to outgoing mail
- `markdown.py`: Markdown rendering used by both the API and the Jekyll export
- `schemas.py`: Loads the bundled JSON schemas from [`../schema/`](../schema/README.md) (`load_schemas`, `get_schema`)
- `defaults.py`: Reads `FieldDefaults` rows to seed model form defaults

## Usage
Utility modules are imported and used throughout the application:

```python
# In Django settings for email backend
EMAIL_BACKEND = 'parodynews.utils.dkim_backend.DKIMEmailBackend'

# Required settings
DKIM_PRIVATE_KEY = 'base64_encoded_private_key'
DKIM_SELECTOR = 'your_selector'
DKIM_DOMAIN = 'barodybroject.com'
```

The DKIM backend functionality:
- Extends Django's built-in SMTP email backend
- Adds DKIM signature headers to outgoing emails
- Improves email deliverability and reduces spam filtering
- Supports domain authentication for email security
- Handles base64 encoded private key configuration

## Container Configuration
Utilities are loaded as part of the Django application:
- Email backend configured in Django settings
- DKIM private keys managed through environment variables or Azure Key Vault
- Secure handling of cryptographic keys in containerized environments

## Related Paths
- Incoming: Used by Django email system and application modules requiring email functionality
- Outgoing: Sends authenticated emails through SMTP with DKIM signatures for improved deliverability
