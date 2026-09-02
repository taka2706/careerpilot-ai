"""Job ranking response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.job import JobResponse, JobSearchRequest


class JobAnalyzeRequest(BaseModel):
    profile_id: str
    preferences: JobSearchRequest = Field(default_factory=JobSearchRequest)


class RankingCalculation(BaseModel):
    overall_score: float = Field(ge=0, le=100)
    skills_score: float = Field(ge=0, le=100)
    experience_score: float = Field(ge=0, le=100)
    education_score: float = Field(ge=0, le=100)
    location_score: float = Field(ge=0, le=100)
    beginner_score: float = Field(ge=0, le=100)
    project_relevance_score: float = Field(ge=0, le=100)
    explanation: str
    missing_requirements: list[str] = Field(default_factory=list)


class RankedJobResponse(BaseModel):
    job: JobResponse
    ranking: "JobRankingResponse"


class JobRankingResponse(BaseModel):
    """Transparent deterministic scores returned for a job/profile pair."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    profile_id: str
    job_id: str
    overall_score: float = Field(ge=0, le=100)
    skills_score: float = Field(ge=0, le=100)
    experience_score: float = Field(ge=0, le=100)
    education_score: float = Field(ge=0, le=100)
    location_score: float = Field(ge=0, le=100)
    explanation: str
    missing_requirements: list[str] = Field(default_factory=list)
    created_at: datetime
