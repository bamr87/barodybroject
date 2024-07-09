from django.db import models
from django.utils import timezone

class Post(models.Model):
    role = models.TextField(default="you are a helpful assistant.")
    prompt = models.TextField(default="say this is a test")
    content = models.TextField()


class Assistant(models.Model):
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name