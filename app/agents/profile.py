"""Profile retrieval agent."""

from app.rag.base import RetrievedChunk
from app.schemas.profile import ProfileResponse
from app.services.profile_service import ProfileService


class ProfileAgent:
    def __init__(self, profiles: ProfileService) -> None:
        self._profiles = profiles

    def retrieve(self, profile_id: str, query: str) -> tuple[ProfileResponse, list[RetrievedChunk]]:
        return self._profiles.get(profile_id), self._profiles.retrieve(profile_id, query)
