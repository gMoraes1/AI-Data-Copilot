"""Execução segura de SQL no PostgreSQL.

Defesa em profundidade no nível da SESSÃO do banco:
- Conexão com papel SOMENTE-LEITURA (copilot_ro), sujeito ao Row-Level Security.
- Variável de sessão `app.current_tenant` -> o RLS filtra as linhas por empresa.
- Transação explícita marcada como READ ONLY (Postgres rejeita escrita).
- statement_timeout para evitar consultas longas.
- A transação é sempre revertida (rollback) — nada é persistido.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import SQLExecutionError
from app.core.logging import get_logger

logger = get_logger(__name__)


def _serialize(value: Any) -> Any:
    """Converte tipos do Postgres para algo serializável em JSON."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


class SQLExecutor:
    def __init__(self, engine: Engine, statement_timeout_ms: int, max_rows: int) -> None:
        self._engine = engine
        self._statement_timeout_ms = statement_timeout_ms
        self._max_rows = max_rows

    def execute(self, sql: str, *, tenant_id: int) -> list[dict[str, Any]]:
        try:
            with self._engine.connect() as conn:
                # Transação read-only: qualquer tentativa de escrita falha aqui.
                conn.execution_options(postgresql_readonly=True)
                conn.execute(text(f"SET LOCAL statement_timeout = {self._statement_timeout_ms}"))

                # Define o tenant da requisição (escopo da transação). O RLS usa
                # este valor para filtrar as linhas. set_config aceita parâmetro,
                # evitando injeção de SQL.
                conn.execute(
                    text("SELECT set_config('app.current_tenant', :tid, true)"),
                    {"tid": str(tenant_id)},
                )

                result = conn.execute(text(sql))
                rows = result.mappings().fetchmany(self._max_rows)
                conn.rollback()  # garante que nada foi persistido.

            return [{k: _serialize(v) for k, v in row.items()} for row in rows]
        except SQLAlchemyError as exc:
            logger.warning("Erro ao executar SQL", extra={"sql": sql, "error": str(exc)})
            raise SQLExecutionError(f"Erro ao executar a consulta: {exc.__class__.__name__}") from exc
