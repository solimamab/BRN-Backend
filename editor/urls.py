from django.urls import path
from .views import DocumentAPI, TemplateListAPI

urlpatterns = [
    path('templates/', TemplateListAPI.as_view(), name='template_list'),
    path('document/', DocumentAPI.as_view(), name='document_create'),
]