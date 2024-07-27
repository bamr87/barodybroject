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
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    # Content management
    path('content/', views.manage_content, name='manage_content'),
    path('content/update/<int:content_id>/', views.update_content, name='update_content_url'),
    path('content/save', views.save_edited_content, name='save_edited_content'),
    path('get-raw-content', views.get_raw_content, name='get_raw_content'),
    # Role management
    path('roles/', views.manage_roles, name='manage_roles'),
    path('roles/delete/<int:role_id>/', views.manage_roles, name='delete_role'),
    path('roles/get-instructions/', views.get_role_instructions, name='get-role-instructions'),
    
    path('assistants/', views.manage_assistants, name='manage_assistants'),
    path('delete_assistant/<str:assistant_id>/', views.delete_assistant, name='delete_assistant'),
    
    path('create_message/', views.create_message, name='create_message'),
    path('messages/', views.message_detail, name='list_messages'),
    path('messages/<str:message_id>/', views.message_detail, name='message_detail'),
    path('messages/delete/<str:message_id>/', views.delete_message, name='delete_message'),
    path('messages/assign/<str:message_id>/', views.assign_assistant_to_message, name='assign_assistant_to_message'),
    path('messages/run/<str:message_id>/', views.run_messages, name='run_message'),
    path('add_message_to_db/', views.add_message_to_db, name='add_message_to_db'),
    
    path('threads/', views.thread_detail, name='thread_detail'),
    path('threads/<str:thread_id>/', views.thread_detail, name='thread_detail'),
    path('threads/delete/<str:thread_id>/', views.delete_thread, name='delete_thread'),
    
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    

    # path('posts/', views.manage_posts, name='manage_posts'),

    # Uncomment the following lines if the views are defined and you plan to use them
    # path('create_post/', views.post_create, name='create_post'),
    # path('post/fail/', views.post_fail, name='post_fail'),
    # Assuming you have a view for assistant details
    # path('assistants/<int:assistant_id>/', views.assistant_detail, name='assistant_detail'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


