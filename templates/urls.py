from django.urls import path
from .views import ProcessDocumentView

urlpatterns = [
    # other paths
    path('documents/parse/', ProcessDocumentView.as_view(), name='process_document'),
]