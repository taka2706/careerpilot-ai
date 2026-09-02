"""Persistent orchestration service for CareerPilot's LangGraph."""

from datetime import UTC, datetime
from time import perf_counter
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.critic import CriticAgent
from app.agents.graph import CareerPilotGraph
from app.agents.job_research import JobResearchAgent
from app.agents.planner import PlannerAgent
from app.agents.profile import ProfileAgent
from app.agents.ranking import JobRankingAgent
from app.agents.skill_gap import SkillGapAgent
from app.agents.writer import ApplicationWriterAgent
from app.core.config import Settings
from app.core.llm import create_llm
from app.core.logging import get_logger
from app.db.models.agent_run import AgentRun
from app.db.models.application import ApplicationDraft
from app.db.models.error import ErrorRecord
from app.schemas.run import AgentRunRequest, AgentRunResponse
from app.services.job_service import JobService
from app.services.profile_service import ProfileService

logger = get_logger(__name__)


class WorkflowService:
    """Run the graph synchronously and persist status, output, drafts, and errors."""

    def __init__(
        self, session: Session, settings: Settings, profiles: ProfileService, jobs: JobService
    ) -> None:
        self._session = session
        self._settings = settings
        self._profiles = profiles
        self._jobs = jobs
        self._llm = create_llm(settings)
        self._graph = CareerPilotGraph(
            PlannerAgent(self._llm),
            JobResearchAgent(jobs),
            ProfileAgent(profiles),
            JobRankingAgent(jobs),
            SkillGapAgent(),
            ApplicationWriterAgent(self._llm),
            CriticAgent(),
        ).compiled

    def run(self, request: AgentRunRequest) -> AgentRunResponse:
        run = AgentRun(status="running", user_request=request.user_request, current_step="planner")
        self._session.add(run)
        self._session.commit()
        self._session.refresh(run)
        started = perf_counter()
        try:
            result = self._graph.invoke(
                {
                    "user_request": request.user_request,
                    "profile_id": request.profile_id,
                    "retries": 0,
                    "max_retries": self._settings.max_agent_retries,
                    "status": "running",
                    "errors": [],
                }
            )
            run.status = result.get("status", "failed")
            run.current_step = result.get("current_step")
            run.retries = result.get("retries", 0)
            run.completed_at = datetime.now(UTC)
            run.run_data = self._serialize_result(result, perf_counter() - started)
            if run.status == "completed":
                self._persist_applications(result)
            else:
                run.error_message = "; ".join(result.get("errors", [])) or "Workflow failed."
            self._session.commit()
            self._session.refresh(run)
            return AgentRunResponse.model_validate(run)
        except Exception as exc:
            logger.exception("Agent run %s failed: %s", run.id, type(exc).__name__)
            self._session.rollback()
            persisted_run = self._session.get(AgentRun, run.id)
            if persisted_run is None:
                raise
            persisted_run.status = "failed"
            persisted_run.current_step = "failure"
            persisted_run.completed_at = datetime.now(UTC)
            persisted_run.error_message = "The workflow encountered an unexpected error."
            self._session.add(
                ErrorRecord(
                    run_id=run.id,
                    component="workflow",
                    error_type=type(exc).__name__,
                    message="Unexpected workflow failure; inspect protected server logs.",
                )
            )
            self._session.commit()
            self._session.refresh(persisted_run)
            return AgentRunResponse.model_validate(persisted_run)

    def get(self, run_id: str) -> AgentRunResponse:
        run = self._session.get(AgentRun, run_id)
        if run is None:
            raise LookupError(f"Run {run_id} was not found.")
        return AgentRunResponse.model_validate(run)

    def list_runs(self, limit: int = 20) -> list[AgentRunResponse]:
        runs = self._session.scalars(
            select(AgentRun).order_by(AgentRun.started_at.desc()).limit(min(max(limit, 1), 100))
        )
        return [AgentRunResponse.model_validate(run) for run in runs]

    def _persist_applications(self, result: dict[str, Any]) -> None:
        rankings = result.get("rankings", [])
        for ranking, content in zip(rankings[:3], result.get("applications", []), strict=True):
            self._session.add(
                ApplicationDraft(
                    profile_id=result["profile"].id,
                    job_id=ranking.job_id,
                    **content.model_dump(),
                    verification_status="verified",
                    retry_count=result.get("retries", 0),
                )
            )

    def _serialize_result(self, result: dict[str, Any], execution_time: float) -> dict[str, Any]:
        def dump_many(key: str) -> list[dict[str, Any]]:
            return [item.model_dump(mode="json") for item in result.get(key, [])]

        return {
            "plan": result["plan"].model_dump(mode="json") if result.get("plan") else None,
            "jobs": dump_many("jobs"),
            "rankings": dump_many("rankings"),
            "skill_gaps": dump_many("skill_gaps"),
            "applications": dump_many("applications"),
            "verification": dump_many("verification"),
            "evidence": dump_many("evidence"),
            "errors": result.get("errors", []),
            "execution_time_seconds": round(execution_time, 4),
            "estimated_tokens": self._llm.total_tokens if self._llm else 0,
            "estimated_api_cost": 0.0,
        }
