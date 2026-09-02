"""LangGraph workflow execution and run-status routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_job_provider
from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.schemas.run import AgentRunRequest, AgentRunResponse
from app.services.job_service import JobService
from app.services.profile_service import ProfileService
from app.services.workflow_service import WorkflowService
from app.tools.jobs.base import JobProvider

router = APIRouter(prefix="/agents", tags=["agents"])
run_router = APIRouter(prefix="/runs", tags=["agents"])


def _service(session: Session, settings: Settings, provider: JobProvider) -> WorkflowService:
    profiles = ProfileService(session, settings)
    jobs = JobService(session, provider)
    return WorkflowService(session, settings, profiles, jobs)


@router.post("/run", response_model=AgentRunResponse, status_code=status.HTTP_201_CREATED)
def run_agents(
    payload: AgentRunRequest,
    session: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    provider: Annotated[JobProvider, Depends(get_job_provider)],
) -> AgentRunResponse:
    return _service(session, settings, provider).run(payload)


@run_router.get("/{run_id}", response_model=AgentRunResponse)
def get_run(
    run_id: str,
    session: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    provider: Annotated[JobProvider, Depends(get_job_provider)],
) -> AgentRunResponse:
    try:
        return _service(session, settings, provider).get(run_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@run_router.get("", response_model=list[AgentRunResponse])
def list_runs(
    session: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    provider: Annotated[JobProvider, Depends(get_job_provider)],
    limit: int = 20,
) -> list[AgentRunResponse]:
    return _service(session, settings, provider).list_runs(limit)
