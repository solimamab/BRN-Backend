# serializers.py
from venv import logger
from rest_framework import serializers
from .models import Paper, Experiment, Measurement

class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measurement
        fields = ['description', 'parameters', 'interpretation', 'coordinates', 'regions', 'unique_identifier']

class ExperimentSerializer(serializers.ModelSerializer):
    measurements = MeasurementSerializer(many=True)

    class Meta:
        model = Experiment
        fields = ['name', 'task_context', 'task', 'task_explained', 'discussion', 'url', 'measurements', 'unique_identifier']

    def create(self, validated_data):
        measurements_data = validated_data.pop('measurements', [])
        experiment = Experiment.objects.create(**validated_data)
        for measurement_data in measurements_data:
            Measurement.objects.create(experiment=experiment, **measurement_data)
        return experiment

 
class PaperSerializer(serializers.ModelSerializer):
    experiments = ExperimentSerializer(many=True)

    class Meta:
        model = Paper
        fields = ['name', 'introduction', 'theory', 'summary', 'url', 'experiments', 'unique_identifier', 'document']

    def create(self, validated_data):
        experiments_data = validated_data.pop('experiments', [])
        paper = Paper.objects.create(**validated_data)
        logger.debug("Creating paper with data: {}".format(validated_data))
        for experiment_data in experiments_data:
            experiment_serializer = ExperimentSerializer(data=experiment_data)
            if experiment_serializer.is_valid():
                experiment_serializer.save(paper=paper)
            else:
                logger.error("Experiment validation errors: {}".format(experiment_serializer.errors))
                raise serializers.ValidationError(experiment_serializer.errors)
        return paper
