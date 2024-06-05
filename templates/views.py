from rest_framework.parsers import JSONParser
from editor.models import Document
from .parsers import parse_document
from django.http import JsonResponse
from rest_framework.views import APIView
from .serializers import ExperimentSerializer, PaperSerializer
from parcel_utils.atlas import load_atlas, find_closest_parcel
from .models import GlasserRegion, Paper, Experiment, Measurement
from parcel_utils import brodmann
import uuid
import numpy as np
import logging
import json
import os
from BRN import settings

logger = logging.getLogger(__name__)

class ProcessDocumentView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        json_data = request.data
        logger.debug(f"Received JSON data: {json_data}")
        try:
            paper_data, experiments = parse_document(json_data)
            # Define the directory and filename
            directory = 'parsed_documents'
            filename = 'parsed_data.json'

            # Ensure the directory exists
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Define the full path
            full_path = os.path.join(directory, filename)

            # Write the data to a file
            with open(full_path, 'w') as file:
                json.dump({
                    'paper': paper_data,
                    'experiments': experiments
                }, file, indent=4)

            return JsonResponse({
                'status': 'success',
                'paper': paper_data,
                'experiments': experiments
            }, safe=False)
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        
class PaperSubmissionView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        json_data = request.data.get('content')
        logger.debug("Received JSON data: {}".format(json_data))
        document_uuid = request.data.get('uuid')  
        try:
            document = Document.objects.get(unique_identifier=document_uuid)
            paper_data, experiments_data = parse_document(json_data)
            #give document foriegn key to paper_data
            
            paper_mapped = {
                'name': paper_data.get('paperName', '').strip(),
                'document': document.id, # Assigning the document id to the paper 'document' field
                'introduction': paper_data.get('introduction', '').strip(),
                'theory': paper_data.get('theory', '').strip(),
                'summary': paper_data.get('summary', '').strip(),
                'url': paper_data.get('paperURL', '').strip(),
                'experiments': []
            }

            atlas_path = settings.GLASSER_ATLAS_PATH
            try:
                glasserAtlas = load_atlas(atlas_path)
                logger.info("Atlas loaded successfully")
            except FileNotFoundError as e:
                logger.error("Atlas file not found: {}".format(e))
                return JsonResponse({"error": "Atlas file not found: {}".format(e)}, status=500)

            logger.debug("Processing experiments with data: %s", experiments_data)
            for exp_data in experiments_data:
                logger.debug("Setting up experiment with initial data: %s", exp_data)
                experiment_mapped = {
                    'name': exp_data.get('experimentName', '').strip(),
                    'task_context': exp_data.get('taskContext', '').strip(),
                    'task': exp_data.get('task', '').strip(),
                    'task_explained': exp_data.get('taskExplained', '').strip(),
                    'discussion': exp_data.get('discussion', '').strip(),
                    'url': exp_data.get('experimentURL', '').strip(),
                    'measurements': [],
                }
                logger.debug("Experiment mapped data prepared: %s", experiment_mapped)

                for meas_data in exp_data.get('measurements', []):
                    logger.debug("Processing measurement with data: %s", meas_data)
                    coordinates, region_str = self.format_coordinates_and_label(meas_data, glasserAtlas)
                    logger.debug("Formatted coordinates: %s, Region String: %s", coordinates, region_str)
                    measurement_mapped = {
                        'description': meas_data.get('mDescription', '').strip(),
                        'parameters': meas_data.get('mParameters', '').strip(),
                        'interpretation': meas_data.get('mInterpertation', '').strip(),
                        'coordinates': coordinates,
                        'regions': region_str,

                    }
                    logger.debug("Measurement mapped data prepared: %s", measurement_mapped)
                    logger.debug("Appending measurement to experiment. Current measurements: %s", experiment_mapped['measurements'])
                    experiment_mapped['measurements'].append(measurement_mapped)
                    logger.debug("After appending measurement: %s", experiment_mapped['measurements'])

                logger.debug("Appending experiment to paper. Current experiments: %s", paper_mapped['experiments'])
                paper_mapped['experiments'].append(experiment_mapped)
                logger.debug("Experiment added to paper data: %s", experiment_mapped)
                logger.debug("After appending experiment: %s", paper_mapped['experiments'])

            logger.debug("Final paper data to be saved: %s", paper_mapped)
            serializer = PaperSerializer(data=paper_mapped)
            if serializer.is_valid():
                paper = serializer.save()
                logger.info("Paper data saved successfully, ID: %s", paper.id)
                # add the unique identifier to the paper mapped data from serializer

                # Serialize experiments data
                experiments_serialized = [ExperimentSerializer(exp).data for exp in paper.experiments.all()]
                # attmpeting to log what the content of the serialized data is 
                logger.debug("Serialized experiments data: %s", experiments_serialized)
                logger.debug("Serialized  data: %s", serializer.data)


                # Create metadata JSON including serialized paper and experiments data
                metadata = {
                    'paper': serializer.data,
                }

                # Save metadata to the Document
                document.metadata = metadata
                document.save()
                return JsonResponse(serializer.data, status=201)
            else:
                logger.error("Serializer errors: {}".format(serializer.errors))
                return JsonResponse(serializer.errors, status=400)

        except Exception as e:
            logger.error("Error processing document: {}".format(str(e)))
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Document.DoesNotExist:
            return JsonResponse({'error': 'Document not found'}, status=404)
        
    def format_coordinates_and_label(self, meas_data, glasserAtlas):
        """Formats coordinates and label string based on input data."""
        if 'bArea' in meas_data and meas_data['bArea']:
            x, y, z = brodmann.get_mni_from_brodmann(int(meas_data['bArea']))
        else:
            x = float(meas_data.get('xCoordinate', 0))
            y = float(meas_data.get('yCoordinate', 0))
            z = float(meas_data.get('zCoordinate', 0))
        label = meas_data.get('mLabel', '').strip()

        # Find the closest parcel
        parcel = find_closest_parcel(glasserAtlas, np.array([x, y, z]))
        regions_str = label
        if parcel:
            try:
                # Removing extra digits at the beginning if present
                parcel_str = str(parcel)
                if len(parcel_str) == 4 and parcel_str[0] == '1':
                    parcel_str = parcel_str[1:]
                elif len(parcel_str) == 4 and parcel_str[1] == '0':
                    parcel_str = parcel_str[2:]
                region = GlasserRegion.objects.get(index=parcel_str)
                regions_str = f'"{label}":{region.index}'
            except GlasserRegion.DoesNotExist:
                regions_str = f'"{label}": "Unknown"'
        coordinates = f'"{label}": {x:.1f}, {y:.1f}, {z:.1f}'
        return coordinates, regions_str