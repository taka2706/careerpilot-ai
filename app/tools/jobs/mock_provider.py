"""Offline, deterministic job provider backed by fictional demo data."""

import json
from pathlib import Path

from pydantic import TypeAdapter, ValidationError

from app.core.logging import get_logger
from app.schemas.job import JobResponse, JobSearchRequest, RemoteStatus
from app.tools.jobs.base import JobProvider, JobProviderError

logger = get_logger(__name__)
DEFAULT_MOCK_JOBS_PATH = Path(__file__).resolve().parents[3] / "data" / "mock_jobs.json"


class MockJobProvider(JobProvider):
    """Search schema-validated demo jobs using ordinary Python filters."""

    def __init__(self, data_path: Path = DEFAULT_MOCK_JOBS_PATH) -> None:
        self._data_path = data_path

    def load_jobs(self) -> list[JobResponse]:
        """Load the complete demo dataset or raise a stable provider error."""

        try:
            raw_jobs = json.loads(self._data_path.read_text(encoding="utf-8"))
            return TypeAdapter(list[JobResponse]).validate_python(raw_jobs)
        except (OSError, json.JSONDecodeError, ValidationError) as exc:
            logger.error("Unable to load mock job data: %s", type(exc).__name__)
            raise JobProviderError("The demo job dataset is unavailable or malformed.") from exc

    def search_jobs(self, request: JobSearchRequest) -> list[JobResponse]:
        """Apply query, location, remote, and beginner filters in source order."""

        query_terms = request.query.casefold().split()
        location = request.location.casefold().strip() if request.location else None
        matches: list[JobResponse] = []

        for job in self.load_jobs():
            searchable_text = " ".join(
                [
                    job.title,
                    job.company,
                    job.description,
                    *job.required_skills,
                    *job.preferred_skills,
                ]
            ).casefold()

            if query_terms and not all(term in searchable_text for term in query_terms):
                continue
            if location and location not in job.location.casefold():
                continue
            if request.remote_only and job.remote_status is not RemoteStatus.REMOTE:
                continue
            if request.beginner_friendly and not job.beginner_friendly:
                continue

            matches.append(job)
            if len(matches) == request.limit:
                break

        return matches
