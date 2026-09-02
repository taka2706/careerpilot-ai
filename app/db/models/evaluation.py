"""Evaluation result database model."""

from uuid import uuid4

from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAtMixin


class EvaluationResult(CreatedAtMixin, Base):
    """Quality and reliability metrics for one evaluation scenario."""

    __tablename__ = "evaluation_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    scenario_name: Mapped[str] = mapped_column(String(200), index=True)
    success: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    execution_time: Mapped[float] = mapped_column(Float)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    tool_success_rate: Mapped[float] = mapped_column(Float)
    ranking_consistency: Mapped[float] = mapped_column(Float)
    unsupported_claim_rate: Mapped[float] = mapped_column(Float)
    estimated_tokens: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)
