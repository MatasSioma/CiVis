"""Match score calculation. Edit the formula here."""

import numpy as np

REQUIRED_WEIGHT = 2.0
OPTIONAL_WEIGHT = 1.0


def _cosine(a, b) -> float:
	a_arr = np.asarray(a, dtype=np.float32)
	b_arr = np.asarray(b, dtype=np.float32)
	denom = float(np.linalg.norm(a_arr) * np.linalg.norm(b_arr))
	if denom == 0.0:
		return 0.0
	return float(np.dot(a_arr, b_arr) / denom)


def compute_match_score(job_posting_skills, cv_skills) -> int:
	"""For each JobPostingSkill, take the best cosine similarity against any
	CVSkill embedding; weight required skills more; average; rescale to 0-100."""
	jp = [s for s in job_posting_skills if s.embedding is not None]
	cv_embs = [s.embedding for s in cv_skills if s.embedding is not None]

	if not jp or not cv_embs:
		return 0

	total_weight = 0.0
	weighted_sum = 0.0

	for jp_skill in jp:
		weight = REQUIRED_WEIGHT if jp_skill.is_required else OPTIONAL_WEIGHT
		best = max(_cosine(jp_skill.embedding, ce) for ce in cv_embs)
		best = max(0.0, best)
		weighted_sum += weight * best
		total_weight += weight

	score = (weighted_sum / total_weight) * 100
	return max(0, min(100, int(round(score))))


def recompute_scores_for_posting(posting) -> None:
	"""Refresh MatchScore rows and Application.match_score for every CV tied
	to this posting. Called when posting skills change so previously shown /
	applied scores stay in sync with the new requirements."""
	from .models import Application, CV, JobPostingSkill, MatchScore

	jp_skills = list(JobPostingSkill.objects.filter(job_posting=posting))

	cv_ids = set(
		MatchScore.objects.filter(job_posting=posting).values_list('cv_id', flat=True)
	) | set(
		Application.objects.filter(job_posting=posting).values_list('cv_id', flat=True)
	)

	if not cv_ids:
		return

	cvs = list(CV.objects.filter(id__in=cv_ids).prefetch_related('cvskill_set'))

	for cv in cvs:
		score = compute_match_score(jp_skills, list(cv.cvskill_set.all()))
		MatchScore.objects.update_or_create(
			job_posting=posting,
			cv=cv,
			defaults={'score': score},
		)
		Application.objects.filter(job_posting=posting, cv=cv).update(
			match_score=score
		)
