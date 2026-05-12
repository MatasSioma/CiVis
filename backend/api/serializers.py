from django.contrib.auth import password_validation
from django.contrib.auth.hashers import check_password
from rest_framework import serializers

from .models import (
	CV,
	Application,
	Company,
	CVSkill,
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

		if User.objects.filter(personal_code_hash=personal_code_hash, role=attrs['role']).exists():
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


class JobPostingSerializer(serializers.ModelSerializer):
	skills = SkillSerializer(many=True, read_only=True)

	def validate_company(self, company):
		request = self.context.get('request')

		if request and company.owner_id != request.user.id:
			raise serializers.ValidationError('Galite naudoti tik savo imone.')

		return company

	class Meta:
		model = JobPosting
		fields = [
			'id',
			'company',
			'title',
			'description',
			'location',
			'salary_min',
			'salary_max',
			'skills',
			'created_at',
			'updated_at',
		]
		read_only_fields = ['id', 'created_at', 'updated_at']


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
		fields = ['id', 'cv', 'skill', 'type', 'description', 'years_of_experience']


class CVDetailSkillSerializer(serializers.Serializer):
	name = serializers.CharField(source='skill.name')
	type = serializers.CharField()
	years_of_experience = serializers.IntegerField()


class CVDetailSerializer(serializers.ModelSerializer):
	skills = CVDetailSkillSerializer(source='cvskill_set', many=True, read_only=True)

	class Meta:
		model = CV
		fields = ['id', 'file_key', 'skills', 'created_at', 'updated_at']
		read_only_fields = fields


class CVSubmitSkillSerializer(serializers.Serializer):
	name = serializers.CharField(max_length=100)
	type = serializers.ChoiceField(choices=SkillType.choices)
	years_of_experience = serializers.IntegerField(min_value=0)


class CVSubmitSerializer(serializers.Serializer):
	file_key = serializers.CharField(max_length=512)
	skills = CVSubmitSkillSerializer(many=True, allow_empty=False)

	def validate_skills(self, value):
		names = [s['name'].strip().lower() for s in value]
		if len(names) != len(set(names)):
			raise serializers.ValidationError('Įgūdžių pavadinimai negali kartotis.')
		return value


class JobPostingSkillSerializer(serializers.ModelSerializer):
	class Meta:
		model = JobPostingSkill
		fields = [
			'id',
			'job_posting',
			'skill',
			'type',
			'description',
			'is_required',
		]
