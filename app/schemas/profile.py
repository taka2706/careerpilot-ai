"""Profile request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.rag.base import RetrievedChunk


class ProfileCreate(BaseModel):
    """Validated input for a manually created profile."""

    name: str = Field(min_length=1, max_length=120)
    email: str | None = Field(default=None, max_length=320)


class ProfileResponse(ProfileCreate):
    """Profile returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    education: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    programming_languages: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


# Backward-compatible name retained for code written during the initial scaffold.
ProfileRead = ProfileResponse


class ProfileRetrieveRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    limit: int = Field(default=5, ge=1, le=20)


class ProfileRetrieveResponse(BaseModel):
    profile_id: str
    results: list[RetrievedChunk] = Field(default_factory=list)
