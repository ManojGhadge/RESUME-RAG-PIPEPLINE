"""
Shared pytest fixtures for all test modules.
Patches: DB init, embedding model, ChromaDB, and auth (get_current_user).
"""

import sys
import os
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def make_resume(resume_id: str = "test-resume-id") -> SimpleNamespace:
    return SimpleNamespace(
        id=resume_id,
        user_id="test-user-id",
        filename="test_resume.pdf",
        full_text="John Doe. Python developer with FastAPI and Docker experience.",
    )


def make_user(user_id: str = "test-user-id") -> SimpleNamespace:
    return SimpleNamespace(
        id=user_id,
        email="test@example.com",
        full_name="Test User",
        is_verified=True,
    )


def make_db(resume=None) -> MagicMock:
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = resume
    return mock_db


@pytest.fixture(scope="session")
def app():
    """
    Import the FastAPI app with all heavy startup mocked.
    Auth dependency is bypassed by overriding get_current_user globally.
    """
    with (
        patch("app.models.db._ensure_database_exists"),
        patch("app.models.db.create_engine") as mock_engine,
        patch("app.services.embedding_service.SentenceTransformer") as mock_st,
        patch("chromadb.PersistentClient"),
    ):
        mock_engine.return_value = MagicMock()
        mock_model = MagicMock()
        mock_model.encode.return_value = [[0.1] * 384]
        mock_st.return_value = mock_model

        from app.main import app as fastapi_app
        from app.core.dependencies import get_current_user

        # Override auth for all tests — returns a fake verified user
        fastapi_app.dependency_overrides[get_current_user] = lambda: make_user()

        yield fastapi_app

        fastapi_app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def client(app):
    return TestClient(app)
