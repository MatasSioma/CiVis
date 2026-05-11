from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
	ApplicationViewSet,
	CompanyViewSet,
	CVViewSet,
	JobPostingViewSet,
	LoginView,
	LogoutView,
	SessionView,
	SkillViewSet,
	SignupView,
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
	path('', include(router.urls)),
]
