"""Application and ranking verification agent."""

from app.schemas.application import ApplicationContent, VerificationIssue, VerificationResult
from app.schemas.job import JobResponse, JobSearchRequest
from app.schemas.profile import ProfileResponse
from app.schemas.ranking import JobRankingResponse
from app.services.ranking import DeterministicJobRanker, normalize_term


class CriticAgent:
    """Reject unsupported skills and inconsistent deterministic ranking claims."""

    def __init__(self) -> None:
        self._ranker = DeterministicJobRanker()

    def verify(
        self,
        profile: ProfileResponse,
        job: JobResponse,
        preferences: JobSearchRequest,
        ranking: JobRankingResponse,
        draft: ApplicationContent,
    ) -> VerificationResult:
        issues: list[VerificationIssue] = []
        profile_evidence = normalize_term(
            " ".join(
                [
                    *profile.skills,
                    *profile.tools,
                    *profile.programming_languages,
                    *profile.projects,
                    *profile.experience,
                    *profile.education,
                    *profile.certifications,
                ]
            )
        )
        draft_text = normalize_term(" ".join(str(value) for value in draft.model_dump().values()))
        for skill in [*job.required_skills, *job.preferred_skills]:
            normalized = normalize_term(skill)
            if normalized not in profile_evidence and normalized in draft_text:
                issues.append(
                    VerificationIssue(
                        field="application",
                        claim=skill,
                        reason=(
                            "The draft mentions a job skill not present in the verified profile."
                        ),
                    )
                )

        expected = self._ranker.score(profile, job, preferences)
        score_pairs = {
            "overall_score": (ranking.overall_score, expected.overall_score),
            "skills_score": (ranking.skills_score, expected.skills_score),
            "experience_score": (ranking.experience_score, expected.experience_score),
            "education_score": (ranking.education_score, expected.education_score),
            "location_score": (ranking.location_score, expected.location_score),
        }
        for field, (actual, calculated) in score_pairs.items():
            if abs(actual - calculated) > 0.01:
                issues.append(
                    VerificationIssue(
                        field=field,
                        claim=str(actual),
                        reason=f"Deterministic scoring function calculated {calculated}.",
                    )
                )
        if set(ranking.missing_requirements) != set(expected.missing_requirements):
            issues.append(
                VerificationIssue(
                    field="missing_requirements",
                    claim=str(ranking.missing_requirements),
                    reason="Important required skills were omitted or added incorrectly.",
                )
            )
        return VerificationResult(
            valid=not issues,
            issues=issues,
            feedback=[f"Correct {issue.field}: {issue.reason}" for issue in issues],
        )
