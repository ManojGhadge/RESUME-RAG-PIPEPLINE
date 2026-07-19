"""POST /api/resumes/{resume_id}/ats-suggestions (requires auth)"""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.db import get_db, Resume, User
from app.models.schemas import ATSSuggestionsResponse
from app.services.ats_service import get_full_text
from app.services.llm.provider import llm as _llm
from app.prompts.ats_prompt import build_ats_prompt
from app.core.dependencies import get_current_user
from app.core.exceptions import ResumeNotFoundError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/resumes/{resume_id}/ats-suggestions", response_model=ATSSuggestionsResponse,
             summary="Get ATS improvement suggestions for a resume")
def get_ats_suggestions(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify ownership
    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.user_id == current_user.id
    ).first()
    if resume is None:
        raise ResumeNotFoundError(f"Resume '{resume_id}' not found.")

    full_text = get_full_text(resume_id=resume_id, db=db)
    prompt = build_ats_prompt(full_text=full_text)
    suggestions = _llm.generate(prompt)
    logger.info(f"ATS suggestions generated for resume {resume_id}")
    return ATSSuggestionsResponse(suggestions=suggestions)
