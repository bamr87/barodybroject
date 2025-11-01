"""
File: services.py
Description: Installation wizard service for managing first-time setup and configuration
Author: Barodybroject Team <team@example.com>
Created: 2025-10-30
Last Modified: 2025-10-30
Version: 0.2.0

Dependencies:
- django: >=4.2
- secrets: for secure token generation
- os: for file system operations

Container Requirements:
- Base Image: python:3.11-slim
- Volumes: /app/src:rw (for installation state persistence)
- Environment: DJANGO_SETTINGS_MODULE=barodybroject.settings

Usage: from setup.services import InstallationService
"""

import hashlib
import json
import logging
import os
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

logger = logging.getLogger(__name__)
User = get_user_model()


class InstallationService:
    """
    Service for managing first-time installation and setup wizard
    
    This service provides:
    - Installation state management
    - Secure token generation for headless setup
    - Configuration persistence
    - Setup validation and completion tracking
    """
    
    def __init__(self):
        self.installation_file = Path(settings.BASE_DIR) / '.installation'
        # Use settings path if available, otherwise default
        config_path = getattr(settings, 'INSTALLATION_CONFIG_PATH', Path(settings.BASE_DIR) / '.setup_config.json')
        # Ensure config_file is always a Path object
        if isinstance(config_path, str):
            self.config_file = Path(config_path)
        else:
            self.config_file = config_path
        
    def is_installation_complete(self) -> bool:
        """Check if initial installation has been completed"""
        try:
            if not self.installation_file.exists():
                return False
                
            with open(self.installation_file, 'r') as f:
                data = json.load(f)
                
            return (
                data.get('completed', False) and
                self._validate_installation_integrity(data)
            )
        except Exception as e:
            logger.warning(f"Error checking installation status: {e}")
            return False
    
    def is_admin_created_during_install(self) -> bool:
        """Check if admin user was created during installation process"""
        try:
            if not self.installation_file.exists():
                return False
                
            with open(self.installation_file, 'r') as f:
                data = json.load(f)
                
            return data.get('admin_created', False)
        except Exception as e:
            logger.warning(f"Error checking admin creation status: {e}")
            return False
    
    def generate_setup_token(self, expires_hours: int = 24) -> str:
        """
        Generate secure token for headless setup
        
        Args:
            expires_hours: Token expiration time in hours
            
        Returns:
            Secure token string for setup authentication
        """
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Store token info
        token_data = {
            'token_hash': token_hash,
            'created_at': timezone.now().isoformat(),
            'expires_at': (timezone.now() + timedelta(hours=expires_hours)).isoformat(),
            'used': False
        }
        
        self._save_config({'setup_token': token_data})
        
        logger.info("Setup token generated successfully")
        return token
    
    def validate_setup_token(self, token: str) -> bool:
        """
        Validate setup token for web-based admin creation
        
        Args:
            token: Token to validate
            
        Returns:
            True if token is valid and not expired
        """
        try:
            config = self._load_config()
            token_data = config.get('setup_token', {})
            
            if not token_data or token_data.get('used', True):
                return False
                
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            if token_hash != token_data.get('token_hash'):
                return False
                
            expires_at = datetime.fromisoformat(token_data['expires_at'].replace('Z', '+00:00'))
            if timezone.now() > expires_at:
                logger.warning("Setup token has expired")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error validating setup token: {e}")
            return False
    
    def validate_token(self, token: str) -> bool:
        """Alias for validate_setup_token for backward compatibility"""
        return self.validate_setup_token(token)
    
    def consume_setup_token(self, token: str) -> bool:
        """
        Mark setup token as used (one-time use)
        
        Args:
            token: Token to consume
            
        Returns:
            True if token was valid and consumed
        """
        if not self.validate_setup_token(token):
            return False
            
        try:
            config = self._load_config()
            config['setup_token']['used'] = True
            config['setup_token']['used_at'] = timezone.now().isoformat()
            self._save_config(config)
            
            logger.info("Setup token consumed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error consuming setup token: {e}")
            return False
    
    def save_installation_config(self, config: Dict[str, Any]) -> None:
        """
        Save installation configuration during setup
        
        Args:
            config: Configuration dictionary to save
        """
        try:
            existing_config = self._load_config()
            existing_config.update(config)
            existing_config['last_updated'] = timezone.now().isoformat()
            
            self._save_config(existing_config)
            logger.info("Installation configuration saved")
            
        except Exception as e:
            logger.error(f"Error saving installation config: {e}")
            raise ValidationError(f"Failed to save configuration: {e}")
    
    def mark_installation_complete(self, admin_user_id: Optional[int] = None) -> bool:
        """
        Mark installation as complete
        
        Args:
            admin_user_id: Optional admin user ID to associate with installation
            
        Returns:
            True if installation was marked complete successfully
        """
        try:
            # Verify admin user exists
            if admin_user_id:
                User.objects.get(id=admin_user_id, is_superuser=True)
            
            installation_data = {
                'completed': True,
                'completed_at': timezone.now().isoformat(),
                'admin_created': self.admin_user_created,
                'installation_id': secrets.token_hex(16),
                'version': '0.2.0'
            }
            
            with open(self.installation_file, 'w') as f:
                json.dump(installation_data, f, indent=2)
                
            logger.info("Installation marked as complete")
            return True
            
        except User.DoesNotExist:
            raise ValidationError("Admin user not found")
        except Exception as e:
            logger.error(f"Error marking installation complete: {e}")
            raise ValidationError(f"Failed to complete installation: {e}")
    
    def get_installation_status(self) -> Dict[str, Any]:
        """Get detailed installation status information"""
        try:
            # Get basic installation info
            if self.installation_file.exists():
                with open(self.installation_file, 'r') as f:
                    installation_data = json.load(f)
            else:
                installation_data = {}
            
            # Check if admin user exists
            has_admin_user = User.objects.filter(is_superuser=True).exists()
            
            # Return standardized status format
            return {
                'installation_complete': installation_data.get('completed', False),
                'completed_at': installation_data.get('completed_at'),
                'has_admin_user': has_admin_user,
                'admin_created_during_install': installation_data.get('admin_created', False),
                'installation_id': installation_data.get('installation_id'),
                'version': installation_data.get('version', '0.2.0')
            }
        except Exception as e:
            logger.error(f"Error getting installation status: {e}")
            return {
                'installation_complete': False,
                'completed_at': None,
                'has_admin_user': False,
                'admin_created_during_install': False,
                'installation_id': None,
                'version': '0.2.0',
                'error': str(e)
            }
    
    def get_installation_info(self) -> Dict[str, Any]:
        """Get current installation information"""
        try:
            if self.installation_file.exists():
                with open(self.installation_file, 'r') as f:
                    return json.load(f)
            return {'completed': False}
        except Exception as e:
            logger.error(f"Error reading installation info: {e}")
            return {'completed': False, 'error': str(e)}
    
    def get_setup_progress(self) -> Dict[str, Any]:
        """Get current setup progress and requirements"""
        progress = {
            'database_ready': self._check_database_ready(),
            'migrations_applied': self._check_migrations_applied(),
            'admin_exists': self._check_admin_exists(),
            'installation_complete': self.is_installation_complete(),
        }
        
        progress['ready_for_admin_creation'] = (
            progress['database_ready'] and 
            progress['migrations_applied'] and 
            not progress['admin_exists']
        )
        
        return progress
    
    def create_admin_user(self, username: str, email: str, password: str, 
                         first_name: str = '', last_name: str = ''):
        """
        Create superuser account during setup
        
        Args:
            username: Admin username
            email: Admin email address
            password: Admin password
            first_name: Optional first name
            last_name: Optional last name
            
        Returns:
            Created User instance
            
        Raises:
            ValidationError: If user creation fails or admin already exists
        """
        try:
            # Check if admin already exists
            if User.objects.filter(is_superuser=True).exists():
                raise ValidationError("Admin user already exists")
            
            # Validate required fields
            if not all([username, email, password]):
                raise ValidationError("Username, email, and password are required")
            
            # Validate email format
            from django.core.validators import validate_email
            try:
                validate_email(email)
            except Exception:
                raise ValidationError("Invalid email format")
            
            # Validate password strength
            if len(password) < 8:
                raise ValidationError("Password must be at least 8 characters long")
            
            # Create superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            logger.info(f"Admin user '{username}' created successfully")
            return user
            
        except Exception as e:
            logger.error(f"Error creating admin user: {e}")
            raise ValidationError(f"Failed to create admin user: {e}")
    
    def cleanup_expired_tokens(self) -> None:
        """Clean up expired setup tokens"""
        try:
            config = self._load_config()
            token_data = config.get('setup_token', {})
            
            if token_data:
                expires_at = datetime.fromisoformat(token_data['expires_at'].replace('Z', '+00:00'))
                if timezone.now() > expires_at:
                    del config['setup_token']
                    self._save_config(config)
                    logger.info("Expired setup token cleaned up")
                    
        except Exception as e:
            logger.warning(f"Error cleaning up tokens: {e}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.warning(f"Error loading config: {e}")
            return {}
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file"""
        try:
            # Ensure config_file is a Path object
            if isinstance(self.config_file, str):
                self.config_file = Path(self.config_file)
            
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            raise
    
    def _validate_installation_integrity(self, data: Dict[str, Any]) -> bool:
        """Validate installation data integrity"""
        required_fields = ['completed', 'completed_at', 'installation_id', 'version']
        return all(field in data for field in required_fields)
    
    def _check_database_ready(self) -> bool:
        """Check if database connection is working"""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    def _check_migrations_applied(self) -> bool:
        """Check if Django migrations have been applied"""
        try:
            import sys
            from io import StringIO

            from django.core.management import execute_from_command_line

            # Capture output
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            try:
                execute_from_command_line(['manage.py', 'showmigrations', '--plan'])
                output = sys.stdout.getvalue()
                return '[X]' in output  # Applied migrations show [X]
            finally:
                sys.stdout = old_stdout
                
        except Exception:
            return False
    
    def _check_admin_exists(self) -> bool:
        """Check if admin user exists"""
        try:
            return User.objects.filter(is_superuser=True).exists()
        except Exception:
            return False