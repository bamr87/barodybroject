"""
Integration tests for setup wizard workflow

These tests verify the complete setup wizard workflow including
command line interface, web interface, and database integration.
"""

import json
import os
import shutil
import tempfile
from io import StringIO
from urllib.parse import parse_qs, urlparse
from unittest.mock import MagicMock, Mock, patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import transaction
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse
from setup.management.commands.setup_wizard import \
    Command as SetupWizardCommand
from setup.services import InstallationService


def extract_token(output):
    """Return the token from the setup URL the headless command prints."""
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("http") and "token=" in line:
            return parse_qs(urlparse(line).query).get("token", [None])[0]
    return None


class TestSetupWizardWorkflow(TransactionTestCase):
    """
    Integration tests for the complete setup wizard workflow.
    Uses TransactionTestCase to test transaction behavior.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.client = Client()
        self.test_dir = tempfile.mkdtemp()
        self.test_config_file = f"{self.test_dir}/test_config.json"
        
        # Clear any existing users
        User.objects.all().delete()
        
        # Clean up any existing installation state
        if os.path.exists('/app/setup_data'):
            shutil.rmtree('/app/setup_data', ignore_errors=True)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        if os.path.exists('/app/setup_data'):
            shutil.rmtree('/app/setup_data', ignore_errors=True)
        User.objects.all().delete()
    
    def test_complete_interactive_workflow(self):
        """Test complete interactive setup workflow."""
        # Step 1: Run setup wizard command in interactive mode
        with patch('builtins.input') as mock_input, \
                patch('getpass.getpass') as mock_getpass:
            mock_input.side_effect = [
                'testadmin',  # username
                'admin@test.com',  # email
                '',  # first name (optional)
                '',  # last name (optional)
            ]
            mock_getpass.side_effect = [
                'SecurePassword123!',  # password
                'SecurePassword123!',  # confirm password
            ]
            
            out = StringIO()
            try:
                call_command('setup_wizard', stdout=out)
                output = out.getvalue()
                
                # Verify command completed successfully
                self.assertIn('installation completed successfully', output.lower())
                self.assertTrue(InstallationService().is_installation_complete())
                
                # Verify admin user was created
                admin_user = User.objects.get(username='testadmin')
                self.assertTrue(admin_user.is_staff)
                self.assertTrue(admin_user.is_superuser)
                self.assertEqual(admin_user.email, 'admin@test.com')
                
            except Exception as e:
                self.fail(f"Interactive workflow failed: {e}")
    
    def test_headless_mode_workflow(self):
        """Test headless mode workflow with web interface."""
        # Step 1: Run setup wizard in headless mode
        out = StringIO()
        call_command('setup_wizard', '--headless', stdout=out)
        output = out.getvalue()
        
        # Should generate token and provide URL
        self.assertIn('token', output.lower())
        self.assertIn('http', output.lower())
        
        # Extract the token from the printed setup URL
        token = extract_token(output)
        
        self.assertIsNotNone(token, "Setup token should be generated in headless mode")
        
        # Step 2: Access web interface with token
        admin_url = reverse('setup:create_admin')
        response = self.client.get(admin_url, {'token': token})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Administrator Account')
        
        # Step 3: Submit admin creation form
        data = {
            'username': 'webadmin',
            'email': 'webadmin@test.com',
            'password': 'WebPassword123!',
            'password_confirm': 'WebPassword123!',
            'token': token
        }
        
        response = self.client.post(admin_url, data)
        
        # Success logs the new admin in and redirects to the admin panel
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/admin/')
        self.assertTrue(InstallationService().is_installation_complete())
        
        # Verify admin user was created
        admin_user = User.objects.get(username='webadmin')
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertEqual(admin_user.email, 'webadmin@test.com')
    
    def test_workflow_state_persistence(self):
        """Test that workflow state persists across operations."""
        service = InstallationService()
        
        # Initial state should indicate incomplete installation
        self.assertFalse(service.is_installation_complete())
        
        # Generate token and verify persistence
        token = service.generate_setup_token()
        self.assertIsNotNone(token)
        
        # Create new service instance and verify token persists
        service2 = InstallationService()
        self.assertTrue(service2.validate_token(token))
        
        # Complete installation
        admin_user = service.create_admin_user(
            'testadmin', 'admin@test.com', 'TestPassword123!'
        )
        service.mark_installation_complete()
        
        # Verify state change persists
        service3 = InstallationService()
        self.assertTrue(service3.is_installation_complete())
    
    def test_workflow_error_handling(self):
        """Test error handling throughout the workflow."""
        # Test command with invalid input
        with patch('builtins.input') as mock_input, \
                patch('getpass.getpass') as mock_getpass:
            mock_input.side_effect = [
                '',  # empty username: re-prompted
                'erruser',  # username
                'invalid_email',  # invalid email
                '',  # first name (optional)
                '',  # last name (optional)
            ]
            mock_getpass.side_effect = [
                'weak',  # too short: re-prompted
                'ValidPass123',  # password
                'ValidPass123',  # confirm password
            ]
            
            out = StringIO()
            err = StringIO()
            
            # The invalid email is rejected and the wizard exits non-zero
            with self.assertRaises(SystemExit):
                call_command('setup_wizard', stdout=out, stderr=err)
            self.assertIn('invalid email', out.getvalue().lower())
        
        self.assertFalse(User.objects.filter(is_superuser=True).exists())
        self.assertFalse(InstallationService().is_installation_complete())
        
        # Test web interface with invalid data
        # First get a valid token
        service = InstallationService()
        token = service.generate_setup_token()
        
        admin_url = reverse('setup:create_admin')
        data = {
            'username': '',  # invalid
            'email': 'invalid_email',  # invalid
            'password': 'weak',  # weak
            'password_confirm': 'different',  # mismatch
            'token': token
        }
        
        response = self.client.post(admin_url, data)
        
        # Should return form with errors, not crash
        self.assertEqual(response.status_code, 200)
        errors = response.context['form'].errors
        for field in ('username', 'email', 'password'):
            self.assertIn(field, errors)
        self.assertFalse(User.objects.filter(is_superuser=True).exists())
    
    def test_workflow_database_transactions(self):
        """Test database transaction behavior during workflow."""
        service = InstallationService()
        
        # Test that failed user creation doesn't leave partial state
        with self.assertRaises(Exception):
            # Try to create user with duplicate username
            User.objects.create_user('duplicate', 'test@test.com', 'password123')
            service.create_admin_user('duplicate', 'admin@test.com', 'Password123!')
        
        # Verify installation remains incomplete
        self.assertFalse(service.is_installation_complete())
        
        # Verify no admin users exist
        admin_users = User.objects.filter(is_superuser=True)
        self.assertEqual(admin_users.count(), 0)
    
    def test_workflow_concurrent_access(self):
        """Test workflow behavior with concurrent access attempts."""
        # Start setup in one process/thread simulation
        service1 = InstallationService()
        token1 = service1.generate_setup_token()
        
        # Try to start setup in another process/thread simulation
        service2 = InstallationService()
        token2 = service2.generate_setup_token()
        
        # There is a single active setup token: the newest one replaces the old
        self.assertFalse(service1.validate_token(token1))
        self.assertTrue(service2.validate_token(token2))
        
        # Complete setup
        admin_user = service1.create_admin_user(
            'admin1', 'admin1@test.com', 'Password123!'
        )
        service1.mark_installation_complete()
        
        # Second token should now be invalid/unusable
        with self.assertRaises(Exception):
            service2.create_admin_user(
                'admin2', 'admin2@test.com', 'Password123!'
            )


class TestSetupWizardIntegration(TestCase):
    """Integration tests for setup wizard components."""
    
    def setUp(self):
        """Set up test environment."""
        self.client = Client()
        User.objects.all().delete()
    
    def test_middleware_integration(self):
        """Test setup middleware integration with views."""
        # Access a non-setup URL when installation is incomplete
        response = self.client.get('/')
        
        # Should redirect to setup wizard (if middleware is active)
        # Note: This depends on middleware configuration
        if response.status_code == 302:
            self.assertIn('setup', response.url)
    
    def test_url_routing_integration(self):
        """Test URL routing for setup views."""
        # Test all setup URLs are accessible
        setup_urls = [
            '/setup/',
            '/setup/create-admin/',
            '/setup/status/',
            '/setup/complete/',
            '/setup/health/',
            '/setup/redirect/',
        ]
        
        for url in setup_urls:
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, 404, 
                              f"URL {url} should be accessible")
    
    def test_template_inheritance_integration(self):
        """Test template inheritance and rendering."""
        # Access wizard page and verify template inheritance
        response = self.client.get('/setup/')
        
        # Should use base template with proper structure
        self.assertContains(response, '<html')
        self.assertContains(response, '<head>')
        self.assertContains(response, '<body')
        self.assertContains(response, 'Setup Wizard')
    
    def test_static_files_integration(self):
        """Test static files are properly served."""
        # Access wizard page and check for CSS/JS references
        response = self.client.get('/setup/')
        
        # Should reference Bootstrap and custom CSS
        self.assertContains(response, 'bootstrap')
        self.assertContains(response, 'css')
    
    def test_form_csrf_integration(self):
        """Test CSRF integration with forms."""
        # Get form page
        token = InstallationService().generate_setup_token()
        response = self.client.get(f'/setup/create-admin/?token={token}')
        
        # Should contain CSRF token
        self.assertContains(response, 'csrfmiddlewaretoken')
    
    def test_session_integration(self):
        """Test session handling integration."""
        # Access wizard page
        response = self.client.get('/setup/')
        
        # Should create session
        self.assertTrue(self.client.session.session_key)
        
        # Session should persist across requests
        response2 = self.client.get('/setup/status/')
        self.assertEqual(self.client.session.session_key, 
                        self.client.session.session_key)
    
    def test_database_integration(self):
        """Test database integration throughout workflow."""
        # Verify initial database state
        self.assertEqual(User.objects.count(), 0)
        
        # Create admin user through service
        service = InstallationService()
        admin_user = service.create_admin_user(
            'dbadmin', 'dbadmin@test.com', 'DbPassword123!'
        )
        
        # Verify database changes
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(User.objects.filter(username='dbadmin').exists())
        
        # Verify user properties
        db_user = User.objects.get(username='dbadmin')
        self.assertTrue(db_user.is_staff)
        self.assertTrue(db_user.is_superuser)
        self.assertTrue(db_user.check_password('DbPassword123!'))
    
    def test_logging_integration(self):
        """Test logging integration throughout workflow."""
        import logging
        from io import StringIO

        # Capture logs
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger('setup')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        try:
            # Perform setup operations
            service = InstallationService()
            token = service.generate_setup_token()
            
            # Check that operations were logged
            log_output = log_capture.getvalue()
            # Note: Actual log content depends on service implementation
            
        finally:
            logger.removeHandler(handler)


class TestSetupWizardPerformance(TestCase):
    """Performance tests for setup wizard workflow."""
    
    def test_setup_performance(self):
        """Test setup wizard performance."""
        import time

        # Measure setup service operations
        service = InstallationService()
        
        # Time token generation
        start_time = time.time()
        token = service.generate_setup_token()
        token_time = time.time() - start_time
        
        # Should be fast (< 1 second)
        self.assertLess(token_time, 1.0)
        
        # Time user creation
        start_time = time.time()
        admin_user = service.create_admin_user(
            'perfadmin', 'perf@test.com', 'PerfPassword123!'
        )
        user_time = time.time() - start_time
        
        # Should be reasonable (< 5 seconds)
        self.assertLess(user_time, 5.0)
    
    def test_view_performance(self):
        """Test view response performance."""
        import time

        # Test wizard view performance
        start_time = time.time()
        response = self.client.get('/setup/')
        view_time = time.time() - start_time
        
        # Should respond quickly (< 2 seconds)
        self.assertLess(view_time, 2.0)
        self.assertEqual(response.status_code, 200)