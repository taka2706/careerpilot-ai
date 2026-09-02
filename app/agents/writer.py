"""Grounded application writer agent."""

from app.core.llm import StructuredLLM
from app.core.logging import get_logger
from app.schemas.application import ApplicationContent
from app.schemas.job import JobResponse
from app.schemas.profile import ProfileResponse
from app.services.ranking import normalize_term

logger = get_logger(__name__)


class ApplicationWriterAgent:
    """Generate materials using only facts present in the verified profile."""

    def __init__(self, llm: StructuredLLM | None = None) -> None:
        self._llm = llm

    def write(
        self,
        profile: ProfileResponse,
        job: JobResponse,
        feedback: list[str] | None = None,
    ) -> ApplicationContent:
        if self._llm:
            try:
                return self._llm.generate(
                    instructions=(
                        "Write concise application materials. Every experience, project, tool, "
                        "education, certification, and skill claim must appear verbatim or be "
                        "directly supported by the supplied profile. Never imply missing job "
                        "skills are owned."
                    ),
                    input_text=(
                        f"PROFILE:\n{profile.model_dump_json()}\nJOB:\n{job.model_dump_json()}\n"
                        f"CORRECTION FEEDBACK:\n{feedback or []}"
                    ),
                    response_model=ApplicationContent,
                )
            except Exception as exc:
                logger.warning(
                    "LLM writer unavailable; using local fallback: %s", type(exc).__name__
                )

        owned = {
            normalize_term(skill): skill
            for skill in [*profile.skills, *profile.tools, *profile.programming_languages]
        }
        matched = [
            owned[normalize_term(skill)]
            for skill in [*job.required_skills, *job.preferred_skills]
            if normalize_term(skill) in owned
        ]
        matched = list(dict.fromkeys(matched))
        skills_phrase = ", ".join(matched[:5]) or "a growing technical foundation"
        project = profile.projects[0] if profile.projects else None
        summary = f"{profile.name} is an early-career candidate with {skills_phrase}."
        if project:
            summary += f" Their verified project background includes: {project}."

        bullets = [f"Project evidence: {item}" for item in profile.projects[:3]]
        evidence_sentence = (
            f"My profile includes {skills_phrase} and the project “{project}”."
            if project
            else f"My verified profile includes {skills_phrase}."
        )
        cover_letter = (
            f"Dear {job.company} hiring team,\n\n"
            f"I am applying for the {job.title} role. {evidence_sentence} "
            "I would welcome the opportunity to learn from your team and contribute within the "
            "scope of my demonstrated background.\n\nSincerely,\n"
            f"{profile.name}"
        )
        recruiter_message = (
            f"Hello, I’m {profile.name}. I’m interested in the {job.title} demo opportunity at "
            f"{job.company}. My verified background includes {skills_phrase}. "
            "May I share my application?"
        )
        linkedin_message = (
            f"Hi, I’m exploring the {job.title} role at {job.company}. I have verified experience "
            f"with {skills_phrase} and would value learning more about the team."
        )
        return ApplicationContent(
            resume_summary=summary,
            project_bullets=bullets,
            cover_letter=cover_letter,
            recruiter_message=recruiter_message,
            linkedin_message=linkedin_message,
        )
