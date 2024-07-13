from django.contrib import admin
from django.urls import path, include
from parodynews import views  # Make sure to replace 'myapp' with the actual name of your Django app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('parodynews/', include('parodynews.urls')),

]