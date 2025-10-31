"""
Setup application for Django installation wizard.

This Django application provides a comprehensive installation wizard
for first-time setup of the Barodybroject application. It includes
both interactive CLI and web-based setup modes with secure token
authentication for headless installations.

Features:
- Interactive setup wizard with progress tracking
- Headless mode with secure token-based authentication
- Admin user creation and initial configuration
- System health monitoring and validation
- Responsive Bootstrap UI with modern UX
- Comprehensive logging and error handling

Author: Barodybroject Team
Version: 1.0.0
"""

default_app_config = 'setup.apps.SetupConfig'