from django.db import models
import uuid
from django.db.models import JSONField

class Template(models.Model):
    name = models.CharField(max_length=100, unique=True)
    schema = JSONField(default=dict)  # Stores configuration for template forms

    def __str__(self):
        return self.name

class Document(models.Model):
    unique_identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    template = models.ForeignKey(Template, related_name="documents", on_delete=models.CASCADE)
    content = models.JSONField(default=dict)  # TipTap editor content
    metadata = models.JSONField(default=dict)  # Template-specific metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.template.name} Document - {self.unique_identifier}"