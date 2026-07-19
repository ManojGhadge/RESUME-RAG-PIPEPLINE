"""
Tests for text_utils — clean_text, strip_llm_preamble, parse_llm_json.
No external dependencies.
"""

import pytest
from app.utils.text_utils import clean_text, strip_llm_preamble, parse_llm_json
from app.core.exceptions import LLMParseError


# --------------------------------------------------------------------------- #
#  parse_llm_json                                                               #
# --------------------------------------------------------------------------- #

def test_parse_clean_json():
    raw = '{"match_percentage": 75, "matching_skills": ["Python"]}'
    result = parse_llm_json(raw)
    assert result["match_percentage"] == 75
    assert result["matching_skills"] == ["Python"]


def test_parse_json_with_preamble():
    """LLM often adds text before the JSON — should still parse."""
    raw = 'Sure! Here is the analysis:\n{"match_percentage": 80, "missing_skills": ["Go"]}'
    result = parse_llm_json(raw)
    assert result["match_percentage"] == 80


def test_parse_json_with_markdown_fence():
    """LLM sometimes wraps JSON in ```json ... ``` fences."""
    raw = '```json\n{"rating": "Strong", "strengths": ["Good"]}\n```'
    result = parse_llm_json(raw)
    assert result["rating"] == "Strong"


def test_parse_json_with_trailing_text():
    """LLM adds explanation after JSON — should still parse."""
    raw = '{"match_percentage": 60}\n\nThis means the candidate has a moderate match.'
    result = parse_llm_json(raw)
    assert result["match_percentage"] == 60


def test_parse_empty_string_raises():
    with pytest.raises(LLMParseError, match="empty response"):
        parse_llm_json("", context="test")


def test_parse_no_json_object_raises():
    with pytest.raises(LLMParseError, match="no JSON object"):
        parse_llm_json("The candidate is a great fit!", context="test")


def test_parse_malformed_json_raises():
    with pytest.raises(LLMParseError, match="malformed JSON"):
        parse_llm_json('{"match_percentage": 75, "skills": }', context="test")


# --------------------------------------------------------------------------- #
#  strip_llm_preamble                                                           #
# --------------------------------------------------------------------------- #

def test_strip_sure_preamble():
    # "Sure, " prefix is stripped; the rest remains
    result = strip_llm_preamble("Sure, I can help with that. Here is the answer.")
    assert "Sure" not in result
    assert len(result) > 0


def test_strip_of_course_preamble():
    result = strip_llm_preamble("Of course! Here is my answer: Python")
    assert "Of course" not in result


def test_no_preamble_unchanged():
    text = "1. What is your experience with Python?"
    assert strip_llm_preamble(text) == text


# --------------------------------------------------------------------------- #
#  clean_text                                                                   #
# --------------------------------------------------------------------------- #

def test_clean_removes_ligatures():
    text = "pro\ufb01le skills"  # ﬁ ligature
    assert "fi" in clean_text(text)
    assert "\ufb01" not in clean_text(text)


def test_clean_collapses_blank_lines():
    text = "line1\n\n\n\n\nline2"
    cleaned = clean_text(text)
    assert "\n\n\n" not in cleaned


def test_clean_empty_string():
    assert clean_text("") == ""


def test_clean_strips_trailing_whitespace():
    text = "hello   \nworld   "
    lines = clean_text(text).splitlines()
    for line in lines:
        assert line == line.rstrip()
