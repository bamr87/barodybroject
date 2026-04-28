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


def send_welcome_email(user_email):
    """Send welcome email to new user registrations."""
    subject = "Welcome to Barody Broject"
    message = "Thank you for signing up for Barody Broject."
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]
    send_mail(subject, message, email_from, recipient_list)

