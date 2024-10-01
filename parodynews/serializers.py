# serializers.py
from rest_framework import serializers
from .models import ContentItem, ContentDetail  # Replace with your actual model

class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentItem
        fields = '__all__'  # Or specify the fields you want to include