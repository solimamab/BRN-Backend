from django.urls import path
from .views import DocumentAPI, DocumentMetadata, DocumentDetailAPI, DocumentList, DocumentDelete, DocumentNeuro1

urlpatterns = [
    path('documents/', DocumentAPI.as_view(), name='document_api'),  # For listing documents
    path('documents/<uuid:unique_identifier>/', DocumentDetailAPI.as_view(), name='document_detail'),
    path('documents/list/', DocumentList.as_view(), name='document_list'),  # For listing documents
    path('documents/delete/<uuid:unique_identifier>/', DocumentDelete.as_view(), name='document_delete'),  # For deleting documents
    path('documents/neuro1/', DocumentNeuro1.as_view(), name='document_neuro1'),  # For creating template neuro1 documents
    path('documents/metadata/<uuid:unique_identifier>/', DocumentMetadata.as_view(), name='document_metadata')
]