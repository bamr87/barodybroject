"""
File: views.py
Description: Django views for web-based installation wizard
Author: Barodybroject Team <team@example.com>
Created: 2025-10-30
Last Modified: 2025-10-30
Version: 1.0.0

Dependencies:
- django.views: View classes
- django.forms: Form handling
- setup.services: Installation service

Container Requirements:
- Django web server running
- Volume persistence for installation state

Usage: Accessible via /setup/ URLs with proper token authentication
"""

import logging

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.core.exceptions import ValidationError
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, View

from setup.forms import AdminUserForm
from setup.services import InstallationService

logger = logging.getLogger(__name__)
User = get_user_model()


class SetupRequiredMixin:
    """Mixin to ensure setup access is authorized"""
    
    def dispatch(self, request, *args, **kwargs):
        # Check if installation is already complete
        installation_service = InstallationService()
        if installation_service.is_installation_complete():
            messages.info(
                request, 
                'Installation is already complete. Access the admin panel to manage your site.'
            )
            return redirect('/admin/')
        
        return super().dispatch(request, *args, **kwargs)


class SetupWizardView(SetupRequiredMixin, View):
    """
    Main setup wizard view that handles token validation and routing
    """
    
    def get(self, request):
        """Display setup wizard or redirect based on state"""
        installation_service = InstallationService()
        token = request.GET.get('token')
        
        # Check setup progress
        progress = installation_service.get_setup_progress()
        
        context = {
            'progress': progress,
            'token': token,
            'token_valid': False,
            'show_admin_form': False
        }
        
        if token:
            # Validate token
            if installation_service.validate_setup_token(token):
                context['token_valid'] = True
                context['show_admin_form'] = progress.get('ready_for_admin_creation', False)
            else:
                messages.error(request, 'Invalid or expired setup token.')
        
        return render(request, 'setup/wizard.html', context)


class CreateAdminView(SetupRequiredMixin, FormView):
    """
    View for creating admin user through web interface
    """
    template_name = 'setup/create_admin.html'
    form_class = AdminUserForm
    
    def dispatch(self, request, *args, **kwargs):
        # Validate token
        self.token = request.GET.get('token') or request.POST.get('token')
        self.installation_service = InstallationService()
        
        if not self.token or not self.installation_service.validate_setup_token(self.token):
            messages.error(request, 'Invalid or expired setup token.')
            return redirect('/setup/')
        
        # Check if admin already exists
        if User.objects.filter(is_superuser=True).exists():
            messages.warning(request, 'Admin user already exists.')
            return redirect('/admin/')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['token'] = self.token
        context['progress'] = self.installation_service.get_setup_progress()
        return context
    
    def form_valid(self, form):
        """Create admin user and complete installation"""
        try:
            # Consume the token (one-time use)
            if not self.installation_service.consume_setup_token(self.token):
                messages.error(self.request, 'Setup token has already been used or is invalid.')
                return redirect('/setup/')
            
            # Create admin user
            user = self.installation_service.create_admin_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data.get('first_name', ''),
                last_name=form.cleaned_data.get('last_name', '')
            )
            
            # Mark installation as complete
            self.installation_service.mark_installation_complete(admin_user_id=user.id)
            
            # Log the user in
            login(self.request, user)
            
            messages.success(
                self.request, 
                f'Welcome! Admin user "{user.username}" created successfully. '
                'Installation is now complete.'
            )
            
            return redirect('/admin/')
            
        except ValidationError as e:
            messages.error(self.request, f'Failed to create admin user: {e}')
            return self.form_invalid(form)
        except Exception as e:
            logger.exception("Error creating admin user")
            messages.error(self.request, 'An unexpected error occurred. Please try again.')
            return self.form_invalid(form)


class SetupStatusView(SetupRequiredMixin, View):
    """
    API endpoint for checking setup status
    """
    
    def get(self, request):
        """Return setup status as JSON"""
        installation_service = InstallationService()
        progress = installation_service.get_setup_progress()
        installation_info = installation_service.get_installation_info()
        
        data = {
            'status': 'success',
            'progress': progress,
            'installation_complete': installation_info.get('completed', False),
            'installation_info': installation_info
        }
        
        return JsonResponse(data)


@method_decorator(csrf_exempt, name='dispatch')
class SetupHealthCheckView(View):
    """
    Health check endpoint for setup wizard
    """
    
    def get(self, request):
        """Basic health check for setup system"""
        try:
            installation_service = InstallationService()
            progress = installation_service.get_setup_progress()
            
            # Basic health indicators
            health_status = {
                'status': 'healthy' if progress['database_ready'] else 'unhealthy',
                'database': 'ok' if progress['database_ready'] else 'error',
                'migrations': 'ok' if progress['migrations_applied'] else 'pending',
                'timestamp': installation_service.get_installation_info().get('completed_at', 'Not completed')
            }
            
            status_code = 200 if progress['database_ready'] else 503
            return JsonResponse(health_status, status=status_code)
            
        except Exception as e:
            logger.exception("Setup health check failed")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)


class SetupRedirectView(View):
    """
    Redirect view for users who access setup without proper context
    """
    
    def get(self, request):
        """Redirect to appropriate setup step or admin"""
        installation_service = InstallationService()
        
        if installation_service.is_installation_complete():
            return redirect('/admin/')
        
        # Check if there's a valid token in session or cookies
        token = request.session.get('setup_token') or request.COOKIES.get('setup_token')
        
        if token and installation_service.validate_setup_token(token):
            return redirect(f'/setup/?token={token}')
        
        # No valid token, show instructions
        return render(request, 'setup/no_token.html')


class CompletionView(View):
    """
    View shown after successful installation completion
    """
    
    def get(self, request):
        """Show completion message and next steps"""
        installation_service = InstallationService()
        
        if not installation_service.is_installation_complete():
            return redirect('/setup/')
        
        installation_info = installation_service.get_installation_info()
        
        context = {
            'installation_info': installation_info,
            'admin_url': '/admin/',
            'next_steps': [
                'Explore the Django admin panel',
                'Configure your parody news categories',
                'Set up OpenAI integration',
                'Create your first parody article',
                'Customize your site settings'
            ]
        }
        
        return render(request, 'setup/completion.html', context)