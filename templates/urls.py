from django.urls import path
from .views import DocumentNodeManagementAPI, PaperSubmissionView

urlpatterns = [
    # other paths
    path('documents/parse/', PaperSubmissionView.as_view(), name='process_document'),
    path('documents/node-management/<uuid:unique_identifier>/', DocumentNodeManagementAPI.as_view(), name='document_node_management'),   
]