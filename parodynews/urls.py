from django.contrib import admin
from django.urls import path, include
from parodynews import views  # Make sure to replace 'myapp' with the actual name of your Django app


urlpatterns = [
    path('admin/', admin.site.urls),
    path('parodynews/', include('parodynews.urls')),
    path('create_post/', views.post_create, name='create_post'),
    path('post/success/', views.post_success, name='post_success'),  # Ensure there's a view called `success_view`
    path('create_assistant/', views.create_assistant_view, name='create_assistant'),
    path('assistants/', views.list_assistants_view, name='list_assistants'),
    # Path for assistant details. Assuming you use an assistant ID to fetch details
    path('assistants/<int:assistant_id>/', views.assistant_detail, name='assistant_detail'),ç
]