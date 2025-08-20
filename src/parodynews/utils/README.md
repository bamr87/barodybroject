
# utils Directory

## Purpose
This directory contains utility modules and helper functions for the parodynews Django application. It provides specialized functionality that supports the main application features, including email handling with DKIM signing for secure email delivery.

## Contents
- `dkim_backend.py`: Custom Django email backend that implements DKIM (DomainKeys Identified Mail) signing for email authentication and deliverability

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
