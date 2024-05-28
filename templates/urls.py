from django.urls import path
from .views import ProcessDocumentView, PaperSubmissionView

urlpatterns = [
    # other paths
    path('documents/parse/', PaperSubmissionView.as_view(), name='process_document'),
]