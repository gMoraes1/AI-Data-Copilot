"""Fixtures de teste.

Configura ambiente isolado ANTES de importar a app:
- ENVIRONMENT=production -> pula o bootstrap automático do banco no startup.
- LLM_PROVIDER=fake      -> sem dependência do Ollama.
- Banco SQLite em memória via override da dependency get_session.
"""

import os

os.environ.setdefault("ENVIRONMENT", "production")
os.environ.setdefault("LLM_PROVIDER", "fake")
os.environ.setdefault("SECRET_KEY", "test-secret-key-0123456789abcdef-0123456789")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.db.session import get_session  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base  # noqa: E402


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_session():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
