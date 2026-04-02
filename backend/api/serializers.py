from rest_framework import serializers

from .models import (
	CV,
	Application,
	Company,
	CVSkill,
	JobPosting,
	JobPostingSkill,
	Skill,
	User,
)


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ['id', 'username', 'email', 'role', 'created_at', 'updated_at']
		read_only_fields = ['id', 'created_at', 'updated_at']


class CompanySerializer(serializers.ModelSerializer):
	class Meta:
		model = Company
		fields = ['id', 'owner', 'name', 'description', 'created_at', 'updated_at']
		read_only_fields = ['id', 'created_at', 'updated_at']


class SkillSerializer(serializers.ModelSerializer):
	class Meta:
		model = Skill
		fields = ['id', 'name']
		read_only_fields = ['id']


class CVSerializer(serializers.ModelSerializer):
	skills = SkillSerializer(many=True, read_only=True)

	class Meta:
		model = CV
		fields = ['id', 'user', 'file_url', 'skills', 'created_at', 'updated_at']
		read_only_fields = ['id', 'created_at', 'updated_at']


class JobPostingSerializer(serializers.ModelSerializer):
	skills = SkillSerializer(many=True, read_only=True)

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
		read_only_fields = ['id', 'created_at', 'updated_at']


class CVSkillSerializer(serializers.ModelSerializer):
	class Meta:
		model = CVSkill
		fields = ['id', 'cv', 'skill']


class JobPostingSkillSerializer(serializers.ModelSerializer):
	class Meta:
		model = JobPostingSkill
		fields = ['id', 'job_posting', 'skill']
