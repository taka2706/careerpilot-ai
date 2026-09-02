"""Deterministic skill-gap agent."""

from app.schemas.application import GapPriority, SkillGap, SkillGapAnalysis
from app.schemas.job import JobResponse
from app.schemas.profile import ProfileResponse
from app.services.ranking import normalize_term


class SkillGapAgent:
    """Compare verified profile skills with job requirements."""

    def analyze(self, profile: ProfileResponse, job: JobResponse) -> SkillGapAnalysis:
        profile_skills = {
            normalize_term(skill): skill
            for skill in [*profile.skills, *profile.tools, *profile.programming_languages]
        }
        existing = [
            skill
            for skill in [*job.required_skills, *job.preferred_skills]
            if normalize_term(skill) in profile_skills
        ]
        missing_required = [
            skill for skill in job.required_skills if normalize_term(skill) not in profile_skills
        ]
        missing_preferred = [
            skill for skill in job.preferred_skills if normalize_term(skill) not in profile_skills
        ]
        gaps = [self._gap(skill, required=True) for skill in missing_required]
        gaps.extend(self._gap(skill, required=False) for skill in missing_preferred)
        return SkillGapAnalysis(
            job_id=job.id,
            existing_skills=list(dict.fromkeys(existing)),
            missing_required_skills=missing_required,
            missing_preferred_skills=missing_preferred,
            gaps=gaps,
        )

    @staticmethod
    def _gap(skill: str, *, required: bool) -> SkillGap:
        priority = GapPriority.CRITICAL if required else GapPriority.HIGH
        return SkillGap(
            skill=skill,
            priority=priority,
            required=required,
            suggested_learning=(
                f"Learn the fundamentals of {skill} and practice one focused exercise."
            ),
            suggested_project=(
                f"Build a small portfolio feature that demonstrates {skill} with tests."
            ),
        )
