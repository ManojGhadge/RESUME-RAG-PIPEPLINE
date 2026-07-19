"""
FastAPI application entry point — v3.0 with authentication.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.db import init_db
from app.services.embedding_service import EmbeddingService
from app.services.vectorstore_service import VectorStoreService

from app.core.errors import (
    pdf_extraction_handler, resume_not_found_handler, no_chunks_handler,
    llm_error_handler, invalid_file_type_handler, file_too_large_handler,
    llm_parse_error_handler, jd_not_found_handler,
    auth_error_handler, user_exists_handler,
    user_not_verified_handler, invalid_otp_handler,
)
from app.core.exceptions import (
    PDFExtractionError, ResumeNotFoundError, NoChunksFoundError,
    LLMError, InvalidFileTypeError, FileTooLargeError,
    LLMParseError, JDNotFoundError,
    AuthError, UserAlreadyExistsError, UserNotVerifiedError, InvalidOTPError,
)
from app.api.routes import upload, chat, interview, ats, jd_match, mock_interview, auth

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=== Starting up Resume RAG backend ===")
    logger.info("Initialising database tables...")
    init_db()
    logger.info("Database ready.")
    logger.info("Warming embedding model...")
    EmbeddingService.get()
    logger.info("Embedding model ready.")
    logger.info("Initialising ChromaDB...")
    VectorStoreService.get()
    logger.info("ChromaDB ready.")
    logger.info("=== Backend ready ===")
    yield
    logger.info("=== Shutting down ===")


app = FastAPI(
    title="AI Resume Analyzer & Interview Assistant",
    description=(
        "RAG-powered resume analysis with authentication. "
        "Upload resumes, chat with them, generate interview questions, "
        "get ATS feedback, match JDs, and practice mock interviews."
    ),
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Domain exception → HTTP status mapping
app.add_exception_handler(PDFExtractionError, pdf_extraction_handler)
app.add_exception_handler(ResumeNotFoundError, resume_not_found_handler)
app.add_exception_handler(NoChunksFoundError, no_chunks_handler)
app.add_exception_handler(LLMError, llm_error_handler)
app.add_exception_handler(InvalidFileTypeError, invalid_file_type_handler)
app.add_exception_handler(FileTooLargeError, file_too_large_handler)
app.add_exception_handler(LLMParseError, llm_parse_error_handler)
app.add_exception_handler(JDNotFoundError, jd_not_found_handler)
app.add_exception_handler(AuthError, auth_error_handler)
app.add_exception_handler(UserAlreadyExistsError, user_exists_handler)
app.add_exception_handler(UserNotVerifiedError, user_not_verified_handler)
app.add_exception_handler(InvalidOTPError, invalid_otp_handler)

API_PREFIX = "/api"

app.include_router(auth.router, prefix=API_PREFIX)          # /api/auth/*
app.include_router(upload.router, prefix=API_PREFIX, tags=["Resume"])
app.include_router(chat.router, prefix=API_PREFIX, tags=["Chat"])
app.include_router(interview.router, prefix=API_PREFIX, tags=["Interview"])
app.include_router(ats.router, prefix=API_PREFIX, tags=["ATS"])
app.include_router(jd_match.router, prefix=API_PREFIX, tags=["JD Matching"])
app.include_router(mock_interview.router, prefix=API_PREFIX, tags=["Mock Interview"])


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "resume-rag-backend", "version": "3.0.0"}
