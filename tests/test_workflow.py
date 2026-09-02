"""LangGraph and evaluation integration tests."""

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.evaluation.runner import EvaluationRunner
from app.schemas.job import JobResponse, JobSearchRequest
from app.schemas.profile import ProfileCreate
from app.schemas.run import AgentRunRequest
from app.services.job_service import JobService
from app.services.profile_service import ProfileService
from app.services.workflow_service import WorkflowService
from app.tools.jobs.base import JobProvider
from app.tools.jobs.mock_provider import MockJobProvider


class EmptyJobProvider(JobProvider):
    def search_jobs(self, request: JobSearchRequest) -> list[JobResponse]:
        del request
        return []


def test_full_workflow_completes_without_an_api_key(
    db_session: Session, test_settings: Settings
) -> None:
    profiles = ProfileService(db_session, test_settings)
    profile = profiles.ingest_resume(
        "Demo Candidate",
        None,
        "resume.md",
        b"# Skills\nPython, Git, REST APIs\n# Projects\nBuilt a Python REST API",
    )
    jobs = JobService(db_session, MockJobProvider())

    run = WorkflowService(db_session, test_settings, profiles, jobs).run(
        AgentRunRequest(
            profile_id=profile.id,
            user_request="Find remote AI internships in India suitable for a beginner",
        )
    )

    assert run.status == "completed"
    assert run.retries == 0
    assert len(run.run_data["jobs"]) >= 1
    assert len(run.run_data["rankings"]) == len(run.run_data["jobs"])
    assert all(item["valid"] for item in run.run_data["verification"])


def test_evaluation_runner_executes_ten_scenarios(db_session: Session) -> None:
    report = EvaluationRunner(db_session).run_all()

    assert report.total_scenarios == 10
    assert report.task_success_rate == 1
    assert report.ranking_consistency == 1
    assert report.unsupported_claim_rate == 0


def test_workflow_enters_failure_state_when_no_jobs_match(
    db_session: Session, test_settings: Settings
) -> None:
    profiles = ProfileService(db_session, test_settings)
    profile = profiles.create(ProfileCreate(name="No Match Candidate"))
    jobs = JobService(db_session, EmptyJobProvider())

    run = WorkflowService(db_session, test_settings, profiles, jobs).run(
        AgentRunRequest(profile_id=profile.id, user_request="Find quantum archaeology roles")
    )

    assert run.status == "failed"
    assert run.current_step == "failure"
    assert "No jobs matched" in (run.error_message or "")
