"""
POST /api/resumes/{resume_id}/chat (requires auth)
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.db import get_db, Resume, User
from app.models.schemas import ChatRequest, ChatResponse, SourceChunk
from app.services.retrieval_service import retrieve_chunks
from app.services.llm.provider import llm as _llm
from app.prompts.chat_prompt import build_chat_prompt
from app.core.exceptions import ResumeNotFoundError
from app.core.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/resumes/{resume_id}/chat", response_model=ChatResponse,
             summary="Ask a question about the uploaded resume")
def chat_with_resume(
    resume_id: str,
    body: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Scope to current user — prevents accessing another user's resume
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id,
    ).first()
    if resume is None:
        raise ResumeNotFoundError(f"Resume '{resume_id}' not found.")

    chunks = retrieve_chunks(resume_id=resume_id, query=body.question)
    prompt = build_chat_prompt(question=body.question, chunks=chunks)
    answer = _llm.generate(prompt)

    sources = [
        SourceChunk(id=c["id"], text=c["text"], distance=c["distance"])
        for c in chunks
    ]
    return ChatResponse(answer=answer, sources_used=sources)
