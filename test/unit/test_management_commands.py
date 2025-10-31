"""
File: test_management_commands.py
Description: Comprehensive tests for setup_wizard management command
Author: Barodybroject Team <team@example.com>
Created: 2025-10-30
Last Modified: 2025-10-30
Version: 1.0.0

Dependencies:
- pytest: Test framework
- django.test: Django test utilities
- django.core.management: Management command testing

Container Requirements:
- Django test environment with management commands
- Setup app and command available
- Mock user input capabilities

Usage: pytest test/unit/test_management_commands.py
"""

import os
# Import the command and service we're testing
import sys
import tempfile
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

sys.path.append('/workspace/src')
from setup.management.commands.setup_wizard import Command
from setup.services import InstallationService


class TestSetupWizardCommand(TestCase):
    """Test suite for setup_wizard management command."""
    
    def setUp(self):
        """Set up test environment."""
        self.command = Command()
        self.output = StringIO()
        
        # Create temporary config for testing
        self.test_dir = tempfile.mkdtemp()
        self.test_config_file = os.path.join(self.test_dir, 'test_setup_config.json')
        
        # Clean any existing users
        User.objects.all().delete()
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)
        os.rmdir(self.test_dir)
    
    def test_command_help_text(self):
        """Test command help text is informative and comprehensive."""
        help_text = self.command.help
        self.assertIn('installation wizard', help_text.lower())
        self.assertIn('setup', help_text.lower())
        self.assertIsNotNone(help_text)
        self.assertGreater(len(help_text), 20)
    
    def test_command_arguments_parser(self):
        """Test command line argument parsing."""
        parser = self.command.create_parser('manage.py', 'setup_wizard')
        
        # Test headless argument
        args = parser.parse_args(['--headless'])
        self.assertTrue(args.headless)
        
        # Test force argument
        args = parser.parse_args(['--force'])
        self.assertTrue(args.force)
        
        # Test quiet argument
        args = parser.parse_args(['--quiet'])
        self.assertTrue(args.quiet)
        
        # Test combined arguments
        args = parser.parse_args(['--headless', '--force', '--quiet'])
        self.assertTrue(args.headless)
        self.assertTrue(args.force)
        self.assertTrue(args.quiet)
    
    def test_headless_mode_token_generation(self):
        """Test headless mode generates and displays token."""
        with patch('setup.services.InstallationService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.is_installation_complete.return_value = False
            mock_service.generate_setup_token.return_value = 'test_token_abc123'
            
            call_command('setup_wizard', '--headless', stdout=self.output)
            
            # Verify service methods were called
            mock_service.generate_setup_token.assert_called_once()
            
            # Verify output contains required information
            output_content = self.output.getvalue()
            self.assertIn('headless', output_content.lower())
            self.assertIn('test_token_abc123', output_content)
            self.assertIn('complete setup at:', output_content.lower())
    
    def test_force_option_bypasses_completion_check(self):
        """Test force option allows reinstallation."""
        with patch('setup.services.InstallationService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.is_installation_complete.return_value = True  # Already complete
            
            with patch('builtins.input', side_effect=[
                'forcedadmin', 'forced@example.com', 'ForcePassword123!', 'ForcePassword123!'
            ]):
                call_command('setup_wizard', '--force', stdout=self.output)
            
            # Verify service methods were called despite installation being complete
            mock_service.create_admin_user.assert_called()
            mock_service.mark_installation_complete.assert_called()
    
    def test_quiet_mode_suppresses_output(self):
        """Test quiet mode suppresses all output."""
        with patch('setup.services.InstallationService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.is_installation_complete.return_value = True
            
            call_command('setup_wizard', '--quiet', stdout=self.output)
            
            output_content = self.output.getvalue()
            self.assertEqual(output_content.strip(), '')
    
    def test_installation_already_complete_message(self):
        """Test appropriate message when installation is already complete."""
        with patch('setup.services.InstallationService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.is_installation_complete.return_value = True
            
            call_command('setup_wizard', stdout=self.output)
            
            output_content = self.output.getvalue()
            self.assertIn('already complete', output_content.lower())
            
            # Should not call user creation methods
            mock_service.create_admin_user.assert_not_called()
    
    @patch('builtins.input')
    def test_interactive_mode_successful_flow(self, mock_input):
        """Test complete interactive mode flow with valid inputs."""
        # Mock user inputs
        mock_input.side_effect = [
            'interactiveadmin',       # username
            'interactive@test.com',   # email
            'InteractivePass123!',    # password
            'InteractivePass123!',    # password confirmation
        ]
        
        with patch('setup.services.InstallationService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.is_installation_complete.return_value = False
            
            # Mock successful user creation
            mock_user = MagicMock()
            mock_user.username = 'interactiveadmin'
            mock_service.create_admin_user.return_value = mock_user
            
            call_command('setup_wizard', stdout=self.output)
            
            # Verify correct service calls
            mock_service.create_admin_user.assert_called_once_with(
                'interactiveadmin', 'interactive@test.com', 'InteractivePass123!'
            )
            mock_service.mark_installation_complete.assert_called_once()
            
            # Verify success message
            output_content = self.output.getvalue()
            self.assertIn('success', output_content.lower())
    
    @patch('builtins.input')
    def test_password_mismatch_retry_logic(self, mock_input):
        """Test password mismatch detection and retry mechanism."""
        # Mock password mismatch then correct entry
        mock_input.side_effect = [
            'retryadmin',             # username
            'retry@test.com',         # email
            'RetryPassword123!',      # password
            'WrongPassword456!',      # password confirmation (mismatch)
            'RetryPassword123!',      # password (retry)
            'RetryPassword123!',      # password confirmation (match)
        ]
        
        with patch('setup.services.InstallationService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.is_installation_complete.return_value = False
            mock_service.create_admin_user.return_value = MagicMock()
            
            call_command('setup_wizard', stdout=self.output)
            
            output_content = self.output.getvalue()
            self.assertIn('passwords do not match', output_content.lower())
            
            # Should eventually succeed with correct password
            mock_service.create_admin_user.assert_called_once_with(
                'retryadmin', 'retry@test.com', 'RetryPassword123!'
            )
    
    @patch('builtins.input')
    def test_invalid_email_retry_logic(self, mock_input):
        """Test invalid email detection and retry mechanism."""
        # Mock invalid email then valid email
        mock_input.side_effect = [
            'emailadmin',             # username
            'invalid-email-format',   # invalid email
            'valid@test.com',         # valid email
            'EmailPassword123!',      # password
            'EmailPassword123!',      # password confirmation
        ]
        
        with patch('setup.services.InstallationService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.is_installation_complete.return_value = False
            mock_service.create_admin_user.return_value = MagicMock()
            
            call_command('setup_wizard', stdout=self.output)
            
            output_content = self.output.getvalue()
            self.assertIn('valid email', output_content.lower())
            
            # Should succeed with valid email
            mock_service.create_admin_user.assert_called_once_with(
                'emailadmin', 'valid@test.com', 'EmailPassword123!'
            )
    
    @patch('builtins.input')
    def test_empty_input_validation(self, mock_input):
        """Test handling of empty inputs with retry logic."""
        # Mock empty inputs then valid inputs
        mock_input.side_effect = [
            '',                       # empty username
            'validadmin',             # valid username
            '',                       # empty email
            'valid@test.com',         # valid email
            '',                       # empty password
            'ValidPassword123!',      # valid password
            'ValidPassword123!',      # password confirmation
        ]
        
        with patch('setup.services.InstallationService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.is_installation_complete.return_value = False
            mock_service.create_admin_user.return_value = MagicMock()
            
            call_command('setup_wizard', stdout=self.output)
            
            output_content = self.output.getvalue()
            # Should show validation messages for empty inputs
            self.assertIn('required', output_content.lower())
    
    def test_database_connection_validation(self):
        """Test database connection is validated before proceeding."""
        with patch('django.db.connection.ensure_connection', side_effect=Exception('DB Connection Error')):
            with self.assertRaises(CommandError) as context:
                call_command('setup_wizard', stdout=self.output)
            
            self.assertIn('database', str(context.exception).lower())
    
    def test_system_requirements_check(self):
        """Test system requirements validation."""
        with patch('setup.services.InstallationService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.is_installation_complete.return_value = False
            
            # Mock system requirements check
            with patch.object(self.command, '_check_system_requirements') as mock_check:
                mock_check.return_value = True
                
                with patch('builtins.input', side_effect=[
                    'sysadmin', 'sys@test.com', 'SysPassword123!', 'SysPassword123!'
                ]):
                    call_command('setup_wizard', stdout=self.output)
                
                # Verify system check was called
                mock_check.assert_called_once()
    
    def test_service_exception_handling(self):
        """Test graceful handling of service exceptions."""
        with patch('setup.services.InstallationService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.is_installation_complete.return_value = False
            
            # Mock service exception during user creation
            mock_service.create_admin_user.side_effect = Exception('Service failure')
            
            with patch('builtins.input', side_effect=[
                'erroradmin', 'error@test.com', 'ErrorPassword123!', 'ErrorPassword123!'
            ]):
                with self.assertRaises(CommandError):
                    call_command('setup_wizard', stdout=self.output)
    
    def test_verbosity_levels(self):
        """Test different verbosity levels."""
        with patch('setup.services.InstallationService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.is_installation_complete.return_value = True
            
            # Test verbosity 0 (quiet)
            output_quiet = StringIO()
            call_command('setup_wizard', verbosity=0, stdout=output_quiet)
            self.assertEqual(output_quiet.getvalue().strip(), '')
            
            # Test verbosity 2 (verbose)
            output_verbose = StringIO()
            call_command('setup_wizard', verbosity=2, stdout=output_verbose)
            verbose_content = output_verbose.getvalue()
            self.assertGreater(len(verbose_content), 0)


class TestSetupWizardCommandIntegration(TestCase):
    """Integration tests for setup_wizard command with real services."""
    
    def setUp(self):
        """Set up integration test environment."""
        # Clean up any existing users
        User.objects.all().delete()
        
        # Create temporary directory for test configuration
        self.test_dir = tempfile.mkdtemp()
        self.test_config_file = os.path.join(self.test_dir, 'integration_config.json')
    
    def tearDown(self):
        """Clean up integration test environment."""
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)
        os.rmdir(self.test_dir)
        
        # Clean up users
        User.objects.all().delete()
    
    def test_complete_installation_workflow(self):
        """Test complete installation workflow from start to finish."""
        # Mock service to use test config file
        with patch.object(InstallationService, '_get_config_file_path', return_value=self.test_config_file):
            with patch('builtins.input', side_effect=[
                'workflowadmin',
                'workflow@integration.com',
                'WorkflowPassword123!',
                'WorkflowPassword123!',
            ]):
                output = StringIO()
                call_command('setup_wizard', '--force', stdout=output)
            
            # Verify user was created in database
            user = User.objects.get(username='workflowadmin')
            self.assertEqual(user.email, 'workflow@integration.com')
            self.assertTrue(user.is_staff)
            self.assertTrue(user.is_superuser)
            self.assertTrue(user.is_active)
            
            # Verify installation status
            service = InstallationService()
            service._get_config_file_path = lambda: self.test_config_file
            self.assertTrue(service.is_installation_complete())
    
    def test_headless_mode_with_real_service(self):
        """Test headless mode integration with real InstallationService."""
        with patch.object(InstallationService, '_get_config_file_path', return_value=self.test_config_file):
            output = StringIO()
            call_command('setup_wizard', '--headless', '--force', stdout=output)
            
            output_content = output.getvalue()
            
            # Verify required elements in output
            self.assertIn('Installation token:', output_content)
            self.assertIn('Complete setup at:', output_content)
            self.assertIn('Token expires:', output_content)
            
            # Extract and validate token
            lines = output_content.split('\n')
            token_line = next(line for line in lines if 'Installation token:' in line)
            token = token_line.split('Installation token:')[1].strip()
            
            # Verify token can be validated
            service = InstallationService()
            service._get_config_file_path = lambda: self.test_config_file
            self.assertTrue(service.validate_token(token))
    
    def test_installation_persistence_across_commands(self):
        """Test that installation state persists across command invocations."""
        with patch.object(InstallationService, '_get_config_file_path', return_value=self.test_config_file):
            # First run: complete installation
            with patch('builtins.input', side_effect=[
                'persistadmin', 'persist@integration.com', 'PersistPassword123!', 'PersistPassword123!'
            ]):
                output1 = StringIO()
                call_command('setup_wizard', '--force', stdout=output1)
            
            # Second run: should detect installation is complete
            output2 = StringIO()
            call_command('setup_wizard', stdout=output2)
            
            output2_content = output2.getvalue()
            self.assertIn('already complete', output2_content.lower())
    
    def test_force_reinstallation_workflow(self):
        """Test force reinstallation over existing installation."""
        with patch.object(InstallationService, '_get_config_file_path', return_value=self.test_config_file):
            # First installation
            with patch('builtins.input', side_effect=[
                'originaladmin', 'original@integration.com', 'OriginalPassword123!', 'OriginalPassword123!'
            ]):
                call_command('setup_wizard', '--force', stdout=StringIO())
            
            # Verify first user exists
            original_user = User.objects.get(username='originaladmin')
            self.assertIsNotNone(original_user)
            
            # Force reinstallation with different user
            with patch('builtins.input', side_effect=[
                'newadmin', 'new@integration.com', 'NewPassword123!', 'NewPassword123!'
            ]):
                call_command('setup_wizard', '--force', stdout=StringIO())
            
            # Verify new user exists (original should still exist too)
            new_user = User.objects.get(username='newadmin')
            self.assertIsNotNone(new_user)
            
            # Both users should be superusers
            self.assertTrue(User.objects.get(username='originaladmin').is_superuser)
            self.assertTrue(User.objects.get(username='newadmin').is_superuser)


@pytest.mark.django_db
class TestSetupWizardCommandPytest:
    """Pytest-style tests for setup_wizard command."""
    
    def test_command_import_success(self):
        """Test that the setup_wizard command can be imported."""
        from setup.management.commands.setup_wizard import Command
        assert Command is not None
        assert hasattr(Command, 'handle')
    
    def test_command_has_required_methods(self):
        """Test command has all required methods."""
        from setup.management.commands.setup_wizard import Command
        command = Command()
        
        # Standard Django command methods
        assert hasattr(command, 'handle')
        assert hasattr(command, 'add_arguments')
        assert callable(command.handle)
        assert callable(command.add_arguments)
    
    def test_command_line_options_comprehensive(self):
        """Test all command line options are properly configured."""
        from setup.management.commands.setup_wizard import Command
        command = Command()
        parser = command.create_parser('manage.py', 'setup_wizard')
        
        # Test all boolean flags
        args = parser.parse_args(['--headless', '--force', '--quiet'])
        assert args.headless is True
        assert args.force is True
        assert args.quiet is True
        
        # Test default values
        args = parser.parse_args([])
        assert args.headless is False
        assert args.force is False
        assert args.quiet is False
    
    @patch('setup.services.InstallationService')
    def test_token_generation_and_format(self, mock_service_class):
        """Test token generation produces correct format."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.is_installation_complete.return_value = False
        
        # Mock realistic token
        test_token = 'a' * 64  # Typical SHA256 hex length
        mock_service.generate_setup_token.return_value = test_token
        
        output = StringIO()
        call_command('setup_wizard', '--headless', stdout=output)
        
        output_content = output.getvalue()
        assert 'Installation token:' in output_content
        assert test_token in output_content
        assert 'Complete setup at:' in output_content
        assert 'Token expires:' in output_content
    
    @patch('builtins.input')
    @patch('setup.services.InstallationService')
    def test_user_input_edge_cases(self, mock_service_class, mock_input):
        """Test edge cases in user input handling."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.is_installation_complete.return_value = False
        mock_service.create_admin_user.return_value = MagicMock()
        
        # Test whitespace handling
        mock_input.side_effect = [
            '  spacedadmin  ',        # username with spaces
            '  spaced@test.com  ',    # email with spaces
            'SpacedPassword123!',     # password
            'SpacedPassword123!',     # password confirmation
        ]
        
        output = StringIO()
        call_command('setup_wizard', stdout=output)
        
        # Verify service called with trimmed values
        mock_service.create_admin_user.assert_called_once_with(
            'spacedadmin', 'spaced@test.com', 'SpacedPassword123!'
        )
    
    def test_command_error_codes(self):
        """Test command returns appropriate error codes."""
        # This would test actual command return codes in a more complex setup
        # For now, verify exceptions are raised appropriately
        
        with patch('django.db.connection.ensure_connection', side_effect=Exception('DB Error')):
            with pytest.raises(CommandError):
                call_command('setup_wizard')


if __name__ == '__main__':
    # Run with pytest
    pytest.main([__file__, '-v'])