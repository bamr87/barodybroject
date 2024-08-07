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
from parodynews.views import ManageContentView, MyObjectView



urlpatterns = [
    # Home page and admin page
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    
    # Content management
    path('content/', ManageContentView.as_view(), name='manage_content'),
    path('content/<int:content_id>', ManageContentView.as_view(), name='content_detail'),
    path('content/update/<int:content_id>', views.update_content, name='update_content'),
    path('content/delete/<int:content_id>', ManageContentView.as_view(), name='delete_content'),
    path('content/get-assistants/', views.get_assistants, name='get-assistants'),
    path('get-raw-content', views.get_raw_content, name='get_raw_content'),

    
    path('assistants/', views.manage_assistants, name='manage_assistants'),
    path('assistants/<str:assistant_id>', views.manage_assistants, name='manage_assistants'),
    path('assistants/delete/<str:assistant_id>/', views.delete_assistant, name='delete_assistant'),
    
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
    
    path('objects/', MyObjectView.as_view(), name='object-list'),
    path('objects/create/', MyObjectView.as_view(), {'action': 'create'}, name='object-create'),
    path('objects/<int:pk>/', MyObjectView.as_view(), name='object-detail'),
    path('objects/<int:pk>/update/', MyObjectView.as_view(), {'action': 'update'}, name='object-update'),
    path('objects/<int:pk>/delete/', MyObjectView.as_view(), {'action': 'delete'}, name='object-delete'),

    path('generate_markdown/', views.generate_markdown_view, name='generate_markdown'),


    # path('posts/', views.manage_posts, name='manage_posts'),

    # Uncomment the following lines if the views are defined and you plan to use them
    # path('create_post/', views.post_create, name='create_post'),
    # path('post/fail/', views.post_fail, name='post_fail'),
    # Assuming you have a view for assistant details
    # path('assistants/<int:assistant_id>/', views.assistant_detail, name='assistant_detail'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

