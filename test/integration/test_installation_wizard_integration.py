"""
File: test_installation_wizard_integration.py
Description: Comprehensive integration tests for the installation wizard workflow
Author: Barodybroject Team <team@example.com>
Created: 2025-10-30
Last Modified: 2025-10-30
Version: 1.0.0

Dependencies:
- django.test: Django test utilities
- setup: Complete setup application
- requests: HTTP client for web testing

Container Requirements:
- Django test environment with complete setup
- Database with clean state
- Web server capability for HTTP testing

Usage: pytest test/integration/test_installation_wizard_integration.py
"""

import json
import os
import sys
import tempfile
import time
from io import StringIO
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import transaction
from django.test import (Client, TestCase, TransactionTestCase,
                         override_settings)
from django.urls import reverse

sys.path.append('/workspace/src')
from setup.forms import AdminUserForm
from setup.services import InstallationService
from setup.views import CreateAdminView, SetupStatusView, SetupWizardView


class TestInstallationWizardIntegration(TransactionTestCase):
    """Integration tests for complete installation wizard workflow."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.client = Client()
        
        # Create temporary directory for test configuration
        self.test_dir = tempfile.mkdtemp()
        self.test_config_file = os.path.join(self.test_dir, 'integration_test_config.json')
        
        # Clean any existing users and sessions
        User.objects.all().delete()
        
        # Mock service configuration path
        self.config_patcher = patch.object(InstallationService, '_get_config_file_path')
        self.mock_config_path = self.config_patcher.start()
        self.mock_config_path.return_value = self.test_config_file
    
    def tearDown(self):
        """Clean up integration test environment."""
        self.config_patcher.stop()
        
        # Clean up test files
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)
        os.rmdir(self.test_dir)
        
        # Clean up database
        User.objects.all().delete()
    
    def test_complete_interactive_installation_workflow(self):
        """Test complete installation workflow in interactive mode."""
        # Step 1: Initial state check
        service = InstallationService()
        self.assertFalse(service.is_installation_complete())
        
        # Step 2: Access setup wizard view
        response = self.client.get(reverse('setup:wizard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Installation Wizard')
        
        # Step 3: Submit admin user creation form
        form_data = {
            'username': 'integrationadmin',
            'email': 'integration@test.com',
            'password1': 'IntegrationPassword123!',
            'password2': 'IntegrationPassword123!',
        }
        
        response = self.client.post(reverse('setup:create_admin'), form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Step 4: Verify user was created
        user = User.objects.get(username='integrationadmin')
        self.assertEqual(user.email, 'integration@test.com')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password('IntegrationPassword123!'))
        
        # Step 5: Verify installation is marked complete
        service = InstallationService()  # Fresh instance to reload config
        self.assertTrue(service.is_installation_complete())
        
        # Step 6: Verify setup wizard redirects when complete
        response = self.client.get(reverse('setup:wizard'))
        self.assertRedirects(response, reverse('setup:status'))
    
    def test_headless_installation_with_web_completion(self):
        """Test headless installation mode with web-based completion."""
        # Step 1: Run headless setup command
        output = StringIO()
        call_command('setup_wizard', '--headless', '--force', stdout=output)
        
        output_content = output.getvalue()
        self.assertIn('Installation token:', output_content)
        
        # Step 2: Extract token from command output
        lines = output_content.split('\\n')
        token_line = next(line for line in lines if 'Installation token:' in line)
        token = token_line.split('Installation token:')[1].strip()
        
        # Step 3: Verify token is valid
        service = InstallationService()
        self.assertTrue(service.validate_token(token))
        
        # Step 4: Access web setup with token
        response = self.client.get(reverse('setup:create_admin'), {'token': token})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Complete Installation')
        
        # Step 5: Submit admin user form with token
        form_data = {
            'username': 'headlessadmin',
            'email': 'headless@test.com',
            'password1': 'HeadlessPassword123!',
            'password2': 'HeadlessPassword123!',
            'token': token,
        }
        
        response = self.client.post(reverse('setup:create_admin'), form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Step 6: Verify admin user was created
        user = User.objects.get(username='headlessadmin')
        self.assertTrue(user.is_superuser)
        
        # Step 7: Verify installation is complete
        service = InstallationService()
        self.assertTrue(service.is_installation_complete())
        
        # Step 8: Verify token is no longer valid (single use)
        self.assertFalse(service.validate_token(token))
    
    def test_installation_state_persistence_across_requests(self):
        """Test that installation state persists across multiple requests."""
        # Step 1: Generate token
        service = InstallationService()
        token = service.generate_setup_token()
        
        # Step 2: Make multiple requests to verify state persistence
        for i in range(3):
            response = self.client.get(reverse('setup:status'))
            self.assertEqual(response.status_code, 200)
            
            # Should still be incomplete
            self.assertContains(response, 'incomplete')
            
            # Token should still be valid
            self.assertTrue(service.validate_token(token))
        
        # Step 3: Complete installation
        form_data = {
            'username': f'persistadmin{int(time.time())}',
            'email': 'persist@test.com',
            'password1': 'PersistPassword123!',
            'password2': 'PersistPassword123!',
            'token': token,
        }
        
        response = self.client.post(reverse('setup:create_admin'), form_data)
        
        # Step 4: Verify state change persists
        for i in range(3):
            response = self.client.get(reverse('setup:status'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'complete')
    
    def test_concurrent_installation_attempts(self):
        """Test handling of concurrent installation attempts."""
        # Step 1: Generate token
        service = InstallationService()
        token = service.generate_setup_token()
        
        # Step 2: Simulate concurrent admin creation attempts
        form_data_1 = {
            'username': 'concurrent1',
            'email': 'concurrent1@test.com',
            'password1': 'ConcurrentPassword123!',
            'password2': 'ConcurrentPassword123!',
            'token': token,
        }
        
        form_data_2 = {
            'username': 'concurrent2',
            'email': 'concurrent2@test.com',
            'password1': 'ConcurrentPassword123!',
            'password2': 'ConcurrentPassword123!',
            'token': token,
        }
        
        # Step 3: Submit both forms (first should succeed, second should handle gracefully)
        response1 = self.client.post(reverse('setup:create_admin'), form_data_1)
        response2 = self.client.post(reverse('setup:create_admin'), form_data_2)
        
        # Step 4: Verify one succeeded and system remains stable
        users = User.objects.filter(username__in=['concurrent1', 'concurrent2'])
        self.assertGreaterEqual(users.count(), 1)  # At least one should succeed
        
        # Step 5: Verify installation is marked complete
        service = InstallationService()
        self.assertTrue(service.is_installation_complete())
    
    def test_security_token_validation_workflow(self):
        """Test security aspects of token validation workflow."""
        # Step 1: Generate valid token
        service = InstallationService()
        valid_token = service.generate_setup_token()
        
        # Step 2: Test valid token access
        response = self.client.get(reverse('setup:create_admin'), {'token': valid_token})
        self.assertEqual(response.status_code, 200)
        
        # Step 3: Test invalid token access
        response = self.client.get(reverse('setup:create_admin'), {'token': 'invalid_token'})
        self.assertEqual(response.status_code, 403)  # Should be forbidden
        
        # Step 4: Test no token access
        response = self.client.get(reverse('setup:create_admin'))
        self.assertEqual(response.status_code, 403)  # Should be forbidden
        
        # Step 5: Test expired token (simulate expiration)
        with patch.object(service, 'validate_token', return_value=False):
            response = self.client.get(reverse('setup:create_admin'), {'token': valid_token})
            self.assertEqual(response.status_code, 403)
    
    def test_form_validation_integration(self):
        """Test form validation integration across the workflow."""
        # Step 1: Generate token
        service = InstallationService()
        token = service.generate_setup_token()
        
        # Step 2: Test various invalid form submissions
        invalid_forms = [
            # Empty username
            {
                'username': '',
                'email': 'test@example.com',
                'password1': 'ValidPassword123!',
                'password2': 'ValidPassword123!',
                'token': token,
            },
            # Invalid email
            {
                'username': 'validuser',
                'email': 'invalid-email',
                'password1': 'ValidPassword123!',
                'password2': 'ValidPassword123!',
                'token': token,
            },
            # Password mismatch
            {
                'username': 'validuser',
                'email': 'test@example.com',
                'password1': 'ValidPassword123!',
                'password2': 'DifferentPassword123!',
                'token': token,
            },
            # Weak password
            {
                'username': 'validuser',
                'email': 'test@example.com',
                'password1': '123',
                'password2': '123',
                'token': token,
            },
        ]
        
        for form_data in invalid_forms:
            response = self.client.post(reverse('setup:create_admin'), form_data)
            self.assertEqual(response.status_code, 200)  # Should return form with errors
            self.assertContains(response, 'error')  # Should contain error messages
        
        # Step 3: Test valid form submission
        valid_form_data = {
            'username': 'validuser',
            'email': 'valid@example.com',
            'password1': 'ValidPassword123!',
            'password2': 'ValidPassword123!',
            'token': token,
        }
        
        response = self.client.post(reverse('setup:create_admin'), valid_form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify user was created
        user = User.objects.get(username='validuser')
        self.assertTrue(user.is_superuser)
    
    def test_database_transaction_integrity(self):
        """Test database transaction integrity during installation."""
        # Step 1: Generate token
        service = InstallationService()
        token = service.generate_setup_token()
        
        # Step 2: Mock database error during user creation
        with patch('django.contrib.auth.models.User.objects.create_user', side_effect=Exception('DB Error')):
            form_data = {
                'username': 'transactiontest',
                'email': 'transaction@test.com',
                'password1': 'TransactionPassword123!',
                'password2': 'TransactionPassword123!',
                'token': token,
            }
            
            response = self.client.post(reverse('setup:create_admin'), form_data)
            
            # Step 3: Verify no partial state was saved
            self.assertEqual(User.objects.filter(username='transactiontest').count(), 0)
            
            # Step 4: Verify installation is still incomplete
            service = InstallationService()
            self.assertFalse(service.is_installation_complete())
            
            # Step 5: Verify token is still valid
            self.assertTrue(service.validate_token(token))
    
    def test_middleware_integration(self):
        """Test installation wizard middleware integration."""
        # Step 1: Test middleware blocks non-setup URLs when installation incomplete
        service = InstallationService()
        self.assertFalse(service.is_installation_complete())
        
        # Try to access main site URLs (should be blocked by middleware)
        blocked_urls = [
            '/',
            '/admin/',
            '/parodynews/',
        ]
        
        for url in blocked_urls:
            response = self.client.get(url)
            # Should redirect to setup wizard
            self.assertIn(response.status_code, [302, 301])
            self.assertIn('setup', response.url)
        
        # Step 2: Complete installation
        with patch('builtins.input', side_effect=[
            'middlewaretest', 'middleware@test.com', 'MiddlewarePassword123!', 'MiddlewarePassword123!'
        ]):
            call_command('setup_wizard', '--force', stdout=StringIO())
        
        # Step 3: Test middleware allows access after installation complete
        service = InstallationService()
        self.assertTrue(service.is_installation_complete())
        
        # Some URLs should now be accessible (depending on URL configuration)
        response = self.client.get('/')
        self.assertNotEqual(response.status_code, 302)  # Should not redirect to setup


class TestInstallationWizardPerformance(TestCase):
    """Performance and load testing for installation wizard."""
    
    def setUp(self):
        """Set up performance test environment."""
        self.client = Client()
        self.test_dir = tempfile.mkdtemp()
        self.test_config_file = os.path.join(self.test_dir, 'performance_test_config.json')
        
        # Mock service configuration
        self.config_patcher = patch.object(InstallationService, '_get_config_file_path')
        self.mock_config_path = self.config_patcher.start()
        self.mock_config_path.return_value = self.test_config_file
    
    def tearDown(self):
        """Clean up performance test environment."""
        self.config_patcher.stop()
        
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)
        os.rmdir(self.test_dir)
        
        User.objects.all().delete()
    
    def test_token_generation_performance(self):
        """Test token generation performance."""
        service = InstallationService()
        
        # Measure token generation time
        start_time = time.time()
        for i in range(10):
            token = service.generate_setup_token()
            self.assertIsNotNone(token)
        end_time = time.time()
        
        # Should generate 10 tokens in reasonable time (less than 1 second)
        total_time = end_time - start_time
        self.assertLess(total_time, 1.0)
        
        # Average should be less than 100ms per token
        average_time = total_time / 10
        self.assertLess(average_time, 0.1)
    
    def test_token_validation_performance(self):
        """Test token validation performance."""
        service = InstallationService()
        token = service.generate_setup_token()
        
        # Measure validation time
        start_time = time.time()
        for i in range(100):
            result = service.validate_token(token)
            self.assertTrue(result)
        end_time = time.time()
        
        # Should validate 100 tokens in reasonable time
        total_time = end_time - start_time
        self.assertLess(total_time, 1.0)
        
        # Average should be less than 10ms per validation
        average_time = total_time / 100
        self.assertLess(average_time, 0.01)
    
    def test_concurrent_status_requests(self):
        """Test handling of concurrent status requests."""
        # Simulate multiple concurrent requests to status endpoint
        responses = []
        
        # Use threading to simulate concurrent requests
        import threading
        
        def make_request():
            response = self.client.get(reverse('setup:status'))
            responses.append(response)
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        end_time = time.time()
        
        # Verify all requests succeeded
        self.assertEqual(len(responses), 10)
        for response in responses:
            self.assertEqual(response.status_code, 200)
        
        # Should complete within reasonable time (2 seconds for 10 concurrent requests)
        total_time = end_time - start_time
        self.assertLess(total_time, 2.0)


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])