from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('unique_identifier', 'name', 'content', 'template', 'created_at', 'updated_at')

    def create(self, validated_data):
        document = Document.objects.create(**validated_data)
        return document