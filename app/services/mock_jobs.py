"""Read and validate local demo jobs for development and tests."""

import json
from pathlib import Path

from pydantic import TypeAdapter, ValidationError

from app.schemas.job import JobRead

MOCK_JOBS_PATH = Path(__file__).resolve().parents[1] / "data" / "mock_jobs.json"


class MockJobDataError(RuntimeError):
    """Raised when bundled mock job data cannot be read or validated."""


def load_mock_jobs(path: Path = MOCK_JOBS_PATH) -> list[JobRead]:
    """Load demo jobs through the same schema future providers will use."""

    try:
        raw_jobs = json.loads(path.read_text(encoding="utf-8"))
        return TypeAdapter(list[JobRead]).validate_python(raw_jobs)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        raise MockJobDataError(f"Unable to load mock jobs from {path}") from exc

