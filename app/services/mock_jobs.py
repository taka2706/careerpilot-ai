"""Compatibility helper for loading local demo jobs."""

from pathlib import Path

from app.schemas.job import JobRead
from app.tools.jobs.base import JobProviderError
from app.tools.jobs.mock_provider import DEFAULT_MOCK_JOBS_PATH, MockJobProvider

MOCK_JOBS_PATH = DEFAULT_MOCK_JOBS_PATH


class MockJobDataError(RuntimeError):
    """Raised when bundled mock job data cannot be read or validated."""


def load_mock_jobs(path: Path = MOCK_JOBS_PATH) -> list[JobRead]:
    """Load demo jobs through the same schema future providers will use."""

    try:
        return MockJobProvider(path).load_jobs()
    except JobProviderError as exc:
        raise MockJobDataError(f"Unable to load mock jobs from {path}") from exc
