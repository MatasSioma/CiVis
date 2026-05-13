from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

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


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
	list_display = (
		'username',
		'email',
		'first_name',
		'last_name',
		'role',
		'date_of_birth',
		'is_staff',
	)
	list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
	search_fields = ('username', 'email', 'first_name', 'last_name')
	ordering = ('-date_joined',)
	fieldsets = DjangoUserAdmin.fieldsets + (
		('CiVis', {'fields': ('role', 'date_of_birth', 'personal_code_hash')}),
	)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
	list_display = ('name', 'owner', 'created_at')
	search_fields = ('name', 'owner__username', 'owner__email')
	list_filter = ('created_at',)
	autocomplete_fields = ('owner',)


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)


class CVSkillInline(admin.TabularInline):
	model = CVSkill
	extra = 0
	fields = ('name', 'type', 'description')


@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
	list_display = ('user', 'file_key', 'created_at')
	search_fields = ('user__username', 'user__email', 'file_key')
	list_filter = ('created_at',)
	autocomplete_fields = ('user',)
	inlines = [CVSkillInline]


class JobPostingSkillInline(admin.TabularInline):
	model = JobPostingSkill
	extra = 0
	fields = ('name', 'type', 'is_required', 'description')


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
	list_display = ('title', 'company', 'industry', 'job_type', 'status', 'created_at')
	list_filter = ('status', 'job_type', 'industry', 'created_at')
	search_fields = ('title', 'company__name', 'description', 'location')
	autocomplete_fields = ('company', 'industry')
	inlines = [JobPostingSkillInline]


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
	list_display = ('applicant', 'job_posting', 'match_score', 'status', 'created_at')
	list_filter = ('status', 'created_at')
	search_fields = ('applicant__username', 'job_posting__title')
	autocomplete_fields = ('applicant', 'cv', 'job_posting')


@admin.register(CVSkill)
class CVSkillAdmin(admin.ModelAdmin):
	list_display = ('cv', 'name', 'type')
	list_filter = ('type',)
	search_fields = ('cv__user__username', 'name', 'description')
	autocomplete_fields = ('cv',)


@admin.register(PendingCVPayment)
class PendingCVPaymentAdmin(admin.ModelAdmin):
	list_display = ('user', 'stripe_session_id', 'created_at')
	search_fields = ('user__username', 'stripe_session_id')
	readonly_fields = ('stripe_session_id', 'skills_data')


@admin.register(JobPostingSkill)
class JobPostingSkillAdmin(admin.ModelAdmin):
	list_display = ('job_posting', 'name', 'type', 'is_required')
	list_filter = ('type', 'is_required')
	search_fields = ('job_posting__title', 'name', 'description')
	autocomplete_fields = ('job_posting',)
