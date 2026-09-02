"""Grounded application-draft generation route."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.agents.critic import CriticAgent
from app.agents.writer import ApplicationWriterAgent
from app.api.dependencies import get_job_provider
from app.core.config import Settings, get_settings
from app.core.llm import create_llm
from app.db.session import get_db
from app.schemas.application import ApplicationGenerateRequest, ApplicationResponse
from app.services.application_service import ApplicationService
from app.services.job_service import JobNotFoundError, JobService
from app.services.profile_service import ProfileNotFoundError, ProfileService
from app.tools.jobs.base import JobProvider

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("/generate", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def generate_application(
    payload: ApplicationGenerateRequest,
    session: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    provider: Annotated[JobProvider, Depends(get_job_provider)],
) -> ApplicationResponse:
    service = ApplicationService(
        session,
        ProfileService(session, settings),
        JobService(session, provider),
        ApplicationWriterAgent(create_llm(settings)),
        CriticAgent(),
        settings.max_agent_retries,
    )
    try:
        return service.generate(payload.profile_id, payload.job_id)
    except (ProfileNotFoundError, JobNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
