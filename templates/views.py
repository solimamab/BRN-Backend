from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated  # Optional: If you require authentication
from rest_framework.parsers import JSONParser
from .parsers import parse_document
import logging

logger = logging.getLogger(__name__)

class ProcessDocumentView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        json_data = request.data
        try:
            paper_data, experiments = parse_document(json_data)
            return JsonResponse({
                'status': 'success',
                'paper': paper_data,
                'experiments': experiments
            }, safe=False)
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)