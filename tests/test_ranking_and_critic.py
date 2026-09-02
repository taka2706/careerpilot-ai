"""Deterministic ranking and unsupported-claim verification tests."""

from datetime import UTC, datetime

from app.agents.critic import CriticAgent
from app.agents.writer import ApplicationWriterAgent
from app.schemas.job import JobSearchRequest
from app.schemas.profile import ProfileResponse
from app.schemas.ranking import JobRankingResponse
from app.services.ranking import DeterministicJobRanker
from app.tools.jobs.mock_provider import MockJobProvider


def _profile() -> ProfileResponse:
    now = datetime.now(UTC)
    return ProfileResponse(
        id="profile-test",
        name="Test Candidate",
        skills=["Python", "Git", "REST APIs"],
        projects=["Built a Python REST API"],
        education=["Computer science student"],
        created_at=now,
        updated_at=now,
    )


def test_ranking_is_repeatable_and_reports_missing_requirements() -> None:
    job = MockJobProvider().load_jobs()[0]
    request = JobSearchRequest(remote_only=True, location="India")
    ranker = DeterministicJobRanker()

    first = ranker.score(_profile(), job, request)
    second = ranker.score(_profile(), job, request)

    assert first == second
    assert first.skills_score == 100
    assert 0 <= first.overall_score <= 100
    assert "Fixed weights" in first.explanation


def test_critic_rejects_an_invented_job_skill() -> None:
    profile = _profile()
    job = MockJobProvider().load_jobs()[0]
    preferences = JobSearchRequest()
    calculation = DeterministicJobRanker().score(profile, job, preferences)
    ranking = JobRankingResponse(
        id="ranking-test",
        profile_id=profile.id,
        job_id=job.id,
        **calculation.model_dump(
            include={
                "overall_score",
                "skills_score",
                "experience_score",
                "education_score",
                "location_score",
                "explanation",
                "missing_requirements",
            }
        ),
        created_at=datetime.now(UTC),
    )
    draft = ApplicationWriterAgent().write(profile, job)
    draft.resume_summary += " Expert in Docker."

    result = CriticAgent().verify(profile, job, preferences, ranking, draft)

    assert result.valid is False
    assert any(issue.claim == "Docker" for issue in result.issues)
