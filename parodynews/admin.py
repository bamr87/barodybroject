from django.contrib import admin
from .models import AppConfig

print("Registering AppConfig model")

# Register your models here.
admin.site.register(AppConfig)