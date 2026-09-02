"""Profile creation, secure upload, and retrieval routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.schemas.profile import (
    ProfileCreate,
    ProfileResponse,
    ProfileRetrieveRequest,
    ProfileRetrieveResponse,
)
from app.services.profile_service import ProfileNotFoundError, ProfileService
from app.services.resume_parser import ResumeValidationError

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    payload: ProfileCreate,
    session: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ProfileResponse:
    return ProfileService(session, settings).create(payload)


@router.get("", response_model=list[ProfileResponse])
def list_profiles(
    session: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> list[ProfileResponse]:
    return ProfileService(session, settings).list_profiles()


@router.post("/upload", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def upload_profile(
    name: Annotated[str, Form(min_length=1, max_length=120)],
    resume: Annotated[UploadFile, File()],
    session: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    email: Annotated[str | None, Form(max_length=320)] = None,
) -> ProfileResponse:
    maximum_bytes = settings.max_upload_size_mb * 1024 * 1024
    content = await resume.read(maximum_bytes + 1)
    try:
        return ProfileService(session, settings).ingest_resume(
            name=name,
            email=email,
            filename=resume.filename or "resume",
            content=content,
        )
    except ResumeValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        await resume.close()


@router.get("/{profile_id}", response_model=ProfileResponse)
def get_profile(
    profile_id: str,
    session: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ProfileResponse:
    try:
        return ProfileService(session, settings).get(profile_id)
    except ProfileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{profile_id}/retrieve", response_model=ProfileRetrieveResponse)
def retrieve_profile(
    profile_id: str,
    payload: ProfileRetrieveRequest,
    session: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ProfileRetrieveResponse:
    try:
        results = ProfileService(session, settings).retrieve(
            profile_id, payload.query, payload.limit
        )
        return ProfileRetrieveResponse(profile_id=profile_id, results=results)
    except ProfileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
