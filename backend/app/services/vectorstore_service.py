"""
ChromaDB vector store service.

Key design decisions:
- One collection per resume_id (named "resume_<resume_id>")
  → strictly prevents cross-resume leakage in retrieval
- Persistent client (data survives server restarts)
- ChromaDB is only used for vector storage/retrieval — NOT for chunking or prompting
"""

import logging
from typing import List, Dict, Any, Optional

import chromadb

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class VectorStoreService:
    """Manages ChromaDB collections — one per resume."""

    _client: Optional[chromadb.PersistentClient] = None

    def __init__(self):
        if VectorStoreService._client is None:
            logger.info(f"Initialising ChromaDB at: {settings.chroma_path}")
            VectorStoreService._client = chromadb.PersistentClient(
                path=settings.chroma_path,
            )
            logger.info("ChromaDB ready.")

    @classmethod
    def get(cls) -> "VectorStoreService":
        instance = cls()
        return instance

    @property
    def client(self) -> chromadb.PersistentClient:
        return VectorStoreService._client

    def _collection_name(self, resume_id: str) -> str:
        # ChromaDB collection names must be 3–63 chars, alphanumeric + hyphens
        return f"resume-{resume_id}"

    def get_or_create_collection(self, resume_id: str):
        """Get existing collection or create a new one for this resume."""
        name = self._collection_name(resume_id)
        return self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},  # cosine similarity for MiniLM
        )

    def store_chunks(
        self,
        resume_id: str,
        chunks: List[str],
        embeddings: List[List[float]],
    ) -> int:
        """
        Store chunks + embeddings in this resume's Chroma collection.
        Returns the number of chunks stored.
        """
        collection = self.get_or_create_collection(resume_id)

        # Build IDs: chunk_0, chunk_1, …
        ids = [f"chunk_{i}" for i in range(len(chunks))]

        collection.upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
        )
        logger.info(f"Stored {len(chunks)} chunks for resume {resume_id}")
        return len(chunks)

    def query(
        self,
        resume_id: str,
        query_embedding: List[float],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the top_k most similar chunks for a given query embedding.
        Returns a list of dicts: [{text, id, distance}, ...]
        Raises ResumeNotFoundError if the collection doesn't exist.
        """
        from app.core.exceptions import ResumeNotFoundError
    
        name = self._collection_name(resume_id)
        try:
            collection = self.client.get_collection(name=name)
        except Exception as e:
            raise ResumeNotFoundError(
                f"No vector data found for resume '{resume_id}'. "
                "The resume may not have been uploaded yet."
            ) from e

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count()),
            include=["documents", "distances"],
        )

        chunks = []
        if results["documents"] and results["documents"][0]:
            for doc, dist, doc_id in zip(
                results["documents"][0],
                results["distances"][0],
                results["ids"][0],
            ):
                chunks.append({"text": doc, "id": doc_id, "distance": dist})

        return chunks

    def delete_collection(self, resume_id: str) -> None:
        """Delete a resume's collection. No-op if it doesn't exist."""
        name = self._collection_name(resume_id)
        try:
            self.client.delete_collection(name=name)
        except Exception:
            pass  # collection already gone — acceptable
