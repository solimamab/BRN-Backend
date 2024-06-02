from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .models import Document 
from .serializers import DocumentSerializer


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