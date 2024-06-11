from django.shortcuts import get_object_or_404
from requests import Response
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework import status
from django.http import JsonResponse
from django.db import transaction
from BRN import settings
from .models import Document, GlasserRegion, Paper, Experiment, Measurement
from .serializers import PaperSerializer, ExperimentSerializer, MeasurementSerializer
from .parsers import parse_document
from parcel_utils.atlas import load_atlas, find_closest_parcel
from parcel_utils import brodmann
import numpy as np
import logging

logger = logging.getLogger(__name__)

class PaperSubmissionView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        json_data = request.data.get('content')
        document_uuid = request.data.get('uuid')
        logger.debug(f"Received JSON data: {json_data}")

        try:
            document = Document.objects.get(unique_identifier=document_uuid)
            paper_data, experiments_data = parse_document(json_data)

            with transaction.atomic():
                paper = self.handle_paper(document, paper_data)
                self.handle_experiments(paper, experiments_data)

                paper_serializer = PaperSerializer(paper)
                document.metadata = {'paper': paper_serializer.data}
                document.save()

                return JsonResponse(paper_serializer.data, status=status.HTTP_201_CREATED)

        except Document.DoesNotExist:
            return JsonResponse({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def handle_paper(self, document, paper_data):
        uuid = paper_data.get('uuid')
        if uuid:
            paper = Paper.objects.filter(unique_identifier=uuid).first()
            if paper:
                self.update_paper(paper, paper_data)
            else:
                raise ValueError("Paper with given UUID not found")
        else:
            paper = self.create_paper(paper_data, document)
        return paper

    def update_paper(self, paper, data):
        paper.name = data.get('paperName', paper.name)
        paper.introduction = data.get('introduction', paper.introduction)
        paper.theory = data.get('theory', paper.theory)
        paper.summary = data.get('summary', paper.summary)
        paper.url = data.get('paperURL', paper.url)
        paper.save()

    def create_paper(self, data, document):
        return Paper.objects.create(
            name=data.get('paperName', ''),
            introduction=data.get('introduction', ''),
            theory=data.get('theory', ''),
            summary=data.get('summary', ''),
            url=data.get('paperURL', ''),
            document=document
        )

    def handle_experiments(self, paper, experiments_data):
        for exp_data in experiments_data:
            uuid = exp_data.get('uuid')
            if uuid:
                experiment = Experiment.objects.filter(unique_identifier=uuid).first()
                if experiment:
                    self.update_experiment(experiment, exp_data)
                else:
                    raise ValueError("Experiment with given UUID not found")
            else:
                experiment = self.create_experiment(exp_data, paper)

            self.handle_measurements(experiment, exp_data.get('measurements', []))

    def update_experiment(self, experiment, data):
        experiment.name = data.get('experimentName', experiment.name)
        experiment.task_context = data.get('taskContext', experiment.task_context)
        experiment.task = data.get('task', experiment.task)
        experiment.task_explained = data.get('taskExplained', experiment.task_explained)
        experiment.discussion = data.get('discussion', experiment.discussion)
        experiment.url = data.get('experimentURL', experiment.url)
        experiment.save()

    def create_experiment(self, data, paper):
        return Experiment.objects.create(
            name=data.get('experimentName', ''),
            task_context=data.get('taskContext', ''),
            task=data.get('task', ''),
            task_explained=data.get('taskExplained', ''),
            discussion=data.get('discussion', ''),
            url=data.get('experimentURL', ''),
            paper=paper
        )

    def handle_measurements(self, experiment, measurements_data):
        for meas_data in measurements_data:
            uuid = meas_data.get('uuid')
            if uuid:
                measurement = Measurement.objects.filter(unique_identifier=uuid).first()
                if measurement:
                    self.update_measurement(measurement, meas_data)
                else:
                    raise ValueError("Measurement with given UUID not found")
            else:
                self.create_measurement(meas_data, experiment)

    def update_measurement(self, measurement, data):
        measurement.description = data.get('mDescription', measurement.description)
        measurement.parameters = data.get('mParameters', measurement.parameters)
        measurement.interpretation = data.get('mInterpertation', measurement.interpretation)
        measurement.coordinates, measurement.regions = self.format_coordinates_and_label(data)
        measurement.save()

    def create_measurement(self, data, experiment):
        coordinates, region_str = self.format_coordinates_and_label(data)
        return Measurement.objects.create(
            description=data.get('mDescription', ''),
            parameters=data.get('mParameters', ''),
            interpretation=data.get('mInterpertation', ''),
            coordinates=coordinates,
            regions=region_str,
            experiment=experiment
        )

    def format_coordinates_and_label(self, meas_data):
        if 'bArea' in meas_data and meas_data['bArea']:
            x, y, z = brodmann.get_mni_from_brodmann(int(meas_data['bArea']))
        else:
            x = float(meas_data.get('xCoordinate', 0))
            y = float(meas_data.get('yCoordinate', 0))
            z = float(meas_data.get('zCoordinate', 0))
        label = meas_data.get('mLabel', '').strip()

        atlas_path = settings.GLASSER_ATLAS_PATH
        try:
            glasserAtlas = load_atlas(atlas_path)
            parcel = find_closest_parcel(glasserAtlas, np.array([x, y, z]))
        except FileNotFoundError as e:
            logger.error(f"Atlas file not found: {e}")
            raise

        if parcel:
            try:
                region = GlasserRegion.objects.get(index=str(parcel).lstrip('10'))
                regions_str = f'"{label}":{region.index}'
            except GlasserRegion.DoesNotExist:
                regions_str = f'"{label}": "Unknown"'
        else:
            regions_str = f'"{label}": "Unknown"'

        coordinates = f'"{label}": {x:.1f}, {y:.1f}, {z:.1f}'
        return coordinates, regions_str
    

class DocumentNodeManagementAPI(APIView):
    def get(self, request, unique_identifier):
        """
        Fetch metadata for a document given its unique identifier.
        """
        document = get_object_or_404(Document, unique_identifier=unique_identifier)
        if document.metadata:
            return Response(document.metadata)
        else:
            return Response({"error": "No metadata found for the specified document"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, unique_identifier):
        """
        Delete a node (paper, experiment, or measurement) based on UUID and type provided in the request.
        """
        node_type = request.GET.get('type')  # Assuming type is sent as a query parameter
        node_uuid = unique_identifier  # Assuming uuid is in the URL

        if not node_type or not node_uuid:
            return JsonResponse({'error': 'Missing type or uuid'}, status=status.HTTP_400_BAD_REQUEST)

        model_map = {
            'paper': Paper,
            'experiment': Experiment,
            'measurement': Measurement
        }

        model = model_map.get(node_type)

        if not model:
            return JsonResponse({'error': 'Invalid node type specified'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            node = model.objects.get(unique_identifier=node_uuid)
            node.delete()
            return JsonResponse({'message': f'{node_type} deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except model.DoesNotExist:
            return JsonResponse({'error': 'Node not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting {node_type}: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class DeleteNeuro1DocumentView(APIView):
    def delete(self, request, unique_identifier):
        document = get_object_or_404(Document, unique_identifier=unique_identifier)
        if document.template != 'neuro1':
            return JsonResponse({'error': 'Not a neuro1 document'}, status=400)

        try:
            with transaction.atomic():
                if document.metadata.get('experiments'):
                    for exp in document.metadata['experiments']:
                        Experiment.objects.filter(unique_identifier=exp['unique_identifier']).delete()
                        for meas in exp.get('measurements', []):
                            Measurement.objects.filter(unique_identifier=meas['unique_identifier']).delete()

                if document.metadata.get('paper'):
                    Paper.objects.filter(unique_identifier=document.metadata['paper']['unique_identifier']).delete()

                document.delete()
            return Response({'message': 'Document and all associated nodes deleted successfully.'}, status=204)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
