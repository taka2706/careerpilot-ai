"""Profile request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProfileCreate(BaseModel):
    """Validated input for a manually created profile."""

    display_name: str = Field(min_length=1, max_length=120)
    email: str | None = Field(default=None, max_length=320)
    skills: list[str] = Field(default_factory=list, max_length=200)


class ProfileRead(ProfileCreate):
    """Profile returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime

