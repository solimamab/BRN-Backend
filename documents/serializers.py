from rest_framework import serializers
from .models import Document, Template

class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = '__all__'

class DocumentSerializer(serializers.ModelSerializer):
    template = TemplateSerializer()

    class Meta:
        model = Document
        fields = '__all__'
