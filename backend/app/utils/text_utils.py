"""
Text cleaning utilities used by pdf_service and chunking_service.
"""

import re
import json
from typing import Any


def clean_text(text: str) -> str:
    """
    Remove common PDF extraction artifacts:
    - Excessive whitespace / blank lines
    - Ligature characters (ﬁ, ﬂ, etc.)
    - Null bytes and control characters
    - Repeated dashes/underscores used as dividers (kept as single newline)
    """
    if not text:
        return ""

    # Replace ligatures
    ligatures = {
        "\ufb01": "fi",
        "\ufb02": "fl",
        "\ufb03": "ffi",
        "\ufb04": "ffl",
        "\u2019": "'",
        "\u2018": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u00a0": " ",  # non-breaking space
    }
    for char, replacement in ligatures.items():
        text = text.replace(char, replacement)

    # Remove null bytes and non-printable control chars (keep \n \t)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Collapse lines that are just dashes/underscores/equals into a single newline
    text = re.sub(r"^[-_=]{3,}\s*$", "", text, flags=re.MULTILINE)

    # Collapse 3+ consecutive blank lines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip trailing whitespace on each line
    lines = [line.rstrip() for line in text.splitlines()]
    text = "\n".join(lines)

    return text.strip()


def strip_llm_preamble(text: str) -> str:
    """
    Remove common LLM warm-up phrases before the actual answer.
    Examples: "Sure, here are 5 questions:", "Of course! Here's my answer:"
    """
    preamble_patterns = [
        r"^(Sure[,!]?\s+)",
        r"^(Of course[,!]?\s+)",
        r"^(Certainly[,!]?\s+)",
        r"^(Absolutely[,!]?\s+)",
        r"^(Great[,!]?\s+)",
        r"^(Here (are|is)[^:]*:\s*\n?)",
        r"^(Based on (the|your) (resume|provided)[^:]*:\s*\n?)",
        r"^(As per (the|your) resume[^:]*:\s*\n?)",
    ]
    for pattern in preamble_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE).lstrip()
    return text.strip()


def parse_llm_json(raw: str, context: str = "") -> Any:
    """
    Defensively parse JSON from LLM output.

    LLMs often wrap JSON in markdown fences or add preamble text.
    Strategy:
      1. Strip everything before the first '{' and after the last '}'
      2. Attempt json.loads
      3. Raise LLMParseError with context if it still fails

    Args:
        raw:     Raw LLM response string
        context: Short description of which feature called this (for error messages)

    Returns:
        Parsed Python dict/list

    Raises:
        LLMParseError: if JSON cannot be parsed after cleanup
    """
    from app.core.exceptions import LLMParseError

    if not raw or not raw.strip():
        raise LLMParseError(f"LLM returned empty response{' for ' + context if context else ''}.")

    # Find the outermost JSON object boundaries
    start = raw.find("{")
    end = raw.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise LLMParseError(
            f"LLM response contains no JSON object{' for ' + context if context else ''}. "
            f"Raw response: {raw[:200]}"
        )

    candidate = raw[start: end + 1]

    try:
        return json.loads(candidate)
    except json.JSONDecodeError as e:
        raise LLMParseError(
            f"LLM returned malformed JSON{' for ' + context if context else ''}: {e}. "
            f"Raw snippet: {candidate[:300]}"
        )


# Section headers typically found in resumes — used by chunking service
RESUME_SECTION_HEADERS = [
    "education",
    "experience",
    "work experience",
    "professional experience",
    "employment",
    "projects",
    "skills",
    "technical skills",
    "certifications",
    "awards",
    "publications",
    "summary",
    "objective",
    "profile",
    "about",
    "interests",
    "volunteer",
    "languages",
    "references",
    "achievements",
    "extracurricular",
    "internship",
    "research",
    "contact",
]
