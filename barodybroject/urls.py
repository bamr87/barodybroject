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
from django.urls import path
from parodynews import views  # Make sure to replace 'myapp' with the actual name of your Django app


urlpatterns = [
    path('', views.index, name='index'),  # Add this line for the root index page
    path('admin/', admin.site.urls),
    path('generate_content/', views.content_create, name='content_create'),
    path('content/', views.list_content, name='list_content'),
    path('assistants/', views.list_assistants, name='list_assistants'),
    # path('create_post/', views.post_create, name='create_post'),
    path('post/success/', views.post_success, name='post_success'),  # Ensure there's a view called `success_view`
    # path('post/fail/', views.post_fail, name='post_fail'),  # Ensure there's a view called `success_view`
    path('create_assistant/', views.create_assistant, name='create_assistant'),
    # Path for assistant details. Assuming you use an assistant ID to fetch details
    # path('assistants/<int:assistant_id>/', views.assistant_detail, name='assistant_detail'),
    path('delete_assistant/<str:assistant_id>/', views.delete_assistant, name='delete_assistant'),


]
