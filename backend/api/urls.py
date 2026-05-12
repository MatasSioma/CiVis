from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
	ApplicationViewSet,
	CompanyViewSet,
	CVCheckoutView,
	CVMeView,
	CVSubmitView,
	CVUploadView,
	CVViewSet,
	JobPostingViewSet,
	LoginView,
	LogoutView,
	SessionView,
	SignupView,
	SkillViewSet,
	StripeWebhookView,
)

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'skills', SkillViewSet)
router.register(r'cvs', CVViewSet)
router.register(r'job-postings', JobPostingViewSet)
router.register(r'applications', ApplicationViewSet)

urlpatterns = [
	path('auth/session/', SessionView.as_view(), name='auth-session'),
	path('auth/signup/', SignupView.as_view(), name='auth-signup'),
	path('auth/login/', LoginView.as_view(), name='auth-login'),
	path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
	path('cv/me/', CVMeView.as_view(), name='cv-me'),
	path('cv/upload/', CVUploadView.as_view(), name='cv-upload'),
	path('cv/submit/', CVSubmitView.as_view(), name='cv-submit'),
	path('cv/checkout/', CVCheckoutView.as_view(), name='cv-checkout'),
	path('stripe/webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
	path('', include(router.urls)),
]
