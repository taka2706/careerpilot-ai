"""User profile database model."""

from uuid import uuid4

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class UserProfile(TimestampMixin, Base):
    """A user's basic identity and optional extracted resume text."""

    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    resume_text: Mapped[str | None] = mapped_column(Text, nullable=True)
