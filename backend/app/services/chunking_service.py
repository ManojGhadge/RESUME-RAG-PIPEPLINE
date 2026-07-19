"""
Section-aware chunking service.

Strategy:
1. Split the resume text into sections by detecting known section headers
   (Education, Experience, Projects, Skills, etc.)
2. Within each section, split into fixed-size chunks with overlap so
   no chunk crosses a section boundary.

This keeps context coherent: a chunk about "Work Experience" won't
bleed into "Education", which would confuse retrieval.

Why hand-rolled instead of LangChain splitters:
- Transparent and explainable in an interview
- Section-awareness requires domain logic LangChain doesn't provide by default
"""

import re
from typing import List

from app.config import get_settings
from app.utils.text_utils import RESUME_SECTION_HEADERS

settings = get_settings()


def _detect_section_boundaries(text: str) -> List[int]:
    """
    Return line indices where resume sections start.
    A section header is a line that:
    - Matches a known header keyword (case-insensitive)
    - Is relatively short (< 60 chars)
    - Is either ALL CAPS, Title Case, or ends with ':'
    """
    lines = text.splitlines()
    boundary_indices = [0]  # always start a section at line 0

    # Build pattern from known headers
    header_pattern = re.compile(
        r"^(" + "|".join(re.escape(h) for h in RESUME_SECTION_HEADERS) + r")\s*:?\s*$",
        re.IGNORECASE,
    )

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or len(stripped) > 60:
            continue
        if header_pattern.match(stripped):
            if i not in boundary_indices:
                boundary_indices.append(i)

    return sorted(set(boundary_indices))


def _split_section_into_chunks(section_text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Split a single section's text into overlapping word-based chunks.
    Using words (not chars) gives more natural boundaries.
    """
    words = section_text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk = " ".join(chunk_words).strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(words):
            break
        start += chunk_size - overlap  # slide window with overlap

    return chunks


def chunk_text(text: str) -> List[str]:
    """
    Main entry point. Takes full resume text, returns a list of chunks.
    Each chunk is section-aware and suitable for embedding.
    """
    chunk_size = settings.chunk_size
    overlap = settings.chunk_overlap

    lines = text.splitlines()
    boundaries = _detect_section_boundaries(text)
    boundaries.append(len(lines))  # sentinel end

    all_chunks: List[str] = []

    for i in range(len(boundaries) - 1):
        section_lines = lines[boundaries[i]: boundaries[i + 1]]
        section_text = "\n".join(section_lines).strip()
        if not section_text:
            continue
        section_chunks = _split_section_into_chunks(section_text, chunk_size, overlap)
        all_chunks.extend(section_chunks)

    # Fallback: if no section boundaries detected, chunk the whole text directly
    if not all_chunks:
        all_chunks = _split_section_into_chunks(text, chunk_size, overlap)

    # Filter out very short chunks (less than 20 words) — usually noise
    all_chunks = [c for c in all_chunks if len(c.split()) >= 20]

    return all_chunks
