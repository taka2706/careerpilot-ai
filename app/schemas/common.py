"""Schemas shared across API endpoints."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Public service health information."""

    status: Literal["ok"]
    service: str
    version: str


class ErrorDetail(BaseModel):
    """Stable error information safe to return to API clients."""

    code: str
    message: str


class ErrorResponse(BaseModel):
    """Envelope used for structured API errors."""

    error: ErrorDetail
