from .models import Paper, Experiment, Measurement
from .serializers import PaperSerializer, ExperimentSerializer
import logging

logger = logging.getLogger(__name__)

def parse_paper1_template(document, metadata):
    """
    Parse the Paper1 template metadata and associate with a Document.
    """
    paper_data = metadata.get('paper', {})
    paper_serializer = PaperSerializer(data=paper_data)
    if paper_serializer.is_valid():
        paper = paper_serializer.save(document=document)

        for exp_data in paper_data.get('experiments', []):
            experiment_serializer = ExperimentSerializer(data=exp_data, context={'paper': paper})
            if experiment_serializer.is_valid():
                experiment_serializer.save()
            else:
                logger.error(f"Experiment Error: {experiment_serializer.errors}")
    else:
        logger.error(f"Paper Error: {paper_serializer.errors}")