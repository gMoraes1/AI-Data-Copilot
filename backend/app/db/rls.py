"""Configuração de Row-Level Security (RLS) e do papel somente-leitura.

Em desenvolvimento, é executado no startup (idempotente). Em produção, o
equivalente vive na migração Alembic 0003 e o papel é provisionado pela infra.

Como funciona o isolamento por tenant:
- As tabelas de negócio têm uma policy RLS: só retornam linhas cujo `tenant_id`
  bate com a variável de sessão `app.current_tenant`.
- O executor conecta com `copilot_ro` (papel SEM BYPASSRLS e que NÃO é dono das
  tabelas), portanto a policy é aplicada. O owner/superuser burlaria o RLS — por
  isso a execução das queries do LLM usa um papel dedicado.
"""

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_BUSINESS_TABLES = ("clientes", "pedidos")


def setup_readonly_role_and_rls(engine: Engine, settings: Settings) -> None:
    """Cria o papel read-only, concede grants e habilita o RLS (idempotente).

    Deve ser chamado com um engine conectado como owner/superuser (copilot).
    """
    role = settings.readonly_db_user
    # role/password vêm da configuração (não de input de usuário); ainda assim
    # escapamos o identificador e o literal por segurança.
    safe_role = role.replace('"', '""')
    safe_pwd = settings.readonly_db_password.replace("'", "''")

    with engine.begin() as conn:
        # 1. Cria o papel somente-leitura, se ainda não existir.
        exists = conn.execute(
            text("SELECT 1 FROM pg_roles WHERE rolname = :r"), {"r": role}
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE ROLE "{safe_role}" LOGIN PASSWORD \'{safe_pwd}\''))

        # 2. Grants mínimos: conectar, usar o schema e SELECT só nas tabelas de
        #    negócio. (Sem acesso a 'users'/'chat_history' — defesa em profundidade.)
        conn.execute(text(f'GRANT USAGE ON SCHEMA public TO "{safe_role}"'))
        for tbl in _BUSINESS_TABLES:
            conn.execute(text(f'GRANT SELECT ON "{tbl}" TO "{safe_role}"'))

        # 3. Habilita RLS e (re)cria a policy de isolamento por tenant.
        for tbl in _BUSINESS_TABLES:
            conn.execute(text(f'ALTER TABLE "{tbl}" ENABLE ROW LEVEL SECURITY'))
            conn.execute(text(f'DROP POLICY IF EXISTS tenant_isolation ON "{tbl}"'))
            conn.execute(
                text(
                    f'CREATE POLICY tenant_isolation ON "{tbl}" FOR SELECT '
                    "USING (tenant_id = current_setting('app.current_tenant', true)::int)"
                )
            )

    logger.info("RLS e papel somente-leitura configurados", extra={"role": role})
