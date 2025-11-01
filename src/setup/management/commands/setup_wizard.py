"""
File: setup_wizard.py
Description: Django management command for first-time installation wizard
Author: Barodybroject Team <team@example.com>
Created: 2025-10-30
Last Modified: 2025-10-30
Version: 0.2.0

Dependencies:
- django.core.management: Base command functionality
- setup.services: Installation service
- getpass: Secure password input

Container Requirements:
- Interactive terminal for non-headless mode
- Volume persistence for installation state

Usage: 
  python manage.py setup_wizard            # Interactive mode
  python manage.py setup_wizard --headless # Headless mode
"""

import getpass
import logging
import os
import sys

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import execute_from_command_line
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from setup.services import InstallationService

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    """
    Django management command for setting up the application on first run
    
    Supports both interactive and headless installation modes:
    - Interactive: Prompts for configuration and admin user creation
    - Headless: Generates setup token for web-based admin creation
    """
    
    help = 'Run first-time installation wizard for Barodybroject'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--headless',
            action='store_true',
            help='Run in headless mode (generates setup token for web-based admin creation)',
        )
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Skip running database migrations',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force setup even if installation appears complete',
        )
        parser.add_argument(
            '--token-expires',
            type=int,
            default=24,
            help='Token expiration time in hours for headless mode (default: 24)',
        )
    
    def handle(self, *args, **options):
        """Main command handler"""
        try:
            self.setup_service = InstallationService()
            self.options = options
            
            # Check if installation is already complete
            if self.setup_service.is_installation_complete() and not options['force']:
                self.stdout.write(
                    self.style.SUCCESS('✓ Installation already complete!')
                )
                self._show_admin_info()
                return
            
            self.stdout.write(
                self.style.HTTP_INFO('🚀 Starting Barodybroject Installation Wizard')
            )
            self._print_separator()
            
            # Run setup based on mode
            if options['headless']:
                self._run_headless_setup()
            else:
                self._run_interactive_setup()
                
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.ERROR('\n❌ Installation cancelled by user')
            )
            sys.exit(1)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Installation failed: {e}')
            )
            logger.exception("Installation wizard failed")
            sys.exit(1)
    
    def _run_interactive_setup(self):
        """Run interactive installation wizard"""
        self.stdout.write(
            self.style.HTTP_INFO('🔧 Interactive Installation Mode')
        )
        self._print_separator()
        
        # Step 1: System checks
        self._perform_system_checks()
        
        # Step 2: Database setup
        self._setup_database()
        
        # Step 3: Admin user creation
        self._create_admin_user_interactive()
        
        # Step 4: Finalize installation
        self._finalize_installation()
        
        # Step 5: Display completion message
        self._show_completion_message()
    
    def _run_headless_setup(self):
        """Run headless installation (generates setup token)"""
        self.stdout.write(
            self.style.HTTP_INFO('🤖 Headless Installation Mode')
        )
        self._print_separator()
        
        # Step 1: System checks
        self._perform_system_checks()
        
        # Step 2: Database setup
        self._setup_database()
        
        # Step 3: Generate setup token
        token = self.setup_service.generate_setup_token(
            expires_hours=self.options['token_expires']
        )
        
        # Step 4: Display setup instructions
        self._show_headless_instructions(token)
    
    def _perform_system_checks(self):
        """Perform system and database checks"""
        self.stdout.write('📋 Performing system checks...')
        
        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(
                self.style.SUCCESS('  ✓ Database connection: OK')
            )
        except Exception as e:
            raise CommandError(f'Database connection failed: {e}')
        
        # Check Django installation
        try:
            import django
            self.stdout.write(
                self.style.SUCCESS(f'  ✓ Django version: {django.get_version()}')
            )
        except ImportError:
            raise CommandError('Django not properly installed')
        
        # Check for existing admin users
        admin_count = User.objects.filter(is_superuser=True).count()
        if admin_count > 0 and not self.options['force']:
            self.stdout.write(
                self.style.WARNING(f'  ⚠ Found {admin_count} existing admin user(s)')
            )
            if not self.options['headless']:
                if not self._confirm_action('Continue anyway?'):
                    self.stdout.write(
                        self.style.ERROR('Installation cancelled')
                    )
                    sys.exit(0)
        else:
            self.stdout.write(
                self.style.SUCCESS('  ✓ No existing admin users')
            )
    
    def _setup_database(self):
        """Setup database and run migrations"""
        if self.options['skip_migrations']:
            self.stdout.write(
                self.style.WARNING('⏭ Skipping database migrations')
            )
            return
        
        self.stdout.write('🗄 Setting up database...')
        
        try:
            # Run migrations
            execute_from_command_line(['manage.py', 'migrate', '--noinput'])
            self.stdout.write(
                self.style.SUCCESS('  ✓ Database migrations applied')
            )
        except Exception as e:
            raise CommandError(f'Database migration failed: {e}')
    
    def _create_admin_user_interactive(self):
        """Create admin user through interactive prompts"""
        self.stdout.write('👤 Creating admin user...')
        self._print_separator()
        
        # Get admin user details
        username = self._get_input('Admin username', required=True)
        email = self._get_input('Admin email', required=True)
        first_name = self._get_input('First name (optional)', required=False)
        last_name = self._get_input('Last name (optional)', required=False)
        
        # Get password with confirmation
        password = self._get_password()
        
        try:
            user = self.setup_service.create_admin_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'  ✓ Admin user "{username}" created successfully')
            )
            
            # Store user ID for completion
            self.admin_user_id = user.id
            
        except ValidationError as e:
            raise CommandError(f'Failed to create admin user: {e}')
    
    def _finalize_installation(self):
        """Mark installation as complete"""
        self.stdout.write('🏁 Finalizing installation...')
        
        try:
            self.setup_service.mark_installation_complete(
                admin_user_id=getattr(self, 'admin_user_id', None)
            )
            self.stdout.write(
                self.style.SUCCESS('  ✓ Installation marked as complete')
            )
        except Exception as e:
            raise CommandError(f'Failed to finalize installation: {e}')
    
    def _show_completion_message(self):
        """Show installation completion message"""
        self._print_separator()
        self.stdout.write(
            self.style.SUCCESS('🎉 Installation completed successfully!')
        )
        self.stdout.write('')
        self.stdout.write('Next steps:')
        self.stdout.write('  1. Start the development server: python manage.py runserver')
        self.stdout.write('  2. Visit http://localhost:8000/admin/ to access the admin panel')
        self.stdout.write('  3. Begin creating your parody news content!')
        self._print_separator()
    
    def _show_headless_instructions(self, token):
        """Show instructions for headless setup completion"""
        self._print_separator()
        self.stdout.write(
            self.style.SUCCESS('🔑 Headless installation prepared!')
        )
        self.stdout.write('')
        self.stdout.write('To complete the setup, follow these steps:')
        self.stdout.write('')
        self.stdout.write(
            self.style.HTTP_INFO(f'1. Start the web server')
        )
        self.stdout.write('   python manage.py runserver')
        self.stdout.write('')
        self.stdout.write(
            self.style.HTTP_INFO(f'2. Visit the setup URL in your browser:')
        )
        self.stdout.write(f'   http://localhost:8000/setup/?token={token}')
        self.stdout.write('')
        self.stdout.write(
            self.style.HTTP_INFO(f'3. Create your admin user through the web interface')
        )
        self.stdout.write('')
        self.stdout.write(
            self.style.WARNING(f'⚠ Token expires in {self.options["token_expires"]} hours')
        )
        self.stdout.write(
            self.style.WARNING('⚠ Keep this token secure - it grants admin access!')
        )
        self._print_separator()
    
    def _show_admin_info(self):
        """Show existing admin user information"""
        admin_users = User.objects.filter(is_superuser=True)
        if admin_users.exists():
            self.stdout.write('Current admin users:')
            for user in admin_users:
                self.stdout.write(f'  • {user.username} ({user.email})')
    
    def _get_input(self, prompt, required=True, default=''):
        """Get user input with validation"""
        while True:
            value = input(f'{prompt}: ').strip() or default
            if required and not value:
                self.stdout.write(
                    self.style.ERROR('This field is required.')
                )
                continue
            return value
    
    def _get_password(self):
        """Get password with confirmation"""
        while True:
            password = getpass.getpass('Admin password: ')
            if not password:
                self.stdout.write(
                    self.style.ERROR('Password is required.')
                )
                continue
                
            if len(password) < 8:
                self.stdout.write(
                    self.style.ERROR('Password must be at least 8 characters.')
                )
                continue
                
            confirm = getpass.getpass('Confirm password: ')
            if password != confirm:
                self.stdout.write(
                    self.style.ERROR('Passwords do not match.')
                )
                continue
                
            return password
    
    def _confirm_action(self, message):
        """Get user confirmation"""
        response = input(f'{message} [y/N]: ').strip().lower()
        return response in ['y', 'yes']
    
    def _print_separator(self):
        """Print visual separator"""
        self.stdout.write('=' * 60)