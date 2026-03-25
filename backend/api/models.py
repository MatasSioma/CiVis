from django.db import models
from pgvector.django import VectorField


class Document(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
