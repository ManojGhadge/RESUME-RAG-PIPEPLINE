"""
FastAPI exception handlers — map domain exceptions to HTTP responses.
Register these in main.py via app.add_exception_handler(...).
"""

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    PDFExtractionError,
    ResumeNotFoundError,
    NoChunksFoundError,
    LLMError,
    InvalidFileTypeError,
    FileTooLargeError,
    LLMParseError,
    JDNotFoundError,
    AuthError,
    UserAlreadyExistsError,
    UserNotVerifiedError,
    InvalidOTPError,
)


async def pdf_extraction_handler(request: Request, exc: PDFExtractionError):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc) or "PDF has no extractable text layer (possibly scanned)."},
    )


async def resume_not_found_handler(request: Request, exc: ResumeNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc) or "Resume not found."},
    )


async def no_chunks_handler(request: Request, exc: NoChunksFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc) or "No relevant content found in this resume for that query."},
    )


async def llm_error_handler(request: Request, exc: LLMError):
    return JSONResponse(
        status_code=503,
        content={"detail": str(exc) or "LLM service unavailable. Is Ollama running?"},
    )


async def invalid_file_type_handler(request: Request, exc: InvalidFileTypeError):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc) or "Only PDF files are accepted."},
    )


async def file_too_large_handler(request: Request, exc: FileTooLargeError):
    return JSONResponse(
        status_code=413,
        content={"detail": str(exc) or "File exceeds the 10MB limit."},
    )


async def llm_parse_error_handler(request: Request, exc: LLMParseError):
    return JSONResponse(
        status_code=502,
        content={"detail": str(exc) or "LLM returned malformed JSON. Please retry."},
    )


async def jd_not_found_handler(request: Request, exc: JDNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc) or "Job description not found."},
    )


async def auth_error_handler(request: Request, exc: AuthError):
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc) or "Invalid credentials."},
    )


async def user_exists_handler(request: Request, exc: UserAlreadyExistsError):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc) or "An account with this email already exists."},
    )


async def user_not_verified_handler(request: Request, exc: UserNotVerifiedError):
    return JSONResponse(
        status_code=403,
        content={"detail": str(exc) or "Email not verified. Check your inbox for the OTP."},
    )


async def invalid_otp_handler(request: Request, exc: InvalidOTPError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc) or "OTP is invalid, expired, or already used."},
    )
