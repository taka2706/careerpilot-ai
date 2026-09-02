"""Profile request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProfileCreate(BaseModel):
    """Validated input for a manually created profile."""

    name: str = Field(min_length=1, max_length=120)
    email: str | None = Field(default=None, max_length=320)


class ProfileResponse(ProfileCreate):
    """Profile returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


# Backward-compatible name retained for code written during the initial scaffold.
ProfileRead = ProfileResponse
