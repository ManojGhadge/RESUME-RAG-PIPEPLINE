"""
Tests for pdf_service — validate, extract, clean.
No Ollama, no MySQL, no ChromaDB needed.
"""

import pytest
import io
import pymupdf

from app.core.exceptions import InvalidFileTypeError, FileTooLargeError, PDFExtractionError
from app.services.pdf_service import validate_pdf, extract_text


# --------------------------------------------------------------------------- #
#  Helpers — build minimal in-memory PDFs                                       #
# --------------------------------------------------------------------------- #

def _make_pdf_bytes(text: str = "John Doe\nSoftware Engineer\nSkills: Python, FastAPI") -> bytes:
    """Create a minimal valid PDF with a text layer using PyMuPDF."""
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), text, fontsize=12)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


# --------------------------------------------------------------------------- #
#  validate_pdf tests                                                           #
# --------------------------------------------------------------------------- #

def test_validate_pdf_accepts_valid_file():
    pdf_bytes = _make_pdf_bytes()
    # Should not raise
    validate_pdf("resume.pdf", pdf_bytes)


def test_validate_pdf_rejects_non_pdf_extension():
    pdf_bytes = _make_pdf_bytes()
    with pytest.raises(InvalidFileTypeError, match="not a PDF"):
        validate_pdf("resume.docx", pdf_bytes)


def test_validate_pdf_rejects_wrong_magic_bytes():
    fake_bytes = b"NOTPDF" + b"\x00" * 100
    with pytest.raises(InvalidFileTypeError, match="not appear to be a valid PDF"):
        validate_pdf("resume.pdf", fake_bytes)


def test_validate_pdf_rejects_oversized_file():
    large_bytes = b"%PDF" + b"\x00" * (11 * 1024 * 1024)  # 11 MB
    with pytest.raises(FileTooLargeError, match="limit"):
        validate_pdf("resume.pdf", large_bytes)


# --------------------------------------------------------------------------- #
#  extract_text tests                                                           #
# --------------------------------------------------------------------------- #

def test_extract_text_returns_cleaned_string():
    content = (
        "John Doe  |  john@example.com  |  github.com/johndoe\n\n"
        "EXPERIENCE\n"
        "Software Engineer at Acme Corp (2021 - Present)\n"
        "- Developed RESTful APIs using Python and FastAPI\n"
        "- Reduced latency by 35 percent through query optimisation\n\n"
        "SKILLS\n"
        "Python, FastAPI, Docker, PostgreSQL, Redis\n"
    )
    pdf_bytes = _make_pdf_bytes(content)
    text = extract_text(pdf_bytes, "resume.pdf")
    assert isinstance(text, str)
    assert "John Doe" in text
    assert len(text) >= 50


def test_extract_text_raises_on_empty_pdf():
    """A PDF with a page but no text should raise PDFExtractionError."""
    doc = pymupdf.open()
    doc.new_page()  # blank page, no text
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    blank_bytes = buf.getvalue()

    with pytest.raises(PDFExtractionError, match="No extractable text"):
        extract_text(blank_bytes, "blank.pdf")
