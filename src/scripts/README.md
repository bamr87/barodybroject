
# scripts Directory

## Purpose
This directory contains utility scripts and tools that support various aspects of the parody news generator application. These scripts provide specialized functionality for email security, cryptographic operations, and system administration tasks that complement the main Django application.

## Contents
- `dkim_key_generator.py`: Python script for generating DKIM (DomainKeys Identified Mail) private/public key pairs for email authentication and security

## Usage
Scripts are executed as standalone utilities for system administration:

```bash
# Generate DKIM keys for email authentication
python scripts/dkim_key_generator.py

# Example DKIM key generation
python scripts/dkim_key_generator.py \
    --domain example.com \
    --selector default \
    --key-size 2048 \
    --output-dir ./keys/
```

Script features:
- **DKIM Key Generation**: Create cryptographic keys for email authentication
- **Domain Configuration**: Support for multiple domains and selectors
- **Security Standards**: Generate keys meeting modern security requirements
- **Output Flexibility**: Configurable output formats and directories
- **Integration Ready**: Keys formatted for DNS and email server configuration

## Container Configuration
Scripts can be executed within container environments:
- Python dependencies managed through requirements.txt
- Output files can be mounted to host filesystem
- Support for environment variable configuration
- Secure key generation with proper entropy sources

## Related Paths
- Incoming: Used by system administrators for email and security configuration
- Outgoing: Generates cryptographic keys and configuration files for email infrastructure
