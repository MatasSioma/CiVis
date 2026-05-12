import uuid

import boto3
from django.conf import settings


def get_s3_client():
	return boto3.client(
		's3',
		endpoint_url=f'{"https" if settings.MINIO_USE_SSL else "http"}://{settings.MINIO_ENDPOINT}',
		aws_access_key_id=settings.MINIO_ACCESS_KEY,
		aws_secret_access_key=settings.MINIO_SECRET_KEY,
	)


def ensure_bucket():
	client = get_s3_client()
	try:
		client.head_bucket(Bucket=settings.MINIO_BUCKET)
	except client.exceptions.ClientError:
		client.create_bucket(Bucket=settings.MINIO_BUCKET)


def upload_cv(file_obj, original_filename: str) -> str:
	ext = original_filename.rsplit('.', 1)[-1] if '.' in original_filename else 'pdf'
	file_key = f'cvs/{uuid.uuid4()}.{ext}'

	client = get_s3_client()
	ensure_bucket()
	client.upload_fileobj(
		file_obj,
		settings.MINIO_BUCKET,
		file_key,
		ExtraArgs={'ContentType': 'application/pdf'},
	)
	return file_key
