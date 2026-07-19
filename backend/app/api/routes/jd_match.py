"""
JD Matching routes (requires auth):
  POST /api/resumes/{id}/jd-match
  GET  /api/resumes/{id}/matches
"""
import uuid
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.db import get_db, Resume, JobDescription, Match, User, _utcnow
from app.models.schemas import (
    JDMatchRequest, JDMatchResponse, MatchHistoryItem, MatchHistoryResponse,
)
from app.services.retrieval_service import retrieve_chunks
from app.services.llm.provider import llm as _llm
from app.prompts.jd_match_prompt import build_jd_match_prompt
from app.utils.text_utils import clean_text, parse_llm_json
from app.core.exceptions import ResumeNotFoundError
from app.core.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/resumes/{resume_id}/jd-match", response_model=JDMatchResponse,
             summary="Match a resume against a job description", status_code=201)
def match_jd(
    resume_id: str,
    body: JDMatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.user_id == current_user.id
    ).first()
    if resume is None:
        raise ResumeNotFoundError(f"Resume '{resume_id}' not found.")

    jd_clean = clean_text(body.jd_text)
    chunks = retrieve_chunks(resume_id=resume_id, query=jd_clean, top_k=6)
    chunk_texts = [c["text"] for c in chunks]

    prompt = build_jd_match_prompt(context_chunks=chunk_texts, jd_text=jd_clean)
    raw_response = _llm.generate(prompt)
    parsed = parse_llm_json(raw_response, context="jd-match")

    pct = max(0, min(100, int(parsed.get("match_percentage", 0))))
    matching = [str(s) for s in (parsed.get("matching_skills") or []) if s]
    missing = [str(s) for s in (parsed.get("missing_skills") or []) if s]
    suggestions = [str(s) for s in (parsed.get("suggestions") or []) if s]

    now = _utcnow()
    jd_id = str(uuid.uuid4())
    db.add(JobDescription(id=jd_id, resume_id=resume_id,
                          user_id=current_user.id, jd_text=body.jd_text, created_at=now))

    match_id = str(uuid.uuid4())
    db.add(Match(id=match_id, resume_id=resume_id, user_id=current_user.id,
                 job_description_id=jd_id, match_percentage=pct,
                 matching_skills=matching, missing_skills=missing,
                 suggestions=suggestions, created_at=now))
    db.commit()

    logger.info(f"JD match saved: resume={resume_id} match_id={match_id} pct={pct}%")
    return JDMatchResponse(
        match_id=match_id, resume_id=resume_id, match_percentage=pct,
        matching_skills=matching, missing_skills=missing,
        suggestions=suggestions, created_at=now,
    )


@router.get("/resumes/{resume_id}/matches", response_model=MatchHistoryResponse,
            summary="Get JD match history for a resume")
def get_match_history(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.user_id == current_user.id
    ).first()
    if resume is None:
        raise ResumeNotFoundError(f"Resume '{resume_id}' not found.")

    rows = (
        db.query(Match, JobDescription)
        .join(JobDescription, Match.job_description_id == JobDescription.id)
        .filter(Match.resume_id == resume_id, Match.user_id == current_user.id)
        .order_by(Match.created_at.desc())
        .all()
    )

    items = [
        MatchHistoryItem(
            match_id=m.id,
            jd_label=(jd.jd_text[:60] + "...") if len(jd.jd_text) > 60 else jd.jd_text,
            match_percentage=m.match_percentage,
            created_at=m.created_at,
        )
        for m, jd in rows
    ]
    return MatchHistoryResponse(resume_id=resume_id, total=len(items), matches=items)
