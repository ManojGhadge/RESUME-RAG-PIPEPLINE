"""
Retrieval service — the bridge between a query string and relevant resume chunks.

Accepts an arbitrary query string (ready for JD-matching in V2 without changes).
Returns top-k chunks from the resume's Chroma collection.
Raises NoChunksFoundError if nothing is retrieved — callers must NOT call the LLM
with empty context.
"""

import logging
from typing import List, Dict, Any, Optional

from app.services.embedding_service import EmbeddingService
from app.services.vectorstore_service import VectorStoreService
from app.core.exceptions import NoChunksFoundError, ResumeNotFoundError
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def retrieve_chunks(
    resume_id: str,
    query: str,
    top_k: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Embed the query, search the resume's Chroma collection, return top-k chunks.

    Args:
        resume_id: The resume to search within.
        query:     Free-form query string (question, category, job description excerpt…)
        top_k:     Override default top_k from config.

    Returns:
        List of dicts: [{text: str, id: str, distance: float}]

    Raises:
        ResumeNotFoundError: If no Chroma collection exists for this resume_id.
        NoChunksFoundError:  If the query returns 0 results.
    """
    k = top_k if top_k is not None else settings.top_k

    embedder = EmbeddingService.get()
    vs = VectorStoreService.get()

    # Embed the query
    query_embedding = embedder.embed_query(query)

    # Retrieve
    try:
        chunks = vs.query(resume_id=resume_id, query_embedding=query_embedding, top_k=k)
    except ResumeNotFoundError:
        raise  # re-raise as-is — already the correct domain exception

    if not chunks:
        raise NoChunksFoundError(
            f"No relevant content found in resume '{resume_id}' for this query. "
            "Try rephrasing your question."
        )

    logger.info(f"Retrieved {len(chunks)} chunks for resume {resume_id}")
    return chunks
