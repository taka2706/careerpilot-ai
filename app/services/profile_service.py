"""Profile persistence, resume ingestion, and local RAG indexing."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.models.profile import UserProfile
from app.rag.base import RetrievedChunk
from app.rag.faiss_store import FaissProfileStore
from app.schemas.profile import ProfileCreate, ProfileResponse
from app.services.resume_parser import extract_resume_text, parse_resume_sections


class ProfileNotFoundError(LookupError):
    """Raised when a requested profile does not exist."""


class ProfileService:
    """Coordinates profile storage and verified-profile retrieval."""

    def __init__(self, session: Session, settings: Settings) -> None:
        self._session = session
        self._settings = settings
        self._vector_store = FaissProfileStore(
            settings.rag_storage_path, settings.embedding_dimensions
        )

    def create(self, payload: ProfileCreate) -> ProfileResponse:
        profile = UserProfile(name=payload.name, email=payload.email)
        self._session.add(profile)
        self._session.commit()
        self._session.refresh(profile)
        return ProfileResponse.model_validate(profile)

    def ingest_resume(
        self, name: str, email: str | None, filename: str, content: bytes
    ) -> ProfileResponse:
        text = extract_resume_text(filename, content, self._settings.max_upload_size_mb)
        sections = parse_resume_sections(text)
        profile = UserProfile(name=name, email=email, resume_text=text, **sections)
        self._session.add(profile)
        self._session.commit()
        self._session.refresh(profile)
        self._index_profile(profile)
        return ProfileResponse.model_validate(profile)

    def get(self, profile_id: str) -> ProfileResponse:
        profile = self._session.get(UserProfile, profile_id)
        if profile is None:
            raise ProfileNotFoundError(f"Profile {profile_id} was not found.")
        return ProfileResponse.model_validate(profile)

    def retrieve(self, profile_id: str, query: str, limit: int = 5) -> list[RetrievedChunk]:
        profile = self._session.get(UserProfile, profile_id)
        if profile is None:
            raise ProfileNotFoundError(f"Profile {profile_id} was not found.")
        results = self._vector_store.search(profile_id, query, limit)
        if not results and profile.resume_text:
            self._index_profile(profile)
            results = self._vector_store.search(profile_id, query, limit)
        return results

    def list_profiles(self) -> list[ProfileResponse]:
        profiles = self._session.scalars(
            select(UserProfile).order_by(UserProfile.created_at.desc())
        )
        return [ProfileResponse.model_validate(profile) for profile in profiles]

    def _index_profile(self, profile: UserProfile) -> int:
        chunks: list[tuple[str, str]] = []
        for field in (
            "education",
            "skills",
            "projects",
            "experience",
            "certifications",
            "tools",
            "programming_languages",
        ):
            for value in getattr(profile, field):
                chunks.append((field, value))
        if profile.resume_text:
            paragraphs = [
                part.strip() for part in profile.resume_text.split("\n\n") if part.strip()
            ]
            chunks.extend(("resume", paragraph[:1_000]) for paragraph in paragraphs)
        return self._vector_store.index(profile.id, chunks)
