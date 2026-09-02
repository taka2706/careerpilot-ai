"""Job ranking agent."""

from app.schemas.job import JobResponse, JobSearchRequest
from app.schemas.profile import ProfileResponse
from app.schemas.ranking import JobRankingResponse
from app.services.job_service import JobService


class JobRankingAgent:
    def __init__(self, jobs: JobService) -> None:
        self._jobs = jobs

    def rank(
        self, profile: ProfileResponse, jobs: list[JobResponse], preferences: JobSearchRequest
    ) -> list[JobRankingResponse]:
        rankings = [self._jobs.analyze(profile, job, preferences) for job in jobs]
        return sorted(rankings, key=lambda item: (-item.overall_score, item.job_id))
