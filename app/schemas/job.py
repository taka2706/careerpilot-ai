"""Job search and job result schemas."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class RemoteStatus(StrEnum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"


class JobSearchRequest(BaseModel):
    """Validated job preferences shared by all future providers."""

    query: str = Field(default="", max_length=200)
    location: str | None = Field(default=None, max_length=200)
    remote_only: bool = False
    beginner_friendly: bool = False
    limit: int = Field(default=20, ge=1, le=50)


class JobResponse(BaseModel):
    """Provider-neutral representation of a job opportunity."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    external_id: str
    title: str
    company: str
    location: str
    remote_status: RemoteStatus
    description: str
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    experience_requirement: str | None = None
    education_requirement: str | None = None
    application_url: HttpUrl
    salary: str | None = None
    source: str
    beginner_friendly: bool = False


# Backward-compatible name retained for the original Phase 1 loader.
JobRead = JobResponse
