from rest_framework import serializers
from .models import Document, Template

class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = '__all__'

class DocumentSerializer(serializers.ModelSerializer):
    template = TemplateSerializer(required=False)  # Ensure this is set correctly

    class Meta:
        model = Document
        fields = ('unique_identifier', 'content', 'template', 'created_at', 'updated_at')

    def create(self, validated_data):
        template_data = validated_data.pop('template', None)
        document = Document.objects.create(**validated_data)
        if template_data:
            # Assuming 'Template' is a related model and we're creating a new instance
            template = Template.objects.create(**template_data, document=document)
            document.template = template
            document.save()
        return document