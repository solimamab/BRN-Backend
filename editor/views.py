from django.shortcuts import get_object_or_404, render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Document, Template
from .serializers import DocumentSerializer, TemplateSerializer
from templates.parsers import parse_paper1_template  # Import parsing function
from rest_framework import generics

class TemplateListAPI(APIView):
    def get(self, request):
        templates = Template.objects.all()
        serializer = TemplateSerializer(templates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

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