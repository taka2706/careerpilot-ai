"""Job research agent."""

from app.schemas.job import JobResponse, JobSearchRequest
from app.services.job_service import JobService


class JobResearchAgent:
    def __init__(self, jobs: JobService) -> None:
        self._jobs = jobs

    def research(self, request: JobSearchRequest) -> list[JobResponse]:
        return self._jobs.search(request)
