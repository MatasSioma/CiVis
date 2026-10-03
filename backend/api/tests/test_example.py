from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Industry


class ExampleUnitTest(SimpleTestCase):
	"""Placeholder: plain unit test, no database."""

	def test_example(self):
		self.assertEqual(1 + 1, 2)


class ExampleDatabaseTest(TestCase):
	"""Placeholder: runs against the test database (PostgreSQL + pgvector)."""

	def test_example(self):
		Industry.objects.create(name='IT')

		self.assertEqual(Industry.objects.count(), 1)


class ExampleAPITest(APITestCase):
	"""Placeholder: calls an endpoint through DRF's test client."""

	def test_example(self):
		response = self.client.get(reverse('auth-session'))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertFalse(response.data['authenticated'])
