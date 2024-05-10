# In editor/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from documents.models import Document
from BRN import settings
from parcel_utils.atlas import load_atlas
from parcel_utils import brodmann, atlas
from editor.parsers import parse_paper1_template
import numpy as np
import logging
import uuid

logger = logging.getLogger(__name__)

class PaperSubmissionAPI(APIView):
    def post(self, request, *args, **kwargs):
        from documents.serializers import DocumentSerializer  
        from editor.models import GlasserRegion

        paper_data = request.data.get('paper', {})
        logger.info(f"Incoming paper data: {paper_data}")

        experiments_info = {}
        measurements_info = {}

        # Load the atlas
        atlas_path = settings.GLASSER_ATLAS_PATH
        try:
            glasserAtlas = load_atlas(atlas_path)
            logger.info("Atlas loaded successfully")
        except FileNotFoundError as e:
            logger.error(f"Atlas file not found: {e}")
            return Response({"error": f"Atlas file not found: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Process experiments and measurements
        for exp_index, exp_data in enumerate(paper_data.get('experiments', [])):
            experiments_info[exp_index] = {
                'unique_identifier': uuid.uuid4(),
                'name': exp_data.get('name', ''),
                'task_context': exp_data.get('task_context', ''),
                'task': exp_data.get('task', ''),
                'task_explained': exp_data.get('task_explained', ''),
                'discussion': exp_data.get('discussion', ''),
                'url': exp_data.get('url', ''),
                'measurements': []
            }
            measurements_info[exp_index] = {}

            for meas_index, meas_data in enumerate(exp_data.get('measurements', [])):
                # Handle Brodmann Area conversion if present
                if 'brodmann_area' in meas_data and meas_data['brodmann_area']:
                    try:
                        x, y, z = brodmann.get_mni_from_brodmann(int(meas_data['brodmann_area']))
                        label = meas_data.get('label', '')
                        formatted_coordinate = f'"{label}": {x:.1f}, {y:.1f}, {z:.1f}'
                    except Exception as e:
                        x, y, z = 0, 0, 0
                        logger.error(f"Error converting Brodmann Area: {e}")
                        formatted_coordinate = f'"{meas_data["label"]}": {x:.1f}, {y:.1f}, {z:.1f}'
                else:
                    # Parse coordinates directly from meas_data
                    try:
                        x, y, z = float(meas_data.get('x', 0)), float(meas_data.get('y', 0)), float(meas_data.get('z', 0))
                    except ValueError:
                        x, y, z = 0, 0, 0
                        logger.error(f"Invalid coordinate data for measurement: {meas_data}")
                    label = meas_data.get('label', '')
                    formatted_coordinate = f'"{label}": {x:.1f}, {y:.1f}, {z:.1f}'

                # Find the closest parcel and handle regions
                parcel = atlas.find_closest_parcel(glasserAtlas, np.array([x, y, z]))
                regions_str = ""
                if parcel:
                    if len(str(parcel)) == 4 and str(parcel).startswith("1"):
                        # Remove leading '1' for four-digit parcels and add '.R' for right hemisphere
                        parcel = int(str(parcel)[1:])
                        label = f"{label.strip()}.R"
                    try:
                        from editor.models import GlasserRegion
                        region = GlasserRegion.objects.get(index=parcel)
                        regions_str = f'"{label}":{region.index}'
                    except GlasserRegion.DoesNotExist:
                        logger.error(f"GlasserRegion with index {parcel} does not exist.")
                        regions_str = ""  # Reset regions_str if region does not exist
                else:
                    logger.error(f"No parcel found for coordinates: {x}, {y}, {z}")
                    regions_str = ""

                # Store measurement data
                measurements_info[exp_index][meas_index] = {
                    'unique_identifier': uuid.uuid4(),
                    'coordinates': formatted_coordinate,
                    'regions': regions_str,
                    'description': meas_data.get('description', ''),
                    'parameters': meas_data.get('parameters', ''),
                    'interpretation': meas_data.get('interpretation', ''),
                    'label': label,
                    'x': x,
                    'y': y,
                    'z': z
                }
                logger.info(f"Processed measurement: {measurements_info[exp_index][meas_index]}")

        # Combine all data back into paper_data for serialization
        for exp_index, exp_data in experiments_info.items():
            exp_data['measurements'] = list(measurements_info[exp_index].values())
        paper_data['experiments'] = list(experiments_info.values())
        paper_data['url'] = paper_data.get('url', '')

        # Create the document metadata
        document_data = {
            'template': {'name': 'Paper1'},
            'content': {},  # Placeholder for TipTap content
            'metadata': {'paper': paper_data}
        }

        # Serialize and save the document
        document_serializer = DocumentSerializer(data=document_data)
        if document_serializer.is_valid():
            document = document_serializer.save()
            parse_paper1_template(document, document_data['metadata'])
            logger.info("Paper data successfully saved.")
            return Response(document_serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Serializer errors: {document_serializer.errors}")
            return Response(document_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
