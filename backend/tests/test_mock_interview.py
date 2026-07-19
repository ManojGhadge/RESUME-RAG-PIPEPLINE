"""Tests for mock interview critique route. Auth bypassed via conftest."""
import json
from unittest.mock import patch
from tests.conftest import make_resume, make_db

SAMPLE_Q = "Tell me about your FastAPI experience."
SAMPLE_A = (
    "I built REST APIs with FastAPI at my current company serving 50k daily requests. "
    "I reduced latency by 35 percent using Redis caching and containerised with Docker."
)
SAMPLE_CHUNKS = [{"id": "chunk_0", "text": "FastAPI Docker Python experience.", "distance": 0.1}]
VALID_JSON = json.dumps({
    "rating": "Strong",
    "strengths": ["Cited FastAPI from resume.", "Used specific numbers."],
    "improvements": ["Add STAR structure.", "Mention team size."],
})


def test_critique_returns_result(client, app):
    from app.models.db import get_db
    app.dependency_overrides[get_db] = lambda: make_db(resume=make_resume())
    with (
        patch("app.api.routes.mock_interview.retrieve_chunks", return_value=SAMPLE_CHUNKS),
        patch("app.api.routes.mock_interview._llm") as mock_llm,
    ):
        mock_llm.generate.return_value = VALID_JSON
        r = client.post("/api/resumes/test-resume-id/mock-interview/critique",
                        json={"question": SAMPLE_Q, "user_answer": SAMPLE_A})
    app.dependency_overrides.pop(get_db, None)
    assert r.status_code == 200
    d = r.json()
    assert d["rating"] == "Strong"
    assert len(d["strengths"]) >= 1
    assert len(d["improvements"]) >= 1
    assert "sources_used" in d


def test_critique_normalises_unknown_rating(client, app):
    from app.models.db import get_db
    app.dependency_overrides[get_db] = lambda: make_db(resume=make_resume())
    weird = json.dumps({"rating": "Pretty good", "strengths": ["Good."], "improvements": ["More detail."]})
    with (
        patch("app.api.routes.mock_interview.retrieve_chunks", return_value=SAMPLE_CHUNKS),
        patch("app.api.routes.mock_interview._llm") as mock_llm,
    ):
        mock_llm.generate.return_value = weird
        r = client.post("/api/resumes/test-resume-id/mock-interview/critique",
                        json={"question": SAMPLE_Q, "user_answer": SAMPLE_A})
    app.dependency_overrides.pop(get_db, None)
    assert r.status_code == 200
    assert r.json()["rating"] in {"Excellent", "Strong", "Good", "Needs Work", "Weak"}


def test_critique_404_unknown_resume(client, app):
    from app.models.db import get_db
    app.dependency_overrides[get_db] = lambda: make_db(resume=None)
    r = client.post("/api/resumes/bad-id/mock-interview/critique",
                    json={"question": SAMPLE_Q, "user_answer": SAMPLE_A})
    app.dependency_overrides.pop(get_db, None)
    assert r.status_code == 404


def test_critique_502_bad_llm_json(client, app):
    from app.models.db import get_db
    app.dependency_overrides[get_db] = lambda: make_db(resume=make_resume())
    with (
        patch("app.api.routes.mock_interview.retrieve_chunks", return_value=SAMPLE_CHUNKS),
        patch("app.api.routes.mock_interview._llm") as mock_llm,
    ):
        mock_llm.generate.return_value = "That is a great answer!"
        r = client.post("/api/resumes/test-resume-id/mock-interview/critique",
                        json={"question": SAMPLE_Q, "user_answer": SAMPLE_A})
    app.dependency_overrides.pop(get_db, None)
    assert r.status_code == 502


def test_critique_503_llm_down(client, app):
    from app.models.db import get_db
    from app.core.exceptions import LLMError
    app.dependency_overrides[get_db] = lambda: make_db(resume=make_resume())
    with (
        patch("app.api.routes.mock_interview.retrieve_chunks", return_value=SAMPLE_CHUNKS),
        patch("app.api.routes.mock_interview._llm") as mock_llm,
    ):
        mock_llm.generate.side_effect = LLMError("Ollama unavailable")
        r = client.post("/api/resumes/test-resume-id/mock-interview/critique",
                        json={"question": SAMPLE_Q, "user_answer": SAMPLE_A})
    app.dependency_overrides.pop(get_db, None)
    assert r.status_code == 503


def test_critique_422_short_question(client):
    r = client.post("/api/resumes/id/mock-interview/critique",
                    json={"question": "hi", "user_answer": SAMPLE_A})
    assert r.status_code == 422


def test_critique_422_short_answer(client):
    r = client.post("/api/resumes/id/mock-interview/critique",
                    json={"question": SAMPLE_Q, "user_answer": "short"})
    assert r.status_code == 422


def test_critique_422_missing_fields(client):
    r = client.post("/api/resumes/id/mock-interview/critique", json={"question": SAMPLE_Q})
    assert r.status_code == 422
