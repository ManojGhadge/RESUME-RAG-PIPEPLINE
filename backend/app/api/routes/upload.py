"""
POST /api/resumes — Upload and index a resume PDF (requires auth).
"""

import uuid
import logging

from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from app.models.db import get_db, Resume, User
from app.models.schemas import UploadResponse
from app.services.pdf_service import validate_pdf, extract_text, save_upload
from app.services.chunking_service import chunk_text
from app.services.embedding_service import EmbeddingService
from app.services.vectorstore_service import VectorStoreService
from app.core.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/resumes",
    response_model=UploadResponse,
    summary="Upload and index a resume PDF",
    status_code=201,
)
async def upload_resume(
    file: UploadFile = File(..., description="PDF resume file (max 10MB)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_bytes = await file.read()
    filename = file.filename or "resume.pdf"
    
    validate_pdf(filename, file_bytes)
    full_text = extract_text(file_bytes, filename)
    logger.info(f"Extracted {len(full_text)} chars from '{filename}'")

    resume_id = str(uuid.uuid4())
    save_upload(file_bytes, filename, resume_id)

    chunks = chunk_text(full_text)
    logger.info(f"Created {len(chunks)} chunks for resume {resume_id}")

    embedder = EmbeddingService.get()
    embeddings = embedder.embed_texts(chunks)

    vs = VectorStoreService.get()
    vs.store_chunks(resume_id=resume_id, chunks=chunks, embeddings=embeddings)

    resume_record = Resume(
        id=resume_id,
        user_id=current_user.id,
        filename=filename,
        full_text=full_text,
    )
    db.add(resume_record)
    db.commit()
    logger.info(f"Persisted resume {resume_id} for user {current_user.id}")

    return UploadResponse(
        resume_id=resume_id,
        filename=filename,
        chunk_count=len(chunks),
    )


@router.get(
    "/resumes",
    summary="List all resumes for the current user",
)
def list_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns all resumes uploaded by the current user, newest first."""
    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.uploaded_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "filename": r.filename,
            "uploaded_at": r.uploaded_at.isoformat(),
        }
        for r in resumes
    ]
