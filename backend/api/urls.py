from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
	ApplicationViewSet,
	CompanyViewSet,
	CVViewSet,
	JobPostingViewSet,
	SkillViewSet,
)

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'skills', SkillViewSet)
router.register(r'cvs', CVViewSet)
router.register(r'job-postings', JobPostingViewSet)
router.register(r'applications', ApplicationViewSet)

urlpatterns = [
	path('', include(router.urls)),
]
