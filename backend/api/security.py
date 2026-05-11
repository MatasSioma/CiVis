import hashlib
import hmac
import re

from django.conf import settings
from rest_framework import serializers


PERSONAL_CODE_PATTERN = re.compile(r'^\d{11}$')


def normalize_personal_code(value: str) -> str:
	normalized = re.sub(r'[\s-]', '', value or '')

	if not PERSONAL_CODE_PATTERN.match(normalized):
		raise serializers.ValidationError('Asmens kodas turi buti 11 skaitmenu.')

	return normalized


def make_personal_code_hash(value: str) -> str:
	personal_code = normalize_personal_code(value)
	pepper = settings.PERSONAL_CODE_PEPPER.encode('utf-8')

	return hmac.new(pepper, personal_code.encode('utf-8'), hashlib.sha256).hexdigest()
