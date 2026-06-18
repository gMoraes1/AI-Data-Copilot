"""Introspecção do esquema do banco para alimentar o LLM.

Lê tabelas e colunas reais via SQLAlchemy Inspector. Assim o prompt sempre
reflete o schema atual — nada hard-coded — e o LLM só conhece o que existe.
"""

from sqlalchemy import inspect
from sqlalchemy.engine import Engine

# Tabelas internas que NÃO devem ser expostas ao LLM/usuário.
# 'users'/'tenants' ficam ocultas por segurança (credenciais / metadados internos).
_HIDDEN_TABLES = {"chat_history", "alembic_version", "users", "tenants"}

# Colunas ocultas do LLM. 'tenant_id' é controlado pelo RLS, não pelo modelo —
# expô-lo só geraria filtros redundantes ou confusos no SQL.
_HIDDEN_COLUMNS = {"tenant_id"}


def get_schema_map(engine: Engine) -> dict[str, list[str]]:
    """Retorna {tabela: [colunas]} para as tabelas de negócio."""
    inspector = inspect(engine)
    schema: dict[str, list[str]] = {}
    for table_name in inspector.get_table_names():
        if table_name in _HIDDEN_TABLES:
            continue
        columns = [
            col["name"]
            for col in inspector.get_columns(table_name)
            if col["name"] not in _HIDDEN_COLUMNS
        ]
        schema[table_name] = columns
    return schema


def format_schema_for_prompt(schema: dict[str, list[str]]) -> str:
    """Formata o schema em texto legível para inserir no prompt do LLM."""
    lines = []
    for table, columns in schema.items():
        lines.append(f"- {table}({', '.join(columns)})")
    return "\n".join(lines)
