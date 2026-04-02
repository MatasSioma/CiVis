import uuid

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
import pgvector.django.indexes
import pgvector.django.vector
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
	initial = True

	dependencies = [
		('auth', '0012_alter_user_first_name_max_length'),
	]

	operations = [
		migrations.CreateModel(
			name='Skill',
			fields=[
				(
					'id',
					models.UUIDField(
						default=uuid.uuid4, editable=False, primary_key=True, serialize=False
					),
				),
				('name', models.CharField(max_length=100, unique=True)),
			],
		),
		migrations.CreateModel(
			name='User',
			fields=[
				('password', models.CharField(max_length=128, verbose_name='password')),
				(
					'last_login',
					models.DateTimeField(blank=True, null=True, verbose_name='last login'),
				),
				(
					'is_superuser',
					models.BooleanField(
						default=False,
						help_text='Designates that this user has all permissions without explicitly assigning them.',
						verbose_name='superuser status',
					),
				),
				(
					'username',
					models.CharField(
						error_messages={'unique': 'A user with that username already exists.'},
						help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
						max_length=150,
						unique=True,
						validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
						verbose_name='username',
					),
				),
				(
					'first_name',
					models.CharField(blank=True, max_length=150, verbose_name='first name'),
				),
				(
					'last_name',
					models.CharField(blank=True, max_length=150, verbose_name='last name'),
				),
				(
					'is_staff',
					models.BooleanField(
						default=False,
						help_text='Designates whether the user can log into this admin site.',
						verbose_name='staff status',
					),
				),
				(
					'is_active',
					models.BooleanField(
						default=True,
						help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.',
						verbose_name='active',
					),
				),
				(
					'date_joined',
					models.DateTimeField(
						default=django.utils.timezone.now, verbose_name='date joined'
					),
				),
				(
					'id',
					models.UUIDField(
						default=uuid.uuid4, editable=False, primary_key=True, serialize=False
					),
				),
				('email', models.EmailField(max_length=254, unique=True)),
				(
					'role',
					models.CharField(
						choices=[('job_seeker', 'Job Seeker'), ('employer', 'Employer')],
						max_length=64,
					),
				),
				('created_at', models.DateTimeField(auto_now_add=True)),
				('updated_at', models.DateTimeField(auto_now=True)),
				(
					'groups',
					models.ManyToManyField(
						blank=True,
						help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
						related_name='user_set',
						related_query_name='user',
						to='auth.group',
						verbose_name='groups',
					),
				),
				(
					'user_permissions',
					models.ManyToManyField(
						blank=True,
						help_text='Specific permissions for this user.',
						related_name='user_set',
						related_query_name='user',
						to='auth.permission',
						verbose_name='user permissions',
					),
				),
			],
			managers=[
				('objects', django.contrib.auth.models.UserManager()),
			],
		),
		migrations.CreateModel(
			name='Company',
			fields=[
				(
					'id',
					models.UUIDField(
						default=uuid.uuid4, editable=False, primary_key=True, serialize=False
					),
				),
				('name', models.CharField(max_length=255)),
				('description', models.CharField(max_length=512)),
				('created_at', models.DateTimeField(auto_now_add=True)),
				('updated_at', models.DateTimeField(auto_now=True)),
				(
					'owner',
					models.ForeignKey(
						on_delete=django.db.models.deletion.CASCADE,
						related_name='companies',
						to=settings.AUTH_USER_MODEL,
					),
				),
			],
			options={
				'verbose_name_plural': 'companies',
			},
		),
		migrations.CreateModel(
			name='CV',
			fields=[
				(
					'id',
					models.UUIDField(
						default=uuid.uuid4, editable=False, primary_key=True, serialize=False
					),
				),
				('file_url', models.URLField(max_length=512)),
				(
					'embedding',
					pgvector.django.vector.VectorField(blank=True, dimensions=1536, null=True),
				),
				('created_at', models.DateTimeField(auto_now_add=True)),
				('updated_at', models.DateTimeField(auto_now=True)),
				(
					'user',
					models.OneToOneField(
						on_delete=django.db.models.deletion.CASCADE,
						related_name='cv',
						to=settings.AUTH_USER_MODEL,
					),
				),
			],
			options={
				'verbose_name': 'CV',
				'verbose_name_plural': 'CVs',
			},
		),
		migrations.CreateModel(
			name='JobPosting',
			fields=[
				(
					'id',
					models.UUIDField(
						default=uuid.uuid4, editable=False, primary_key=True, serialize=False
					),
				),
				('title', models.CharField(max_length=255)),
				('description', models.TextField()),
				('location', models.CharField(blank=True, max_length=64, null=True)),
				('salary_min', models.IntegerField(blank=True, null=True)),
				('salary_max', models.IntegerField(blank=True, null=True)),
				(
					'embedding',
					pgvector.django.vector.VectorField(blank=True, dimensions=1536, null=True),
				),
				('created_at', models.DateTimeField(auto_now_add=True)),
				('updated_at', models.DateTimeField(auto_now=True)),
				(
					'company',
					models.ForeignKey(
						on_delete=django.db.models.deletion.CASCADE,
						related_name='job_postings',
						to='api.company',
					),
				),
			],
		),
		migrations.CreateModel(
			name='Application',
			fields=[
				(
					'id',
					models.UUIDField(
						default=uuid.uuid4, editable=False, primary_key=True, serialize=False
					),
				),
				('match_score', models.SmallIntegerField()),
				('created_at', models.DateTimeField(auto_now_add=True)),
				('updated_at', models.DateTimeField(auto_now=True)),
				(
					'applicant',
					models.ForeignKey(
						on_delete=django.db.models.deletion.CASCADE,
						related_name='applications',
						to=settings.AUTH_USER_MODEL,
					),
				),
				(
					'cv',
					models.ForeignKey(
						on_delete=django.db.models.deletion.CASCADE,
						related_name='applications',
						to='api.cv',
					),
				),
				(
					'job_posting',
					models.ForeignKey(
						on_delete=django.db.models.deletion.CASCADE,
						related_name='applications',
						to='api.jobposting',
					),
				),
			],
		),
		migrations.CreateModel(
			name='JobPostingSkill',
			fields=[
				(
					'id',
					models.BigAutoField(
						auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
					),
				),
				(
					'job_posting',
					models.ForeignKey(
						on_delete=django.db.models.deletion.CASCADE, to='api.jobposting'
					),
				),
				(
					'skill',
					models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.skill'),
				),
			],
		),
		migrations.AddField(
			model_name='jobposting',
			name='skills',
			field=models.ManyToManyField(
				blank=True,
				related_name='job_postings',
				through='api.JobPostingSkill',
				to='api.skill',
			),
		),
		migrations.CreateModel(
			name='CVSkill',
			fields=[
				(
					'id',
					models.BigAutoField(
						auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
					),
				),
				('cv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.cv')),
				(
					'skill',
					models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.skill'),
				),
			],
		),
		migrations.AddField(
			model_name='cv',
			name='skills',
			field=models.ManyToManyField(
				blank=True, related_name='cvs', through='api.CVSkill', to='api.skill'
			),
		),
		migrations.AddIndex(
			model_name='user',
			index=models.Index(fields=['role'], name='api_user_role_9b9076_idx'),
		),
		migrations.AddIndex(
			model_name='company',
			index=models.Index(fields=['owner'], name='api_company_owner_i_45041b_idx'),
		),
		migrations.AddIndex(
			model_name='company',
			index=models.Index(fields=['name'], name='api_company_name_35e8e7_idx'),
		),
		migrations.AddIndex(
			model_name='application',
			index=models.Index(fields=['applicant'], name='api_applica_applica_2c7a92_idx'),
		),
		migrations.AddIndex(
			model_name='application',
			index=models.Index(fields=['match_score'], name='api_applica_match_s_938b21_idx'),
		),
		migrations.AddIndex(
			model_name='application',
			index=models.Index(fields=['created_at'], name='api_applica_created_c9aa05_idx'),
		),
		migrations.AddConstraint(
			model_name='application',
			constraint=models.UniqueConstraint(
				fields=('job_posting', 'applicant'), name='idx_unique_application'
			),
		),
		migrations.AddConstraint(
			model_name='application',
			constraint=models.CheckConstraint(
				condition=models.Q(('match_score__gte', 0), ('match_score__lte', 100)),
				name='match_score_range',
			),
		),
		migrations.AddConstraint(
			model_name='jobpostingskill',
			constraint=models.UniqueConstraint(
				fields=('job_posting', 'skill'), name='job_posting_skill_unique'
			),
		),
		migrations.AddIndex(
			model_name='jobposting',
			index=models.Index(fields=['company'], name='api_jobpost_company_ca53a0_idx'),
		),
		migrations.AddIndex(
			model_name='jobposting',
			index=models.Index(fields=['location'], name='api_jobpost_locatio_22037f_idx'),
		),
		migrations.AddIndex(
			model_name='jobposting',
			index=models.Index(fields=['salary_min', 'salary_max'], name='idx_salary_range'),
		),
		migrations.AddIndex(
			model_name='jobposting',
			index=models.Index(fields=['created_at'], name='api_jobpost_created_7d2003_idx'),
		),
		migrations.AddIndex(
			model_name='jobposting',
			index=pgvector.django.indexes.HnswIndex(
				ef_construction=64,
				fields=['embedding'],
				m=16,
				name='idx_job_posting_embedding',
				opclasses=['vector_cosine_ops'],
			),
		),
		migrations.AddConstraint(
			model_name='cvskill',
			constraint=models.UniqueConstraint(fields=('cv', 'skill'), name='cv_skill_unique'),
		),
	]
