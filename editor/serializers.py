from rest_framework import serializers
from .models import Paper, Experiment, Measurement

class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measurement
        exclude = ('experiment',)  # Exclude experiment since it will be set in the ExperimentSerializer

class ExperimentSerializer(serializers.ModelSerializer):
    measurements = MeasurementSerializer(many=True, required=False)

    class Meta:
        model = Experiment
        exclude = ('paper',)  # Exclude the 'paper' field to prevent it from being processed automatically

    def create(self, validated_data):
        measurements_data = validated_data.pop('measurements', [])
        paper = self.context['paper']
        experiment = Experiment.objects.create(paper=paper, **validated_data)
        for meas_data in measurements_data:
            Measurement.objects.create(experiment=experiment, **meas_data)
        return experiment

class PaperSerializer(serializers.ModelSerializer):
    experiments = ExperimentSerializer(many=True)

    class Meta:
        model = Paper
        fields = '__all__'

    def create(self, validated_data):
        experiments_data = validated_data.pop('experiments', [])
        paper = Paper.objects.create(**validated_data)
        for exp_data in experiments_data:
            exp_serializer = ExperimentSerializer(data=exp_data, context={'paper': paper})
            if exp_serializer.is_valid():
                exp_serializer.save()
            else:
                raise serializers.ValidationError(exp_serializer.errors)
        return paper

class PaperWithDocumentSerializer(serializers.ModelSerializer):
    document = serializers.UUIDField(source='document.unique_identifier', read_only=True)

    class Meta:
        model = Paper
        fields = '__all__'