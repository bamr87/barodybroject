"""
File: middleware.py
Description: Django middleware for automatic installation wizard redirection
Author: Barodybroject Team <team@example.com>
Created: 2025-01-27
Last Modified: 2025-01-27
Version: 1.0.0

Dependencies:
- django.http: HTTP response handling
- django.urls: URL resolution and redirection
- django.conf: Django settings access
- setup.services: InstallationService for state checking

Container Requirements:
- Django application container with middleware processing
- Access to configuration storage and URL routing
- Installation state persistence

Usage: 
Add 'setup.middleware.InstallationMiddleware' to MIDDLEWARE in Django settings
"""

import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import resolve, reverse
from django.utils.deprecation import MiddlewareMixin

from .services import InstallationService

logger = logging.getLogger(__name__)


class InstallationMiddleware(MiddlewareMixin):
    """
    Middleware to redirect incomplete installations to setup wizard.
    
    This middleware checks the installation status on every request and
    redirects users to the setup wizard if the installation is not complete.
    Certain URLs are exempted to allow the setup process to function.
    
    Features:
    - Automatic redirection to setup wizard for incomplete installations
    - URL exemptions for setup process, admin, static files, and APIs
    - Debug mode awareness for development environments
    - Comprehensive logging for troubleshooting
    - Minimal performance impact with efficient checking
    """
    
    # URLs that should be accessible even during setup
    EXEMPTED_PATHS = [
        # Setup wizard URLs
        '/setup/',
        
        # Django admin (might be needed for advanced setup)
        '/admin/',
        
        # Static and media files
        '/static/',
        '/media/',
        
        # API endpoints (for external integrations)
        '/api/',
        
        # Health check endpoints
        '/health/',
        '/readiness/',
        '/liveness/',
        
        # Django development server specific
        '/__debug__/',  # Django Debug Toolbar
        '/favicon.ico',
    ]
    
    def __init__(self, get_response):
        """Initialize middleware with response handler."""
        self.get_response = get_response
        self.installation_service = InstallationService()
        super().__init__(get_response)
        
        # Log middleware initialization
        logger.info("InstallationMiddleware initialized")
    
    def process_request(self, request):
        """
        Process incoming request and redirect if installation incomplete.
        
        Args:
            request: Django HttpRequest object
            
        Returns:
            HttpResponseRedirect if redirection needed, None otherwise
        """
        # Skip processing for exempted paths
        if self._is_exempted_path(request.path):
            logger.debug(f"Skipping installation check for exempted path: {request.path}")
            return None
        
        # Skip in debug mode for development (optional)
        if getattr(settings, 'DEBUG', False) and getattr(settings, 'SKIP_INSTALLATION_CHECK', False):
            logger.debug("Skipping installation check in debug mode")
            return None
        
        try:
            # Check if installation is complete
            if not self.installation_service.is_installation_complete():
                logger.info(f"Installation incomplete, redirecting {request.path} to setup wizard")
                
                # Store the original URL to redirect back after setup
                request.session['post_setup_redirect'] = request.get_full_path()
                
                # Redirect to setup wizard
                setup_url = reverse('setup:wizard')
                return HttpResponseRedirect(setup_url)
                
        except Exception as e:
            # Log error but don't break the application
            logger.error(f"Error in InstallationMiddleware: {e}")
            
            # In case of error, assume installation is needed for safety
            if not self._is_debug_mode():
                try:
                    setup_url = reverse('setup:wizard')
                    return HttpResponseRedirect(setup_url)
                except Exception as inner_e:
                    logger.error(f"Failed to redirect to setup: {inner_e}")
        
        # Allow request to continue normally
        return None
    
    def _is_exempted_path(self, path):
        """
        Check if the given path should be exempted from installation checks.
        
        Args:
            path: Request path to check
            
        Returns:
            bool: True if path should be exempted
        """
        # Check against exempted path prefixes
        for exempted_path in self.EXEMPTED_PATHS:
            if path.startswith(exempted_path):
                return True
        
        # Additional checks for specific patterns
        
        # Django admin login/logout
        if path in ['/admin/login/', '/admin/logout/']:
            return True
        
        # Django auth views
        if path.startswith('/accounts/'):
            return True
        
        # Allow JSON/XML endpoints for APIs
        if any(path.endswith(ext) for ext in ['.json', '.xml', '.txt']):
            return True
        
        return False
    
    def _is_debug_mode(self):
        """Check if Django is running in debug mode."""
        return getattr(settings, 'DEBUG', False)
    
    def process_response(self, request, response):
        """
        Process response after view execution.
        
        This can be used to add headers or modify responses
        related to installation status.
        
        Args:
            request: Django HttpRequest object
            response: Django HttpResponse object
            
        Returns:
            Modified or original response
        """
        # Add installation status header for debugging
        if self._is_debug_mode():
            try:
                is_complete = self.installation_service.is_installation_complete()
                response['X-Installation-Complete'] = str(is_complete)
            except Exception as e:
                logger.debug(f"Could not add installation header: {e}")
                response['X-Installation-Complete'] = 'unknown'
        
        return response


class SetupRequiredMixin:
    """
    Mixin for views that require installation to be complete.
    
    This provides a decorator-like functionality for class-based views
    that should only be accessible after installation is complete.
    
    Usage:
        class MyView(SetupRequiredMixin, View):
            pass
    """
    
    def dispatch(self, request, *args, **kwargs):
        """Check installation status before dispatching to view."""
        installation_service = InstallationService()
        
        if not installation_service.is_installation_complete():
            logger.warning(f"Access denied to {self.__class__.__name__}: installation incomplete")
            
            # Store redirect URL
            request.session['post_setup_redirect'] = request.get_full_path()
            
            # Redirect to setup wizard
            setup_url = reverse('setup:wizard')
            return HttpResponseRedirect(setup_url)
        
        return super().dispatch(request, *args, **kwargs)


def setup_required(view_func):
    """
    Decorator for function-based views that require installation to be complete.
    
    Args:
        view_func: The view function to decorate
        
    Returns:
        Decorated view function
        
    Usage:
        @setup_required
        def my_view(request):
            return HttpResponse("Hello")
    """
    def wrapper(request, *args, **kwargs):
        installation_service = InstallationService()
        
        if not installation_service.is_installation_complete():
            logger.warning(f"Access denied to {view_func.__name__}: installation incomplete")
            
            # Store redirect URL
            request.session['post_setup_redirect'] = request.get_full_path()
            
            # Redirect to setup wizard
            setup_url = reverse('setup:wizard')
            return HttpResponseRedirect(setup_url)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper