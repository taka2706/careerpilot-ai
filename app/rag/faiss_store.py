"""Local FAISS profile store with deterministic hashing embeddings."""

import hashlib
import json
import re
from pathlib import Path

import faiss
import numpy as np

from app.rag.base import ProfileVectorStore, RetrievedChunk


class FaissProfileStore(ProfileVectorStore):
    """Persist one small cosine-similarity index per profile on local disk."""

    def __init__(self, storage_path: Path, dimensions: int = 384) -> None:
        self._storage_path = storage_path
        self._dimensions = dimensions
        self._storage_path.mkdir(parents=True, exist_ok=True)

    def _safe_profile_id(self, profile_id: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9-]{1,64}", profile_id):
            raise ValueError("Invalid profile identifier for vector storage.")
        return profile_id

    def _embed(self, text: str) -> np.ndarray:
        vector = np.zeros(self._dimensions, dtype="float32")
        tokens = re.findall(r"[a-z][a-z0-9+#.-]*", text.casefold())
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self._dimensions
            vector[index] += 1.0 if digest[4] % 2 == 0 else -1.0
        norm = np.linalg.norm(vector)
        if norm:
            vector /= norm
        return vector

    def index(self, profile_id: str, chunks: list[tuple[str, str]]) -> int:
        safe_id = self._safe_profile_id(profile_id)
        usable_chunks = [(section, text.strip()) for section, text in chunks if text.strip()]
        if not usable_chunks:
            return 0

        vectors = np.vstack([self._embed(text) for _, text in usable_chunks])
        index = faiss.IndexFlatIP(self._dimensions)
        index.add(vectors)
        faiss.write_index(index, str(self._storage_path / f"{safe_id}.faiss"))

        metadata = [
            {"profile_id": safe_id, "section": section, "text": text}
            for section, text in usable_chunks
        ]
        (self._storage_path / f"{safe_id}.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return len(usable_chunks)

    def search(self, profile_id: str, query: str, limit: int = 5) -> list[RetrievedChunk]:
        safe_id = self._safe_profile_id(profile_id)
        index_path = self._storage_path / f"{safe_id}.faiss"
        metadata_path = self._storage_path / f"{safe_id}.json"
        if not index_path.exists() or not metadata_path.exists() or not query.strip():
            return []

        index = faiss.read_index(str(index_path))
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        search_limit = min(max(limit, 1), len(metadata))
        scores, positions = index.search(self._embed(query).reshape(1, -1), search_limit)
        results: list[RetrievedChunk] = []
        for score, position in zip(scores[0], positions[0], strict=True):
            if position < 0:
                continue
            item = metadata[int(position)]
            results.append(
                RetrievedChunk(
                    profile_id=item["profile_id"],
                    section=item["section"],
                    text=item["text"],
                    score=max(float(score), 0.0),
                )
            )
        return results
