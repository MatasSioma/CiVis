import json

from django.conf import settings
from openai import OpenAI


def extract_skills_from_text(cv_text: str) -> list[dict]:
	client = OpenAI(api_key=settings.OPENAI_API_KEY)

	response = client.chat.completions.create(
		model='gpt-4o-mini',
		temperature=0,
		response_format={'type': 'json_object'},
		messages=[
			{
				'role': 'system',
				'content': (
					'You are an expert HR analyst. Extract skills from the CV text provided. '
					'Return a JSON object with key "skills" '
					'containing an array of objects. '
					'Each object must have these fields:\n'
					'- "name": string, the skill name in English, lowercase, concise '
					'(e.g. "python", "project management", "team leadership")\n'
					'- "type": one of "hard", "soft", or "experience"\n'
					'  - "hard" = technical skills, tools, programming languages, frameworks\n'
					'  - "soft" = interpersonal skills, communication, leadership\n'
					'  - "experience" = domain experience, industry knowledge, job roles\n'
					'- "years_of_experience": integer, estimated years '
					'of experience with this skill based on CV timeline. '
					'Use 0 if undetermined.\n\n'
					'Rules:\n'
					'- Extract at most 20 skills\n'
					'- Do not duplicate skills (merge similar ones)\n'
					'- Normalize skill names to their common form '
					'(e.g. "JS" -> "javascript", "React.js" -> "react")\n'
					'- If the CV text is empty or unreadable, return {"skills": []}'
				),
			},
			{
				'role': 'user',
				'content': f'Extract skills from this CV:\n\n{cv_text[:8000]}',
			},
		],
	)

	content = response.choices[0].message.content
	parsed = json.loads(content)
	return parsed.get('skills', [])
