"""
PDF extraction service using PyMuPDF.

Validates file type and size, extracts text page by page,
cleans it, and raises clear domain exceptions for bad inputs.
"""

import logging
from pathlib import Path

import pymupdf  # PyMuPDF

from app.config import get_settings
from app.core.exceptions import (
    InvalidFileTypeError,
    FileTooLargeError,
    PDFExtractionError,
)
from app.utils.text_utils import clean_text

settings = get_settings()
logger = logging.getLogger(__name__)


def validate_pdf(filename: str, file_bytes: bytes) -> None:
    """
    Raise domain exceptions for invalid inputs before touching the file.
    - Must be a PDF (by extension AND magic bytes)
    - Must be under MAX_PDF_SIZE
    """
    # Extension check
    if not filename.lower().endswith(".pdf"):
        raise InvalidFileTypeError(f"'{filename}' is not a PDF file.")

    # Size check
    if len(file_bytes) > settings.max_pdf_size:
        size_mb = len(file_bytes) / 1_048_576
        limit_mb = settings.max_pdf_size / 1_048_576
        raise FileTooLargeError(
            f"File is {size_mb:.1f} MB; limit is {limit_mb:.0f} MB."
        )

    # Magic bytes check — PDF starts with %PDF
    if not file_bytes.startswith(b"%PDF"):
        raise InvalidFileTypeError("File does not appear to be a valid PDF.")


def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Extract and clean all text from a PDF byte stream.

    Raises PDFExtractionError if:
    - PyMuPDF cannot open the file
    - Extracted text is empty (likely a scanned/image-only PDF)

    Returns the full cleaned text as a single string.
    """
    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise PDFExtractionError(f"Could not open PDF: {e}")

    pages_text = []
    for page_num, page in enumerate(doc):
        page_text = page.get_text("text")
        if page_text:
            pages_text.append(page_text)

    doc.close()

    if not pages_text:
        raise PDFExtractionError(
            "No extractable text found. This PDF may be scanned or image-based. "
            "Please upload a text-layer PDF."
        )

    full_text = "\n\n".join(pages_text)
    cleaned = clean_text(full_text)

    if len(cleaned.strip()) < 50:
        raise PDFExtractionError(
            "Extracted text is too short to be a valid resume. "
            "The PDF may be scanned or nearly empty."
        )

    return cleaned


def save_upload(file_bytes: bytes, filename: str, resume_id: str) -> str:
    """
    Save the uploaded PDF to disk under data/uploads/<resume_id>_<filename>.
    Returns the saved file path.
    """
    upload_dir = Path(settings.upload_path)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Sanitise filename
    safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in filename)
    dest_path = upload_dir / f"{resume_id}_{safe_name}"
    dest_path.write_bytes(file_bytes)
    return str(dest_path)
