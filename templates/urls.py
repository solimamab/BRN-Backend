from django.urls import path
from .views import DocumentNodeManagementAPI, PaperSubmissionView, delete_neuro1_document

urlpatterns = [
    # other paths
    path('documents/parse/', PaperSubmissionView.as_view(), name='process_document'),
    path('documents/node-management/<uuid:unique_identifier>/', DocumentNodeManagementAPI.as_view(), name='document_node_management'),   
    path('documents/neuro1/delete/<uuid:unique_identifier>/', delete_neuro1_document, name='delete_neuro1_document'),
]