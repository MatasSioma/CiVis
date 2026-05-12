from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from pypdf import PdfReader
from rest_framework import permissions, status, viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .extraction import extract_skills_from_text
from .models import CV, Application, Company, CVSkill, JobPosting, Skill, User
from .permissions import IsEmployer, IsEmployerForWrite, IsJobSeeker, IsJobSeekerForWrite
from .serializers import (
	ApplicationSerializer,
	CompanySerializer,
	CVDetailSerializer,
	CVSerializer,
	CVSubmitSerializer,
	JobPostingSerializer,
	LoginSerializer,
	SignupSerializer,
	SkillSerializer,
	UserSerializer,
)
from .storage import upload_cv


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


class CVUploadView(APIView):
	permission_classes = [IsJobSeeker]
	parser_classes = [MultiPartParser]

	def post(self, request):
		file = request.FILES.get('file')

		if not file:
			return Response(
				{'file': ['Failas privalomas.']},
				status=status.HTTP_400_BAD_REQUEST,
			)

		if file.content_type != 'application/pdf':
			return Response(
				{'file': ['Leidžiami tik PDF failai.']},
				status=status.HTTP_400_BAD_REQUEST,
			)

		if file.size > 10 * 1024 * 1024:
			return Response(
				{'file': ['Failo dydis negali viršyti 10 MB.']},
				status=status.HTTP_400_BAD_REQUEST,
			)

		reader = PdfReader(file)
		text = '\n'.join(page.extract_text() or '' for page in reader.pages)

		file.seek(0)
		file_key = upload_cv(file, file.name)

		if not text.strip():
			return Response(
				{'file': ['Nepavyko išgauti teksto iš PDF failo.']},
				status=status.HTTP_400_BAD_REQUEST,
			)

		skills = extract_skills_from_text(text)

		return Response({'file_key': file_key, 'skills': skills})


class CVSubmitView(APIView):
	permission_classes = [IsJobSeeker]

	def post(self, request):
		serializer = CVSubmitSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		file_key = serializer.validated_data['file_key']
		skills_data = serializer.validated_data['skills']

		CV.objects.filter(user=request.user).delete()

		cv = CV.objects.create(user=request.user, file_key=file_key)

		for skill_data in skills_data:
			skill_name = skill_data['name'].strip().lower()
			skill, _created = Skill.objects.get_or_create(name=skill_name)
			CVSkill.objects.create(
				cv=cv,
				skill=skill,
				type=skill_data['type'],
				years_of_experience=skill_data['years_of_experience'],
			)

		return Response(CVSerializer(cv).data, status=status.HTTP_201_CREATED)


class CVMeView(APIView):
	permission_classes = [IsJobSeeker]

	def get(self, request):
		try:
			cv = CV.objects.prefetch_related('cvskill_set__skill').get(user=request.user)
		except CV.DoesNotExist:
			return Response(
				{'detail': 'CV nerastas.'},
				status=status.HTTP_404_NOT_FOUND,
			)
		return Response(CVDetailSerializer(cv).data)


class CompanyViewSet(viewsets.ModelViewSet):
	queryset = Company.objects.all().order_by('-created_at')
	serializer_class = CompanySerializer
	permission_classes = [IsEmployer]

	def get_queryset(self):
		return Company.objects.filter(owner=self.request.user).order_by('-created_at')

	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)


class SkillViewSet(viewsets.ModelViewSet):
	queryset = Skill.objects.all().order_by('name')
	serializer_class = SkillSerializer


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
	serializer_class = JobPostingSerializer
	permission_classes = [IsEmployerForWrite]

	def get_queryset(self):
		queryset = JobPosting.objects.all().order_by('-created_at')

		if self.request.user.is_authenticated and self.request.user.role == User.Role.EMPLOYER:
			return queryset.filter(company__owner=self.request.user)

		return queryset.filter(status=JobPosting.Status.OPEN)


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
