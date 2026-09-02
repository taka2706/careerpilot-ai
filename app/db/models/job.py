"""Job database model."""

from uuid import uuid4

from sqlalchemy import JSON, Boolean, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAtMixin


class Job(CreatedAtMixin, Base):
    """A provider-neutral job record."""

    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("source", "external_id", name="uq_job_source_external_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    external_id: Mapped[str] = mapped_column(String(160), nullable=False)
    title: Mapped[str] = mapped_column(String(200), index=True)
    company: Mapped[str] = mapped_column(String(200), index=True)
    location: Mapped[str] = mapped_column(String(200), index=True)
    remote_status: Mapped[str] = mapped_column(String(30), index=True)
    description: Mapped[str] = mapped_column(Text)
    required_skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    preferred_skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    experience_requirement: Mapped[str | None] = mapped_column(Text, nullable=True)
    education_requirement: Mapped[str | None] = mapped_column(Text, nullable=True)
    application_url: Mapped[str] = mapped_column(String(2048))
    salary: Mapped[str | None] = mapped_column(String(200), nullable=True)
    source: Mapped[str] = mapped_column(String(80), index=True)
    beginner_friendly: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
