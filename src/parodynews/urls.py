from django.urls import path, include
from rest_framework import routers
from .views import (
    AssistantViewSet,
    AssistantGroupViewSet,
    ContentItemViewSet,
    ContentDetailViewSet,
    ThreadViewSet,
    MessageViewSet,
    PostViewSet,
    PostFrontMatterViewSet,
    JSONSchemaViewSet,
    PoweredByViewSet,
    MyObjectViewSet,
    GeneralizedCodesViewSet,
    FooterView,
    ManageContentView,
    ManageAssistantsView,
    ManageMessageView,
    ProcessContentView,
    ManagePostView,
    UserLoginView,
    PostPageView,
    get_assistant_details,
    index,
    list_schemas,
    edit_schema,
    create_schema,
    delete_schema,
    export_schema,
    MyObjectView,
    post_detail,
    ManageAssistantGroupsView,
    )

from django.contrib.auth.views import LogoutView, LoginView
from django.conf import settings
from django.conf.urls.static import static

print("Registering parodynews urls")

router = routers.DefaultRouter()
# Register the viewsets
router.register(r'assistants', AssistantViewSet)
router.register(r'assistant-groups', AssistantGroupViewSet)
router.register(r'content-items', ContentItemViewSet)
router.register(r'content-details', ContentDetailViewSet)
router.register(r'threads', ThreadViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'posts', PostViewSet)
router.register(r'post-front-matters', PostFrontMatterViewSet)
router.register(r'json-schemas', JSONSchemaViewSet)
router.register(r'powered-by', PoweredByViewSet)
router.register(r'my-objects', MyObjectViewSet)
router.register(r'generalized-codes', GeneralizedCodesViewSet)

urlpatterns = [

    path("postpage/", PostPageView.as_view(), name='index'),

    path('martor/', include('martor.urls')),

    # Remove or adjust the root path to prevent conflict with django CMS
    path('news/', index, name='index'),
    path('footer/', FooterView.as_view(), name='footer'),

    # Include API endpoints under 'api/' path
    path('api/', include(router.urls)),

    # Content management
    path('content/', ManageContentView.as_view(), name='manage_content'),
    path('content/<int:content_detail_id>', ManageContentView.as_view(), name='content_detail'),
    path('content/edit/<int:content_detail_id>', ManageContentView.as_view(), name='edit_content'),
    path('content/delete/<int:content_detail_id>', ManageContentView.as_view(), name='delete_content'),
    path('content/generate/<int:content_detail_id>', ManageContentView.as_view(), name='generate_content'),
    path('content/generate/', ManageContentView.as_view(), name='generate_content'),
    path('content/thread/create/<int:content_detail_id>/', ManageContentView.as_view(), name='create_thread'),
    path('content/thread/create/', ManageContentView.as_view(), name='manage_content'),

    # Sub routines for AJAX requests
    path('get_assistant_details/<str:assistant_id>/', get_assistant_details, name='get_assistant_details'),

    # Content Processing
    path('threads/', ProcessContentView.as_view(), name='process_content'),
    path('threads/<str:thread_id>/', ProcessContentView.as_view(), name='thread_detail'),
    path('threads/save/<str:thread_id>/', ProcessContentView.as_view(), name='save_thread'),
    path('threads/delete/<str:thread_id>/', ProcessContentView.as_view(), name='delete_thread'),
    path('threads/<str:thread_id>/messages/<str:message_id>/', ProcessContentView.as_view(), name='thread_message_detail'),
    path('threads/<str:thread_id>/messages/delete/<str:message_id>/', ProcessContentView.as_view(), name='delete_thread_message'),
    path('threads/<str:thread_id>/messages/create/<str:message_id>/', ProcessContentView.as_view(), name='create_content'),
    path('threads/<str:thread_id>/messages/run/<str:message_id>/', ProcessContentView.as_view(), name='run_assistant_message'),
    path('threads/<str:thread_id>/messages/run/<str:assistant_group_id>/', ProcessContentView.as_view(), name='run_assistant_group'),
    path('threads/<str:thread_id>/messages/post/<str:message_id>/', ProcessContentView.as_view(), name='create_post'),

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

    # Post Management
    path('posts/', ManagePostView.as_view(), name='manage_post'),
    path('posts/<int:post_id>', ManagePostView.as_view(), name='post_detail'),
    path('posts/edit/', ManagePostView.as_view(), name='edit_post'),
    path('posts/edit/<int:post_id>', ManagePostView.as_view(), name='edit_post'),
    path('posts/delete/', ManagePostView.as_view(), name='delete_post'),
    path('posts/delete/<int:post_id>', ManagePostView.as_view(), name='delete_post'),
    path('posts/delete/', ManagePostView.as_view(), name='delete_post'),
    path('posts/publish/<int:post_id>', ManagePostView.as_view(), name='publish_post'),
    path('posts/<int:post_id>/', ManagePostView.as_view(), name='post_detail'),

    # Assistant management
    path('assistants/', ManageAssistantsView.as_view(), name='manage_assistants'),
    path('assistants/<str:assistant_id>', ManageAssistantsView.as_view(), name='assistant_detail'),
    path('assistants/edit/<str:assistant_id>/', ManageAssistantsView.as_view(), name='edit_assistant'),
    path('assistants/delete/<str:assistant_id>/', ManageAssistantsView.as_view(), name='delete_assistant'),

    # Assistant Groups management
    path('assistant-groups/', ManageAssistantGroupsView.as_view(), name='manage_assistant_groups'),
    path('assistant-groups/<int:assistant_group_id>/', ManageAssistantGroupsView.as_view(), name='assistant_group_detail'),
    path('assistant-groups/create/', ManageAssistantGroupsView.as_view(), name='create_assistant_group'),
    path('assistant-groups/edit/<int:assistant_group_id>/', ManageAssistantGroupsView.as_view(), name='edit_assistant_group'),
    path('assistant-groups/delete/<int:assistant_group_id>/', ManageAssistantGroupsView.as_view(), name='delete_assistant_group'),

    # Assistant Groups Membership Management
    

    # User management
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='registration/logged_out.html', next_page='login'), name='logout'),

    # Object management
    path('objects/', MyObjectView.as_view(), name='object-list'),
    path('objects/create/', MyObjectView.as_view(), {'action': 'create'}, name='object-create'),
    path('objects/<int:pk>/', MyObjectView.as_view(), name='object-detail'),
    path('objects/<int:pk>/update/', MyObjectView.as_view(), {'action': 'update'}, name='object-update'),
    path('objects/<int:pk>/delete/', MyObjectView.as_view(), {'action': 'delete'}, name='object-delete'),

    # JSON Schema management
    path('schemas/', list_schemas, name='list_schemas'),
    path('schemas/create/', create_schema, name='create_schema'),
    path('schemas/edit/<int:pk>/', edit_schema, name='edit_schema'),
    path('schemas/export/<int:pk>/', export_schema, name='export_schema'),
    path('schemas/delete/<int:pk>/', delete_schema, name='delete_schema'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

