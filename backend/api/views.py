import stripe
from django.conf import settings as django_settings
from django.contrib.auth import login, logout
from django.db import transaction
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from pypdf import PdfReader
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.parsers import MultiPartParser

from .embeddings import EmbeddingError, generate_embeddings
from .extraction import extract_skills_from_text
from .models import (
	CV,
	Application,
	Company,
	CVSkill,
	Industry,
	JobPosting,
	JobPostingSkill,
	PendingCVPayment,
	User,
)
from .permissions import IsEmployer, IsEmployerForWrite, IsJobSeeker, IsJobSeekerForWrite
from .serializers import (
	ApplicationSerializer,
	CompanySerializer,
	CVDetailSerializer,
	CVSubmitSerializer,
	IndustrySerializer,
	JobPostingListSerializer,
	JobPostingSerializer,
	LoginSerializer,
	SignupSerializer,
	UserSerializer,
	skill_embed_text,
)
from .storage import upload_cv

stripe.api_key = django_settings.STRIPE_SECRET_KEY


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


def create_cv_for_user(user, file_key, skills_data):
	prepared = []

	for skill_data in skills_data:
		name = skill_data['name'].strip()
		skill_type = skill_data['type']
		description = (skill_data.get('description') or '').strip()
		prepared.append(
			{
				'name': name,
				'type': skill_type,
				'description': description,
				'embed_text': skill_embed_text(name, skill_type, description),
			}
		)

	try:
		embeddings = generate_embeddings([r['embed_text'] for r in prepared]) if prepared else []
	except EmbeddingError as exc:
		raise ValidationError({'skills': f'Nepavyko sugeneruoti embeddingų: {exc}'}) from exc

	with transaction.atomic():
		CV.objects.filter(user=user).delete()
		cv = CV.objects.create(user=user, file_key=file_key)
		CVSkill.objects.bulk_create(
			[
				CVSkill(
					cv=cv,
					name=row['name'],
					type=row['type'],
					description=row['description'],
					embedding=embedding,
				)
				for row, embedding in zip(prepared, embeddings)
			]
		)

	return cv


class CVCheckoutView(APIView):
	permission_classes = [IsJobSeeker]

	def post(self, request):
		serializer = CVSubmitSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		file_key = serializer.validated_data['file_key']
		skills_data = serializer.validated_data['skills']

		session = stripe.checkout.Session.create(
			payment_method_types=['card'],
			line_items=[{'price': django_settings.STRIPE_PRICE_ID, 'quantity': 1}],
			mode='payment',
			success_url=(
				f'{django_settings.FRONTEND_URL}/candidate/my-cv'
				'?payment=success&session_id={CHECKOUT_SESSION_ID}'
			),
			cancel_url=f'{django_settings.FRONTEND_URL}/candidate/upload-cv?payment=cancelled',
			client_reference_id=str(request.user.id),
		)

		PendingCVPayment.objects.filter(user=request.user).delete()
		PendingCVPayment.objects.create(
			user=request.user,
			file_key=file_key,
			skills_data=skills_data,
			stripe_session_id=session.id,
		)

		return Response({'checkout_url': session.url})


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
	permission_classes = [permissions.AllowAny]
	authentication_classes = []

	def post(self, request):
		payload = request.body
		sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

		try:
			event = stripe.Webhook.construct_event(
				payload, sig_header, django_settings.STRIPE_WEBHOOK_SECRET
			)
		except (ValueError, stripe.SignatureVerificationError):
			return Response(status=status.HTTP_400_BAD_REQUEST)

		if event['type'] == 'checkout.session.completed':
			session_data = event['data']['object']
			_finalize_pending_payment(session_data['id'])

		return Response(status=status.HTTP_200_OK)


def _finalize_pending_payment(session_id):
	"""Idempotently convert a PendingCVPayment into a CV. Returns the CV, or
	None if there's no pending payment for this session id."""
	with transaction.atomic():
		try:
			pending = (
				PendingCVPayment.objects
				.select_for_update()
				.select_related('user')
				.get(stripe_session_id=session_id)
			)
		except PendingCVPayment.DoesNotExist:
			return None

		cv = create_cv_for_user(pending.user, pending.file_key, pending.skills_data)
		pending.delete()

	return cv


class CVFinalizeView(APIView):
	"""Frontend hits this on return from Stripe checkout so the CV is saved
	even when the Stripe webhook can't reach the server (local dev). Safe to
	race with the webhook — whichever finds the PendingCVPayment row first
	wins, the other becomes a no-op."""

	permission_classes = [IsJobSeeker]

	def post(self, request):
		session_id = (request.data.get('session_id') or '').strip()

		if not session_id:
			return Response(
				{'session_id': ['Privaloma.']},
				status=status.HTTP_400_BAD_REQUEST,
			)

		pending = PendingCVPayment.objects.filter(
			user=request.user, stripe_session_id=session_id
		).first()

		if pending is None:
			# Webhook already finalized (or there was no pending payment for this
			# user). Return existing CV if any.
			try:
				cv = CV.objects.get(user=request.user)
				return Response(CVDetailSerializer(cv).data)
			except CV.DoesNotExist:
				return Response(
					{'detail': 'CV nerastas.'},
					status=status.HTTP_404_NOT_FOUND,
				)

		session = stripe.checkout.Session.retrieve(session_id)

		if session.payment_status != 'paid':
			return Response(
				{'detail': 'Mokėjimas dar nepatvirtintas.'},
				status=status.HTTP_402_PAYMENT_REQUIRED,
			)

		cv = _finalize_pending_payment(session_id)

		if cv is None:
			# Webhook beat us to it after our initial check.
			cv = CV.objects.get(user=request.user)

		return Response(CVDetailSerializer(cv).data)


class CVMeView(APIView):
	permission_classes = [IsJobSeeker]

	def get(self, request):
		try:
			cv = CV.objects.prefetch_related('cvskill_set').get(user=request.user)
		except CV.DoesNotExist:
			return Response(
				{'detail': 'CV nerastas.'},
				status=status.HTTP_404_NOT_FOUND,
			)
		return Response(CVDetailSerializer(cv).data)

	def delete(self, request):
		deleted, _ = CV.objects.filter(user=request.user).delete()

		if not deleted:
			return Response(
				{'detail': 'CV nerastas.'},
				status=status.HTTP_404_NOT_FOUND,
			)

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


class JobPostingViewSet(viewsets.ModelViewSet):
	queryset = JobPosting.objects.all()
	permission_classes = [IsEmployerForWrite]
	filter_backends = [SearchFilter, OrderingFilter]
	search_fields = ['title']
	ordering_fields = ['created_at', 'title', 'applicant_count']
	ordering = ['-created_at']

	def get_serializer_class(self):
		if self.action == 'list':
			return JobPostingListSerializer

		return JobPostingSerializer

	def get_queryset(self):
		queryset = JobPosting.objects.all()

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
			queryset = queryset.select_related('industry').annotate(
				applicant_count=Count('applications')
			)

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
