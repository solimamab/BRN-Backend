from django.urls import path
from .views import DocumentAPI, TemplateListAPI, DocumentDetailAPI

urlpatterns = [
    path('api/templates/', TemplateListAPI.as_view(), name='template_list'),
    path('documents/', DocumentAPI.as_view(), name='document_list'),  # For listing documents
    path('documents/<uuid:unique_identifier>/', DocumentDetailAPI.as_view(), name='document_detail'),

]