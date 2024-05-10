from django.core.management.base import BaseCommand
from editor.models import Measurement, GlasserRegion
import json

class Command(BaseCommand):
    help = 'Updates GlasserRegion additional_labels with Measurement labels and UUIDs'

    def handle(self, *args, **options):
        for measurement in Measurement.objects.all():
            if measurement.regions:
                # Assuming regions are stored as "; " separated values like '"label":index'
                region_data = [r.split(':') for r in measurement.regions.split('; ')]
                for label, index in region_data:
                    label = label.strip('"')
                    index = int(index.strip())
                    region = GlasserRegion.objects.get(index=index)
                    if region.additional_labels is None:
                        region.additional_labels = {}
                    if label not in region.additional_labels:
                        region.additional_labels[label] = []
                    region.additional_labels[label].append(str(measurement.unique_identifier))
                    region.save()
        self.stdout.write(self.style.SUCCESS('Successfully updated GlasserRegion labels.'))
