"""Structured deterministic planner with an optional LLM enhancement."""

from app.core.llm import StructuredLLM
from app.core.logging import get_logger
from app.schemas.job import JobSearchRequest
from app.schemas.planning import AgentName, AgentPlan, PlanStep

logger = get_logger(__name__)


class PlannerAgent:
    """Convert a natural-language goal into typed workflow steps."""

    def __init__(self, llm: StructuredLLM | None = None) -> None:
        self._llm = llm

    def plan(self, user_request: str) -> AgentPlan:
        if self._llm:
            try:
                return self._llm.generate(
                    instructions=(
                        "Create a concise CareerPilot job-search plan. Use only the available "
                        "agent enum values. Extract search filters conservatively."
                    ),
                    input_text=user_request,
                    response_model=AgentPlan,
                )
            except Exception as exc:
                logger.warning(
                    "LLM planner unavailable; using local fallback: %s", type(exc).__name__
                )

        lowered = user_request.casefold()
        query = "AI"
        for phrase in (
            "Agentic AI",
            "Generative AI",
            "Machine Learning",
            "Data Science",
            "LLM",
            "Python AI",
        ):
            if phrase.casefold() in lowered:
                query = phrase
                break
        location = "India" if "india" in lowered else None
        search = JobSearchRequest(
            query=query,
            location=location,
            remote_only="remote" in lowered,
            beginner_friendly=any(term in lowered for term in ("beginner", "intern", "entry")),
            limit=10,
        )
        agents = [
            (AgentName.JOB_RESEARCH, "Find matching opportunities through job tools."),
            (AgentName.PROFILE_RAG, "Retrieve verified profile evidence."),
            (AgentName.JOB_RANKING, "Calculate transparent deterministic scores."),
            (AgentName.SKILL_GAP, "Identify and prioritize missing skills."),
            (AgentName.APPLICATION_WRITER, "Draft grounded application materials."),
            (AgentName.CRITIC, "Verify claims, requirements, and score explanations."),
        ]
        return AgentPlan(
            intent=user_request,
            search=search,
            steps=[
                PlanStep(order=index, agent=agent, objective=objective)
                for index, (agent, objective) in enumerate(agents, 1)
            ],
        )
