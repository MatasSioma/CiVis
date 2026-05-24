import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from pgvector.django import HnswIndex, VectorField


class User(AbstractUser):
	class Role(models.TextChoices):
		JOB_SEEKER = 'job_seeker', 'Job Seeker'
		EMPLOYER = 'employer', 'Employer'

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	email = models.EmailField()
	personal_code_hash = models.CharField(max_length=64, null=True, blank=True)
	role = models.CharField(max_length=64, choices=Role.choices)
	date_of_birth = models.DateField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['personal_code_hash', 'role'],
				name='unique_personal_code_per_role',
			),
		]
		indexes = [
			models.Index(fields=['personal_code_hash'], name='api_user_person_3d4420_idx'),
			models.Index(fields=['role']),
		]

	def __str__(self):
		return self.username


class Company(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies')
	name = models.CharField(max_length=255)
	description = models.TextField()
	registration_code = models.CharField(max_length=9, blank=True, default='')
	address = models.CharField(max_length=255, blank=True, default='')
	contact_email = models.EmailField(blank=True, default='')
	contact_phone = models.CharField(max_length=32, blank=True, default='')
	website = models.URLField(blank=True, default='')
	date_established = models.DateField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name_plural = 'companies'
		indexes = [
			models.Index(fields=['name']),
		]

	def __str__(self):
		return self.name


class Industry(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=100, unique=True)

	class Meta:
		verbose_name_plural = 'industries'

	def __str__(self):
		return self.name


class CV(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cv')
	file_key = models.CharField(max_length=512)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = 'CV'
		verbose_name_plural = 'CVs'

	def __str__(self):
		return f'CV of {self.user}'


class PendingCVPayment(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pending_cv_payments')
	file_key = models.CharField(max_length=512)
	skills_data = models.JSONField()
	stripe_session_id = models.CharField(max_length=255, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'PendingCV({self.user}, {self.stripe_session_id})'


class JobPosting(models.Model):
	class Status(models.TextChoices):
		DRAFT = 'draft', 'Draft'
		OPEN = 'open', 'Open'
		CLOSED = 'closed', 'Closed'

	class JobType(models.TextChoices):
		FULL_TIME = 'full_time', 'Full-time'
		PART_TIME = 'part_time', 'Part-time'
		CONTRACT = 'contract', 'Contract'
		INTERNSHIP = 'internship', 'Internship'
		TEMPORARY = 'temporary', 'Temporary'

	class WorkplaceType(models.TextChoices):
		ON_SITE = 'on_site', 'On-site'
		REMOTE = 'remote', 'Remote'

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='job_postings')
	industry = models.ForeignKey(Industry, on_delete=models.PROTECT, related_name='job_postings')
	title = models.CharField(max_length=255)
	description = models.TextField()
	workplace_type = models.CharField(
		max_length=16, choices=WorkplaceType.choices, default=WorkplaceType.ON_SITE
	)
	location = models.CharField(max_length=64, null=True, blank=True)
	salary_min = models.IntegerField(null=True, blank=True)
	salary_max = models.IntegerField(null=True, blank=True)
	job_type = models.CharField(max_length=32, choices=JobType.choices)
	status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		indexes = [
			models.Index(fields=['location']),
			models.Index(fields=['job_type']),
			models.Index(fields=['status']),
			models.Index(fields=['salary_min', 'salary_max'], name='idx_salary_range'),
			models.Index(fields=['created_at']),
		]

	def __str__(self):
		return self.title


class Application(models.Model):
	class Status(models.TextChoices):
		PENDING = 'pending', 'Pending'
		REJECTED = 'rejected', 'Rejected'
		ACCEPTED = 'accepted', 'Accepted'

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	job_posting = models.ForeignKey(
		JobPosting, on_delete=models.CASCADE, related_name='applications'
	)
	applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
	cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='applications')
	match_score = models.SmallIntegerField()
	status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['job_posting', 'applicant'],
				name='idx_unique_application',
			),
			models.CheckConstraint(
				condition=models.Q(match_score__gte=0) & models.Q(match_score__lte=100),
				name='match_score_range',
			),
		]
		indexes = [
			models.Index(
				fields=['job_posting', '-match_score'],
				name='idx_application_ranking',
			),
			models.Index(fields=['status']),
			models.Index(fields=['created_at']),
		]

	def __str__(self):
		return f'{self.applicant} → {self.job_posting}'


class SkillType(models.TextChoices):
	HARD = 'hard', 'Hard skill'
	SOFT = 'soft', 'Soft skill'
	EXPERIENCE = 'experience', 'Experience'


class CVSkill(models.Model):
	cv = models.ForeignKey(CV, on_delete=models.CASCADE)
	name = models.CharField(max_length=100)
	type = models.CharField(max_length=16, choices=SkillType.choices, default=SkillType.HARD)
	description = models.TextField(blank=True)
	embedding = VectorField(dimensions=1536, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['cv', 'name'], name='cv_skill_unique'),
		]
		indexes = [
			HnswIndex(
				name='idx_cv_skill_embedding',
				fields=['embedding'],
				m=16,
				ef_construction=64,
				opclasses=['vector_cosine_ops'],
			),
		]

	def __str__(self):
		return f'{self.cv} - {self.name}'


class JobPostingSkill(models.Model):
	job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
	name = models.CharField(max_length=100)
	type = models.CharField(max_length=16, choices=SkillType.choices, default=SkillType.HARD)
	description = models.TextField(blank=True)
	is_required = models.BooleanField(default=False)
	embedding = VectorField(dimensions=1536, null=True, blank=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['job_posting', 'name'], name='job_posting_skill_unique'
			),
		]
		indexes = [
			HnswIndex(
				name='idx_job_posting_skill_embedding',
				fields=['embedding'],
				m=16,
				ef_construction=64,
				opclasses=['vector_cosine_ops'],
			),
		]

	def __str__(self):
		return f'{self.job_posting} - {self.name}'


class MatchScore(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	job_posting = models.ForeignKey(
		JobPosting, on_delete=models.CASCADE, related_name='match_scores'
	)
	cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='match_scores')
	score = models.SmallIntegerField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['job_posting', 'cv'], name='match_score_unique'
			),
			models.CheckConstraint(
				condition=models.Q(score__gte=0) & models.Q(score__lte=100),
				name='match_score_value_range',
			),
		]
		indexes = [
			models.Index(fields=['cv', '-score'], name='idx_match_score_cv_score'),
		]

	def __str__(self):
		return f'MatchScore({self.cv}, {self.job_posting}) = {self.score}'
