"""
File: base.py
Description: Base template views (index, login, footer) for parodynews
Author: Barodybroject Team <team@example.com>
Created: 2025-12-19
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- django: >=5.1

Usage: Included via parodynews URL routing.
"""

from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.views.generic import TemplateView

from ..models import PoweredBy


class FooterView(TemplateView):
    """Footer template view for rendering page footers."""

    template_name = "footer.html"

    def get_context_data(self, **kwargs):
        """Get context data including PoweredBy objects for footer display."""
        context = super().get_context_data(**kwargs)
        context["powered_by"] = PoweredBy.objects.all()
        return context


class UserLoginView(LoginView):
    """Custom user login view with custom template."""

    template_name = "login.html"


def index(request):
    """Home page view function."""
    return render(request, "parodynews/index.html", {})

