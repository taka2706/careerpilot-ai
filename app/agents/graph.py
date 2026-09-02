"""Explicit CareerPilot LangGraph orchestration."""

from typing import Literal

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agents.critic import CriticAgent
from app.agents.job_research import JobResearchAgent
from app.agents.planner import PlannerAgent
from app.agents.profile import ProfileAgent
from app.agents.ranking import JobRankingAgent
from app.agents.skill_gap import SkillGapAgent
from app.agents.state import CareerPilotState
from app.agents.writer import ApplicationWriterAgent


class CareerPilotGraph:
    """Build the multi-step workflow with bounded critic correction."""

    def __init__(
        self,
        planner: PlannerAgent,
        research: JobResearchAgent,
        profile: ProfileAgent,
        ranking: JobRankingAgent,
        skill_gap: SkillGapAgent,
        writer: ApplicationWriterAgent,
        critic: CriticAgent,
    ) -> None:
        self._planner = planner
        self._research = research
        self._profile = profile
        self._ranking = ranking
        self._skill_gap = skill_gap
        self._writer = writer
        self._critic = critic
        self.compiled = self._build()

    def _build(
        self,
    ) -> CompiledStateGraph[CareerPilotState, None, CareerPilotState, CareerPilotState]:
        graph: StateGraph[CareerPilotState, None, CareerPilotState, CareerPilotState] = StateGraph(
            CareerPilotState
        )
        graph.add_node("planner", self._plan)
        graph.add_node("job_research", self._research_jobs)
        graph.add_node("profile_rag", self._retrieve_profile)
        graph.add_node("job_ranking", self._rank_jobs)
        graph.add_node("skill_gap", self._analyze_gaps)
        graph.add_node("application_writer", self._write_applications)
        graph.add_node("critic", self._verify)
        graph.add_node("complete", self._complete)
        graph.add_node("failure", self._fail)
        graph.add_edge(START, "planner")
        graph.add_edge("planner", "job_research")
        graph.add_conditional_edges(
            "job_research",
            self._after_research,
            {"continue": "profile_rag", "failure": "failure"},
        )
        graph.add_edge("profile_rag", "job_ranking")
        graph.add_edge("job_ranking", "skill_gap")
        graph.add_edge("skill_gap", "application_writer")
        graph.add_edge("application_writer", "critic")
        graph.add_conditional_edges(
            "critic",
            self._after_critic,
            {"retry": "application_writer", "complete": "complete", "failure": "failure"},
        )
        graph.add_edge("complete", END)
        graph.add_edge("failure", END)
        return graph.compile()

    def _plan(self, state: CareerPilotState) -> CareerPilotState:
        return {"plan": self._planner.plan(state["user_request"]), "current_step": "planner"}

    def _research_jobs(self, state: CareerPilotState) -> CareerPilotState:
        jobs = self._research.research(state["plan"].search)
        return {
            "jobs": jobs,
            "current_step": "job_research",
            "errors": [] if jobs else ["No jobs matched the requested filters."],
        }

    def _retrieve_profile(self, state: CareerPilotState) -> CareerPilotState:
        profile, evidence = self._profile.retrieve(state["profile_id"], state["user_request"])
        return {"profile": profile, "evidence": evidence, "current_step": "profile_rag"}

    def _rank_jobs(self, state: CareerPilotState) -> CareerPilotState:
        rankings = self._ranking.rank(state["profile"], state.get("jobs", []), state["plan"].search)
        return {"rankings": rankings, "current_step": "job_ranking"}

    def _top_job_pairs(self, state: CareerPilotState):  # type: ignore[no-untyped-def]
        jobs = {job.id: job for job in state.get("jobs", [])}
        return [
            (jobs[item.job_id], item)
            for item in state.get("rankings", [])[:3]
            if item.job_id in jobs
        ]

    def _analyze_gaps(self, state: CareerPilotState) -> CareerPilotState:
        gaps = [
            self._skill_gap.analyze(state["profile"], job) for job, _ in self._top_job_pairs(state)
        ]
        return {"skill_gaps": gaps, "current_step": "skill_gap"}

    def _write_applications(self, state: CareerPilotState) -> CareerPilotState:
        applications = [
            self._writer.write(state["profile"], job, state.get("feedback"))
            for job, _ in self._top_job_pairs(state)
        ]
        return {"applications": applications, "current_step": "application_writer"}

    def _verify(self, state: CareerPilotState) -> CareerPilotState:
        pairs = self._top_job_pairs(state)
        results = [
            self._critic.verify(state["profile"], job, state["plan"].search, ranking, application)
            for (job, ranking), application in zip(
                pairs, state.get("applications", []), strict=True
            )
        ]
        feedback = [feedback for result in results for feedback in result.feedback]
        retries = state.get("retries", 0) + (0 if all(result.valid for result in results) else 1)
        return {
            "verification": results,
            "feedback": feedback,
            "retries": retries,
            "current_step": "critic",
        }

    @staticmethod
    def _after_research(state: CareerPilotState) -> Literal["continue", "failure"]:
        return "continue" if state.get("jobs") else "failure"

    @staticmethod
    def _after_critic(state: CareerPilotState) -> Literal["retry", "complete", "failure"]:
        if state.get("verification") and all(item.valid for item in state["verification"]):
            return "complete"
        if not state.get("applications"):
            return "failure"
        if state.get("retries", 0) <= state.get("max_retries", 2):
            return "retry"
        return "failure"

    def _complete(self, state: CareerPilotState) -> CareerPilotState:
        del state
        return {"status": "completed", "current_step": "complete"}

    def _fail(self, state: CareerPilotState) -> CareerPilotState:
        errors = [*state.get("errors", []), "Verification failed after the retry limit."]
        return {"status": "failed", "current_step": "failure", "errors": errors}
