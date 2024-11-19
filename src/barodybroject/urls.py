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

from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from parodynews import views
from parodynews.views import (
    FooterView,
    ManageContentView,
    ManageAssistantsView,
    ManageMessageView,
    ProcessContentView,
    ManagePostView,
    MyObjectView)

from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include the app's URLs under the root path
    path('', include('parodynews.urls')),
    # Home page and admin page
    path('', views.index, name='index'),
    path('footer/', FooterView.as_view(), name='footer'),

    path('martor/', include('martor.urls')),

    # Include the API endpoints under 'api/' path
    path('api/', include(router.urls)),
    # Remove the redundant include
    # path('api/', include('parodynews.urls')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
