"""Job search and job result schemas."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class RemoteStatus(StrEnum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"


class JobSearchRequest(BaseModel):
    """Validated job preferences shared by all future providers."""

    query: str = Field(min_length=2, max_length=200)
    locations: list[str] = Field(default_factory=list, max_length=20)
    remote_only: bool = False
    beginner_friendly: bool = True
    limit: int = Field(default=20, ge=1, le=100)


class JobRead(BaseModel):
    """Provider-neutral representation of a job opportunity."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    provider: str
    external_id: str
    title: str
    company: str
    location: str
    remote_status: RemoteStatus
    description: str
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    experience_requirements: str | None = None
    education_requirements: str | None = None
    application_url: HttpUrl
    salary: str | None = None

