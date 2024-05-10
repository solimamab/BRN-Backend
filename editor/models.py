import uuid
from django.db import models

# Create your models here.
class GlasserRegion(models.Model):
    index = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    right_hemisphere_reference_key = models.CharField(max_length=200, blank=True)
    left_hemisphere_reference_key = models.CharField(max_length=200, blank=True)
    additional_labels = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.name} (Region {self.index})"

    def save(self, *args, **kwargs):
        # Set default values for reference keys if they're not already set
        if not self.right_hemisphere_reference_key:
            self.right_hemisphere_reference_key = f"R{self.index}"
        if not self.left_hemisphere_reference_key:
            self.left_hemisphere_reference_key = f"L{self.index}"

        super(GlasserRegion, self).save(*args, **kwargs)

class ColeNetwork(models.Model):
    name = models.CharField(max_length=100)
    parcels_left = models.JSONField(default=list, help_text="List of parcels in the left hemisphere")
    parcels_right = models.JSONField(default=list, help_text="List of parcels in the right hemisphere")
    sections = models.JSONField(default=list, help_text="List of sections associated with this network")

    def __str__(self):
        return self.name

class Paper(models.Model):
    name = models.TextField(blank=True, null=True)
    introduction = models.TextField(blank=True, null=True)
    theory = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    unique_identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    url = models.URLField(blank=True, null=True, help_text="Link to the source document or publication.")

    def __str__(self):
        return self.name or "Unnamed Paper"

class Experiment(models.Model):
    name = models.TextField(blank=True, null=True)
    task_context = models.TextField(blank=True, null=True)
    task = models.TextField(blank=True, null=True)
    task_explained = models.TextField(blank=True, null=True)
    discussion = models.TextField(blank=True, null=True)
    paper = models.ForeignKey(Paper, related_name='experiments', on_delete=models.CASCADE)
    unique_identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    url = models.URLField(blank=True, null=True, help_text="Link to the source document or publication.")

    def __str__(self):
        return self.name or "Unnamed Experiment"

class Measurement(models.Model):
    regions = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    coordinates = models.TextField(blank=True, null=True)
    parameters = models.TextField(blank=True, null=True)
    interpretation = models.TextField(blank=True, null=True)
    experiment = models.ForeignKey(Experiment, related_name='measurements', on_delete=models.CASCADE)
    unique_identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.description or "Unnamed Measurement"