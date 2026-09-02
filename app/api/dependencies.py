"""Reusable FastAPI dependency constructors."""

from functools import lru_cache

from app.tools.jobs.base import JobProvider
from app.tools.jobs.mock_provider import MockJobProvider


@lru_cache
def get_job_provider() -> JobProvider:
    """Return the configured job provider; Phase 1-7 demo mode uses local data."""

    return MockJobProvider()
