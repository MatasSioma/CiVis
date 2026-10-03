import time

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import User

CANDIDATE_SIGNUP = {
	'personal_code': '39001010001',
	'password': 'Slaptazodis-123!',
	'email': 'jonas@example.com',
	'first_name': 'Jonas',
	'last_name': 'Jonaitis',
	'role': User.Role.JOB_SEEKER,
	'date_of_birth': '1990-01-01',
}
EMPLOYER_SIGNUP = {
	'personal_code': '39001010001',
	'password': 'Slaptazodis-123!',
	'email': 'jonas@example.com',
	'first_name': 'Jonas',
	'last_name': 'Jonaitis',
	'role': User.Role.EMPLOYER,
	'company_name': 'UAB Pavyzdys',
}


class RoleAssignmentAPITest(APITestCase):
	"""KAN-92: Sistema turi priskirti vartotojui rolę."""

	def signup(self, data):
		return self.client.post(reverse('auth-signup'), data)

	def test_tc_fr92_01_candidate_signup_assigns_job_seeker_role(self):
		response = self.signup(CANDIDATE_SIGNUP)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		user = User.objects.get(email=CANDIDATE_SIGNUP['email'])
		self.assertEqual(user.role, 'job_seeker')

	def test_tc_fr92_01_employer_signup_assigns_employer_role(self):
		response = self.signup(EMPLOYER_SIGNUP)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		user = User.objects.get(email=EMPLOYER_SIGNUP['email'])
		self.assertEqual(user.role, 'employer')

	def test_tc_fr92_02_existing_candidate_does_not_get_second_role(self):
		self.signup(CANDIDATE_SIGNUP)

		self.signup(EMPLOYER_SIGNUP)

		users = User.objects.filter(email=CANDIDATE_SIGNUP['email'])
		self.assertEqual(users.count(), 1)
		self.assertEqual(users.get().role, 'job_seeker')

	def test_tc_fr92_03_role_is_assigned_within_one_second(self):
		start = time.perf_counter()
		self.signup(CANDIDATE_SIGNUP)
		elapsed = time.perf_counter() - start

		self.assertEqual(User.objects.get(email=CANDIDATE_SIGNUP['email']).role, 'job_seeker')
		self.assertLessEqual(elapsed, 1)

	def test_tc_fr92_04_signup_without_role_creates_no_account(self):
		data = {key: value for key, value in CANDIDATE_SIGNUP.items() if key != 'role'}

		response = self.signup(data)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('role', response.data)
		self.assertFalse(User.objects.exists())

	def test_tc_fr92_04_signup_with_unknown_role_creates_no_account(self):
		response = self.signup({**CANDIDATE_SIGNUP, 'role': 'admin'})

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('role', response.data)
		self.assertFalse(User.objects.exists())
