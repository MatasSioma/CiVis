from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import User

MEGABYTE = 1024 * 1024
DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'


class CVUploadAPITest(APITestCase):
	"""KAN-46: US-01: CV failo įkėlimas. Storage, PDF reading and OpenAI are faked."""

	@classmethod
	def setUpTestData(cls):
		cls.candidate = User.objects.create_user(username='candidate', role=User.Role.JOB_SEEKER)

	def setUp(self):
		pdf = mock.Mock(pages=[mock.Mock(extract_text=lambda: 'Python')])
		patcher = mock.patch.multiple(
			'api.views',
			upload_cv=mock.DEFAULT,
			extract_skills_from_text=mock.Mock(return_value=[]),
			PdfReader=mock.Mock(return_value=pdf),
		)
		self.upload_cv = patcher.start()['upload_cv']
		self.upload_cv.return_value = 'cvs/cv.pdf'
		self.addCleanup(patcher.stop)
		self.client.force_authenticate(self.candidate)

	def upload(self, filename, content_type, size_in_mb):
		file = SimpleUploadedFile(filename, b'x' * round(size_in_mb * MEGABYTE), content_type)
		return self.client.post(reverse('cv-upload'), {'file': file}, format='multipart')

	def test_tc_us46_02_pdf_is_accepted(self):
		response = self.upload('cv.pdf', 'application/pdf', 1)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['file_key'], 'cvs/cv.pdf')

	def test_tc_us46_02_docx_is_rejected(self):
		response = self.upload('cv.docx', DOCX, 1)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.upload_cv.assert_not_called()

	def test_tc_us46_03_file_under_the_limit_is_accepted(self):
		response = self.upload('cv.pdf', 'application/pdf', 9.9)

		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_tc_us46_03_file_at_the_limit_is_accepted(self):
		response = self.upload('cv.pdf', 'application/pdf', 10)

		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_tc_us46_03_file_over_the_limit_is_rejected(self):
		response = self.upload('cv.pdf', 'application/pdf', 10.1)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.upload_cv.assert_not_called()
