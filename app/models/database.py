"""Initial persistent entities for CareerPilot AI."""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(UTC)


class TimestampMixin:
    """Add creation and update timestamps to a model."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )


class UserProfile(TimestampMixin, Base):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    display_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    resume_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    profile_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class Job(TimestampMixin, Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    provider: Mapped[str] = mapped_column(String(80), index=True)
    external_id: Mapped[str] = mapped_column(String(160), index=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    company: Mapped[str] = mapped_column(String(200), index=True)
    location: Mapped[str] = mapped_column(String(200))
    remote_status: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(Text)
    required_skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    preferred_skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    experience_requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    education_requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    application_url: Mapped[str] = mapped_column(String(2048))
    salary: Mapped[str | None] = mapped_column(String(200), nullable=True)


class JobRanking(TimestampMixin, Base):
    __tablename__ = "job_rankings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    profile_id: Mapped[str] = mapped_column(ForeignKey("user_profiles.id"), index=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), index=True)
    overall_score: Mapped[float] = mapped_column(Float)
    score_breakdown: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    explanation: Mapped[str] = mapped_column(Text)
    missing_requirements: Mapped[list[str]] = mapped_column(JSON, default=list)


class ApplicationDraft(TimestampMixin, Base):
    __tablename__ = "application_drafts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    profile_id: Mapped[str] = mapped_column(ForeignKey("user_profiles.id"), index=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), index=True)
    content: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    verification_status: Mapped[str] = mapped_column(String(30), default="pending")


class AgentRun(TimestampMixin, Base):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    status: Mapped[str] = mapped_column(String(30), index=True)
    user_request: Mapped[str] = mapped_column(Text)
    current_step: Mapped[str | None] = mapped_column(String(100), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    run_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class ErrorLog(TimestampMixin, Base):
    __tablename__ = "errors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    run_id: Mapped[str | None] = mapped_column(ForeignKey("agent_runs.id"), nullable=True)
    error_type: Mapped[str] = mapped_column(String(160))
    message: Mapped[str] = mapped_column(Text)
    context: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class Evaluation(TimestampMixin, Base):
    __tablename__ = "evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    scenario_name: Mapped[str] = mapped_column(String(200), index=True)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    passed: Mapped[bool] = mapped_column(default=False)
