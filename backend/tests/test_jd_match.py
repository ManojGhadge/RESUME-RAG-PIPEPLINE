"""Tests for JD matching routes. Auth bypassed via conftest."""
import json
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
from tests.conftest import make_resume, make_db, make_user

SAMPLE_JD = (
    "Python backend engineer with FastAPI, Docker, Kubernetes, Terraform, AWS. "
    "2+ years building scalable REST APIs. PostgreSQL and agile experience required."
)
SAMPLE_CHUNKS = [
    {"id": "chunk_0", "text": "Python, FastAPI, Docker, AWS.", "distance": 0.1},
]
VALID_JSON = json.dumps({
    "match_percentage": 78,
    "matching_skills": ["Python", "FastAPI", "Docker"],
    "missing_skills": ["Kubernetes"],
    "suggestions": ["Add Kubernetes to projects."],
})


def test_jd_match_returns_result(client, app):
    from app.models.db import get_db
    app.dependency_overrides[get_db] = lambda: make_db(resume=make_resume())
    with (
        patch("app.api.routes.jd_match.retrieve_chunks", return_value=SAMPLE_CHUNKS),
        patch("app.api.routes.jd_match._llm") as mock_llm,
    ):
        mock_llm.generate.return_value = VALID_JSON
        r = client.post("/api/resumes/test-resume-id/jd-match", json={"jd_text": SAMPLE_JD})
    app.dependency_overrides.pop(get_db, None)
    assert r.status_code == 201
    assert r.json()["match_percentage"] == 78
    assert "match_id" in r.json()


def test_jd_match_saves_to_db(client, app):
    from app.models.db import get_db
    mock_db = make_db(resume=make_resume())
    app.dependency_overrides[get_db] = lambda: mock_db
    with (
        patch("app.api.routes.jd_match.retrieve_chunks", return_value=SAMPLE_CHUNKS),
        patch("app.api.routes.jd_match._llm") as mock_llm,
    ):
        mock_llm.generate.return_value = VALID_JSON
        client.post("/api/resumes/test-resume-id/jd-match", json={"jd_text": SAMPLE_JD})
    app.dependency_overrides.pop(get_db, None)
    assert mock_db.add.call_count == 2
    assert mock_db.commit.called


def test_jd_match_404_unknown_resume(client, app):
    from app.models.db import get_db
    app.dependency_overrides[get_db] = lambda: make_db(resume=None)
    r = client.post("/api/resumes/bad-id/jd-match", json={"jd_text": SAMPLE_JD})
    app.dependency_overrides.pop(get_db, None)
    assert r.status_code == 404


def test_jd_match_422_jd_too_short(client):
    assert client.post("/api/resumes/id/jd-match", json={"jd_text": "Short"}).status_code == 422


def test_jd_match_502_bad_llm_json(client, app):
    from app.models.db import get_db
    app.dependency_overrides[get_db] = lambda: make_db(resume=make_resume())
    with (
        patch("app.api.routes.jd_match.retrieve_chunks", return_value=SAMPLE_CHUNKS),
        patch("app.api.routes.jd_match._llm") as mock_llm,
    ):
        mock_llm.generate.return_value = "Sure here are my thoughts..."
        r = client.post("/api/resumes/test-resume-id/jd-match", json={"jd_text": SAMPLE_JD})
    app.dependency_overrides.pop(get_db, None)
    assert r.status_code == 502


def test_jd_match_503_llm_down(client, app):
    from app.models.db import get_db
    from app.core.exceptions import LLMError
    app.dependency_overrides[get_db] = lambda: make_db(resume=make_resume())
    with (
        patch("app.api.routes.jd_match.retrieve_chunks", return_value=SAMPLE_CHUNKS),
        patch("app.api.routes.jd_match._llm") as mock_llm,
    ):
        mock_llm.generate.side_effect = LLMError("down")
        r = client.post("/api/resumes/test-resume-id/jd-match", json={"jd_text": SAMPLE_JD})
    app.dependency_overrides.pop(get_db, None)
    assert r.status_code == 503


def test_match_history_returns_list(client, app):
    from app.models.db import get_db
    now = datetime.utcnow()
    fake_match = SimpleNamespace(id="m-abc", resume_id="r-id", job_description_id="jd-xyz",
                                  match_percentage=72, created_at=now)
    fake_jd = SimpleNamespace(id="jd-xyz", jd_text="Python engineer role at Acme Corp FastAPI")
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = make_resume()
    mock_db.query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = [
        (fake_match, fake_jd)
    ]
    app.dependency_overrides[get_db] = lambda: mock_db
    r = client.get("/api/resumes/test-resume-id/matches")
    app.dependency_overrides.pop(get_db, None)
    assert r.status_code == 200
    assert r.json()["total"] == 1


def test_match_history_404_unknown_resume(client, app):
    from app.models.db import get_db
    app.dependency_overrides[get_db] = lambda: make_db(resume=None)
    r = client.get("/api/resumes/bad-id/matches")
    app.dependency_overrides.pop(get_db, None)
    assert r.status_code == 404


def test_match_history_empty(client, app):
    from app.models.db import get_db
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = make_resume()
    mock_db.query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = []
    app.dependency_overrides[get_db] = lambda: mock_db
    r = client.get("/api/resumes/test-resume-id/matches")
    app.dependency_overrides.pop(get_db, None)
    assert r.status_code == 200
    assert r.json()["total"] == 0
