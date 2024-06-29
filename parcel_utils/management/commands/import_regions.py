from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
import pandas as pd
from templates.models import GlasserRegion

class Command(BaseCommand):
    help = 'Populates GlasserRegion models from an Excel file'

    # Hardcoded path to the Excel file
    filepath = 'data/Glasser_2016_Table.xlsx'

    def handle(self, *args, **options):
        try:
            df = pd.read_excel(self.filepath, skiprows=1)  # Adjust skiprows if the layout of the file is different
        except Exception as e:
            raise CommandError(f"Failed to read Excel file from {self.filepath}: {e}")

        for _, row in df.iterrows():
            # Process the original data
            self.process_row(row, int(row[0]), row[2])

            # Process the modified data with new indices
            new_index = 1000 + int(row[0])  # Adding 1000 to the original index
            self.process_row(row, new_index, row[2], suffix=' - Modified')

    def process_row(self, row, index, name, suffix=''):
        try:
            region = GlasserRegion(
                index=index,
                name=f"{name}{suffix}",
                right_hemisphere_reference_key=row.get('Right Hemisphere Key', ''),
                left_hemisphere_reference_key=row.get('Left Hemisphere Key', ''),
                additional_labels=row.get('Additional Labels', {})  # Ensure it's a dictionary if used
            )
            region.save()
            self.stdout.write(self.style.SUCCESS(f"Successfully added: {region}"))
        except ValidationError as ve:
            self.stdout.write(self.style.ERROR(f"Validation error for {name}: {ve}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to add {name}: {e}"))