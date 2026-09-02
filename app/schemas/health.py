"""Health endpoint schemas."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Public service health information."""

    status: Literal["ok"]
    service: str
    version: str
    environment: str

