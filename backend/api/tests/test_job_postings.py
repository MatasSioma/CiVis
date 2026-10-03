from unittest import expectedFailure, mock

from django.db import DatabaseError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..embeddings import EMBEDDING_DIMENSIONS
from ..models import Company, Industry, JobPosting, JobPostingSkill, SkillType, User
from ..serializers import skill_embed_text


def fake_embeddings(texts):
	"""Stands in for OpenAI: text n gets a vector filled with n."""
	return [[float(number)] * EMBEDDING_DIMENSIONS for number, _ in enumerate(texts, start=1)]


def requirement(name='Vue.js', **fields):
	return {
		'name': name,
		'type': SkillType.HARD,
		'description': 'Komponentų kūrimas su Composition API',
		'is_required': True,
		**fields,
	}


def requirements(count):
	return [requirement(f'Įgūdis {number}') for number in range(1, count + 1)]


def skill_names(posting_id):
	skills = JobPostingSkill.objects.filter(job_posting_id=posting_id).order_by('id')
	return list(skills.values_list('name', flat=True))


class JobPostingAPITestCase(APITestCase):
	"""A logged-in employer with a company; OpenAI embeddings are faked."""

	@classmethod
	def setUpTestData(cls):
		cls.employer = User.objects.create_user(username='employer', role=User.Role.EMPLOYER)
		cls.company = Company.objects.create(
			owner=cls.employer, name='UAB Pavyzdys', description=''
		)
		cls.industry = Industry.objects.create(name='IT')

	def setUp(self):
		patcher = mock.patch('api.serializers.generate_embeddings', side_effect=fake_embeddings)
		self.generate_embeddings = patcher.start()
		self.addCleanup(patcher.stop)
		self.client.force_authenticate(self.employer)

	def payload(self, **fields):
		return {
			'industry': str(self.industry.pk),
			'title': 'Frontend programuotojas',
			'description': 'Kurti ir prižiūrėti įmonės interneto aplikacijas.',
			'job_type': JobPosting.JobType.FULL_TIME,
			'skills': [requirement()],
			**fields,
		}

	def create_posting(self, **fields):
		return self.client.post(reverse('jobposting-list'), self.payload(**fields), format='json')

	def update_posting(self, posting_id, **fields):
		url = reverse('jobposting-detail', args=[posting_id])
		return self.client.put(url, self.payload(**fields), format='json')


class JobPostingRequirementsAPITest(JobPostingAPITestCase):
	"""KAN-14: Kuriant darbo skelbimą, noriu išskirti būtinus reikalavimus."""

	def test_tc_us14_01_requirement_can_be_created_and_deleted(self):
		response = self.create_posting(skills=[requirement('Vue.js')])

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		posting_id = response.data['id']
		self.assertEqual(skill_names(posting_id), ['Vue.js'])

		response = self.update_posting(posting_id, skills=[])

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(skill_names(posting_id), [])

	def test_tc_us14_02_requirement_can_be_added_below_the_limit(self):
		for count in (0, 1, 18, 19):
			with self.subTest(existing=count):
				posting_id = self.create_posting(skills=requirements(count)).data['id']

				response = self.update_posting(posting_id, skills=requirements(count + 1))

				self.assertEqual(response.status_code, status.HTTP_200_OK)
				self.assertEqual(len(skill_names(posting_id)), count + 1)

	def test_tc_us14_02_requirement_cannot_be_added_at_the_limit(self):
		posting_id = self.create_posting(skills=requirements(20)).data['id']

		response = self.update_posting(posting_id, skills=requirements(21))

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(response.data['skills'], ['Galima nurodyti daugiausiai 20 įgūdžių.'])
		self.assertEqual(len(skill_names(posting_id)), 20)

	def test_tc_us14_03_requirement_has_name_description_required_flag_and_type(self):
		self.assertEqual(SkillType.values, ['hard', 'soft', 'experience'])
		skill = requirement('Django', type=SkillType.EXPERIENCE, is_required=False)
		posting_id = self.create_posting(skills=[skill]).data['id']

		response = self.client.get(reverse('jobposting-detail', args=[posting_id]))

		self.assertEqual(response.data['skills_detail'], [skill])

	@expectedFailure  # Defect: a requirement with an empty description is saved.
	def test_tc_us14_04_requirement_without_description_is_not_saved(self):
		response = self.create_posting(skills=[requirement(description='')])

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertFalse(JobPosting.objects.exists())

	@expectedFailure  # Defect: a requirement without a type is saved as a hard skill.
	def test_tc_us14_04_requirement_without_type_is_not_saved(self):
		skill = requirement()
		del skill['type']

		response = self.create_posting(skills=[skill])

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertFalse(JobPosting.objects.exists())


class JobPostingSaveAPITest(JobPostingAPITestCase):
	"""KAN-142: Darbo skelbimas išsaugomas duomenų bazėje."""

	def test_tc_fr142_01_saved_posting_has_required_fields(self):
		response = self.create_posting(job_type=JobPosting.JobType.PART_TIME)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		posting = JobPosting.objects.get(pk=response.data['id'])
		self.assertEqual(posting.company, self.company)
		self.assertEqual(posting.industry, self.industry)
		self.assertEqual(posting.title, 'Frontend programuotojas')
		self.assertEqual(posting.description, 'Kurti ir prižiūrėti įmonės interneto aplikacijas.')
		self.assertEqual(posting.job_type, JobPosting.JobType.PART_TIME)

	def test_tc_fr142_02_posting_without_required_field_is_not_saved(self):
		for field in ('industry', 'title', 'description', 'job_type'):
			with self.subTest(field=field):
				response = self.create_posting(**{field: ''})

				self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
				self.assertIn(field, response.data)

		with self.subTest(field='company'):
			self.company.delete()

			response = self.create_posting()

			self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
			self.assertIn('company', response.data)

		self.assertFalse(JobPosting.objects.exists())

	def test_tc_fr142_03_saving_assigns_status_and_links_requirement_embeddings(self):
		skills = [requirement('Vue.js'), requirement('Komandinis darbas', type=SkillType.SOFT)]

		response = self.create_posting(skills=skills)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		posting = JobPosting.objects.get(pk=response.data['id'])
		self.assertEqual(posting.status, JobPosting.Status.OPEN)
		self.generate_embeddings.assert_called_once_with(
			[
				skill_embed_text(skill['name'], skill['type'], skill['description'])
				for skill in skills
			]
		)
		saved = list(posting.jobpostingskill_set.order_by('id'))
		self.assertEqual([skill.name for skill in saved], ['Vue.js', 'Komandinis darbas'])
		self.assertEqual([len(skill.embedding) for skill in saved], [EMBEDDING_DIMENSIONS] * 2)
		self.assertEqual([skill.embedding[0] for skill in saved], [1.0, 2.0])

		listing = self.client.get(reverse('jobposting-list'))

		self.assertEqual([item['id'] for item in listing.data['results']], [str(posting.pk)])

	def test_tc_fr142_04_failed_save_does_not_store_posting(self):
		self.client.raise_request_exception = False

		with (
			mock.patch.object(
				JobPostingSkill.objects, 'bulk_create', side_effect=DatabaseError('Forced failure')
			),
			self.assertLogs('django.request', level='ERROR'),
		):
			response = self.create_posting()

		self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
		self.assertFalse(JobPosting.objects.exists())
