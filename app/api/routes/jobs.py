"""Job search and deterministic analysis routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_job_provider
from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.schemas.job import JobResponse, JobSearchRequest
from app.schemas.ranking import JobAnalyzeRequest, JobRankingResponse
from app.services.job_service import JobNotFoundError, JobService
from app.services.profile_service import ProfileNotFoundError, ProfileService
from app.tools.jobs.base import JobProvider, JobProviderError

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/search", response_model=list[JobResponse])
def search_jobs(
    payload: JobSearchRequest,
    session: Annotated[Session, Depends(get_db)],
    provider: Annotated[JobProvider, Depends(get_job_provider)],
) -> list[JobResponse]:
    try:
        return JobService(session, provider).search(payload)
    except JobProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/rankings/{profile_id}", response_model=list[JobRankingResponse])
def list_rankings(
    profile_id: str,
    session: Annotated[Session, Depends(get_db)],
    provider: Annotated[JobProvider, Depends(get_job_provider)],
) -> list[JobRankingResponse]:
    return JobService(session, provider).list_rankings(profile_id)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: str,
    session: Annotated[Session, Depends(get_db)],
    provider: Annotated[JobProvider, Depends(get_job_provider)],
) -> JobResponse:
    try:
        return JobService(session, provider).get(job_id)
    except JobNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{job_id}/analyze", response_model=JobRankingResponse)
def analyze_job(
    job_id: str,
    payload: JobAnalyzeRequest,
    session: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    provider: Annotated[JobProvider, Depends(get_job_provider)],
) -> JobRankingResponse:
    jobs = JobService(session, provider)
    try:
        profile = ProfileService(session, settings).get(payload.profile_id)
        job = jobs.get(job_id)
        return jobs.analyze(profile, job, payload.preferences)
    except (JobNotFoundError, ProfileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
