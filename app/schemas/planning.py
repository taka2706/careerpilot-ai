"""Structured planner output."""

from enum import StrEnum

from pydantic import BaseModel, Field

from app.schemas.job import JobSearchRequest


class AgentName(StrEnum):
    JOB_RESEARCH = "job_research"
    PROFILE_RAG = "profile_rag"
    JOB_RANKING = "job_ranking"
    SKILL_GAP = "skill_gap"
    APPLICATION_WRITER = "application_writer"
    CRITIC = "critic"


class PlanStep(BaseModel):
    order: int = Field(ge=1)
    agent: AgentName
    objective: str


class AgentPlan(BaseModel):
    intent: str
    search: JobSearchRequest
    steps: list[PlanStep] = Field(min_length=1)
