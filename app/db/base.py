"""SQLAlchemy declarative base and shared model helpers."""

from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class shared by every database model."""


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(UTC)


class CreatedAtMixin:
    """Add an immutable creation timestamp to a model."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class TimestampMixin(CreatedAtMixin):
    """Add creation and update timestamps to a model."""

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
