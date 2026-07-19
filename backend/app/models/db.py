"""
SQLAlchemy setup + ORM models.

Tables:
  users            — registered accounts (email, hashed_password, verified flag)
  otp_codes        — time-limited OTP codes for email verification + password reset
  resumes          — PDF resumes scoped to a user_id
  job_descriptions — pasted JDs linked to a resume
  matches          — JD match results
"""

from datetime import datetime, timezone
import uuid
from urllib.parse import urlparse, unquote

from sqlalchemy import (
    create_engine, Column, String, Text, DateTime,
    Integer, JSON, Boolean, ForeignKey,
)
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings

settings = get_settings()


# --------------------------------------------------------------------------- #
#  Helpers                                                                      #
# --------------------------------------------------------------------------- #

def _utcnow() -> datetime:
    """Return current UTC time. Compatible with Python 3.11 and 3.12+."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _ensure_database_exists() -> None:
    """
    Connect to MySQL without a database name and CREATE DATABASE if it
    doesn't exist. Called explicitly from init_db(), never at import time.
    """
    import pymysql

    parsed = urlparse(settings.mysql_url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 3306
    user = unquote(parsed.username or "root")
    password = unquote(parsed.password or "")
    dbname = parsed.path.lstrip("/")
    
    conn = pymysql.connect(host=host, port=port, user=user, password=password)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{dbname}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
        conn.commit()
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
#  Engine                                                                       #
# --------------------------------------------------------------------------- #

engine = create_engine(
    settings.mysql_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# --------------------------------------------------------------------------- #
#  ORM Models                                                                   #
# --------------------------------------------------------------------------- #

class User(Base):
    """Registered user account."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"


class OTPCode(Base):
    """
    Time-limited one-time password.
    purpose: 'verify_email' | 'reset_password'
    """
    __tablename__ = "otp_codes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    code = Column(String(6), nullable=False)
    purpose = Column(String(20), nullable=False)   # 'verify_email' | 'reset_password'
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<OTPCode user={self.user_id} purpose={self.purpose}>"


class Resume(Base):
    """
    Stores resume metadata + full extracted text, scoped to a user.
    full_text is used by the ATS service.
    ChromaDB stores the chunked/embedded version keyed by resume_id.
    """
    __tablename__ = "resumes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    full_text = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=_utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Resume id={self.id} user={self.user_id} filename={self.filename}>"


class JobDescription(Base):
    """Pasted JD linked to a resume."""
    __tablename__ = "job_descriptions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"),
                       nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    jd_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<JobDescription id={self.id} resume_id={self.resume_id}>"


class Match(Base):
    """JD match result."""
    __tablename__ = "matches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"),
                       nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    job_description_id = Column(String(36), nullable=False, index=True)
    match_percentage = Column(Integer, nullable=False)
    matching_skills = Column(JSON, nullable=True)
    missing_skills = Column(JSON, nullable=True)
    suggestions = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Match id={self.id} resume_id={self.resume_id} pct={self.match_percentage}>"


# --------------------------------------------------------------------------- #
#  Table creation                                                               #
# --------------------------------------------------------------------------- #

def init_db() -> None:
    """Create all tables (idempotent). Called once at startup."""
    _ensure_database_exists()
    Base.metadata.create_all(bind=engine)


# --------------------------------------------------------------------------- #
#  FastAPI dependency                                                           #
# --------------------------------------------------------------------------- #

def get_db():
    """Yield a SQLAlchemy session; always close on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
