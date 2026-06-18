"""Inicialização do banco para desenvolvimento.

Cria as tabelas (create_all), popula dados de exemplo e configura o RLS + papel
somente-leitura. Em produção, use Alembic em vez disto.
"""

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.rls import setup_readonly_role_and_rls
from app.db.seed import seed
from app.db.session import SessionLocal, engine
from app.models import Base  # noqa: F401 — garante o registro dos modelos.

logger = get_logger(__name__)


def init_database() -> None:
    settings = get_settings()
    logger.info("Criando tabelas (dev) e populando dados de exemplo")
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        seed(session)

    if settings.setup_rls_on_startup:
        setup_readonly_role_and_rls(engine, settings)
