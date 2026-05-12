from django.conf import settings
from openai import OpenAI, OpenAIError

EMBEDDING_MODEL = 'text-embedding-3-small'
EMBEDDING_DIMENSIONS = 1536
REQUEST_TIMEOUT = 10.0


class EmbeddingError(Exception):
	pass


def generate_embeddings(texts: list[str]) -> list[list[float]]:
	cleaned = [t.strip() for t in texts]

	if not cleaned:
		return []

	if any(not t for t in cleaned):
		raise EmbeddingError('Tusti embedding tekstai negalimi.')

	api_key = getattr(settings, 'OPENAI_API_KEY', '') or ''

	if not api_key:
		raise EmbeddingError('OpenAI API raktas nesukonfiguruotas.')

	try:
		client = OpenAI(api_key=api_key, timeout=REQUEST_TIMEOUT)
		response = client.embeddings.create(model=EMBEDDING_MODEL, input=cleaned)
	except OpenAIError as exc:
		raise EmbeddingError(str(exc)) from exc

	if len(response.data) != len(cleaned):
		raise EmbeddingError('OpenAI grazino netinkama embeddingu kieki.')

	return [item.embedding for item in response.data]
