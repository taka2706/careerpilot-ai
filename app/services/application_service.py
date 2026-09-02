"""Grounded application generation with bounded critic correction."""

from sqlalchemy.orm import Session

from app.agents.critic import CriticAgent
from app.agents.writer import ApplicationWriterAgent
from app.db.models.application import ApplicationDraft
from app.schemas.application import ApplicationResponse
from app.schemas.job import JobSearchRequest
from app.services.job_service import JobService
from app.services.profile_service import ProfileService


class ApplicationService:
    def __init__(
        self,
        session: Session,
        profiles: ProfileService,
        jobs: JobService,
        writer: ApplicationWriterAgent,
        critic: CriticAgent,
        max_retries: int,
    ) -> None:
        self._session = session
        self._profiles = profiles
        self._jobs = jobs
        self._writer = writer
        self._critic = critic
        self._max_retries = max_retries

    def generate(self, profile_id: str, job_id: str) -> ApplicationResponse:
        profile = self._profiles.get(profile_id)
        job = self._jobs.get(job_id)
        preferences = JobSearchRequest()
        ranking = self._jobs.analyze(profile, job, preferences)
        feedback: list[str] = []
        verification = None
        content = self._writer.write(profile, job)
        retries = 0
        while retries <= self._max_retries:
            verification = self._critic.verify(profile, job, preferences, ranking, content)
            if verification.valid:
                break
            feedback = verification.feedback
            retries += 1
            if retries <= self._max_retries:
                content = self._writer.write(profile, job, feedback)

        draft = ApplicationDraft(
            profile_id=profile_id,
            job_id=job_id,
            **content.model_dump(),
            verification_status="verified" if verification and verification.valid else "rejected",
            retry_count=retries,
        )
        self._session.add(draft)
        self._session.commit()
        self._session.refresh(draft)
        return ApplicationResponse.model_validate(draft)
