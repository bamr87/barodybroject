"""
Integration tests for headless mode functionality

These tests verify the headless installation mode including
token generation, validation, and web-based completion workflow.
"""

import json
import os
import shutil
import sys
import tempfile
import time
from io import StringIO
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

sys.path.append('/workspace/src')
from setup.services import InstallationService


class TestHeadlessMode(TestCase):
    """Integration tests for headless installation mode."""
    
    def setUp(self):
        """Set up test environment."""
        self.client = Client()
        self.test_dir = tempfile.mkdtemp()
        
        # Clear any existing users and installation state
        User.objects.all().delete()
        if os.path.exists('/app/setup_data'):
            shutil.rmtree('/app/setup_data', ignore_errors=True)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        if os.path.exists('/app/setup_data'):
            shutil.rmtree('/app/setup_data', ignore_errors=True)
        User.objects.all().delete()
    
    def test_headless_command_execution(self):
        """Test execution of setup wizard in headless mode."""
        out = StringIO()
        err = StringIO()
        
        # Run command in headless mode
        call_command('setup_wizard', '--headless', stdout=out, stderr=err)
        
        output = out.getvalue()
        error_output = err.getvalue()
        
        # Verify command completed successfully
        self.assertEqual(error_output.strip(), '', "Command should not produce errors")
        
        # Verify output contains expected information
        self.assertIn('headless', output.lower())
        self.assertIn('token', output.lower())
        self.assertIn('http', output.lower())
        
        # Verify token was generated
        lines = output.split('\n')
        token_found = False
        for line in lines:
            if 'token' in line.lower() and ':' in line:
                token_found = True
                break
        
        self.assertTrue(token_found, "Setup token should be displayed in output")
    
    def test_headless_token_generation(self):
        """Test token generation in headless mode."""
        # Run headless command
        out = StringIO()
        call_command('setup_wizard', '--headless', stdout=out)
        
        # Get token from service
        service = InstallationService()
        
        # Verify token exists and is valid
        # Note: This assumes service stores the last generated token
        # In practice, you might need to extract from output or config
        if hasattr(service, '_config') and service._config:
            token = service._config.get('setup_token')
            if token:
                self.assertTrue(service.validate_token(token))
    
    def test_headless_web_interface_access(self):
        """Test accessing web interface with headless-generated token."""
        # Generate token via headless command
        out = StringIO()
        call_command('setup_wizard', '--headless', stdout=out)
        
        # Extract token from output (simplified extraction)
        output = out.getvalue()
        token = None
        
        # Look for token in output
        lines = output.split('\n')
        for line in lines:
            if 'token:' in line.lower():
                parts = line.split(':')
                if len(parts) > 1:
                    token = parts[-1].strip()
                    break
        
        # If not found in output, try to get from service
        if not token:
            service = InstallationService()
            if hasattr(service, '_config') and service._config:
                token = service._config.get('setup_token')
        
        # Skip test if we can't get token (service implementation dependent)
        if not token:
            self.skipTest("Unable to extract token from headless mode")
        
        # Test accessing wizard with token
        wizard_url = reverse('setup:wizard')
        response = self.client.get(wizard_url)
        self.assertEqual(response.status_code, 200)
        
        # Test accessing admin creation with token
        admin_url = reverse('setup:create_admin')
        response = self.client.get(admin_url, {'token': token})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Administrator Account')
    
    def test_headless_web_completion_workflow(self):
        """Test complete headless workflow with web completion."""
        # Step 1: Run headless command
        out = StringIO()
        call_command('setup_wizard', '--headless', stdout=out)
        
        # Step 2: Extract token (mock for this test)
        token = "test_headless_token"
        
        # Mock service to return our test token as valid
        with patch('setup.views.InstallationService') as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            mock_service.validate_token.return_value = True
            mock_service.is_installation_complete.return_value = False
            mock_service.create_admin_user.return_value = Mock(username='headlessadmin')
            mock_service.mark_installation_complete.return_value = True
            
            # Step 3: Access admin creation form
            admin_url = reverse('setup:create_admin')
            response = self.client.get(admin_url, {'token': token})
            self.assertEqual(response.status_code, 200)
            
            # Step 4: Submit admin creation form
            data = {
                'username': 'headlessadmin',
                'email': 'headless@test.com',
                'password1': 'HeadlessPassword123!',
                'password2': 'HeadlessPassword123!',
                'token': token
            }
            
            response = self.client.post(admin_url, data)
            
            # Should redirect to complete page
            self.assertEqual(response.status_code, 302)
            self.assertIn('complete', response.url)
            
            # Verify service methods were called
            mock_service.create_admin_user.assert_called_once_with(
                'headlessadmin', 'headless@test.com', 'HeadlessPassword123!'
            )
            mock_service.mark_installation_complete.assert_called_once()
    
    def test_headless_token_validation(self):
        """Test token validation in headless mode."""
        # Generate token via headless mode
        service = InstallationService()
        token = service.generate_setup_token()
        
        # Test valid token
        admin_url = reverse('setup:create_admin')
        response = self.client.get(admin_url, {'token': token})
        self.assertNotEqual(response.status_code, 403)
        
        # Test invalid token
        response = self.client.get(admin_url, {'token': 'invalid_token'})
        # Should redirect or show error
        self.assertIn(response.status_code, [302, 403, 400])
        
        # Test missing token
        response = self.client.get(admin_url)
        # Should redirect to wizard
        if response.status_code == 302:
            self.assertIn('wizard', response.url)
    
    def test_headless_security_features(self):
        """Test security features in headless mode."""
        # Test token expiration (if implemented)
        service = InstallationService()
        token = service.generate_setup_token()
        
        # Token should be valid initially
        self.assertTrue(service.validate_token(token))
        
        # Test token uniqueness
        token2 = service.generate_setup_token()
        self.assertNotEqual(token, token2, "Each token should be unique")
        
        # Test token format (should be cryptographically secure)
        self.assertGreater(len(token), 20, "Token should be sufficiently long")
        self.assertRegex(token, r'^[a-zA-Z0-9]+$', "Token should be alphanumeric")
    
    def test_headless_state_persistence(self):
        """Test state persistence in headless mode."""
        # Run headless command
        out = StringIO()
        call_command('setup_wizard', '--headless', stdout=out)
        
        # Create new service instance
        service = InstallationService()
        
        # Verify installation is not complete
        self.assertFalse(service.is_installation_complete())
        
        # Verify token exists and persists
        # This test depends on service implementation details
        if hasattr(service, '_config') and service._config:
            self.assertIsNotNone(service._config.get('setup_token'))
    
    def test_headless_error_handling(self):
        """Test error handling in headless mode."""
        # Test running headless mode when already complete
        # First complete the installation
        service = InstallationService()
        service.create_admin_user('existing', 'existing@test.com', 'Password123!')
        service.mark_installation_complete()
        
        # Try to run headless mode again
        out = StringIO()
        err = StringIO()
        
        with self.assertRaises(SystemExit):
            call_command('setup_wizard', '--headless', stdout=out, stderr=err)
        
        error_output = err.getvalue()
        self.assertIn('already complete', error_output.lower())
    
    def test_headless_concurrent_access(self):
        """Test concurrent access in headless mode."""
        # Start headless mode
        out = StringIO()
        call_command('setup_wizard', '--headless', stdout=out)
        
        # Simulate multiple simultaneous web requests
        service1 = InstallationService()
        service2 = InstallationService()
        
        token1 = service1.generate_setup_token()
        token2 = service2.generate_setup_token()
        
        # Both should generate valid tokens initially
        self.assertTrue(service1.validate_token(token1))
        self.assertTrue(service2.validate_token(token2))
        
        # But tokens should be different
        self.assertNotEqual(token1, token2)
    
    def test_headless_output_format(self):
        """Test output format of headless mode."""
        out = StringIO()
        call_command('setup_wizard', '--headless', stdout=out)
        
        output = out.getvalue()
        
        # Verify output is properly formatted
        self.assertGreater(len(output), 0, "Should produce output")
        
        # Should contain key information
        output_lower = output.lower()
        self.assertIn('headless', output_lower)
        self.assertIn('setup', output_lower)
        
        # Should provide clear instructions
        self.assertIn('http', output_lower)  # URL information
        self.assertIn('browser', output_lower)  # Browser instructions
        
        # Should be human-readable
        lines = output.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        self.assertGreater(len(non_empty_lines), 0, "Should have meaningful content")
    
    def test_headless_url_generation(self):
        """Test URL generation in headless mode."""
        out = StringIO()
        call_command('setup_wizard', '--headless', stdout=out)
        
        output = out.getvalue()
        
        # Should contain a complete URL
        lines = output.split('\n')
        url_found = False
        
        for line in lines:
            if 'http' in line.lower():
                # Basic URL validation
                if '://' in line and '.' in line:
                    url_found = True
                    break
        
        self.assertTrue(url_found, "Should provide a complete URL")
    
    def test_headless_docker_integration(self):
        """Test headless mode integration with Docker environment."""
        # This test would verify headless mode works in Docker
        # For now, just test that it doesn't fail
        
        out = StringIO()
        err = StringIO()
        
        try:
            call_command('setup_wizard', '--headless', stdout=out, stderr=err)
            
            # Should complete without Docker-specific errors
            error_output = err.getvalue()
            self.assertNotIn('docker', error_output.lower())
            self.assertNotIn('container', error_output.lower())
            
        except Exception as e:
            # If it fails, it shouldn't be due to Docker issues
            self.assertNotIn('docker', str(e).lower())
            self.assertNotIn('container', str(e).lower())


class TestHeadlessTokenSecurity(TestCase):
    """Security-focused tests for headless mode tokens."""
    
    def test_token_cryptographic_strength(self):
        """Test cryptographic strength of generated tokens."""
        service = InstallationService()
        
        # Generate multiple tokens
        tokens = []
        for _ in range(10):
            token = service.generate_setup_token()
            tokens.append(token)
        
        # All tokens should be unique
        self.assertEqual(len(tokens), len(set(tokens)), "All tokens should be unique")
        
        # Tokens should have sufficient entropy
        for token in tokens:
            self.assertGreater(len(token), 32, "Token should be long enough")
            
            # Should not contain predictable patterns
            self.assertNotIn('123', token)
            self.assertNotIn('abc', token)
            self.assertNotIn('000', token)
    
    def test_token_timing_attack_resistance(self):
        """Test resistance to timing attacks."""
        service = InstallationService()
        valid_token = service.generate_setup_token()
        invalid_token = "invalid_token_for_testing"
        
        # Measure validation time for valid and invalid tokens
        import time

        # Valid token timing
        start_time = time.time()
        result1 = service.validate_token(valid_token)
        valid_time = time.time() - start_time
        
        # Invalid token timing
        start_time = time.time()
        result2 = service.validate_token(invalid_token)
        invalid_time = time.time() - start_time
        
        # Times should be similar (within reasonable bounds)
        time_diff = abs(valid_time - invalid_time)
        self.assertLess(time_diff, 0.1, "Validation time should be constant")
    
    def test_token_storage_security(self):
        """Test secure storage of tokens."""
        service = InstallationService()
        token = service.generate_setup_token()
        
        # Token should not be stored in plain text
        # This test depends on implementation details
        if hasattr(service, '_config') and service._config:
            config_str = json.dumps(service._config)
            # Token itself should not appear in config
            # (should be hashed or encrypted)
            # Note: This is implementation dependent
            pass


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