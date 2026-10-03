from datetime import datetime, timezone

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import CV, Application, Company, Industry, JobPosting, User

PUBLIC_FIELDS = {
	'id',
	'title',
	'company_name',
	'job_type',
	'workplace_type',
	'location',
	'salary_min',
	'salary_max',
	'updated_at',
}


class PublicJobPostingsAPITest(APITestCase):
	"""KAN-151: FR-04: Neprisijungusiam vartotojui rodomas darbo pozicijų sąrašas."""

	@classmethod
	def setUpTestData(cls):
		employer = User.objects.create_user(username='employer', role=User.Role.EMPLOYER)
		company = Company.objects.create(owner=employer, name='UAB Pavyzdys', description='')
		industry = Industry.objects.create(name='IT')

		def create_posting(title, status, day, job_type='full_time', **fields):
			posting = JobPosting.objects.create(
				company=company,
				industry=industry,
				title=title,
				description='',
				job_type=job_type,
				status=status,
				**fields,
			)
			JobPosting.objects.filter(pk=posting.pk).update(
				updated_at=datetime(2026, 9, day, tzinfo=timezone.utc)
			)
			return posting

		cls.frontend = create_posting('Frontend', JobPosting.Status.OPEN, 1, salary_max=3000)
		create_posting('Backend', JobPosting.Status.OPEN, 2, 'part_time', salary_max=2000)
		create_posting('Analitikas', JobPosting.Status.OPEN, 3, salary_max=4000)
		create_posting('Juodraštis', JobPosting.Status.DRAFT, 4)
		create_posting('Uždarytas', JobPosting.Status.CLOSED, 5)

	def titles(self, **filters):
		response = self.client.get(reverse('public-job-postings'), filters)
		return [posting['title'] for posting in response.data['results']]

	def test_tc_fr151_02_only_active_postings_are_listed(self):
		self.assertCountEqual(self.titles(), ['Frontend', 'Backend', 'Analitikas'])

	def test_tc_fr151_04_filter_lists_only_matching_postings(self):
		self.assertEqual(self.titles(job_type='part_time'), ['Backend'])

	def test_tc_fr151_04_filter_without_matches_lists_nothing(self):
		self.assertEqual(self.titles(job_type='internship'), [])

	def test_tc_fr151_05_newest_postings_come_first_by_default(self):
		self.assertEqual(self.titles(), ['Analitikas', 'Backend', 'Frontend'])

	def test_tc_fr151_05_postings_can_be_sorted_oldest_first(self):
		self.assertEqual(self.titles(ordering='updated_at'), ['Frontend', 'Backend', 'Analitikas'])

	def test_tc_fr151_05_postings_can_be_sorted_by_highest_salary(self):
		self.assertEqual(self.titles(ordering='-salary_max'), ['Analitikas', 'Frontend', 'Backend'])

	def test_tc_fr151_05_postings_can_be_sorted_by_lowest_salary(self):
		self.assertEqual(self.titles(ordering='salary_max'), ['Backend', 'Frontend', 'Analitikas'])

	def test_tc_fr151_07_guest_cannot_apply(self):
		response = self.client.post(reverse('application-list'), {'job_posting': self.frontend.pk})

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
		self.assertFalse(Application.objects.exists())

	def test_tc_fr151_08_response_has_only_public_fields(self):
		candidate = User.objects.create_user(username='candidate', role=User.Role.JOB_SEEKER)
		cv = CV.objects.create(user=candidate, file_key='cvs/cv.pdf')
		Application.objects.create(
			job_posting=self.frontend, applicant=candidate, cv=cv, match_score=80
		)

		response = self.client.get(reverse('public-job-postings'))

		for posting in response.data['results']:
			self.assertEqual(set(posting), PUBLIC_FIELDS)
