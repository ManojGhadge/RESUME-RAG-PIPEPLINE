"""
Embedding service — wraps sentence-transformers/all-MiniLM-L6-v2.

The model is loaded ONCE as a class-level singleton and warmed at FastAPI
startup (via the lifespan event in main.py). This means the first upload
request is just as fast as subsequent ones — no lazy-load penalty.
"""

from typing import List, Optional
import logging

from sentence_transformers import SentenceTransformer

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingService:
    """
    Singleton wrapper around SentenceTransformer.
    Call EmbeddingService.get() to get the shared instance.
    """

    _instance: Optional["EmbeddingService"] = None
    _model: Optional[SentenceTransformer] = None
   
    def __init__(self):
        if EmbeddingService._model is None:
            logger.info(f"Loading embedding model: {settings.embedding_model}")
            EmbeddingService._model = SentenceTransformer(settings.embedding_model)
            logger.info("Embedding model loaded.")

    @classmethod
    def get(cls) -> "EmbeddingService":
        """Return (or create) the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of strings. Returns a list of float vectors.
        Used when indexing chunks at upload time.
        """
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """
        Embed a single query string. Used at retrieval time.
        Identical model, identical vector space — ensures cosine similarity works.
        """
        embedding = self._model.encode([query], convert_to_numpy=True)
        return embedding[0].tolist()
