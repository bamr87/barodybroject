"""
File: urls.py
Description: URL configuration for setup wizard
Author: Barodybroject Team <team@example.com>
Created: 2025-10-30
Last Modified: 2025-10-30
Version: 1.0.0

Dependencies:
- django.urls: URL routing
- setup.views: Setup wizard views

Usage: Include in main URLs with path('setup/', include('setup.urls'))
"""

from django.urls import path

from setup import views

app_name = 'setup'

urlpatterns = [
    # Main setup wizard entry point
    path('', views.SetupWizardView.as_view(), name='wizard'),
    
    # Admin user creation
    path('create-admin/', views.CreateAdminView.as_view(), name='create_admin'),
    
    # Setup status and health endpoints
    path('status/', views.SetupStatusView.as_view(), name='status'),
    path('health/', views.SetupHealthCheckView.as_view(), name='health'),
    
    # Completion and redirect views
    path('complete/', views.CompletionView.as_view(), name='completion'),
    path('redirect/', views.SetupRedirectView.as_view(), name='redirect'),
]