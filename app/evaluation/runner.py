"""Offline evaluation runner and aggregate metrics."""

from datetime import UTC, datetime
from statistics import mean
from time import perf_counter
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.agents.critic import CriticAgent
from app.agents.writer import ApplicationWriterAgent
from app.db.models.evaluation import EvaluationResult
from app.evaluation.scenarios import SCENARIOS, EvaluationScenario
from app.schemas.evaluation import EvaluationReport, EvaluationResponse
from app.schemas.profile import ProfileResponse
from app.schemas.ranking import JobRankingResponse
from app.services.ranking import DeterministicJobRanker
from app.tools.jobs.mock_provider import MockJobProvider


class EvaluationRunner:
    """Evaluate deterministic search, ranking, and claim verification without an API key."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._provider = MockJobProvider()
        self._ranker = DeterministicJobRanker()
        self._writer = ApplicationWriterAgent()
        self._critic = CriticAgent()

    def run_all(self, *, replace: bool = True) -> EvaluationReport:
        if replace:
            self._session.execute(delete(EvaluationResult))
        for scenario in SCENARIOS:
            self._session.add(self._run_scenario(scenario))
        self._session.commit()
        return self.report()

    def report(self) -> EvaluationReport:
        records = list(
            self._session.scalars(select(EvaluationResult).order_by(EvaluationResult.scenario_name))
        )
        results = [EvaluationResponse.model_validate(record) for record in records]
        if not results:
            return EvaluationReport(
                total_scenarios=0,
                task_success_rate=0,
                average_execution_time=0,
                average_tool_success_rate=0,
                average_retries=0,
                ranking_consistency=0,
                unsupported_claim_rate=0,
                estimated_tokens=0,
                estimated_cost=0,
                results=[],
            )
        return EvaluationReport(
            total_scenarios=len(results),
            task_success_rate=mean(float(item.success) for item in results),
            average_execution_time=mean(item.execution_time for item in results),
            average_tool_success_rate=mean(item.tool_success_rate for item in results),
            average_retries=mean(item.retry_count for item in results),
            ranking_consistency=mean(item.ranking_consistency for item in results),
            unsupported_claim_rate=mean(item.unsupported_claim_rate for item in results),
            estimated_tokens=sum(item.estimated_tokens for item in results),
            estimated_cost=sum(item.estimated_cost for item in results),
            results=results,
        )

    def _run_scenario(self, scenario: EvaluationScenario) -> EvaluationResult:
        started = perf_counter()
        jobs = self._provider.search_jobs(scenario.search)
        profile = ProfileResponse(
            id=str(uuid4()),
            name="Evaluation Candidate",
            skills=scenario.skills,
            tools=scenario.tools,
            programming_languages=scenario.languages,
            projects=scenario.projects,
            education=scenario.education,
            experience=scenario.experience,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        first_scores = [self._ranker.score(profile, job, scenario.search) for job in jobs]
        second_scores = [self._ranker.score(profile, job, scenario.search) for job in jobs]
        consistent = first_scores == second_scores
        unsupported = 0.0
        critic_valid = False
        if jobs:
            best_index = max(range(len(jobs)), key=lambda index: first_scores[index].overall_score)
            job = jobs[best_index]
            score = first_scores[best_index]
            ranking = JobRankingResponse(
                id=str(uuid4()),
                profile_id=profile.id,
                job_id=job.id,
                **score.model_dump(
                    include={
                        "overall_score",
                        "skills_score",
                        "experience_score",
                        "education_score",
                        "location_score",
                        "explanation",
                        "missing_requirements",
                    }
                ),
                created_at=datetime.now(UTC),
            )
            draft = self._writer.write(profile, job)
            verification = self._critic.verify(profile, job, scenario.search, ranking, draft)
            critic_valid = verification.valid
            unsupported = len(verification.issues) / max(1, len(job.required_skills))
        success = bool(jobs) and consistent and critic_valid
        return EvaluationResult(
            scenario_name=scenario.name,
            success=success,
            execution_time=round(perf_counter() - started, 6),
            retry_count=0,
            tool_success_rate=1.0 if jobs else 0.0,
            ranking_consistency=1.0 if consistent else 0.0,
            unsupported_claim_rate=unsupported,
            estimated_tokens=0,
            estimated_cost=0.0,
        )
