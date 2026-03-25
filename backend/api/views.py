from rest_framework import viewsets

from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by("-created_at")
    serializer_class = DocumentSerializer
