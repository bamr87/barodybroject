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
from parodynews import views


urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('content/', views.manage_content, name='manage_content'),
    path('assistants/', views.manage_assistants, name='manage_assistants'),
    path('delete_assistant/<str:assistant_id>/', views.delete_assistant, name='delete_assistant'),
    path('create_message/', views.create_message, name='create_message'),
    path('messages/', views.list_messages, name='list_messages'),
    path('delete_message/<str:message_id>/', views.delete_message, name='delete_message'),
    path('messages/assign/<str:message_id>/', views.assign_assistant_to_message, name='assign_assistant_to_message'),

    # Uncomment the following lines if the views are defined and you plan to use them
    # path('create_post/', views.post_create, name='create_post'),
    # path('post/fail/', views.post_fail, name='post_fail'),
    # Assuming you have a view for assistant details
    # path('assistants/<int:assistant_id>/', views.assistant_detail, name='assistant_detail'),
]


