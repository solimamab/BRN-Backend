import csv
from django.core.management.base import BaseCommand
from templates.models import ColeNetwork

class Command(BaseCommand):
    help = 'Import Cole Networks and related parcels from a CSV file'

    def handle(self, *args, **kwargs):
        csv_file_path = 'data/ColeGlasser.csv'

        networks = {}

        # Initialize Cole Networks dictionary
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                parcel_index = int(row['Parcel_Index'])
                area_name = row['Area_Name']
                lh_network = row['LH_Network']
                rh_network = row['RH_Network']
                sections = [int(section.strip()) for section in row['Sections'].replace('\n', ',').split(',') if section.strip().isdigit()]

                # Add or update left hemisphere network
                if lh_network not in networks:
                    networks[lh_network] = {'parcels_left': [], 'parcels_right': [], 'sections': set()}
                networks[lh_network]['parcels_left'].append(parcel_index)
                networks[lh_network]['sections'].update(sections)

                # Add or update right hemisphere network
                if rh_network not in networks:
                    networks[rh_network] = {'parcels_left': [], 'parcels_right': [], 'sections': set()}
                networks[rh_network]['parcels_right'].append(parcel_index)
                networks[rh_network]['sections'].update(sections)

        # Create ColeNetwork models
        for network_name, network_data in networks.items():
            ColeNetwork.objects.update_or_create(
                name=network_name,
                defaults={
                    'parcels_left': network_data['parcels_left'],
                    'parcels_right': network_data['parcels_right'],
                    'sections': list(network_data['sections']),
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully imported Cole Networks and parcels'))
