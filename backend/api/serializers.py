from django.contrib.auth import password_validation
from django.contrib.auth.hashers import check_password
from django.db import transaction
from rest_framework import serializers

from .embeddings import EmbeddingError, generate_embeddings
from .models import (
	CV,
	Application,
	Company,
	CVSkill,
	Industry,
	JobPosting,
	JobPostingSkill,
	Skill,
	SkillType,
	User,
)
from .security import make_personal_code_hash


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = [
			'id',
			'email',
			'first_name',
			'last_name',
			'role',
			'date_of_birth',
			'created_at',
			'updated_at',
		]
		read_only_fields = ['id', 'created_at', 'updated_at']


class SignupSerializer(serializers.Serializer):
	personal_code = serializers.CharField(write_only=True)
	password = serializers.CharField(write_only=True, trim_whitespace=False)
	email = serializers.EmailField()
	first_name = serializers.CharField(max_length=150)
	last_name = serializers.CharField(max_length=150)
	role = serializers.ChoiceField(choices=User.Role.choices)
	date_of_birth = serializers.DateField(required=False, allow_null=True)
	company_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
	company_description = serializers.CharField(required=False, allow_blank=True)

	def validate(self, attrs):
		password_validation.validate_password(attrs['password'])

		personal_code_hash = make_personal_code_hash(attrs['personal_code'])

		if User.objects.filter(
			personal_code_hash=personal_code_hash, role=attrs['role']
		).exists():
			raise serializers.ValidationError(
				{'personal_code': 'Paskyra su siuo asmens kodu jau egzistuoja.'}
			)

		if attrs['role'] == User.Role.JOB_SEEKER and not attrs.get('date_of_birth'):
			raise serializers.ValidationError(
				{'date_of_birth': 'Darbo ieškantis asmuo turi nurodyti gimimo datą.'}
			)

		if attrs['role'] == User.Role.EMPLOYER and not attrs.get('company_name'):
			raise serializers.ValidationError(
				{'company_name': 'Darbdavio paskyrai reikalingas imones pavadinimas.'}
			)

		return attrs

	def create(self, validated_data):
		personal_code_hash = make_personal_code_hash(validated_data.pop('personal_code'))
		company_name = validated_data.pop('company_name', '').strip()
		company_description = validated_data.pop('company_description', '').strip()
		password = validated_data.pop('password')
		role = validated_data['role']

		if role != User.Role.JOB_SEEKER:
			validated_data.pop('date_of_birth', None)

		user = User(
			username=f'{role}:{personal_code_hash}',
			personal_code_hash=personal_code_hash,
			**validated_data,
		)
		user.set_password(password)
		user.save()

		if user.role == User.Role.EMPLOYER:
			Company.objects.create(
				owner=user,
				name=company_name,
				description=company_description,
			)

		return user


class LoginSerializer(serializers.Serializer):
	personal_code = serializers.CharField(write_only=True)
	password = serializers.CharField(write_only=True, trim_whitespace=False)
	role = serializers.ChoiceField(choices=User.Role.choices, write_only=True)

	def validate(self, attrs):
		personal_code_hash = make_personal_code_hash(attrs['personal_code'])
		user = User.objects.filter(
			personal_code_hash=personal_code_hash, role=attrs['role']
		).first()

		if user is None:
			raise serializers.ValidationError(
				'Naudotojas su tokiu asmens kodu ir paskyros rūšimi nerastas.'
			)

		if not check_password(attrs['password'], user.password):
			raise serializers.ValidationError('Neteisingas slaptažodis.')

		if not user.is_active:
			raise serializers.ValidationError('Paskyra neaktyvi.')

		attrs['user'] = user
		return attrs


class CompanySerializer(serializers.ModelSerializer):
	class Meta:
		model = Company
		fields = ['id', 'owner', 'name', 'description', 'created_at', 'updated_at']
		read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class IndustrySerializer(serializers.ModelSerializer):
	class Meta:
		model = Industry
		fields = ['id', 'name']
		read_only_fields = ['id']


class SkillSerializer(serializers.ModelSerializer):
	class Meta:
		model = Skill
		fields = ['id', 'name']
		read_only_fields = ['id']


class CVSerializer(serializers.ModelSerializer):
	skills = SkillSerializer(many=True, read_only=True)

	class Meta:
		model = CV
		fields = ['id', 'user', 'file_key', 'skills', 'created_at', 'updated_at']
		read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class JobPostingSkillWriteSerializer(serializers.Serializer):
	name = serializers.CharField(max_length=100)
	type = serializers.ChoiceField(choices=SkillType.choices, default=SkillType.HARD)
	description = serializers.CharField(allow_blank=True, required=False, default='')
	is_required = serializers.BooleanField(default=False)

	def validate_name(self, value):
		value = value.strip()

		if not value:
			raise serializers.ValidationError('Įgūdžio pavadinimas negali būti tuščias.')

		return value


class JobPostingSkillReadSerializer(serializers.ModelSerializer):
	class Meta:
		model = JobPostingSkill
		fields = ['name', 'type', 'description', 'is_required']


class JobPostingListSerializer(serializers.ModelSerializer):
	industry_name = serializers.CharField(source='industry.name', read_only=True)

	class Meta:
		model = JobPosting
		fields = [
			'id',
			'title',
			'industry',
			'industry_name',
			'job_type',
			'workplace_type',
			'status',
			'location',
			'salary_min',
			'salary_max',
			'created_at',
		]
		read_only_fields = fields


class JobPostingSerializer(serializers.ModelSerializer):
	industry = serializers.PrimaryKeyRelatedField(queryset=Industry.objects.all())
	skills = JobPostingSkillWriteSerializer(many=True, write_only=True)
	skills_detail = JobPostingSkillReadSerializer(
		source='jobpostingskill_set', many=True, read_only=True
	)

	class Meta:
		model = JobPosting
		fields = [
			'id',
			'company',
			'industry',
			'title',
			'description',
			'workplace_type',
			'location',
			'salary_min',
			'salary_max',
			'job_type',
			'status',
			'skills',
			'skills_detail',
			'created_at',
			'updated_at',
		]
		read_only_fields = ['id', 'company', 'created_at', 'updated_at']

	def validate(self, attrs):
		skills = attrs.get('skills', [])

		if len(skills) > 20:
			raise serializers.ValidationError(
				{'skills': 'Galima nurodyti daugiausiai 20 įgūdžių.'}
			)

		names_lower = [s['name'].lower() for s in skills]

		if len(names_lower) != len(set(names_lower)):
			raise serializers.ValidationError(
				{'skills': 'Įgūdžiai skelbime turi būti unikalūs.'}
			)

		salary_min = attrs.get('salary_min')
		salary_max = attrs.get('salary_max')

		if salary_min is not None and salary_max is not None and salary_min > salary_max:
			raise serializers.ValidationError(
				{'salary_min': 'Minimalus atlyginimas negali būti didesnis už maksimalų.'}
			)

		return attrs

	def _prepare_skill_rows(self, skills_payload):
		"""Returns list of dicts with embedding-ready text."""
		prepared = []

		for entry in skills_payload:
			name = entry['name']
			skill_type = entry.get('type', SkillType.HARD)
			description = (entry.get('description') or '').strip()
			type_label = SkillType(skill_type).label

			if description:
				embed_text = f'{name} — {type_label}: {description}'
			else:
				embed_text = f'{name} — {type_label}'

			prepared.append(
				{
					'name': name,
					'type': skill_type,
					'description': entry.get('description', ''),
					'is_required': entry.get('is_required', False),
					'embed_text': embed_text,
				}
			)

		return prepared

	def _build_skill_rows(self, posting, prepared, embeddings):
		return [
			JobPostingSkill(
				job_posting=posting,
				name=row['name'],
				type=row['type'],
				description=row['description'],
				is_required=row['is_required'],
				embedding=embedding,
			)
			for row, embedding in zip(prepared, embeddings)
		]

	def create(self, validated_data):
		skills_payload = validated_data.pop('skills', [])
		prepared = self._prepare_skill_rows(skills_payload)

		try:
			embeddings = generate_embeddings([r['embed_text'] for r in prepared])
		except EmbeddingError as exc:
			raise serializers.ValidationError(
				{'skills': f'Nepavyko sugeneruoti embeddingų: {exc}'}
			)

		with transaction.atomic():
			posting = JobPosting.objects.create(**validated_data)
			JobPostingSkill.objects.bulk_create(
				self._build_skill_rows(posting, prepared, embeddings)
			)

		return posting

	def update(self, instance, validated_data):
		skills_payload = validated_data.pop('skills', None)
		embeddings = None
		prepared = None

		if skills_payload is not None:
			prepared = self._prepare_skill_rows(skills_payload)

			try:
				embeddings = generate_embeddings([r['embed_text'] for r in prepared])
			except EmbeddingError as exc:
				raise serializers.ValidationError(
					{'skills': f'Nepavyko sugeneruoti embeddingų: {exc}'}
				)

		with transaction.atomic():
			for field, value in validated_data.items():
				setattr(instance, field, value)

			instance.save()

			if prepared is not None:
				JobPostingSkill.objects.filter(job_posting=instance).delete()
				JobPostingSkill.objects.bulk_create(
					self._build_skill_rows(instance, prepared, embeddings)
				)

		return instance


class ApplicationSerializer(serializers.ModelSerializer):
	def validate_cv(self, cv):
		request = self.context.get('request')

		if request and cv.user_id != request.user.id:
			raise serializers.ValidationError('Galite naudoti tik savo CV.')

		return cv

	class Meta:
		model = Application
		fields = [
			'id',
			'job_posting',
			'applicant',
			'cv',
			'match_score',
			'created_at',
			'updated_at',
		]
		read_only_fields = ['id', 'applicant', 'created_at', 'updated_at']


class CVSkillSerializer(serializers.ModelSerializer):
	class Meta:
		model = CVSkill
		fields = ['id', 'cv', 'skill', 'type', 'description']


class JobPostingSkillSerializer(serializers.ModelSerializer):
	class Meta:
		model = JobPostingSkill
		fields = [
			'id',
			'job_posting',
			'name',
			'type',
			'description',
			'is_required',
		]
