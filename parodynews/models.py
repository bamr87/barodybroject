from django.db import models
from django.utils import timezone

class ContentDetail(models.Model):
    title = models.CharField(max_length=255, default="NEED TITLE.")
    description = models.TextField(blank=True)
    author = models.CharField(max_length=100, default="NEED AUTHOR.")
    published_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
class Content(models.Model):
    role = models.TextField(default="you are a helpful assistant.")
    prompt = models.TextField(default="say this is a test")
    content = models.TextField()
    detail = models.OneToOneField(ContentDetail, on_delete=models.CASCADE, related_name='content')

class Assistant(models.Model):
    assistant_id = models.CharField(max_length=225, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    model = models.CharField(max_length=100, default="gpt-3.5-turbo")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
# New model for threads
class Thread(models.Model):
    thread_id = models.CharField(max_length=255, primary_key=True) 
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Thread created at {self.created_at}"
# New model for storing messages
# https://platform.openai.com/docs/api-reference/messages
class Message(models.Model):
    message_id = models.CharField(max_length=255, primary_key=True)
    created_at = models.DateTimeField(default=timezone.now)
    content = models.ForeignKey(Content, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    thread = models.ForeignKey(Thread, on_delete=models.SET_NULL, null=True, related_name='messages')
    assistant = models.ForeignKey(Assistant, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')

    def __str__(self):
        content_id = f"Content ID {self.content.id}" if self.content else "No Content"
        return f"Message for {content_id} with Thread ID {self.thread.thread_id} created at {self.created_at}"