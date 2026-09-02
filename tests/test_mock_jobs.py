"""Bundled mock job data tests."""

from app.services.mock_jobs import load_mock_jobs


def test_mock_jobs_are_valid_and_unique() -> None:
    jobs = load_mock_jobs()
    external_ids = {job.external_id for job in jobs}

    assert len(jobs) >= 3
    assert len(external_ids) == len(jobs)
    assert all(job.required_skills for job in jobs)

