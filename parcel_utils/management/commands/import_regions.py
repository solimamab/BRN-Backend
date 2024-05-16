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
            try:
                region = GlasserRegion(
                    index=int(row[0]),  # Assuming the first column is 'index'
                    name=row[2],  # Assuming the third column is 'name'
                    right_hemisphere_reference_key=row.get('Right Hemisphere Key', ''),
                    left_hemisphere_reference_key=row.get('Left Hemisphere Key', ''),
                    additional_labels=row.get('Additional Labels', {})  # Ensure it's a dictionary if used
                )
                region.save()
                self.stdout.write(self.style.SUCCESS(f"Successfully added: {region}"))
            except ValidationError as ve:
                self.stdout.write(self.style.ERROR(f"Validation error for {row[2]}: {ve}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to add {row[2]}: {e}"))

