"""Error record database model."""

from uuid import uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAtMixin


class ErrorRecord(CreatedAtMixin, Base):
    """A sanitized operational error associated with an optional agent run."""

    __tablename__ = "error_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    run_id: Mapped[str | None] = mapped_column(
        ForeignKey("agent_runs.id"), nullable=True, index=True
    )
    component: Mapped[str] = mapped_column(String(120), index=True)
    error_type: Mapped[str] = mapped_column(String(160))
    message: Mapped[str] = mapped_column(Text)
