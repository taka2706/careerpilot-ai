"""Application draft database model."""

from uuid import uuid4

from sqlalchemy import JSON, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAtMixin


class ApplicationDraft(CreatedAtMixin, Base):
    """Generated materials that always require user review and manual submission."""

    __tablename__ = "application_drafts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    profile_id: Mapped[str] = mapped_column(ForeignKey("user_profiles.id"), index=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), index=True)
    resume_summary: Mapped[str] = mapped_column(Text)
    project_bullets: Mapped[list[str]] = mapped_column(JSON, default=list)
    cover_letter: Mapped[str] = mapped_column(Text)
    recruiter_message: Mapped[str] = mapped_column(Text)
    linkedin_message: Mapped[str] = mapped_column(Text)
    verification_status: Mapped[str] = mapped_column(String(30), default="pending", index=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
