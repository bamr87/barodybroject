"""
File: utils.py
Description: Utility views and helper functions used by templates and emails
Author: Barodybroject Team <team@example.com>
Created: 2025-12-19
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- django: >=5.1

Usage: Imported by other views.
"""

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render

from ..models import Post


def post_detail(request, post_id):
    """Display detailed view of a specific blog post."""
    post = get_object_or_404(Post, id=post_id)
    context = {
        "post": post,
    }
    return render(request, "parodynews/pages_post_detail.html", context)


def get_app_instance(request):
    """
    Retrieve Django CMS app instance configuration for current request.

    Returns:
        tuple: (namespace, config) for CMS app configuration
    """
    # CMS functionality temporarily disabled - return empty defaults
    return "", None


class AppHookConfigMixin:
    """Mixin for Django CMS app hook configuration handling."""

    def dispatch(self, request, *args, **kwargs):
        self.namespace, self.config = get_app_instance(request)
        request.current_app = self.namespace
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(app_config__namespace=self.namespace)


def send_welcome_email(user_email):
    """Send welcome email to new user registrations."""
    subject = "Welcome to Barody Broject"
    message = "Thank you for signing up for Barody Broject."
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]
    send_mail(subject, message, email_from, recipient_list)

