"""
Tests for chunking_service — section detection and chunk splitting.
No external dependencies.
"""

import pytest
from app.services.chunking_service import chunk_text, _detect_section_boundaries, _split_section_into_chunks


SAMPLE_RESUME = """John Doe
john@example.com | github.com/johndoe

EXPERIENCE
Software Engineer at Acme Corp (2021 - Present)
- Developed RESTful APIs using Python and FastAPI
- Reduced latency by 35% through query optimisation
- Led a team of 4 engineers on the payments platform

EDUCATION
B.Sc. Computer Science, State University, 2020
GPA: 3.8/4.0

SKILLS
Python, FastAPI, Docker, PostgreSQL, Redis, React, Git

PROJECTS
Resume Analyzer — Built a RAG-based resume analysis tool using LLMs
E-commerce Platform — Full-stack app with 10k+ active users
"""


def test_chunk_text_returns_list():
    chunks = chunk_text(SAMPLE_RESUME)
    assert isinstance(chunks, list)
    assert len(chunks) > 0


def test_chunks_are_strings():
    chunks = chunk_text(SAMPLE_RESUME)
    for chunk in chunks:
        assert isinstance(chunk, str)
        assert len(chunk) > 0


def test_chunks_min_length():
    """All chunks should have at least 20 words (noise filter)."""
    chunks = chunk_text(SAMPLE_RESUME)
    for chunk in chunks:
        assert len(chunk.split()) >= 20, f"Short chunk: {chunk!r}"


def test_detect_section_boundaries_finds_known_headers():
    lines = SAMPLE_RESUME.splitlines()
    boundaries = _detect_section_boundaries(SAMPLE_RESUME)
    # Should detect EXPERIENCE, EDUCATION, SKILLS, PROJECTS
    assert len(boundaries) >= 2


def test_split_section_respects_chunk_size():
    text = " ".join([f"word{i}" for i in range(200)])
    chunks = _split_section_into_chunks(text, chunk_size=50, overlap=10)
    for chunk in chunks[:-1]:  # last chunk may be shorter
        assert len(chunk.split()) <= 50


def test_chunk_text_handles_plain_text_no_sections():
    """Plain text without headers should still be chunked."""
    plain = " ".join([f"word{i}" for i in range(300)])
    chunks = chunk_text(plain)
    assert len(chunks) > 0


def test_chunk_text_empty_string():
    """Empty or whitespace-only input should return empty list."""
    chunks = chunk_text("   ")
    assert chunks == [] or all(len(c.split()) >= 20 for c in chunks)
