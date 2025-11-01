"""
URL configuration for barodybroject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView
from rest_framework import routers

from parodynews.views import FooterView

router = routers.DefaultRouter()

urlpatterns = [
    # Installation wizard (must be first to handle redirects properly)
    path("setup/", include("setup.urls")),
    
    # Home page and admin page
    path("", TemplateView.as_view(template_name="index.html")),
    path("accounts/", include("allauth.urls")),
    path("accounts/profile/", TemplateView.as_view(template_name="profile.html")),
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    # Include your app's URLs under a specific prefix to avoid conflicts
    path("", include("parodynews.urls")),
    # CMS URLs temporarily disabled - uncomment when CMS is re-enabled
    # path("", include("cms.urls")),
    path("footer/", FooterView.as_view(), name="footer"),
    # Include django CMS URLs at the root
    # Include the API endpoints under 'api/' path
    path("api/", include(router.urls)),
    # Remove the redundant include
    # path('api/', include('parodynews.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Remove i18n_patterns if not needed or adjust accordingly

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
