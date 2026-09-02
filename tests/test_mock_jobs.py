"""Bundled mock job data tests."""

from pathlib import Path

import pytest

from app.schemas.job import JobSearchRequest, RemoteStatus
from app.tools.jobs import JobProviderError, MockJobProvider


def test_mock_jobs_are_valid_and_unique() -> None:
    jobs = MockJobProvider().load_jobs()
    external_ids = {job.external_id for job in jobs}

    assert len(jobs) >= 10
    assert len(external_ids) == len(jobs)
    assert all(job.required_skills for job in jobs)


def test_remote_only_filter_returns_only_remote_jobs() -> None:
    jobs = MockJobProvider().search_jobs(JobSearchRequest(remote_only=True))

    assert jobs
    assert all(job.remote_status is RemoteStatus.REMOTE for job in jobs)


def test_beginner_filter_returns_only_beginner_friendly_jobs() -> None:
    jobs = MockJobProvider().search_jobs(JobSearchRequest(beginner_friendly=True))

    assert jobs
    assert all(job.beginner_friendly for job in jobs)


def test_query_and_location_filters_are_deterministic() -> None:
    request = JobSearchRequest(query="generative AI", location="India")

    first_result = MockJobProvider().search_jobs(request)
    second_result = MockJobProvider().search_jobs(request)

    assert [job.id for job in first_result] == ["demo-job-003"]
    assert first_result == second_result


def test_malformed_data_raises_stable_provider_error(tmp_path: Path) -> None:
    malformed_file = tmp_path / "jobs.json"
    malformed_file.write_text("not-json", encoding="utf-8")

    with pytest.raises(JobProviderError, match="unavailable or malformed"):
        MockJobProvider(malformed_file).load_jobs()
