"""Evaluation report schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    scenario_name: str
    success: bool
    execution_time: float
    retry_count: int
    tool_success_rate: float
    ranking_consistency: float
    unsupported_claim_rate: float
    estimated_tokens: int
    estimated_cost: float
    created_at: datetime


class EvaluationReport(BaseModel):
    total_scenarios: int
    task_success_rate: float = Field(ge=0, le=1)
    average_execution_time: float = Field(ge=0)
    average_tool_success_rate: float = Field(ge=0, le=1)
    average_retries: float = Field(ge=0)
    ranking_consistency: float = Field(ge=0, le=1)
    unsupported_claim_rate: float = Field(ge=0, le=1)
    estimated_tokens: int = Field(ge=0)
    estimated_cost: float = Field(ge=0)
    results: list[EvaluationResponse] = Field(default_factory=list)
