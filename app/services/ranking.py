"""Transparent deterministic job scoring."""

import re
from dataclasses import dataclass

from app.schemas.job import JobResponse, JobSearchRequest, RemoteStatus
from app.schemas.profile import ProfileResponse
from app.schemas.ranking import RankingCalculation


def normalize_term(value: str) -> str:
    """Normalize skills for deterministic, case-insensitive comparison."""

    return re.sub(r"[^a-z0-9+#.]", "", value.casefold())


@dataclass(frozen=True)
class RankingWeights:
    skills: float = 0.40
    experience: float = 0.20
    education: float = 0.15
    location: float = 0.15
    beginner: float = 0.05
    project_relevance: float = 0.05


class DeterministicJobRanker:
    """Calculate job scores from explicit rules and fixed weights."""

    def __init__(self, weights: RankingWeights | None = None) -> None:
        self.weights = weights or RankingWeights()

    def score(
        self, profile: ProfileResponse, job: JobResponse, preferences: JobSearchRequest
    ) -> RankingCalculation:
        profile_skills = {
            normalize_term(skill)
            for skill in [*profile.skills, *profile.tools, *profile.programming_languages]
        }
        required = {normalize_term(skill): skill for skill in job.required_skills}
        matched_required = [label for key, label in required.items() if key in profile_skills]
        missing_required = [label for key, label in required.items() if key not in profile_skills]
        skills_score = 100.0 if not required else 100.0 * len(matched_required) / len(required)

        requirement = (job.experience_requirement or "").casefold()
        if job.beginner_friendly or "no professional experience" in requirement:
            experience_score = 100.0
        elif profile.experience:
            experience_score = 85.0
        elif "project" in requirement and profile.projects:
            experience_score = 65.0
        else:
            experience_score = 20.0

        if not job.education_requirement:
            education_score = 100.0
        elif profile.education:
            education_score = 100.0
        elif "equivalent" in job.education_requirement.casefold() and profile.projects:
            education_score = 70.0
        else:
            education_score = 25.0

        if preferences.remote_only:
            location_score = 100.0 if job.remote_status is RemoteStatus.REMOTE else 0.0
        elif preferences.location and preferences.location.casefold() in job.location.casefold():
            location_score = 100.0
        elif job.remote_status is RemoteStatus.REMOTE:
            location_score = 90.0
        else:
            location_score = 60.0

        beginner_score = 100.0 if job.beginner_friendly else 35.0
        project_text = " ".join(profile.projects).casefold()
        relevant_terms = [
            skill
            for skill in [*job.required_skills, *job.preferred_skills]
            if normalize_term(skill)
        ]
        relevant_count = sum(
            normalize_term(skill) in normalize_term(project_text) for skill in relevant_terms
        )
        project_score = (
            100.0 * relevant_count / len(relevant_terms)
            if relevant_terms and profile.projects
            else 0.0
        )

        overall = (
            skills_score * self.weights.skills
            + experience_score * self.weights.experience
            + education_score * self.weights.education
            + location_score * self.weights.location
            + beginner_score * self.weights.beginner
            + project_score * self.weights.project_relevance
        )
        explanation = (
            f"Matched {len(matched_required)}/{len(required)} required skills; "
            f"experience={experience_score:.0f}, education={education_score:.0f}, "
            f"location={location_score:.0f}, beginner={beginner_score:.0f}, "
            f"project relevance={project_score:.0f}. Fixed weights: skills 40%, "
            "experience 20%, education 15%, location 15%, beginner 5%, projects 5%."
        )
        return RankingCalculation(
            overall_score=round(overall, 2),
            skills_score=round(skills_score, 2),
            experience_score=experience_score,
            education_score=education_score,
            location_score=location_score,
            beginner_score=beginner_score,
            project_relevance_score=round(project_score, 2),
            explanation=explanation,
            missing_requirements=missing_required,
        )
