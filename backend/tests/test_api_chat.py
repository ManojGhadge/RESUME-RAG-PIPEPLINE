"""Tests for chat route. Auth bypassed via conftest get_current_user override."""
import pytest
from unittest.mock import patch
from tests.conftest import make_resume, make_db


def test_health_check(client):
    assert client.get("/health").status_code == 200
    assert client.get("/health").json()["status"] == "ok"


def test_chat_returns_answer(client, app):
    from app.models.db import get_db
    app.dependency_overrides[get_db] = lambda: make_db(resume=make_resume("test-id"))

    with (
        patch("app.api.routes.chat.retrieve_chunks") as mock_r,
        patch("app.api.routes.chat._llm") as mock_llm,
    ):
        mock_r.return_value = [{"id": "chunk_0", "text": "Python Developer.", "distance": 0.1}]
        mock_llm.generate.return_value = "Python developer with 3 years experience."
        r = client.post("/api/resumes/test-id/chat", json={"question": "What is background?"})

    app.dependency_overrides.pop(get_db, None)
    assert r.status_code == 200
    assert "answer" in r.json()
    assert len(r.json()["sources_used"]) == 1


def test_chat_returns_404_when_resume_missing(client, app):
    from app.models.db import get_db
    app.dependency_overrides[get_db] = lambda: make_db(resume=None)
    r = client.post("/api/resumes/bad-id/chat", json={"question": "What skills?"})
    app.dependency_overrides.pop(get_db, None)
    assert r.status_code == 404


def test_chat_returns_503_when_llm_down(client, app):
    from app.models.db import get_db
    from app.core.exceptions import LLMError
    app.dependency_overrides[get_db] = lambda: make_db(resume=make_resume())
    with (
        patch("app.api.routes.chat.retrieve_chunks") as mock_r,
        patch("app.api.routes.chat._llm") as mock_llm,
    ):
        mock_r.return_value = [{"id": "c0", "text": "text", "distance": 0.1}]
        mock_llm.generate.side_effect = LLMError("down")
        r = client.post("/api/resumes/test-id/chat", json={"question": "What skills do you have?"})
    app.dependency_overrides.pop(get_db, None)
    assert r.status_code == 503


def test_chat_returns_404_when_no_chunks(client, app):
    from app.models.db import get_db
    from app.core.exceptions import NoChunksFoundError
    app.dependency_overrides[get_db] = lambda: make_db(resume=make_resume())
    with patch("app.api.routes.chat.retrieve_chunks") as mock_r:
        mock_r.side_effect = NoChunksFoundError("none")
        r = client.post("/api/resumes/test-id/chat", json={"question": "What is GPA score?"})
    app.dependency_overrides.pop(get_db, None)
    assert r.status_code == 404


def test_chat_validates_short_question(client):
    assert client.post("/api/resumes/id/chat", json={"question": "hi"}).status_code == 422


def test_chat_missing_question_field(client):
    assert client.post("/api/resumes/id/chat", json={}).status_code == 422


def test_chat_question_too_long(client):
    assert client.post("/api/resumes/id/chat", json={"question": "x" * 1001}).status_code == 422
