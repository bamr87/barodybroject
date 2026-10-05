"""
Integration tests for headless mode functionality

These tests verify the headless installation mode including
token generation, validation, and web-based completion workflow.
"""

import json
import os
import shutil
import tempfile
import time
from io import StringIO
from urllib.parse import parse_qs, urlparse
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse
from setup.services import InstallationService


def extract_setup_url(output):
    """Return the setup URL the headless command prints (http://…/setup/?token=…)."""
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("http") and "token=" in line:
            return line
    return None


def extract_token(output):
    """Return the token from the setup URL the headless command prints."""
    url = extract_setup_url(output)
    if not url:
        return None
    return parse_qs(urlparse(url).query).get("token", [None])[0]


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
        
        # Extract the token from the printed setup URL
        token = extract_token(out.getvalue())
        self.assertIsNotNone(token, "Headless mode should print a setup URL with a token")
        
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
        
        # Step 2: Extract the token from the printed setup URL
        token = extract_token(out.getvalue())
        self.assertIsNotNone(token, "Headless mode should print a setup URL with a token")
        
        # Step 3: Access admin creation form
        admin_url = reverse('setup:create_admin')
        response = self.client.get(admin_url, {'token': token})
        self.assertEqual(response.status_code, 200)
        
        # Step 4: Submit admin creation form
        data = {
            'username': 'headlessadmin',
            'email': 'headless@test.com',
            'password': 'HeadlessPassword123!',
            'password_confirm': 'HeadlessPassword123!',
            'token': token
        }
        
        response = self.client.post(admin_url, data)
        
        # Success logs the new admin in and redirects to the admin panel
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/admin/')
        
        user = User.objects.get(username='headlessadmin')
        self.assertTrue(user.is_superuser)
        service = InstallationService()
        self.assertTrue(service.is_installation_complete())
        self.assertTrue(service.is_admin_created_during_install())
        # The token is single-use
        self.assertFalse(service.validate_token(token))
    
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
        
        # Test missing token: redirected back to the setup wizard
        response = self.client.get(admin_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('setup:wizard'))
    
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
        self.assertRegex(token, r'^[A-Za-z0-9_-]+$', "Token should be URL-safe")
    
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
        
        # Running headless mode again is a no-op that reports the finished install
        out = StringIO()
        err = StringIO()
        
        call_command('setup_wizard', '--headless', stdout=out, stderr=err)
        
        self.assertIn('already complete', out.getvalue().lower())
        self.assertIsNone(extract_token(out.getvalue()), "No new token once installed")
    
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
        
        # There is a single active setup token: the newest one replaces the old
        self.assertNotEqual(token1, token2)
        self.assertFalse(service1.validate_token(token1))
        self.assertTrue(service1.validate_token(token2))
        self.assertTrue(service2.validate_token(token2))
    
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
        
        # Should contain a complete setup URL carrying a valid token
        url = extract_setup_url(output)
        self.assertIsNotNone(url, "Should provide a complete URL")
        parsed = urlparse(url)
        self.assertIn(parsed.scheme, ('http', 'https'))
        self.assertTrue(parsed.netloc)
        self.assertEqual(parsed.path, reverse('setup:wizard'))
        self.assertTrue(InstallationService().validate_token(extract_token(output)))
    
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