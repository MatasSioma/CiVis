from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import CV, Application, Company, CVSkill, Industry, JobPosting, User


class CandidateProfileAPITest(APITestCase):
	"""KAN-32: US-03: Peržiūrėti kandidato profilį."""

	@classmethod
	def setUpTestData(cls):
		cls.employer = User.objects.create_user(username='employer', role=User.Role.EMPLOYER)
		cls.other_employer = User.objects.create_user(username='other', role=User.Role.EMPLOYER)
		cls.candidate = User.objects.create_user(
			username='candidate',
			role=User.Role.JOB_SEEKER,
			first_name='Jonas',
			last_name='Jonaitis',
		)

		company = Company.objects.create(owner=cls.employer, name='UAB Pavyzdys', description='')
		posting = JobPosting.objects.create(
			company=company,
			industry=Industry.objects.create(name='IT'),
			title='Frontend programuotojas',
			description='',
			job_type=JobPosting.JobType.FULL_TIME,
		)

		cv = CV.objects.create(user=cls.candidate, file_key='cvs/cv.pdf')
		CVSkill.objects.create(cv=cv, name='Vue.js')
		cls.application = Application.objects.create(
			job_posting=posting, applicant=cls.candidate, cv=cv, match_score=80
		)
		cls.url = reverse('application-detail', args=[cls.application.pk])

	def test_tc_us32_01_employer_can_open_candidate_profile(self):
		self.client.force_authenticate(self.employer)

		response = self.client.get(self.url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_tc_us32_03_profile_has_name_and_competences(self):
		self.client.force_authenticate(self.employer)

		response = self.client.get(self.url)

		self.assertEqual(response.data['applicant']['first_name'], 'Jonas')
		self.assertEqual(response.data['applicant']['last_name'], 'Jonaitis')
		self.assertEqual(response.data['cv']['skills'][0]['name'], 'Vue.js')

	def test_tc_us32_05_profile_has_match_score(self):
		self.client.force_authenticate(self.employer)

		response = self.client.get(self.url)

		self.assertEqual(response.data['match_score'], 80)

	def test_tc_us32_06_guest_cannot_view_candidate_profile(self):
		response = self.client.get(self.url)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
		self.assertNotIn('applicant', response.data)

	def test_tc_us32_06_employer_of_another_company_cannot_view_candidate_profile(self):
		self.client.force_authenticate(self.other_employer)

		response = self.client.get(self.url)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
