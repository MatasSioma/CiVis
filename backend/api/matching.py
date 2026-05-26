"""Match score calculation. Edit the formula here."""

from math import exp, log2

import numpy as np

# ── Rescaling: map raw cosine to meaningful 0-1 range ──────────────
SIM_FLOOR = 0.40
SIM_CEILING = 0.85
SIM_GAMMA = 1.5

# ── Skill weighting ───────────────────────────────────────────────
REQUIRED_WEIGHT = 3.0
OPTIONAL_WEIGHT = 1.0

# ── Type agreement ────────────────────────────────────────────────
TYPE_MATCH_BONUS = 1.15

# ── Required-skill miss penalty ───────────────────────────────────
REQUIRED_MISS_THRESHOLD = 0.15
REQUIRED_MISS_PENALTY = 0.12

# ── Score components ──────────────────────────────────────────────
FULFILLMENT_WEIGHT = 0.70
RELEVANCE_WEIGHT = 0.30

# ── Confidence dampening for few-skill jobs ───────────────────────
MIN_SKILLS_FULL_CONFIDENCE = 3

# ── S-curve: push good matches toward 100, bad toward 0 ──────────
SCORE_CURVE_MIDPOINT = 35
SCORE_CURVE_STEEPNESS = 0.12


def _rescaled_sim(raw: float) -> float:
	if raw <= SIM_FLOOR:
		return 0.0
	if raw >= SIM_CEILING:
		return 1.0
	return ((raw - SIM_FLOOR) / (SIM_CEILING - SIM_FLOOR)) ** SIM_GAMMA


def compute_match_score(job_posting_skills, cv_skills) -> int:
	"""Five-stage matching: rescaled similarity, fulfillment with type bonus,
	required-miss penalty, CV relevance, and confidence dampening."""
	jp = [s for s in job_posting_skills if s.embedding is not None]
	cv = [s for s in cv_skills if s.embedding is not None]

	if not jp or not cv:
		return 0

	jp_embs = np.array([s.embedding for s in jp], dtype=np.float32)
	cv_embs = np.array([s.embedding for s in cv], dtype=np.float32)

	jp_norms = np.linalg.norm(jp_embs, axis=1, keepdims=True)
	cv_norms = np.linalg.norm(cv_embs, axis=1, keepdims=True)
	jp_norms = np.where(jp_norms == 0, 1.0, jp_norms)
	cv_norms = np.where(cv_norms == 0, 1.0, cv_norms)

	raw_sims = (jp_embs / jp_norms) @ (cv_embs / cv_norms).T

	rescaled = np.clip(
		(raw_sims - SIM_FLOOR) / (SIM_CEILING - SIM_FLOOR), 0.0, 1.0
	)
	rescaled = np.power(rescaled, SIM_GAMMA)

	# ── Fulfillment (job → CV) ───────────────────────────────────
	weighted_sum = 0.0
	total_weight = 0.0
	required_misses = 0

	for i, jp_skill in enumerate(jp):
		best_idx = int(np.argmax(rescaled[i]))
		best_sim = float(rescaled[i, best_idx])

		if best_sim > 0.0 and getattr(jp_skill, 'type', None) == getattr(cv[best_idx], 'type', None):
			best_sim = min(1.0, best_sim * TYPE_MATCH_BONUS)

		weight = REQUIRED_WEIGHT if jp_skill.is_required else OPTIONAL_WEIGHT
		weighted_sum += weight * best_sim
		total_weight += weight

		if jp_skill.is_required and best_sim < REQUIRED_MISS_THRESHOLD:
			required_misses += 1

	fulfillment = weighted_sum / total_weight if total_weight > 0.0 else 0.0

	if required_misses > 0:
		fulfillment *= max(0.0, 1.0 - required_misses * REQUIRED_MISS_PENALTY)

	# ── Relevance (CV → job) ─────────────────────────────────────
	relevance = float(np.mean(np.max(rescaled, axis=0)))

	# ── Combine and dampen ───────────────────────────────────────
	combined = FULFILLMENT_WEIGHT * fulfillment + RELEVANCE_WEIGHT * relevance
	raw_score = combined * 100.0

	n_jp = len(jp)
	if n_jp < MIN_SKILLS_FULL_CONFIDENCE:
		confidence = log2(1.0 + n_jp) / log2(1.0 + MIN_SKILLS_FULL_CONFIDENCE)
		raw_score *= confidence

	if raw_score <= 0:
		return 0
	final = 100.0 / (1.0 + exp(-SCORE_CURVE_STEEPNESS * (raw_score - SCORE_CURVE_MIDPOINT)))

	return max(0, min(100, int(round(final))))


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
