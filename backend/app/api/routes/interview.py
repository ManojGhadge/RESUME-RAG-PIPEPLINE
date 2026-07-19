"""
Interview routes (requires auth):
  POST /api/resumes/{id}/interview-questions
  POST /api/resumes/{id}/interview-questions/answer
"""

import logging
import re
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.db import get_db, Resume, User
from app.models.schemas import (
    InterviewQuestionsRequest, InterviewQuestionsResponse,
    AnswerQuestionRequest, AnswerQuestionResponse, SourceChunk,
)
from app.services.retrieval_service import retrieve_chunks
from app.services.llm.provider import llm as _llm
from app.prompts.interview_prompt import build_interview_prompt
from app.prompts.answer_prompt import build_answer_prompt
from app.core.exceptions import ResumeNotFoundError
from app.core.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

CATEGORY_QUERIES = {
    "technical":  "technical skills programming languages frameworks tools technologies",
    "hr":         "work history career background roles responsibilities achievements",
    "project":    "projects built developed created implemented outcomes results",
    "behavioral": "teamwork leadership challenges problem solving collaboration achievements",
}


def _parse_questions(raw: str) -> List[str]:
    lines = raw.strip().splitlines()
    questions = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        cleaned = re.sub(r"^\d+[\.\):\-]\s*", "", line).strip()
        if cleaned and len(cleaned) > 10:
            questions.append(cleaned)
    return questions


@router.post("/resumes/{resume_id}/interview-questions",
             response_model=InterviewQuestionsResponse,
             summary="Generate grounded interview questions")
def generate_interview_questions(
    resume_id: str,
    body: InterviewQuestionsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.user_id == current_user.id
    ).first()
    if resume is None:
        raise ResumeNotFoundError(f"Resume '{resume_id}' not found.")

    query = CATEGORY_QUERIES.get(body.category, "skills experience projects")
    chunks = retrieve_chunks(resume_id=resume_id, query=query, top_k=6)
    prompt = build_interview_prompt(category=body.category, count=body.count, chunks=chunks)
    raw_response = _llm.generate(prompt)
    questions = _parse_questions(raw_response)
    logger.info(f"Generated {len(questions)} {body.category} questions for resume {resume_id}")
    return InterviewQuestionsResponse(category=body.category, questions=questions)


@router.post("/resumes/{resume_id}/interview-questions/answer",
             response_model=AnswerQuestionResponse,
             summary="Generate a first-person answer to an interview question")
def answer_interview_question(
    resume_id: str,
    body: AnswerQuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.user_id == current_user.id
    ).first()
    if resume is None:
        raise ResumeNotFoundError(f"Resume '{resume_id}' not found.")

    chunks = retrieve_chunks(resume_id=resume_id, query=body.question)
    prompt = build_answer_prompt(question=body.question, chunks=chunks)
    answer = _llm.generate(prompt)

    sources = [SourceChunk(id=c["id"], text=c["text"], distance=c["distance"]) for c in chunks]
    return AnswerQuestionResponse(question=body.question, answer=answer, sources_used=sources)
