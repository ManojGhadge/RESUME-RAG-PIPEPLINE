"""
ATS Suggestions service — reads full_text from MySQL (not vector retrieval).
"""
import logging
from sqlalchemy.orm import Session
from app.models.db import Resume
from app.core.exceptions import ResumeNotFoundError

logger = logging.getLogger(__name__)


def get_full_text(resume_id: str, db: Session) -> str:
    """
    Fetch full resume text by resume_id.
    Ownership check is done in the route before calling this.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if resume is None:
        raise ResumeNotFoundError(f"Resume '{resume_id}' not found.")
    if not resume.full_text:
        raise ResumeNotFoundError(f"Resume '{resume_id}' has no stored text.")
    return resume.full_text
