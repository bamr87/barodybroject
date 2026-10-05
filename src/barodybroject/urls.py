"""
URL configuration for barodybroject project.

Order matters: Django-owned prefixes (setup, accounts, admin, i18n, martor)
come first, the parodynews app last because it ends with the React catch-all.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView

urlpatterns = [
    # Installation wizard (must be first to handle redirects properly)
    path("setup/", include("setup.urls")),
    path("accounts/profile/", TemplateView.as_view(template_name="profile.html")),
    path("accounts/", include("allauth.urls")),
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("martor/", include("martor.urls")),
    # REST API + React application (catch-all)
    path("", include("parodynews.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
