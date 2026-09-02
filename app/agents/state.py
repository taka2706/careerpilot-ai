"""Typed LangGraph workflow state."""

from typing import TypedDict

from app.rag.base import RetrievedChunk
from app.schemas.application import ApplicationContent, SkillGapAnalysis, VerificationResult
from app.schemas.job import JobResponse
from app.schemas.planning import AgentPlan
from app.schemas.profile import ProfileResponse
from app.schemas.ranking import JobRankingResponse


class CareerPilotState(TypedDict, total=False):
    user_request: str
    profile_id: str
    plan: AgentPlan
    jobs: list[JobResponse]
    profile: ProfileResponse
    evidence: list[RetrievedChunk]
    rankings: list[JobRankingResponse]
    skill_gaps: list[SkillGapAnalysis]
    applications: list[ApplicationContent]
    verification: list[VerificationResult]
    feedback: list[str]
    retries: int
    max_retries: int
    current_step: str
    status: str
    errors: list[str]
