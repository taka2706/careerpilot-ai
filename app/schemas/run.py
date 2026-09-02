"""Agent run request and response schemas for future workflow endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AgentRunRequest(BaseModel):
    """A validated user request to start the future agent workflow."""

    user_request: str = Field(min_length=3, max_length=2_000)
    profile_id: str | None = None


class AgentRunResponse(BaseModel):
    """Public status information for an agent run."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    current_step: str | None
    retries: int = Field(ge=0)
    started_at: datetime
    completed_at: datetime | None
    error_message: str | None
