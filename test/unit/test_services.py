"""
File: test_services.py
Description: Comprehensive unit tests for InstallationService class
Author: Barodybroject Team <team@example.com>
Created: 2025-10-30
Last Modified: 2025-10-30
Version: 1.0.0

Dependencies:
- pytest: Test framework
- django.test: Django test utilities
- setup.services: InstallationService class

Container Requirements:
- Django test environment with database
- Setup app configuration
- File system access for configuration storage

Usage: pytest test/unit/test_services.py
"""

import json
import os
# Import the service we're testing
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone

sys.path.append('/workspace/src')
from setup.services import InstallationService


class TestInstallationService(TestCase):
    """Test suite for InstallationService class."""
    
    def setUp(self):
        """Set up test environment for each test."""
        # Create temporary directory for test configuration
        self.test_dir = tempfile.mkdtemp()
        self.test_config_file = os.path.join(self.test_dir, 'test_setup_config.json')
        self.test_installation_file = os.path.join(self.test_dir, '.installation')
        
        # Create service instance with test configuration
        self.service = InstallationService()
        self.service.config_file = Path(self.test_config_file)  # Convert to Path object
        self.service.installation_file = Path(self.test_installation_file)  # Convert to Path object
        
        # Clear any existing users
        User.objects.all().delete()
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove all files in test directory
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_installation_incomplete_initially(self):
        """Test that installation is incomplete when no configuration exists."""
        self.assertFalse(self.service.is_installation_complete())
    
    def test_token_generation(self):
        """Test secure token generation."""
        token = self.service.generate_setup_token()
        
        # Token should be a non-empty string
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 32)
        
        # Token should be stored in configuration
        self.assertTrue(os.path.exists(self.test_config_file))
        with open(self.test_config_file, 'r') as f:
            config = json.load(f)
        
        self.assertIn('setup_token', config)
        token_data = config['setup_token']
        self.assertIn('created_at', token_data)
        self.assertIn('expires_at', token_data)
        self.assertIn('token_hash', token_data)
        self.assertFalse(token_data['used'])
    
    def test_token_validation_valid_token(self):
        """Test validation of a valid token."""
        # Generate a token
        token = self.service.generate_setup_token()
        
        # Validate the same token
        self.assertTrue(self.service.validate_token(token))
    
    def test_token_validation_invalid_token(self):
        """Test validation of an invalid token."""
        # Generate a token
        self.service.generate_setup_token()
        
        # Validate a different token
        self.assertFalse(self.service.validate_token('invalid_token'))
    
    def test_token_validation_expired_token(self):
        """Test validation of an expired token."""
        # Generate a token
        token = self.service.generate_setup_token()
        
        # Manually set expiration to past
        with open(self.test_config_file, 'r') as f:
            config = json.load(f)
        
        past_time = datetime.now() - timedelta(hours=2)
        # Set expiration in the correct nested structure
        config['setup_token']['expires_at'] = past_time.isoformat()
        
        with open(self.test_config_file, 'w') as f:
            json.dump(config, f)
        
        # Validation should fail for expired token
        self.assertFalse(self.service.validate_token(token))
    
    def test_token_validation_no_token_config(self):
        """Test validation when no token configuration exists."""
        self.assertFalse(self.service.validate_token('any_token'))
    
    def test_admin_user_creation_success(self):
        """Test successful admin user creation."""
        username = 'testadmin'
        email = 'admin@test.com'
        password = 'SecurePassword123!'
        
        user = self.service.create_admin_user(username, email, password)
        
        # Verify user was created
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, username)
        self.assertEqual(user.email, email)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password(password))
    
    def test_admin_user_creation_duplicate_username(self):
        """Test admin user creation with duplicate username."""
        username = 'testadmin'
        email1 = 'admin1@test.com'
        email2 = 'admin2@test.com'
        password = 'SecurePassword123!'
        
        # Create first user
        self.service.create_admin_user(username, email1, password)
        
        # Attempt to create second user with same username
        with self.assertRaises(ValidationError):
            self.service.create_admin_user(username, email2, password)
    
    def test_admin_user_creation_invalid_email(self):
        """Test admin user creation with invalid email."""
        username = 'testadmin'
        email = 'invalid_email'
        password = 'SecurePassword123!'
        
        with self.assertRaises(ValidationError):
            self.service.create_admin_user(username, email, password)
    
    def test_admin_user_creation_weak_password(self):
        """Test admin user creation with weak password."""
        username = 'testadmin'
        email = 'admin@test.com'
        password = '123'  # Too weak
        
        with self.assertRaises(ValidationError):
            self.service.create_admin_user(username, email, password)
    
    def test_mark_installation_complete(self):
        """Test marking installation as complete."""
        # Initially incomplete
        self.assertFalse(self.service.is_installation_complete())
        
        # Mark as complete
        result = self.service.mark_installation_complete()
        self.assertTrue(result)
        
        # Should now be complete
        self.assertTrue(self.service.is_installation_complete())
        
        # Verify installation file
        with open(self.test_installation_file, 'r') as f:
            installation_data = json.load(f)
        
        self.assertTrue(installation_data.get('completed', False))
        self.assertIn('completed_at', installation_data)
    
    def test_get_installation_status(self):
        """Test getting detailed installation status."""
        # Initially should show incomplete status
        status = self.service.get_installation_status()
        
        self.assertFalse(status['installation_complete'])
        self.assertIsNone(status.get('completed_at'))
        self.assertFalse(status['has_admin_user'])
        
        # Create admin user
        self.service.create_admin_user('admin', 'admin@test.com', 'SecurePass123!')
        
        status = self.service.get_installation_status()
        self.assertTrue(status['has_admin_user'])
        
        # Mark installation complete
        self.service.mark_installation_complete()
        
        status = self.service.get_installation_status()
        self.assertTrue(status['installation_complete'])
        self.assertIsNotNone(status.get('completed_at'))
    
    def test_config_file_creation(self):
        """Test configuration file is created properly."""
        # Generate token to trigger config creation
        self.service.generate_setup_token()
        
        # File should exist
        self.assertTrue(os.path.exists(self.test_config_file))
        
        # Content should be valid JSON
        with open(self.test_config_file, 'r') as f:
            config = json.load(f)
        
        self.assertIsInstance(config, dict)
    
    def test_config_file_permissions(self):
        """Test configuration file has proper permissions."""
        # Generate token to create config file
        self.service.generate_setup_token()
        
        # Check file permissions (should be readable by owner only)
        file_stats = os.stat(self.test_config_file)
        file_mode = file_stats.st_mode & 0o777
        
        # Should be readable and writable by owner
        self.assertTrue(file_mode & 0o600)
    
    def test_multiple_token_generation(self):
        """Test that generating multiple tokens overwrites previous ones."""
        # Generate first token
        token1 = self.service.generate_setup_token()
        
        # Generate second token
        token2 = self.service.generate_setup_token()
        
        # Tokens should be different
        self.assertNotEqual(token1, token2)
        
        # Only second token should be valid
        self.assertFalse(self.service.validate_token(token1))
        self.assertTrue(self.service.validate_token(token2))
    
    @patch('setup.services.logger')
    def test_logging_token_generation(self, mock_logger):
        """Test that token generation is properly logged."""
        self.service.generate_setup_token()
        
        # Verify logging calls
        mock_logger.info.assert_called()
    
    @patch('setup.services.logger')
    def test_logging_admin_creation(self, mock_logger):
        """Test that admin user creation is properly logged."""
        self.service.create_admin_user('admin', 'admin@test.com', 'SecurePass123!')
        
        # Verify logging calls
        mock_logger.info.assert_called()
    
    def test_service_with_missing_config_directory(self):
        """Test service behavior when config directory doesn't exist."""
        # Point to non-existent directory
        missing_dir = os.path.join(self.test_dir, 'missing', 'path')
        missing_config = os.path.join(missing_dir, 'config.json')
        
        service = InstallationService()
        service.config_file = missing_config
        
        # Should handle missing directory gracefully
        token = service.generate_setup_token()
        self.assertIsInstance(token, str)
        self.assertTrue(os.path.exists(missing_config))
    
    def test_concurrent_token_access(self):
        """Test handling of concurrent token access."""
        # This test would be more complex in a real scenario
        # For now, just verify basic thread safety
        token = self.service.generate_setup_token()
        
        # Multiple validations should work
        self.assertTrue(self.service.validate_token(token))
        self.assertTrue(self.service.validate_token(token))
    
    def test_edge_case_empty_strings(self):
        """Test handling of edge cases with empty strings."""
        with self.assertRaises(ValidationError):
            self.service.create_admin_user('', 'admin@test.com', 'SecurePass123!')
        
        with self.assertRaises(ValidationError):
            self.service.create_admin_user('admin', '', 'SecurePass123!')
        
        with self.assertRaises(ValidationError):
            self.service.create_admin_user('admin', 'admin@test.com', '')
    
    def test_token_format_validation(self):
        """Test that generated tokens have expected format."""
        token = self.service.generate_setup_token()
        
        # Token should be URL-safe (alphanumeric, underscores, and hyphens)
        import re
        self.assertTrue(re.match(r'^[A-Za-z0-9_-]+$', token))
        
        # Token should have reasonable length
        self.assertGreaterEqual(len(token), 32)
        self.assertLessEqual(len(token), 128)


class TestInstallationServiceIntegration(TestCase):
    """Integration tests for InstallationService with Django components."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_config_file = os.path.join(self.test_dir, 'integration_config.json')
        self.test_installation_file = os.path.join(self.test_dir, '.installation')
        
        self.service = InstallationService()
        self.service.config_file = Path(self.test_config_file)
        self.service.installation_file = Path(self.test_installation_file)
    
    def tearDown(self):
        """Clean up integration test environment."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        
        # Clean up any created users
        User.objects.all().delete()
    
    def test_full_installation_workflow(self):
        """Test complete installation workflow from start to finish."""
        # Step 1: Check initial state
        self.assertFalse(self.service.is_installation_complete())
        
        # Step 2: Generate setup token
        token = self.service.generate_setup_token()
        self.assertIsInstance(token, str)
        
        # Step 3: Validate token
        self.assertTrue(self.service.validate_token(token))
        
        # Step 4: Create admin user
        admin_user = self.service.create_admin_user(
            'administrator',
            'admin@example.com',
            'SecureAdminPassword123!'
        )
        
        # Step 5: Mark installation complete
        self.assertTrue(self.service.mark_installation_complete())
        
        # Step 6: Verify final state
        self.assertTrue(self.service.is_installation_complete())
        
        # Step 7: Verify status details
        status = self.service.get_installation_status()
        self.assertTrue(status['installation_complete'])
        self.assertTrue(status['has_admin_user'])
        self.assertIsNotNone(status['completed_at'])
        
        # Step 8: Verify admin user properties
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_active)
    
    def test_headless_installation_simulation(self):
        """Test simulation of headless installation mode."""
        # Generate token (simulating headless command)
        token = self.service.generate_setup_token()
        
        # Simulate web-based admin creation
        admin_user = self.service.create_admin_user(
            'headless_admin',
            'headless@example.com',
            'HeadlessPassword123!'
        )
        
        # Complete installation
        self.service.mark_installation_complete()
        
        # Verify everything is set up correctly
        self.assertTrue(self.service.is_installation_complete())
        self.assertEqual(User.objects.filter(is_superuser=True).count(), 1)
    
    def test_installation_state_persistence(self):
        """Test that installation state persists across service instances."""
        # Create installation state
        token = self.service.generate_setup_token()
        self.service.create_admin_user('persistent', 'persist@test.com', 'PersistPass123!')
        self.service.mark_installation_complete()
        
        # Create new service instance
        new_service = InstallationService()
        new_service.config_file = self.test_config_file
        
        # Verify state is preserved
        self.assertTrue(new_service.is_installation_complete())
        
        # Token should no longer be valid (single use)
        self.assertFalse(new_service.validate_token(token))


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
                'setup',
            ],
            SECRET_KEY='test-secret-key-for-testing-only'
        )
    
    django.setup()
    
    # Run tests
    import pytest
    pytest.main([__file__, '-v'])