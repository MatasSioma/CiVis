from rest_framework import viewsets

from .models import CV, Application, Company, JobPosting, Skill
from .serializers import (
	ApplicationSerializer,
	CompanySerializer,
	CVSerializer,
	JobPostingSerializer,
	SkillSerializer,
)


class CompanyViewSet(viewsets.ModelViewSet):
	queryset = Company.objects.all().order_by('-created_at')
	serializer_class = CompanySerializer


class SkillViewSet(viewsets.ModelViewSet):
	queryset = Skill.objects.all().order_by('name')
	serializer_class = SkillSerializer


class CVViewSet(viewsets.ModelViewSet):
	queryset = CV.objects.all().order_by('-created_at')
	serializer_class = CVSerializer


class JobPostingViewSet(viewsets.ModelViewSet):
	queryset = JobPosting.objects.all().order_by('-created_at')
	serializer_class = JobPostingSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
	queryset = Application.objects.all().order_by('-created_at')
	serializer_class = ApplicationSerializer
