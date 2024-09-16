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
from parodynews.views import ManageContentView, ManageAssistantsView, ManageMessageView, ProcessContentView, MyObjectView



urlpatterns = [
    # Home page and admin page
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    
    # Content management
    path('content/', ManageContentView.as_view(), name='manage_content'),
    path('content/<int:content_detail_id>', ManageContentView.as_view(), name='content_detail'),
    path('content/edit/<int:content_detail_id>', ManageContentView.as_view(), name='edit_content'),
    path('content/delete/<int:content_detail_id>', ManageContentView.as_view(), name='delete_content'),
    path('content/generate/<int:content_detail_id>', ManageContentView.as_view(), name='generate_content'),
    path('content/generate/', ManageContentView.as_view(), name='generate_content'),
    path('content/thread/create/<int:content_detail_id>/', ManageContentView.as_view(), name='create_thread'),

    # Sub routines for AJAX requests
    path('get_assistant_details/<str:assistant_id>/', views.get_assistant_details, name='get_assistant_details'),
    path('get-raw-content', views.get_raw_content, name='get_raw_content'),

    # Content Processing
    path('threads/', ProcessContentView.as_view(), name='process_content'),
    path('threads/<str:thread_id>/', ProcessContentView.as_view(), name='thread_detail'),
    path('threads/delete/<str:thread_id>/', ProcessContentView.as_view(), name='delete_thread'),
    path('threads/<str:thread_id>/messages/<str:message_id>/', ProcessContentView.as_view(), name='thread_message_detail'),
    path('threads/<str:thread_id>/messages/run/<str:message_id>/', ProcessContentView.as_view(), name='run_message'),
    path('threads/<str:thread_id>/messages/delete/<str:message_id>/', ProcessContentView.as_view(), name='delete_thread_message'),

    # Message management
    path('messages/', ManageMessageView.as_view(), name='manage_message'),
    path('messages/create/', ManageMessageView.as_view(), name='create_message'),
    path('messages/delete/<str:message_id>/<str:thread_id>/', ManageMessageView.as_view(), name='delete_message'),
    path('messages/delete/', ManageMessageView.as_view(), name='delete_message'),
    path('messages/', ManageMessageView.as_view(), name='message_detail'),
    path('messages/<str:message_id>/', ManageMessageView.as_view(), name='message_detail'),
    path('messages/<str:message_id>/assign/<str:assigned_assistant_id>/', ManageMessageView.as_view(), name='assign_assistant_to_message'),
    path('messages/<str:message_id>/assign/', ManageMessageView.as_view(), name='assign_assistant_to_message'),
    path('messages/assign/', ManageMessageView.as_view(), name='assign_assistant_to_message'),
    path('add_message_to_db/', views.add_message_to_db, name='add_message_to_db'),

    # Thread management
    # path('threads/', views.thread_detail, name='thread_detail'),

    # Assistant management
    path('assistants/', ManageAssistantsView.as_view(), name='manage_assistants'),
    path('assistants/<str:assistant_id>', ManageAssistantsView.as_view(), name='assistant_detail'),
    path('assistants/edit/<str:assistant_id>/', ManageAssistantsView.as_view(), name='edit_assistant'),
    path('assistants/delete/<str:assistant_id>/', ManageAssistantsView.as_view(), name='delete_assistant'),

    # User management
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    # Object management
    path('objects/', MyObjectView.as_view(), name='object-list'),
    path('objects/create/', MyObjectView.as_view(), {'action': 'create'}, name='object-create'),
    path('objects/<int:pk>/', MyObjectView.as_view(), name='object-detail'),
    path('objects/<int:pk>/update/', MyObjectView.as_view(), {'action': 'update'}, name='object-update'),
    path('objects/<int:pk>/delete/', MyObjectView.as_view(), {'action': 'delete'}, name='object-delete'),

    # JSON Schema management
    path('schemas/', views.list_schemas, name='list_schemas'),
    path('schemas/create/', views.create_schema, name='create_schema'),
    path('schemas/edit/<int:pk>/', views.edit_schema, name='edit_schema'),
    path('schemas/export/<int:pk>/', views.export_schema, name='export_schema'),
    path('schemas/delete/<int:pk>/', views.delete_schema, name='delete_schema'),

    # Markdown generation
    path('generate_markdown/', views.generate_markdown_view, name='generate_markdown'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

