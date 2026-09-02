"""Job persistence, deduplication, search, and ranking use cases."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.job import Job
from app.db.models.ranking import JobRanking
from app.schemas.job import JobResponse, JobSearchRequest
from app.schemas.profile import ProfileResponse
from app.schemas.ranking import JobRankingResponse, RankingCalculation
from app.services.ranking import DeterministicJobRanker
from app.tools.jobs.base import JobProvider


class JobNotFoundError(LookupError):
    """Raised when a requested job does not exist."""


class JobService:
    """Coordinates provider searches and persistent, deterministic analysis."""

    def __init__(self, session: Session, provider: JobProvider) -> None:
        self._session = session
        self._provider = provider
        self._ranker = DeterministicJobRanker()

    def search(self, request: JobSearchRequest) -> list[JobResponse]:
        provider_jobs = self._provider.search_jobs(request)
        unique_jobs = {(job.source, job.external_id): job for job in provider_jobs}
        persisted = [self._upsert(job) for job in unique_jobs.values()]
        self._session.commit()
        return [JobResponse.model_validate(job) for job in persisted]

    def get(self, job_id: str) -> JobResponse:
        job = self._session.get(Job, job_id)
        if job is None:
            raise JobNotFoundError(f"Job {job_id} was not found.")
        return JobResponse.model_validate(job)

    def analyze(
        self, profile: ProfileResponse, job: JobResponse, preferences: JobSearchRequest
    ) -> JobRankingResponse:
        calculation = self._ranker.score(profile, job, preferences)
        ranking = self._session.scalar(
            select(JobRanking).where(
                JobRanking.profile_id == profile.id, JobRanking.job_id == job.id
            )
        )
        if ranking is None:
            ranking = JobRanking(
                profile_id=profile.id, job_id=job.id, **self._ranking_values(calculation)
            )
            self._session.add(ranking)
        else:
            for key, value in self._ranking_values(calculation).items():
                setattr(ranking, key, value)
        self._session.commit()
        self._session.refresh(ranking)
        return JobRankingResponse.model_validate(ranking)

    def list_rankings(self, profile_id: str) -> list[JobRankingResponse]:
        rankings = self._session.scalars(
            select(JobRanking)
            .where(JobRanking.profile_id == profile_id)
            .order_by(JobRanking.overall_score.desc())
        )
        return [JobRankingResponse.model_validate(item) for item in rankings]

    def _upsert(self, payload: JobResponse) -> Job:
        job = self._session.scalar(
            select(Job).where(Job.source == payload.source, Job.external_id == payload.external_id)
        )
        values = payload.model_dump(exclude={"id"}, mode="json")
        if job is None:
            job = Job(**values)
            self._session.add(job)
            self._session.flush()
        else:
            for key, value in values.items():
                setattr(job, key, value)
        return job

    @staticmethod
    def _ranking_values(calculation: RankingCalculation) -> dict[str, object]:
        return {
            "overall_score": calculation.overall_score,
            "skills_score": calculation.skills_score,
            "experience_score": calculation.experience_score,
            "education_score": calculation.education_score,
            "location_score": calculation.location_score,
            "explanation": calculation.explanation,
            "missing_requirements": calculation.missing_requirements,
        }
