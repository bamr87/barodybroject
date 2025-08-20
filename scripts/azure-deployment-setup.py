#!/usr/bin/env python3
"""
Azure Deployment Setup Script

This interactive script helps set up a new Azure deployment of the BarodyBroject Django application.
It handles database migrations, admin user creation, static file collection, production configuration,
custom domain setup, and other post-deployment tasks.

Features:
- Environment configuration (Development/Production)
- Custom domain setup with SSL certificates
- Production security hardening
- Database migrations and static file collection
- Admin user creation
- Django CMS initial configuration
- Comprehensive health checks

Usage:
    python scripts/azure-deployment-setup.py

Requirements:
    - Azure CLI installed and logged in
    - azd (Azure Developer CLI) installed
    - Deployment already completed with 'azd up'
"""

import getpass
import json
import subprocess
import sys
from typing import Tuple


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class AzureSetup:
    """Azure deployment setup manager"""
    
    def __init__(self):
        self.resource_group = None
        self.container_app_name = None
        self.app_url = None
        self.env_values = {}
        self.custom_domain = None
        self.is_production = False
        self.environment_type = None
        
    def print_header(self, text: str):
        """Print a formatted header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
        print(f"{text.center(60)}")
        print(f"{'='*60}{Colors.ENDC}")
        
    def print_success(self, text: str):
        """Print success message"""
        print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")
        
    def print_error(self, text: str):
        """Print error message"""
        print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")
        
    def print_warning(self, text: str):
        """Print warning message"""
        print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")
        
    def print_info(self, text: str):
        """Print info message"""
        print(f"{Colors.OKBLUE}ℹ {text}{Colors.ENDC}")
        
    def run_command(self, command: str, capture_output: bool = True) -> Tuple[bool, str]:
        """Run a shell command and return success status and output"""
        try:
            if capture_output:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                return result.returncode == 0, result.stdout.strip()
            else:
                result = subprocess.run(command, shell=True)
                return result.returncode == 0, ""
        except Exception as e:
            return False, str(e)
            
    def check_prerequisites(self) -> bool:
        """Check if required tools are installed"""
        self.print_header("Checking Prerequisites")
        
        # Check Azure CLI
        success, _ = self.run_command("az --version")
        if success:
            self.print_success("Azure CLI is installed")
        else:
            self.print_error("Azure CLI is not installed or not in PATH")
            return False
            
        # Check azd
        success, _ = self.run_command("azd version")
        if success:
            self.print_success("Azure Developer CLI (azd) is installed")
        else:
            self.print_error("Azure Developer CLI (azd) is not installed or not in PATH")
            return False
            
        # Check if logged into Azure
        success, output = self.run_command("az account show")
        if success:
            account_info = json.loads(output)
            self.print_success(f"Logged into Azure as: {account_info.get('user', {}).get('name', 'Unknown')}")
        else:
            self.print_error("Not logged into Azure. Please run 'az login' first")
            return False
            
        return True
        
    def configure_deployment_environment(self) -> bool:
        """Configure deployment environment and domain settings"""
        self.print_header("Deployment Environment Configuration")
        
        print("Let's configure your deployment environment and domain settings.")
        print()
        
        # Ask about environment type
        print("What type of environment is this?")
        print("1. Development/Staging")
        print("2. Production")
        print()
        
        while True:
            choice = input(f"{Colors.OKBLUE}Select environment type (1-2): {Colors.ENDC}").strip()
            if choice == "1":
                self.environment_type = "development"
                self.is_production = False
                self.print_info("Environment set to: Development/Staging")
                break
            elif choice == "2":
                self.environment_type = "production"
                self.is_production = True
                self.print_info("Environment set to: Production")
                break
            else:
                print("Please enter 1 or 2")
        
        print()
        
        # Ask about custom domain for production
        if self.is_production:
            print("For production environments, you can configure a custom domain.")
            if self.get_user_confirmation("Do you want to configure a custom domain?"):
                while True:
                    domain = input(f"{Colors.OKBLUE}Enter your domain name (e.g., myapp.com): {Colors.ENDC}").strip()
                    if domain and '.' in domain and not domain.startswith('http'):
                        self.custom_domain = domain
                        self.print_success(f"Custom domain set to: {domain}")
                        break
                    else:
                        print("Please enter a valid domain name (without http/https)")
            else:
                self.print_info("Using Azure Container Apps default domain")
        else:
            self.print_info("Development environment - using default Azure domain")
            
        return True
        
    def deploy_to_production(self) -> bool:
        """Handle production-specific deployment tasks"""
        if not self.is_production:
            return True
            
        self.print_header("Production Deployment Setup")
        
        print("Setting up production-specific configurations...")
        
        # Production environment variables
        prod_commands = []
        
        # Set production environment variable
        prod_commands.append('az containerapp update --name {} --resource-group {} --set-env-vars RUNNING_IN_PRODUCTION=true'.format(
            self.container_app_name, self.resource_group
        ))
        
        # Set Django settings for production
        prod_commands.append('az containerapp update --name {} --resource-group {} --set-env-vars DJANGO_SETTINGS_MODULE=barodybroject.settings'.format(
            self.container_app_name, self.resource_group
        ))
        
        # Configure custom domain if specified
        if self.custom_domain:
            if self.get_user_confirmation(f"Do you want to configure the custom domain {self.custom_domain} now?"):
                if not self.configure_custom_domain():
                    self.print_warning("Custom domain configuration failed. You can configure it manually later.")
        
        # Execute production configuration commands
        for cmd in prod_commands:
            print(f"Running: {cmd}")
            success, output = self.run_command(cmd)
            if success:
                self.print_success("Production configuration updated")
            else:
                self.print_warning(f"Configuration update had issues: {output}")
        
        # Additional production checks
        if self.get_user_confirmation("Do you want to enable additional security headers for production?"):
            self.configure_production_security()
            
        return True
        
    def configure_custom_domain(self) -> bool:
        """Configure custom domain for the container app"""
        self.print_header("Configuring Custom Domain")
        
        print(f"Setting up custom domain: {self.custom_domain}")
        print()
        
        # Check if domain is already configured
        success, output = self.run_command(f"az containerapp hostname list --name {self.container_app_name} --resource-group {self.resource_group}")
        if success:
            hostnames = json.loads(output) if output else []
            if any(hostname.get('name') == self.custom_domain for hostname in hostnames):
                self.print_success(f"Domain {self.custom_domain} is already configured")
                return True
        
        print("To configure a custom domain, you need:")
        print("1. A valid SSL certificate for your domain")
        print("2. DNS records pointing to your container app")
        print()
        
        # Get certificate information
        cert_choice = None
        while True:
            print("How do you want to handle the SSL certificate?")
            print("1. I have a certificate file (.pfx)")
            print("2. Use Azure managed certificate (requires domain validation)")
            print("3. Skip domain configuration for now")
            
            choice = input(f"{Colors.OKBLUE}Select option (1-3): {Colors.ENDC}").strip()
            if choice in ['1', '2', '3']:
                cert_choice = choice
                break
            else:
                print("Please enter 1, 2, or 3")
        
        if cert_choice == '3':
            self.print_info("Skipping custom domain configuration")
            return True
        elif cert_choice == '1':
            return self.configure_custom_certificate()
        elif cert_choice == '2':
            return self.configure_managed_certificate()
            
        return True
        
    def configure_custom_certificate(self) -> bool:
        """Configure custom domain with user-provided certificate"""
        print("Custom certificate configuration:")
        print()
        
        cert_path = input(f"{Colors.OKBLUE}Enter path to your .pfx certificate file: {Colors.ENDC}").strip()
        if not cert_path:
            self.print_warning("No certificate path provided")
            return False
            
        cert_password = getpass.getpass(f"{Colors.OKBLUE}Enter certificate password: {Colors.ENDC}")
        
        # Upload certificate and configure domain
        cert_name = f"{self.custom_domain.replace('.', '-')}-cert"
        
        commands = [
            f"az containerapp env certificate upload --name {self.env_values.get('AZURE_ENV_NAME', 'env')} --resource-group {self.resource_group} --certificate-file '{cert_path}' --certificate-name {cert_name} --certificate-password '{cert_password}'",
            f"az containerapp hostname add --hostname {self.custom_domain} --name {self.container_app_name} --resource-group {self.resource_group} --certificate {cert_name}"
        ]
        
        for cmd in commands:
            print("Running certificate configuration...")
            success, output = self.run_command(cmd)
            if not success:
                self.print_error(f"Certificate configuration failed: {output}")
                return False
                
        self.print_success(f"Custom domain {self.custom_domain} configured successfully!")
        return True
        
    def configure_managed_certificate(self) -> bool:
        """Configure custom domain with Azure managed certificate"""
        print("Azure managed certificate configuration:")
        print()
        print("Before proceeding, ensure your DNS records point to:")
        print(f"  CNAME: {self.custom_domain} -> {self.app_url.replace('https://', '')}")
        print()
        
        if not self.get_user_confirmation("Have you configured the DNS records?"):
            self.print_info("Please configure DNS records first, then run this script again")
            return False
            
        # Add hostname with managed certificate
        cmd = f"az containerapp hostname add --hostname {self.custom_domain} --name {self.container_app_name} --resource-group {self.resource_group}"
        
        print("Configuring managed certificate...")
        success, output = self.run_command(cmd)
        
        if success:
            self.print_success(f"Custom domain {self.custom_domain} configured with managed certificate!")
            self.app_url = f"https://{self.custom_domain}"
            return True
        else:
            self.print_error(f"Managed certificate configuration failed: {output}")
            return False
            
    def configure_production_security(self) -> bool:
        """Configure additional security settings for production"""
        self.print_header("Configuring Production Security")
        
        security_vars = {
            'SECURE_SSL_REDIRECT': 'True',
            'SECURE_HSTS_SECONDS': '31536000',
            'SECURE_HSTS_INCLUDE_SUBDOMAINS': 'True',
            'SECURE_HSTS_PRELOAD': 'True',
            'SECURE_CONTENT_TYPE_NOSNIFF': 'True',
            'SECURE_BROWSER_XSS_FILTER': 'True',
            'SESSION_COOKIE_SECURE': 'True',
            'CSRF_COOKIE_SECURE': 'True'
        }
        
        env_vars = ' '.join([f"{k}={v}" for k, v in security_vars.items()])
        cmd = f"az containerapp update --name {self.container_app_name} --resource-group {self.resource_group} --set-env-vars {env_vars}"
        
        print("Applying security headers...")
        success, output = self.run_command(cmd)
        
        if success:
            self.print_success("Production security headers configured")
            return True
        else:
            self.print_warning(f"Security configuration had issues: {output}")
            return False
        
    def get_environment_info(self) -> bool:
        """Get Azure environment information from azd"""
        self.print_header("Getting Environment Information")
        
        # Get azd environment values
        success, output = self.run_command("azd env get-values")
        if not success:
            self.print_error("Failed to get azd environment values. Make sure you've run 'azd up' first.")
            return False
            
        # Parse environment values
        for line in output.split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                self.env_values[key] = value.strip('"')
                
        # Extract key information
        self.resource_group = None
        env_name = self.env_values.get('AZURE_ENV_NAME', '')
        location = self.env_values.get('AZURE_LOCATION', '')
        
        if env_name and location:
            # Try common resource group naming patterns
            possible_rg_names = [
                f"rg-{env_name}",
                f"{env_name}-rg",
                f"rg-{env_name}-{location}",
                env_name
            ]
            
            for rg_name in possible_rg_names:
                success, _ = self.run_command(f"az group show --name {rg_name}")
                if success:
                    self.resource_group = rg_name
                    break
                    
        if not self.resource_group:
            self.print_error("Could not determine resource group name")
            return False
            
        self.print_success(f"Environment: {env_name}")
        self.print_success(f"Resource Group: {self.resource_group}")
        self.print_success(f"Location: {location}")
        
        # Find container app
        success, output = self.run_command(f"az containerapp list --resource-group {self.resource_group} --query \"[].{{Name:name, Fqdn:properties.configuration.ingress.fqdn}}\" --output json")
        if success and output:
            apps = json.loads(output)
            if apps:
                self.container_app_name = apps[0]['Name']
                self.app_url = f"https://{apps[0]['Fqdn']}"
                self.print_success(f"Container App: {self.container_app_name}")
                self.print_success(f"App URL: {self.app_url}")
            else:
                self.print_error("No container apps found in resource group")
                return False
        else:
            self.print_error("Failed to get container app information")
            return False
            
        return True
        
    def test_app_connectivity(self) -> bool:
        """Test if the application is responding"""
        self.print_header("Testing Application Connectivity")
        
        success, _ = self.run_command(f"curl -f -s {self.app_url}")
        if success:
            self.print_success("Application is responding")
            return True
        else:
            self.print_warning("Application is not responding or returned an error")
            return False
            
    def run_migrations(self) -> bool:
        """Run Django database migrations"""
        self.print_header("Running Database Migrations")
        
        print("This will run Django migrations to set up the database schema.")
        if not self.get_user_confirmation("Do you want to run migrations?"):
            self.print_info("Skipping migrations")
            return True
            
        command = f'az containerapp exec --name {self.container_app_name} --resource-group {self.resource_group} --command "python manage.py migrate"'
        
        print("Running migrations...")
        success, output = self.run_command(command, capture_output=False)
        
        if success:
            self.print_success("Migrations completed successfully")
            return True
        else:
            self.print_error("Migrations failed")
            return False
            
    def collect_static_files(self) -> bool:
        """Collect Django static files"""
        self.print_header("Collecting Static Files")
        
        print("This will collect static files for proper CSS/JS serving.")
        if not self.get_user_confirmation("Do you want to collect static files?"):
            self.print_info("Skipping static file collection")
            return True
            
        command = f'az containerapp exec --name {self.container_app_name} --resource-group {self.resource_group} --command "python manage.py collectstatic --noinput"'
        
        print("Collecting static files...")
        success, output = self.run_command(command, capture_output=False)
        
        if success:
            self.print_success("Static files collected successfully")
            return True
        else:
            self.print_error("Static file collection failed")
            return False
            
    def create_superuser(self) -> bool:
        """Create Django superuser account"""
        self.print_header("Creating Superuser Account")
        
        print("A superuser account is needed to access the Django admin panel.")
        if not self.get_user_confirmation("Do you want to create a superuser account?"):
            self.print_info("Skipping superuser creation")
            return True
            
        # Get user input
        while True:
            username = input(f"{Colors.OKBLUE}Enter username for superuser: {Colors.ENDC}").strip()
            if username:
                break
            print("Username cannot be empty")
            
        while True:
            email = input(f"{Colors.OKBLUE}Enter email for superuser: {Colors.ENDC}").strip()
            if email and '@' in email:
                break
            print("Please enter a valid email address")
            
        while True:
            password = getpass.getpass(f"{Colors.OKBLUE}Enter password for superuser: {Colors.ENDC}")
            if len(password) >= 8:
                password_confirm = getpass.getpass(f"{Colors.OKBLUE}Confirm password: {Colors.ENDC}")
                if password == password_confirm:
                    break
                else:
                    print("Passwords don't match. Please try again.")
            else:
                print("Password must be at least 8 characters long")
                
        # Create superuser using Django shell
        django_command = f"""
from django.contrib.auth import get_user_model
User = get_user_model()
if User.objects.filter(username='{username}').exists():
    print('User {username} already exists')
else:
    User.objects.create_superuser('{username}', '{email}', '{password}')
    print('Superuser {username} created successfully')
"""
        
        # Escape quotes and format for shell execution
        django_command = django_command.replace('"', '\\"').replace('\n', '; ')
        command = f'az containerapp exec --name {self.container_app_name} --resource-group {self.resource_group} --command "echo \\"{django_command}\\" | python manage.py shell"'
        
        print("Creating superuser...")
        success, output = self.run_command(command, capture_output=False)
        
        if success:
            self.print_success(f"Superuser '{username}' created successfully")
            self.print_info(f"Admin URL: {self.app_url}/admin/")
            return True
        else:
            self.print_error("Superuser creation failed")
            return False
            
    def setup_cms_pages(self) -> bool:
        """Set up initial CMS pages"""
        self.print_header("Setting Up CMS Pages")
        
        print("This will create initial CMS pages and configure the site.")
        if not self.get_user_confirmation("Do you want to set up initial CMS pages?"):
            self.print_info("Skipping CMS setup")
            return True
            
        # Create initial CMS page
        # Use custom domain if configured, otherwise use the app URL
        site_domain = self.custom_domain if self.custom_domain else self.app_url.replace('https://', '')
        
        django_command = """
from cms.api import create_page
from cms.models import Page
from django.contrib.sites.models import Site

# Update site domain
site = Site.objects.get(pk=1)
site.domain = '{}'
site.name = 'BarodyBroject'
site.save()

# Create home page if it doesn't exist
if not Page.objects.filter(title_set__title='Home').exists():
    page = create_page(
        title='Home',
        template='cms/home.html',
        language='en',
        slug='home',
        in_navigation=True,
        published=True
    )
    print('Home page created successfully')
else:
    print('Home page already exists')
""".format(site_domain)
        
        # Escape and format for shell execution
        django_command = django_command.replace('"', '\\"').replace('\n', '; ')
        command = f'az containerapp exec --name {self.container_app_name} --resource-group {self.resource_group} --command "echo \\"{django_command}\\" | python manage.py shell"'
        
        print("Setting up CMS pages...")
        success, output = self.run_command(command, capture_output=False)
        
        if success:
            self.print_success("CMS pages set up successfully")
            return True
        else:
            self.print_error("CMS setup failed")
            return False
            
    def get_user_confirmation(self, message: str) -> bool:
        """Get yes/no confirmation from user"""
        while True:
            response = input(f"{Colors.OKBLUE}{message} (y/n): {Colors.ENDC}").lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")
                
    def run_health_check(self) -> bool:
        """Run final health check"""
        self.print_header("Running Health Check")
        
        # Test main application
        success, _ = self.run_command(f"curl -f -s {self.app_url}")
        if success:
            self.print_success("Main application is responding")
        else:
            self.print_error("Main application is not responding")
            return False
            
        # Test admin panel
        success, _ = self.run_command(f"curl -f -s {self.app_url}/admin/")
        if success:
            self.print_success("Admin panel is accessible")
        else:
            self.print_warning("Admin panel returned an error (this might be normal if redirecting)")
            
        return True
        
    def print_summary(self):
        """Print deployment summary"""
        self.print_header("Deployment Setup Complete")
        
        print(f"{Colors.OKGREEN}{Colors.BOLD}Your Django application is now set up!{Colors.ENDC}")
        print(f"\n{Colors.OKBLUE}Application Details:{Colors.ENDC}")
        print(f"  • Environment: {self.environment_type.title() if self.environment_type else 'Unknown'}")
        print(f"  • App URL: {self.app_url}")
        if self.custom_domain:
            print(f"  • Custom Domain: {self.custom_domain}")
        print(f"  • Admin URL: {self.app_url}/admin/")
        print(f"  • Resource Group: {self.resource_group}")
        print(f"  • Container App: {self.container_app_name}")
        
        print(f"\n{Colors.OKBLUE}Next Steps:{Colors.ENDC}")
        print("  1. Visit your application URL to verify it's working")
        print("  2. Log into the admin panel with your superuser account")
        print("  3. Configure your Django CMS pages and content")
        print("  4. Set up any additional configuration as needed")
        
        if self.is_production:
            print(f"\n{Colors.OKBLUE}Production Checklist:{Colors.ENDC}")
            print("  • Verify SSL certificate is working properly")
            print("  • Test all functionality in production environment")
            print("  • Set up monitoring and alerts")
            print("  • Configure backup procedures")
            if self.custom_domain:
                print(f"  • Verify DNS propagation for {self.custom_domain}")
        
        print(f"\n{Colors.WARNING}Remember to:{Colors.ENDC}")
        print("  • Regularly backup your database")
        print("  • Monitor your Azure costs")
        print("  • Keep your dependencies updated")
        if self.is_production:
            print("  • Monitor security headers and SSL certificate expiration")
            print("  • Review and update security settings regularly")
        
    def run(self):
        """Run the complete setup process"""
        print(f"{Colors.HEADER}{Colors.BOLD}")
        print("╔══════════════════════════════════════════════════════════╗")
        print("║                                                          ║")
        print("║         Azure Deployment Setup for BarodyBroject        ║")
        print("║                                                          ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}")
        
        print("This script will help you set up your Django application after deployment.")
        print("It will run migrations, create admin users, and configure your app.")
        print()
        
        if not self.get_user_confirmation("Do you want to continue with the setup?"):
            print("Setup cancelled.")
            return False
            
        # Run setup steps
        if not self.check_prerequisites():
            return False
            
        # Configure deployment environment and domain
        if not self.configure_deployment_environment():
            return False
            
        if not self.get_environment_info():
            return False
            
        # Test connectivity (non-blocking)
        self.test_app_connectivity()
        
        # Handle production deployment configuration
        if not self.deploy_to_production():
            if not self.get_user_confirmation("Production deployment configuration failed. Continue anyway?"):
                return False
        
        # Run setup tasks
        if not self.run_migrations():
            if not self.get_user_confirmation("Migrations failed. Continue anyway?"):
                return False
                
        if not self.collect_static_files():
            if not self.get_user_confirmation("Static file collection failed. Continue anyway?"):
                return False
                
        if not self.create_superuser():
            if not self.get_user_confirmation("Superuser creation failed. Continue anyway?"):
                return False
                
        if not self.setup_cms_pages():
            if not self.get_user_confirmation("CMS setup failed. Continue anyway?"):
                return False
                
        # Final health check
        self.run_health_check()
        
        # Print summary
        self.print_summary()
        
        return True


def main():
    """Main entry point"""
    setup = AzureSetup()
    
    try:
        success = setup.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Setup interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Unexpected error: {e}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
