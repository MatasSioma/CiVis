from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
	ApplicationViewSet,
	CandidateJobPostingDetailView,
	CandidateJobPostingListView,
	CompanyViewSet,
	CVCheckoutView,
	CVFinalizeView,
	CVMeView,
	CVUploadView,
	IndustryViewSet,
	JobPostingViewSet,
	LoginView,
	LogoutView,
	PublicJobPostingListView,
	SessionView,
	SignupView,
	StripeWebhookView,
)

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'industries', IndustryViewSet)
router.register(r'job-postings', JobPostingViewSet)
router.register(r'applications', ApplicationViewSet)

urlpatterns = [
	path('auth/session/', SessionView.as_view(), name='auth-session'),
	path('auth/signup/', SignupView.as_view(), name='auth-signup'),
	path('auth/login/', LoginView.as_view(), name='auth-login'),
	path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
	path('cv/me/', CVMeView.as_view(), name='cv-me'),
	path('cv/upload/', CVUploadView.as_view(), name='cv-upload'),
	path('cv/checkout/', CVCheckoutView.as_view(), name='cv-checkout'),
	path('cv/finalize/', CVFinalizeView.as_view(), name='cv-finalize'),
	path('stripe/webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
	path(
		'candidate/job-postings/',
		CandidateJobPostingListView.as_view(),
		name='candidate-job-postings',
	),
	path(
		'candidate/job-postings/<uuid:pk>/',
		CandidateJobPostingDetailView.as_view(),
		name='candidate-job-posting-detail',
	),
	path(
		'public/job-postings/',
		PublicJobPostingListView.as_view(),
		name='public-job-postings',
	),
	path('', include(router.urls)),
]
