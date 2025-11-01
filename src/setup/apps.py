"""
File: apps.py
Description: Django app configuration for setup wizard application
Author: Barodybroject Team <team@example.com>
Created: 2025-01-27
Last Modified: 2025-01-27
Version: 0.2.0

Dependencies:
- django.apps: Django application configuration framework

Container Requirements:
- Django application container with app registry
- Access to configuration and logging systems

Usage: Automatically loaded by Django when setup app is in INSTALLED_APPS
"""

import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class SetupConfig(AppConfig):
    """
    Django app configuration for the setup wizard application.
    
    This configuration defines the setup app behavior, including
    automatic service initialization and database table creation.
    
    Features:
    - App name and default auto field configuration
    - Verbose name for admin interface
    - Ready signal handler for initialization
    - Logging integration for setup operations
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'setup'
    verbose_name = 'Installation Setup Wizard'
    
    def ready(self):
        """
        Called when Django starts and the app is ready.
        
        This method is used to perform initialization tasks like:
        - Setting up logging for the setup app
        - Registering signal handlers
        - Validating configuration requirements
        """
        logger.info("Setup wizard application initialized")
        
        # Import signal handlers if needed
        try:
            from . import signals
            logger.debug("Setup signals imported successfully")
        except ImportError:
            logger.debug("No setup signals found, continuing without them")
        
        # Validate setup app configuration
        self._validate_setup_configuration()
    
    def _validate_setup_configuration(self):
        """
        Validate that the setup app configuration is correct.
        
        This performs basic checks to ensure the setup wizard
        can function properly within the Django application.
        """
        from django.conf import settings

        # Check if middleware is properly configured
        middleware_classes = getattr(settings, 'MIDDLEWARE', [])
        setup_middleware = 'setup.middleware.InstallationMiddleware'
        
        if setup_middleware not in middleware_classes:
            logger.warning(
                f"InstallationMiddleware not found in MIDDLEWARE. "
                f"Add '{setup_middleware}' to MIDDLEWARE setting for automatic redirects."
            )
        else:
            logger.debug("InstallationMiddleware found in middleware configuration")
        
        # Check if templates directory exists
        import os
        from pathlib import Path
        
        app_path = Path(__file__).parent
        templates_path = app_path / 'templates' / 'setup'
        
        if not templates_path.exists():
            logger.warning(f"Setup templates directory not found: {templates_path}")
        else:
            logger.debug(f"Setup templates directory found: {templates_path}")
        
        # Log configuration status
        debug_mode = getattr(settings, 'DEBUG', False)
        skip_check = getattr(settings, 'SKIP_INSTALLATION_CHECK', False)
        
        if debug_mode and skip_check:
            logger.info("Setup wizard configured to skip installation checks in debug mode")
        elif debug_mode:
            logger.info("Setup wizard active in debug mode")
        else:
            logger.info("Setup wizard active in production mode")