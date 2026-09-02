"""Deterministic job ranking persistence model."""

from uuid import uuid4

from sqlalchemy import JSON, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAtMixin


class JobRanking(CreatedAtMixin, Base):
    """A stored score breakdown for one profile and one job."""

    __tablename__ = "job_rankings"
    __table_args__ = (UniqueConstraint("profile_id", "job_id", name="uq_ranking_profile_job"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    profile_id: Mapped[str] = mapped_column(ForeignKey("user_profiles.id"), index=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), index=True)
    overall_score: Mapped[float] = mapped_column(Float)
    skills_score: Mapped[float] = mapped_column(Float)
    experience_score: Mapped[float] = mapped_column(Float)
    education_score: Mapped[float] = mapped_column(Float)
    location_score: Mapped[float] = mapped_column(Float)
    explanation: Mapped[str] = mapped_column(Text)
    missing_requirements: Mapped[list[str]] = mapped_column(JSON, default=list)
