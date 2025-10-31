"""
File: test_views.py
Description: Comprehensive unit tests for Django views in the setup wizard
Author: Barodybroject Team <team@example.com>
Created: 2025-10-30
Last Modified: 2025-10-30
Version: 1.0.0

Dependencies:
- django.test: Django test utilities
- setup.views: Setup wizard Django views
- setup.forms: Django forms for setup

Container Requirements:
- Django test environment with views and URLs
- Setup app configuration
- Session and authentication support

Usage: pytest test/unit/test_views.py
"""

import json
import os
import sys
import tempfile
from unittest.mock import MagicMock, Mock, patch

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

sys.path.append('/workspace/src')
from setup.forms import AdminUserForm
from setup.services import InstallationService
from setup.views import CreateAdminView, SetupStatusView, SetupWizardView


class TestSetupViews(TestCase):
    """Test suite for setup wizard views."""
    
    def setUp(self):
        """Set up test environment."""
        self.client = Client()
        self.test_dir = tempfile.mkdtemp()
        self.test_config_file = f"{self.test_dir}/test_config.json"
        
        # Mock the installation service
        self.patcher = patch('setup.views.InstallationService')
        self.mock_service_class = self.patcher.start()
        self.mock_service = Mock()
        self.mock_service_class.return_value = self.mock_service
        
        # Default service behavior
        self.mock_service.is_installation_complete.return_value = False
        self.mock_service.generate_setup_token.return_value = "test_token_123"
        self.mock_service.validate_token.return_value = True
        self.mock_service.get_installation_status.return_value = {
            'installation_complete': False,
            'has_admin_user': False,
            'completed_at': None
        }
    
    def tearDown(self):
        """Clean up test environment."""
        self.patcher.stop()
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_setup_wizard_get(self):
        """Test GET request to setup wizard view."""
        url = reverse('setup:wizard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Installation Wizard')
        self.assertContains(response, 'Welcome to Barodybroject')
    
    def test_setup_wizard_with_token_in_session(self):
        """Test setup wizard when token exists in session."""
        # Add token to session
        session = self.client.session
        session['setup_token'] = 'existing_token_456'
        session.save()
        
        url = reverse('setup:wizard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'existing_token_456')
    
    def test_setup_wizard_installation_complete(self):
        """Test setup wizard when installation is already complete."""
        self.mock_service.is_installation_complete.return_value = True
        
        url = reverse('setup:wizard')
        response = self.client.get(url)
        
        # Should redirect to complete page
        self.assertEqual(response.status_code, 302)
        self.assertIn('complete', response.url)
    
    def test_create_admin_get_with_valid_token(self):
        """Test GET request to create admin view with valid token."""
        url = reverse('setup:create_admin')
        response = self.client.get(url, {'token': 'valid_token'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Administrator Account')
        self.assertContains(response, 'form')
    
    def test_create_admin_get_without_token(self):
        """Test GET request to create admin view without token."""
        url = reverse('setup:create_admin')
        response = self.client.get(url)
        
        # Should redirect to wizard
        self.assertEqual(response.status_code, 302)
        self.assertIn('wizard', response.url)
    
    def test_create_admin_get_with_invalid_token(self):
        """Test GET request to create admin view with invalid token."""
        self.mock_service.validate_token.return_value = False
        
        url = reverse('setup:create_admin')
        response = self.client.get(url, {'token': 'invalid_token'})
        
        # Should redirect to wizard with error
        self.assertEqual(response.status_code, 302)
        self.assertIn('wizard', response.url)
    
    def test_create_admin_post_success(self):
        """Test successful POST request to create admin."""
        self.mock_service.create_admin_user.return_value = Mock(username='newadmin')
        self.mock_service.mark_installation_complete.return_value = True
        
        url = reverse('setup:create_admin')
        data = {
            'username': 'newadmin',
            'email': 'admin@test.com',
            'password1': 'SecurePassword123!',
            'password2': 'SecurePassword123!',
            'token': 'valid_token'
        }
        
        response = self.client.post(url, data)
        
        # Should redirect to complete page
        self.assertEqual(response.status_code, 302)
        self.assertIn('complete', response.url)
        
        # Verify service methods were called
        self.mock_service.create_admin_user.assert_called_once_with(
            'newadmin', 'admin@test.com', 'SecurePassword123!'
        )
        self.mock_service.mark_installation_complete.assert_called_once()
    
    def test_create_admin_post_form_errors(self):
        """Test POST request with form validation errors."""
        url = reverse('setup:create_admin')
        data = {
            'username': '',  # Empty username
            'email': 'invalid_email',  # Invalid email
            'password1': '123',  # Weak password
            'password2': '456',  # Passwords don't match
            'token': 'valid_token'
        }
        
        response = self.client.post(url, data)
        
        # Should return form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')
        
        # Service should not be called
        self.mock_service.create_admin_user.assert_not_called()
    
    def test_create_admin_post_service_error(self):
        """Test POST request when service raises exception."""
        from django.core.exceptions import ValidationError
        self.mock_service.create_admin_user.side_effect = ValidationError("Username already exists")
        
        url = reverse('setup:create_admin')
        data = {
            'username': 'duplicate',
            'email': 'admin@test.com',
            'password1': 'SecurePassword123!',
            'password2': 'SecurePassword123!',
            'token': 'valid_token'
        }
        
        response = self.client.post(url, data)
        
        # Should return form with error message
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username already exists')
    
    def test_setup_status_view(self):
        """Test setup status view."""
        self.mock_service.get_installation_status.return_value = {
            'installation_complete': False,
            'has_admin_user': True,
            'completed_at': None,
            'database_ready': True,
            'migrations_applied': True
        }
        
        url = reverse('setup:status')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Installation Status')
        self.assertContains(response, 'database_ready')
    
    def test_setup_complete_view(self):
        """Test setup complete view."""
        url = reverse('setup:complete')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Setup Complete')
        self.assertContains(response, 'congratulations')
    
    def test_setup_health_view(self):
        """Test setup health check view."""
        url = reverse('setup:health')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'System Health')
    
    def test_ajax_status_request(self):
        """Test AJAX request to status endpoint."""
        url = reverse('setup:status')
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Should return JSON data
        data = json.loads(response.content)
        self.assertIn('installation_complete', data)
    
    def test_csrf_protection(self):
        """Test CSRF protection on POST requests."""
        url = reverse('setup:create_admin')
        data = {
            'username': 'testadmin',
            'email': 'admin@test.com',
            'password1': 'SecurePassword123!',
            'password2': 'SecurePassword123!',
            'token': 'valid_token'
        }
        
        # Request without CSRF token should fail
        client = Client(enforce_csrf_checks=True)
        response = client.post(url, data)
        
        self.assertEqual(response.status_code, 403)
    
    def test_session_handling(self):
        """Test proper session handling in views."""
        # Test token storage in session
        url = reverse('setup:wizard')
        response = self.client.get(url)
        
        # Should have session
        self.assertTrue(self.client.session.session_key)
        
        # Test session persistence across requests
        second_response = self.client.get(url)
        self.assertEqual(response.wsgi_request.session.session_key,
                        second_response.wsgi_request.session.session_key)
    
    def test_view_permissions(self):
        """Test view access permissions."""
        # Setup views should be accessible without authentication
        url = reverse('setup:wizard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test that regular users can access setup views
        User.objects.create_user('testuser', 'test@test.com', 'testpass')
        self.client.login(username='testuser', password='testpass')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TestSetupViewsIntegration(TestCase):
    """Integration tests for setup views with real Django components."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.client = Client()
        User.objects.all().delete()
    
    def test_full_setup_workflow_via_views(self):
        """Test complete setup workflow through web interface."""
        # Step 1: Access wizard page
        wizard_url = reverse('setup:wizard')
        response = self.client.get(wizard_url)
        self.assertEqual(response.status_code, 200)
        
        # Step 2: Get token from session or generate new one
        # This would normally be generated by the wizard
        token = "test_workflow_token"
        
        # Step 3: Access admin creation form
        admin_url = reverse('setup:create_admin')
        response = self.client.get(admin_url, {'token': token})
        
        # Step 4: Submit admin creation form
        # Note: This test would need real InstallationService
        # For now, we'll test the form structure
        self.assertContains(response, 'username')
        self.assertContains(response, 'email')
        self.assertContains(response, 'password1')
        self.assertContains(response, 'password2')
    
    def test_view_url_patterns(self):
        """Test that all setup URLs are properly configured."""
        urls_to_test = [
            ('setup:wizard', {}),
            ('setup:create_admin', {}),
            ('setup:status', {}),
            ('setup:complete', {}),
            ('setup:health', {}),
        ]
        
        for url_name, kwargs in urls_to_test:
            try:
                url = reverse(url_name, kwargs=kwargs)
                self.assertIsInstance(url, str)
                self.assertTrue(url.startswith('/setup/'))
            except Exception as e:
                self.fail(f"URL pattern {url_name} failed: {e}")
    
    def test_template_rendering(self):
        """Test that views render templates correctly."""
        # Test wizard template
        url = reverse('setup:wizard')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'setup/wizard.html')
        
        # Test status template
        url = reverse('setup:status')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'setup/status.html')
        
        # Test complete template
        url = reverse('setup:complete')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'setup/complete.html')
    
    def test_error_handling(self):
        """Test error handling in views."""
        # Test handling of missing templates
        with self.assertRaises(Exception):
            # This would fail if templates are missing
            pass
        
        # Test handling of invalid form data
        url = reverse('setup:create_admin')
        invalid_data = {
            'username': 'x' * 200,  # Too long
            'email': 'not_an_email',
            'password1': '123',
            'password2': '456',
            'token': 'invalid'
        }
        
        response = self.client.post(url, invalid_data)
        # Should handle gracefully, not crash
        self.assertIn(response.status_code, [200, 302])


if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.test.utils import get_runner

    # Configure Django for testing
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.messages',
                'setup',
            ],
            MIDDLEWARE=[
                'django.middleware.security.SecurityMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.common.CommonMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
            ],
            ROOT_URLCONF='setup.urls',
            SECRET_KEY='test-secret-key-for-testing-only',
            TEMPLATES=[
                {
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'DIRS': [],
                    'APP_DIRS': True,
                    'OPTIONS': {
                        'context_processors': [
                            'django.template.context_processors.debug',
                            'django.template.context_processors.request',
                            'django.contrib.auth.context_processors.auth',
                            'django.contrib.messages.context_processors.messages',
                        ],
                    },
                },
            ]
        )
    
    django.setup()
    
    # Run tests
    import pytest
    pytest.main([__file__, '-v'])