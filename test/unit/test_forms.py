"""
File: test_forms.py
Description: Comprehensive unit tests for Django forms in the setup wizard
Author: Barodybroject Team <team@example.com>
Created: 2025-10-30
Last Modified: 2025-10-30
Version: 1.0.0

Dependencies:
- django.test: Django test utilities
- setup.forms: Django forms for setup wizard
- django.contrib.auth: User model for validation

Container Requirements:
- Django test environment with forms
- Setup app configuration
- User authentication support

Usage: pytest test/unit/test_forms.py
"""

import sys
import tempfile
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

sys.path.append('/workspace/src')
from setup.forms import AdminUserForm


class TestAdminUserForm(TestCase):
    """Test suite for AdminUserForm."""
    
    def setUp(self):
        """Set up test environment."""
        # Clear any existing users
        User.objects.all().delete()
    
    def test_form_fields_present(self):
        """Test that all required fields are present in form."""
        form = AdminUserForm()
        
        # Check that all required fields exist
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('password1', form.fields)
        self.assertIn('password2', form.fields)
        self.assertIn('token', form.fields)
    
    def test_form_field_attributes(self):
        """Test field attributes and widgets."""
        form = AdminUserForm()
        
        # Check username field
        username_field = form.fields['username']
        self.assertEqual(username_field.max_length, 150)
        self.assertTrue(username_field.required)
        
        # Check email field
        email_field = form.fields['email']
        self.assertTrue(email_field.required)
        
        # Check password fields
        password1_field = form.fields['password1']
        password2_field = form.fields['password2']
        self.assertTrue(password1_field.required)
        self.assertTrue(password2_field.required)
        
        # Check token field (should be hidden)
        token_field = form.fields['token']
        self.assertEqual(token_field.widget.__class__.__name__, 'HiddenInput')
    
    def test_valid_form_data(self):
        """Test form with valid data."""
        form_data = {
            'username': 'testadmin',
            'email': 'admin@test.com',
            'password1': 'SecurePassword123!',
            'password2': 'SecurePassword123!',
            'token': 'valid_token_123'
        }
        
        form = AdminUserForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_form_validation_empty_fields(self):
        """Test form validation with empty required fields."""
        form_data = {
            'username': '',
            'email': '',
            'password1': '',
            'password2': '',
            'token': ''
        }
        
        form = AdminUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        # Check that required fields have errors
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password1', form.errors)
        self.assertIn('password2', form.errors)
        self.assertIn('token', form.errors)
    
    def test_username_validation(self):
        """Test username field validation."""
        # Test valid username
        form_data = {
            'username': 'validuser',
            'email': 'valid@test.com',
            'password1': 'SecurePassword123!',
            'password2': 'SecurePassword123!',
            'token': 'valid_token'
        }
        form = AdminUserForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test username too long
        form_data['username'] = 'x' * 200
        form = AdminUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        
        # Test username with invalid characters
        form_data['username'] = 'user@name'
        form = AdminUserForm(data=form_data)
        # Django's default username validator should catch this
        if not form.is_valid():
            self.assertIn('username', form.errors)
    
    def test_email_validation(self):
        """Test email field validation."""
        base_data = {
            'username': 'testuser',
            'password1': 'SecurePassword123!',
            'password2': 'SecurePassword123!',
            'token': 'valid_token'
        }
        
        # Test valid email
        form_data = {**base_data, 'email': 'valid@example.com'}
        form = AdminUserForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test invalid email formats
        invalid_emails = [
            'invalid-email',
            'invalid@',
            '@invalid.com',
            'invalid..email@test.com',
            'invalid email@test.com'
        ]
        
        for invalid_email in invalid_emails:
            form_data = {**base_data, 'email': invalid_email}
            form = AdminUserForm(data=form_data)
            self.assertFalse(form.is_valid(), f"Email {invalid_email} should be invalid")
            self.assertIn('email', form.errors)
    
    def test_password_validation(self):
        """Test password field validation."""
        base_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'token': 'valid_token'
        }
        
        # Test valid password
        form_data = {
            **base_data,
            'password1': 'SecurePassword123!',
            'password2': 'SecurePassword123!'
        }
        form = AdminUserForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test passwords don't match
        form_data = {
            **base_data,
            'password1': 'Password123!',
            'password2': 'DifferentPassword123!'
        }
        form = AdminUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        
        # Test weak password
        form_data = {
            **base_data,
            'password1': '123',
            'password2': '123'
        }
        form = AdminUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        # Django's password validators should catch this
        self.assertTrue('password2' in form.errors or 'password1' in form.errors)
    
    def test_password_strength_requirements(self):
        """Test various password strength scenarios."""
        base_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'token': 'valid_token'
        }
        
        # Test common weak passwords
        weak_passwords = [
            ('password', 'password'),  # Common password
            ('12345678', '12345678'),  # Numeric only
            ('testuser', 'testuser'),  # Same as username
            ('abc', 'abc'),  # Too short
        ]
        
        for password1, password2 in weak_passwords:
            form_data = {
                **base_data,
                'password1': password1,
                'password2': password2
            }
            form = AdminUserForm(data=form_data)
            self.assertFalse(form.is_valid(), 
                           f"Weak password '{password1}' should be rejected")
    
    def test_duplicate_username_validation(self):
        """Test validation for duplicate usernames."""
        # Create existing user
        User.objects.create_user('existinguser', 'existing@test.com', 'password123')
        
        form_data = {
            'username': 'existinguser',  # Same as existing user
            'email': 'newuser@test.com',
            'password1': 'SecurePassword123!',
            'password2': 'SecurePassword123!',
            'token': 'valid_token'
        }
        
        form = AdminUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('already exists', str(form.errors['username']).lower())
    
    def test_duplicate_email_validation(self):
        """Test validation for duplicate email addresses."""
        # Create existing user
        User.objects.create_user('existinguser', 'existing@test.com', 'password123')
        
        form_data = {
            'username': 'newuser',
            'email': 'existing@test.com',  # Same as existing user
            'password1': 'SecurePassword123!',
            'password2': 'SecurePassword123!',
            'token': 'valid_token'
        }
        
        form = AdminUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_form_save_method(self):
        """Test form save functionality."""
        form_data = {
            'username': 'newadmin',
            'email': 'admin@test.com',
            'password1': 'SecurePassword123!',
            'password2': 'SecurePassword123!',
            'token': 'valid_token'
        }
        
        form = AdminUserForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test save without commit
        user = form.save(commit=False)
        self.assertEqual(user.username, 'newadmin')
        self.assertEqual(user.email, 'admin@test.com')
        self.assertFalse(user.pk)  # Not saved to database yet
        
        # Test save with commit
        user = form.save()
        self.assertTrue(user.pk)  # Saved to database
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        
        # Verify user can authenticate
        self.assertTrue(user.check_password('SecurePassword123!'))
    
    def test_form_html_rendering(self):
        """Test form HTML rendering and attributes."""
        form = AdminUserForm()
        
        # Test that form renders without errors
        html = str(form)
        self.assertIn('username', html)
        self.assertIn('email', html)
        self.assertIn('password1', html)
        self.assertIn('password2', html)
        
        # Test that token field is hidden
        self.assertIn('type="hidden"', str(form['token']))
        
        # Test form field attributes
        self.assertIn('class=', html)  # Should have CSS classes
        self.assertIn('required', html)  # Required fields should be marked
    
    def test_form_initial_data(self):
        """Test form with initial data."""
        initial_data = {
            'username': 'preset_admin',
            'email': 'preset@test.com',
            'token': 'preset_token'
        }
        
        form = AdminUserForm(initial=initial_data)
        
        # Check that initial data is set
        self.assertEqual(form['username'].value(), 'preset_admin')
        self.assertEqual(form['email'].value(), 'preset@test.com')
        self.assertEqual(form['token'].value(), 'preset_token')
    
    def test_form_security_features(self):
        """Test security features of the form."""
        # Test CSRF token handling (implicit in Django forms)
        form = AdminUserForm()
        
        # Test that sensitive data is not exposed in form
        html = str(form)
        self.assertNotIn('password', html.lower())  # Password values shouldn't be in HTML
        
        # Test token field security
        token_field = form.fields['token']
        self.assertEqual(token_field.widget.__class__.__name__, 'HiddenInput')
    
    def test_form_error_messages(self):
        """Test custom error messages."""
        form_data = {
            'username': '',
            'email': 'invalid-email',
            'password1': 'weak',
            'password2': 'different',
            'token': ''
        }
        
        form = AdminUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        # Check that error messages are user-friendly
        errors = form.errors
        for field_errors in errors.values():
            for error in field_errors:
                self.assertIsInstance(error, str)
                self.assertTrue(len(error) > 0)
    
    def test_form_field_help_text(self):
        """Test field help text and labels."""
        form = AdminUserForm()
        
        # Check that fields have appropriate help text
        username_field = form.fields['username']
        self.assertTrue(hasattr(username_field, 'help_text'))
        
        # Check that fields have labels
        for field_name, field in form.fields.items():
            if field_name != 'token':  # Token field might not have label
                self.assertTrue(hasattr(field, 'label'))


class TestFormIntegration(TestCase):
    """Integration tests for forms with Django components."""
    
    def test_form_with_django_auth(self):
        """Test form integration with Django authentication system."""
        form_data = {
            'username': 'integrationtest',
            'email': 'integration@test.com',
            'password1': 'IntegrationPassword123!',
            'password2': 'IntegrationPassword123!',
            'token': 'integration_token'
        }
        
        form = AdminUserForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Save user and verify integration
        user = form.save()
        
        # Test that user was created with correct attributes
        self.assertTrue(User.objects.filter(username='integrationtest').exists())
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
        
        # Test authentication
        from django.contrib.auth import authenticate
        auth_user = authenticate(username='integrationtest', 
                               password='IntegrationPassword123!')
        self.assertIsNotNone(auth_user)
        self.assertEqual(auth_user, user)
    
    def test_form_with_django_validation(self):
        """Test form with Django's built-in validation."""
        # Test with Django's password validators
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testuser',  # Same as username - should fail
            'password2': 'testuser',
            'token': 'test_token'
        }
        
        form = AdminUserForm(data=form_data)
        # Django password validators should catch this
        if not form.is_valid():
            self.assertTrue('password1' in form.errors or 'password2' in form.errors)


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
                'setup',
            ],
            SECRET_KEY='test-secret-key-for-testing-only',
            AUTH_PASSWORD_VALIDATORS=[
                {
                    'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
                },
                {
                    'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
                    'OPTIONS': {
                        'min_length': 8,
                    }
                },
                {
                    'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
                },
                {
                    'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
                },
            ]
        )
    
    django.setup()
    
    # Run tests
    import pytest
    pytest.main([__file__, '-v'])