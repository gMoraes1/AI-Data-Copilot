"""Configuração do engine e da sessão do SQLAlchemy.

Expomos:
- `engine`: engine compartilhado (pool de conexões).
- `SessionLocal`: factory de sessões.
- `get_session()`: dependency do FastAPI que cuida do ciclo de vida da sessão.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # valida conexões ociosas antes de usar.
    future=True,
)

# Engine SEPARADO, com o papel somente-leitura (copilot_ro), usado exclusivamente
# para executar o SQL gerado pelo LLM. Por ser um papel não-owner, fica sujeito ao
# Row-Level Security — o que garante o isolamento por tenant.
readonly_engine = create_engine(
    settings.database_readonly_url,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_session() -> Generator[Session, None, None]:
    """Dependency do FastAPI: abre uma sessão por request e garante o fechamento."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
