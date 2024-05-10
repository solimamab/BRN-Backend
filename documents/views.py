from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Document, Template
from .serializers import DocumentSerializer, TemplateSerializer
from editor.parsers import parse_paper1_template  # Import parsing function

class TemplateListAPI(APIView):
    def get(self, request):
        templates = Template.objects.all()
        serializer = TemplateSerializer(templates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DocumentAPI(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = DocumentSerializer(data=data)
        if serializer.is_valid():
            document = serializer.save()

            # Parse data into specific models if applicable
            if data['template']['name'] == 'Paper1':
                parse_paper1_template(document, data['metadata'])

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)