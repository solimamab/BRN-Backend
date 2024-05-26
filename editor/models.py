from django.db import models
import uuid
from django.db.models import JSONField

class Document(models.Model):
    unique_identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, blank=True)
    template = models.CharField(max_length=100, blank=True, null=True)  # Template as a simple string
    content = JSONField(default=dict)  # TipTap editor content
    metadata = JSONField(default=dict)  # Template-specific metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Document - {self.unique_identifier} - {self.name}"