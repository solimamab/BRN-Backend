from django.urls import path
from .views import DocumentAPI, DocumentDetailAPI, DocumentList, DocumentDelete

urlpatterns = [
    path('documents/', DocumentAPI.as_view(), name='document_api'),  # For listing documents
    path('documents/<uuid:unique_identifier>/', DocumentDetailAPI.as_view(), name='document_detail'),
    path('documents/list/', DocumentList.as_view(), name='document_list'),  # For listing documents
    path('documents/delete/<uuid:unique_identifier>/', DocumentDelete.as_view(), name='document_delete'),  # For deleting documents
]