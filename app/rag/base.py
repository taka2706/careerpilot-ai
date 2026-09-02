"""Vector-store-neutral profile retrieval contract."""

from abc import ABC, abstractmethod

from pydantic import BaseModel


class RetrievedChunk(BaseModel):
    profile_id: str
    section: str
    text: str
    score: float


class ProfileVectorStore(ABC):
    """Interface for indexing and retrieving verified profile text."""

    @abstractmethod
    def index(self, profile_id: str, chunks: list[tuple[str, str]]) -> int:
        """Replace the profile index and return the number of stored chunks."""

    @abstractmethod
    def search(self, profile_id: str, query: str, limit: int = 5) -> list[RetrievedChunk]:
        """Return the most relevant indexed chunks for one profile."""
