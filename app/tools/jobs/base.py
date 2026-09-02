"""Provider-neutral job search contract."""

from abc import ABC, abstractmethod

from app.schemas.job import JobResponse, JobSearchRequest


class JobProviderError(RuntimeError):
    """Raised when a provider cannot return valid job data."""


class JobProvider(ABC):
    """Interface implemented by demo and future external job providers."""

    @abstractmethod
    def search_jobs(self, request: JobSearchRequest) -> list[JobResponse]:
        """Return deterministic matches for validated search preferences."""

