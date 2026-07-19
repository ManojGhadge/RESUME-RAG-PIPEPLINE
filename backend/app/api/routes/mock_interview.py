"""POST /api/resumes/{resume_id}/mock-interview/critique (requires auth)"""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.db import get_db, Resume, User
from app.models.schemas import (
    MockInterviewCritiqueRequest, MockInterviewCritiqueResponse, SourceChunk,
)
from app.services.retrieval_service import retrieve_chunks
from app.services.llm.provider import llm as _llm
from app.prompts.mock_interview_critique_prompt import build_critique_prompt
from app.utils.text_utils import parse_llm_json
from app.core.exceptions import ResumeNotFoundError
from app.core.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()
VALID_RATINGS = {"Excellent", "Strong", "Good", "Needs Work", "Weak"}


@router.post("/resumes/{resume_id}/mock-interview/critique",
             response_model=MockInterviewCritiqueResponse,
             summary="Critique a candidate's own answer to an interview question")
def critique_answer(
    resume_id: str,
    body: MockInterviewCritiqueRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.user_id == current_user.id
    ).first()
    if resume is None:
        raise ResumeNotFoundError(f"Resume '{resume_id}' not found.")

    chunks = retrieve_chunks(resume_id=resume_id, query=body.question)
    chunk_texts = [c["text"] for c in chunks]

    prompt = build_critique_prompt(
        context_chunks=chunk_texts, question=body.question, user_answer=body.user_answer
    )
    raw_response = _llm.generate(prompt)
    parsed = parse_llm_json(raw_response, context="mock-interview-critique")

    rating = str(parsed.get("rating", "Good")).strip()
    if rating not in VALID_RATINGS:
        r = rating.lower()
        rating = ("Excellent" if "excel" in r else
                  "Strong" if "strong" in r else
                  "Weak" if ("weak" in r or "poor" in r) else
                  "Needs Work" if ("needs" in r or "improve" in r) else "Good")

    strengths = [str(s) for s in (parsed.get("strengths") or []) if s]
    improvements = [str(i) for i in (parsed.get("improvements") or []) if i]
    sources = [SourceChunk(id=c["id"], text=c["text"], distance=c["distance"]) for c in chunks]

    logger.info(f"Mock critique: resume={resume_id} rating={rating}")
    return MockInterviewCritiqueResponse(
        question=body.question, rating=rating,
        strengths=strengths, improvements=improvements, sources_used=sources,
    )
