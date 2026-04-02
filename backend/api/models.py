import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from pgvector.django import HnswIndex, VectorField


class User(AbstractUser):
	class Role(models.TextChoices):
		JOB_SEEKER = 'job_seeker', 'Job Seeker'
		EMPLOYER = 'employer', 'Employer'

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	email = models.EmailField(unique=True)
	role = models.CharField(max_length=64, choices=Role.choices)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		indexes = [
			models.Index(fields=['role']),
		]

	def __str__(self):
		return self.username


class Company(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies')
	name = models.CharField(max_length=255)
	description = models.CharField(max_length=512)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name_plural = 'companies'
		indexes = [
			models.Index(fields=['owner']),
			models.Index(fields=['name']),
		]

	def __str__(self):
		return self.name


class Skill(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=100, unique=True)

	def __str__(self):
		return self.name


class CV(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cv')
	file_url = models.URLField(max_length=512)
	embedding = VectorField(dimensions=1536, null=True, blank=True)
	skills = models.ManyToManyField(Skill, through='CVSkill', related_name='cvs', blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = 'CV'
		verbose_name_plural = 'CVs'

	def __str__(self):
		return f'CV of {self.user}'


class JobPosting(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='job_postings')
	title = models.CharField(max_length=255)
	description = models.TextField()
	location = models.CharField(max_length=64, null=True, blank=True)
	salary_min = models.IntegerField(null=True, blank=True)
	salary_max = models.IntegerField(null=True, blank=True)
	embedding = VectorField(dimensions=1536, null=True, blank=True)
	skills = models.ManyToManyField(
		Skill, through='JobPostingSkill', related_name='job_postings', blank=True
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		indexes = [
			models.Index(fields=['company']),
			models.Index(fields=['location']),
			models.Index(fields=['salary_min', 'salary_max'], name='idx_salary_range'),
			models.Index(fields=['created_at']),
			HnswIndex(
				name='idx_job_posting_embedding',
				fields=['embedding'],
				m=16,
				ef_construction=64,
				opclasses=['vector_cosine_ops'],
			),
		]

	def __str__(self):
		return self.title


class Application(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	job_posting = models.ForeignKey(
		JobPosting, on_delete=models.CASCADE, related_name='applications'
	)
	applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
	cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='applications')
	match_score = models.SmallIntegerField()
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
			models.Index(fields=['applicant']),
			models.Index(fields=['match_score']),
			models.Index(fields=['created_at']),
		]

	def __str__(self):
		return f'{self.applicant} → {self.job_posting}'


class CVSkill(models.Model):
	cv = models.ForeignKey(CV, on_delete=models.CASCADE)
	skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['cv', 'skill'], name='cv_skill_unique'),
		]

	def __str__(self):
		return f'{self.cv} - {self.skill}'


class JobPostingSkill(models.Model):
	job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
	skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['job_posting', 'skill'], name='job_posting_skill_unique'
			),
		]

	def __str__(self):
		return f'{self.job_posting} - {self.skill}'
