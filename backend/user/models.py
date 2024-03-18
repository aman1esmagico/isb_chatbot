from django.db import models

class User(models.Model):
    name = models.CharField(unique=True)
    password = models.CharField(max_length=20)
    # adding state field as CharField
    state = models.IntegerField(default=0)
    # adding resume field as TextField
    resume = models.TextField(null=True, blank=True)
    started_conversation = models.BooleanField(default=False)
    task = models.CharField(max_length=320)
    # Add more fields as needed
    conversation = models.JSONField(blank=True, null=True, default=dict)
    conversation_summary = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)