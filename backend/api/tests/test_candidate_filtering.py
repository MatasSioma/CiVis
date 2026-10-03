
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import CV, Application, Company, CVSkill, Industry, JobPosting, User

# (match score, competence) of the five candidates who applied.
CANDIDATES = [(0, 'Python'), (1, 'Vue.js'), (50, 'Vue.js'), (99, 'Python'), (100, 'Vue.js')]


class CandidateFilteringAPITest(APITestCase):
	"""KAN-25: FR-01: Sistema turi apdoroti kandidatų filtravimo kriterijus."""

	@classmethod
	def setUpTestData(cls):
		cls.employer = User.objects.create_user(username='employer', role=User.Role.EMPLOYER)
		company = Company.objects.create(owner=cls.employer, name='UAB Pavyzdys', description='')
		cls.posting = JobPosting.objects.create(
			company=company,
			industry=Industry.objects.create(name='IT'),
			title='Frontend programuotojas',
			description='',
			job_type=JobPosting.JobType.FULL_TIME,
		)

		for number, (score, skill) in enumerate(CANDIDATES):
			candidate = User.objects.create_user(
				username=f'candidate-{number}', role=User.Role.JOB_SEEKER
			)
			cv = CV.objects.create(user=candidate, file_key=f'cvs/cv-{number}.pdf')
			CVSkill.objects.create(cv=cv, name=skill)
			Application.objects.create(
				job_posting=cls.posting, applicant=candidate, cv=cv, match_score=score
			)

	def filter_candidates(self, **filters):
		self.client.force_authenticate(self.employer)
		return self.client.get(reverse('application-list'), {'job_posting': self.posting.pk, **filters})

	# Defect: the applicant list has no filter by minimum score.
	def test_tc_fr25_01_min_score_inside_range_shows_candidates_with_score_at_least_it(self):
		for min_score, expected_count in {0: 5, 1: 4, 99: 2, 100: 1}.items():
			with self.subTest(min_score=min_score):
				response = self.filter_candidates(min_score=min_score)

				self.assertEqual(response.status_code, status.HTTP_200_OK)
				self.assertEqual(response.data['count'], expected_count)

	# Defect: the applicant list has no filter by minimum score.
	def test_tc_fr25_01_min_score_outside_range_is_rejected(self):
		for min_score in (-1, 101):
			with self.subTest(min_score=min_score):
				response = self.filter_candidates(min_score=min_score)

				self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	# Defect: the applicant list has no filter by competence.
	def test_tc_fr25_02_competence_shows_only_candidates_with_it(self):
		response = self.filter_candidates(skill='Vue.js')

		self.assertEqual(response.data['count'], 3)

	# Defect: the applicant list has no filter by score or competence.
	def test_tc_fr25_03_several_filters_show_only_candidates_matching_all(self):
		response = self.filter_candidates(min_score=50, skill='Vue.js')

		self.assertEqual(response.data['count'], 2)
