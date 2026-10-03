from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import CV, Application, Company, CVSkill, Industry, JobPosting, MatchScore, User


class CVDeleteAPITest(APITestCase):
	"""KAN-28: Naudotojas gali ištrinti savo CV."""

	@classmethod
	def setUpTestData(cls):
		cls.candidate = User.objects.create_user(username='candidate', role=User.Role.JOB_SEEKER)
		cls.employer = User.objects.create_user(username='employer', role=User.Role.EMPLOYER)

		company = Company.objects.create(owner=cls.employer, name='UAB Pavyzdys', description='')
		cls.posting = JobPosting.objects.create(
			company=company,
			industry=Industry.objects.create(name='IT'),
			title='Frontend programuotojas',
			description='',
			job_type=JobPosting.JobType.FULL_TIME,
		)

		cls.cv = CV.objects.create(user=cls.candidate, file_key='cvs/cv.pdf')
		CVSkill.objects.create(cv=cls.cv, name='Vue.js')
		MatchScore.objects.create(cv=cls.cv, job_posting=cls.posting, score=80)
		cls.application = Application.objects.create(
			job_posting=cls.posting, applicant=cls.candidate, cv=cls.cv, match_score=80
		)

	def delete_cv(self, user):
		self.client.force_authenticate(user)
		return self.client.delete(reverse('cv-me'))

	def test_tc_us28_03_confirmed_deletion_removes_cv_and_its_data(self):
		response = self.delete_cv(self.candidate)

		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(CV.objects.filter(pk=self.cv.pk).exists())
		self.assertFalse(CVSkill.objects.filter(cv_id=self.cv.pk).exists())
		self.assertFalse(MatchScore.objects.filter(cv_id=self.cv.pk).exists())
		self.assertFalse(Application.objects.filter(cv_id=self.cv.pk).exists())
		self.assertEqual(self.client.get(reverse('cv-me')).status_code, status.HTTP_404_NOT_FOUND)

	def test_tc_us28_04_employer_no_longer_sees_deleted_cv(self):
		detail_url = reverse('application-detail', args=[self.application.pk])
		self.client.force_authenticate(self.employer)
		self.assertEqual(self.client.get(detail_url).data['cv']['id'], str(self.cv.pk))

		self.delete_cv(self.candidate)
		self.client.force_authenticate(self.employer)

		self.assertEqual(self.client.get(detail_url).status_code, status.HTTP_404_NOT_FOUND)
		response = self.client.get(reverse('application-list'), {'job_posting': self.posting.pk})
		self.assertEqual(response.data['count'], 0)

	def test_tc_us28_06_cannot_delete_cv_that_was_not_uploaded(self):
		job_seeker = User.objects.create_user(username='no-cv', role=User.Role.JOB_SEEKER)

		response = self.delete_cv(job_seeker)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertTrue(CV.objects.filter(pk=self.cv.pk).exists())
