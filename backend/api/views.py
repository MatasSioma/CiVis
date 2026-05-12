from django.contrib.auth import login, logout
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CV, Application, Company, Industry, JobPosting, JobPostingSkill, Skill, User
from .permissions import IsEmployer, IsEmployerForWrite, IsJobSeeker, IsJobSeekerForWrite
from .serializers import (
	ApplicationSerializer,
	CompanySerializer,
	CVSerializer,
	IndustrySerializer,
	JobPostingListSerializer,
	JobPostingSerializer,
	LoginSerializer,
	SignupSerializer,
	SkillSerializer,
	UserSerializer,
)


def set_session_context(request, user):
	request.session['user_id'] = str(user.id)
	request.session['user_role'] = user.role


@method_decorator(ensure_csrf_cookie, name='dispatch')
class SessionView(APIView):
	permission_classes = [permissions.AllowAny]

	def get(self, request):
		if not request.user.is_authenticated:
			return Response({'authenticated': False, 'user': None})

		return Response(
			{
				'authenticated': True,
				'user': UserSerializer(request.user).data,
			}
		)


class SignupView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		serializer = SignupSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()

		login(request, user)
		set_session_context(request, user)

		return Response(
			{
				'authenticated': True,
				'user': UserSerializer(user).data,
			},
			status=status.HTTP_201_CREATED,
		)


class LoginView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		serializer = LoginSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.validated_data['user']

		login(request, user)
		set_session_context(request, user)

		return Response(
			{
				'authenticated': True,
				'user': UserSerializer(user).data,
			}
		)


class LogoutView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		logout(request)
		return Response(status=status.HTTP_204_NO_CONTENT)


class CompanyViewSet(viewsets.ModelViewSet):
	queryset = Company.objects.all().order_by('-created_at')
	serializer_class = CompanySerializer
	permission_classes = [IsEmployer]

	def get_queryset(self):
		return Company.objects.filter(owner=self.request.user).order_by('-created_at')

	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)


class IndustryViewSet(viewsets.ModelViewSet):
	queryset = Industry.objects.all().order_by('name')
	serializer_class = IndustrySerializer
	permission_classes = [IsEmployerForWrite]
	pagination_class = None

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		name = serializer.validated_data['name'].strip()

		if not name:
			raise ValidationError({'name': 'Pavadinimas negali buti tuscias.'})

		industry, _ = Industry.objects.get_or_create(name=name)
		return Response(
			IndustrySerializer(industry).data,
			status=status.HTTP_201_CREATED,
		)


class SkillViewSet(viewsets.ModelViewSet):
	queryset = Skill.objects.all().order_by('name')
	serializer_class = SkillSerializer
	permission_classes = [IsEmployerForWrite]
	pagination_class = None


class CVViewSet(viewsets.ModelViewSet):
	queryset = CV.objects.all().order_by('-created_at')
	serializer_class = CVSerializer
	permission_classes = [IsJobSeeker]

	def get_queryset(self):
		return CV.objects.filter(user=self.request.user).order_by('-created_at')

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)


class JobPostingViewSet(viewsets.ModelViewSet):
	queryset = JobPosting.objects.all().order_by('-created_at')
	permission_classes = [IsEmployerForWrite]

	def get_serializer_class(self):
		if self.action == 'list':
			return JobPostingListSerializer

		return JobPostingSerializer

	def get_queryset(self):
		queryset = JobPosting.objects.all().order_by('-created_at')

		if (
			self.request.user.is_authenticated
			and self.request.user.role == User.Role.EMPLOYER
		):
			queryset = queryset.filter(company__owner=self.request.user)
		else:
			queryset = queryset.filter(status=JobPosting.Status.OPEN)

		if self.action in {'retrieve', 'update', 'partial_update'}:
			queryset = queryset.select_related('industry').prefetch_related(
				'jobpostingskill_set'
			)
		elif self.action == 'list':
			queryset = queryset.select_related('industry')

		return queryset

	def perform_create(self, serializer):
		company = self.request.user.companies.first()

		if company is None:
			raise ValidationError(
				{'company': 'Pirmiausia sukurkite įmonės profilį.'}
			)

		serializer.save(company=company)

	@action(detail=True, methods=['post'])
	def clone(self, request, pk=None):
		original = self.get_object()
		original_skills = list(original.jobpostingskill_set.all())

		with transaction.atomic():
			clone = JobPosting.objects.create(
				company=original.company,
				industry=original.industry,
				title=original.title,
				description=original.description,
				workplace_type=original.workplace_type,
				location=original.location,
				salary_min=original.salary_min,
				salary_max=original.salary_max,
				job_type=original.job_type,
				status=JobPosting.Status.DRAFT,
			)
			JobPostingSkill.objects.bulk_create(
				[
					JobPostingSkill(
						job_posting=clone,
						name=skill.name,
						type=skill.type,
						description=skill.description,
						is_required=skill.is_required,
						embedding=skill.embedding,
					)
					for skill in original_skills
				]
			)

		serializer = JobPostingSerializer(clone, context={'request': request})
		return Response(serializer.data, status=status.HTTP_201_CREATED)


class ApplicationViewSet(viewsets.ModelViewSet):
	queryset = Application.objects.all().order_by('-created_at')
	serializer_class = ApplicationSerializer
	permission_classes = [IsJobSeekerForWrite]

	def get_queryset(self):
		if self.request.user.role == User.Role.EMPLOYER:
			return Application.objects.filter(
				job_posting__company__owner=self.request.user
			).order_by('-created_at')

		return Application.objects.filter(applicant=self.request.user).order_by('-created_at')

	def perform_create(self, serializer):
		serializer.save(applicant=self.request.user)
