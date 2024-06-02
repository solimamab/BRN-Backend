import logging
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .models import Document 
from .serializers import DocumentSerializer
import json
import os

logger = logging.getLogger(__name__)

class DocumentList(generics.ListAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    class DocumentList(APIView):
        def post(self, request, *args, **kwargs):
            serializer = DocumentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DocumentAPI(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        if 'id' in data:  # Check if it's an update to an existing document
            document = Document.objects.get(pk=data['id'])
            serializer = DocumentSerializer(document, data=data)
        else:
            serializer = DocumentSerializer(data=data)
        if serializer.is_valid():
            document = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DocumentDetailAPI(APIView):
    def get(self, request, unique_identifier):
        document = get_object_or_404(Document, unique_identifier=unique_identifier)
        serializer = DocumentSerializer(document)
        return Response(serializer.data)

    def put(self, request, unique_identifier):
        document = get_object_or_404(Document, unique_identifier=unique_identifier)
        serializer = DocumentSerializer(document, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DocumentDelete(APIView):
    def delete(self, request, unique_identifier):
        document = get_object_or_404(Document, unique_identifier=unique_identifier)
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class DocumentNeuro1(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Get the base directory of the Django app
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # Construct the file path to the JSON template file
            template_file_path = os.path.join(base_dir, 'templatesJSON', 'neuro1.json')

            with open(template_file_path) as json_file:
                template_data = json.load(json_file)

            logger.info("Loaded JSON template data successfully.")

            # Create a new document with the neuro1 template
            serializer = DocumentSerializer(data={
                'name': 'N.1 Template',  # You can change the default name if needed
                'template': 'neuro1',
                'content': template_data
            })

            if serializer.is_valid():
                document = serializer.save()
                logger.info("Neuro1 template document created successfully.")
                return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
            else:
                logger.error("Serializer is invalid: %s", serializer.errors)
                return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Error occurred while creating Neuro1 template document: %s", str(e))
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)