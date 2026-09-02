"""Application material and verification schemas."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class GapPriority(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class SkillGap(BaseModel):
    skill: str
    priority: GapPriority
    required: bool
    suggested_learning: str
    suggested_project: str


class SkillGapAnalysis(BaseModel):
    job_id: str
    existing_skills: list[str] = Field(default_factory=list)
    missing_required_skills: list[str] = Field(default_factory=list)
    missing_preferred_skills: list[str] = Field(default_factory=list)
    gaps: list[SkillGap] = Field(default_factory=list)


class ApplicationGenerateRequest(BaseModel):
    profile_id: str
    job_id: str


class ApplicationContent(BaseModel):
    resume_summary: str
    project_bullets: list[str] = Field(default_factory=list)
    cover_letter: str
    recruiter_message: str
    linkedin_message: str


class ApplicationResponse(ApplicationContent):
    model_config = ConfigDict(from_attributes=True)

    id: str
    profile_id: str
    job_id: str
    verification_status: str
    retry_count: int
    created_at: datetime


class VerificationIssue(BaseModel):
    field: str
    claim: str
    reason: str


class VerificationResult(BaseModel):
    valid: bool
    issues: list[VerificationIssue] = Field(default_factory=list)
    feedback: list[str] = Field(default_factory=list)
