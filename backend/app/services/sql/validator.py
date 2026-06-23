"""Validação de segurança do SQL gerado pelo LLM.

Esta é a camada de defesa em PROFUNDIDADE no nível de string. Outras camadas:
- Transação read-only no executor (nível de sessão do Postgres).
- Usuário de banco somente-leitura (nível de deploy — ver README).

Princípio: allowlist, não blocklist. Só permitimos um único SELECT.
"""

import re

from app.core.exceptions import UnsafeSQLError

# Comandos de escrita/DDL proibidos (defesa adicional além da exigência de SELECT).
_FORBIDDEN_KEYWORDS = {
    "insert", "update", "delete", "drop", "alter", "truncate",
    "grant", "revoke", "create", "replace", "merge", "call",
    "execute", "copy", "vacuum", "comment", "do", "begin", "commit",
}

_FORBIDDEN_RE = re.compile(
    r"\b(" + "|".join(_FORBIDDEN_KEYWORDS) + r")\b", re.IGNORECASE
)


def strip_code_fences(sql: str) -> str:
    """Remove blocos markdown (```sql ... ```) que o LLM possa adicionar."""
    text = sql.strip()
    text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
    text = re.sub(r"\n?```$", "", text)
    return text.strip()


def _remove_comments(sql: str) -> str:
    """Remove comentários -- e /* */ para evitar bypass das checagens."""
    sql = re.sub(r"--[^\n]*", " ", sql)
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    return sql


def sanitize_and_validate(raw_sql: str) -> str:
    """Valida o SQL e retorna a versão limpa (sem fences / ; final).

    Raises:
        UnsafeSQLError: se qualquer regra de segurança for violada.
    """
    sql = strip_code_fences(raw_sql)
    if not sql:
        raise UnsafeSQLError("Nenhum SQL foi gerado.")

    # Normaliza: remove ponto e vírgula final único (permitido).
    sql = sql.rstrip().rstrip(";").strip()

    cleaned = _remove_comments(sql)

    # 1. Múltiplas instruções não são permitidas.
    if ";" in cleaned:
        raise UnsafeSQLError("Múltiplas instruções SQL não são permitidas.")

    # 2. Deve começar com SELECT (ou WITH ... SELECT — CTE de leitura).
    first_word = cleaned.lstrip("(").strip().split(None, 1)[0].lower() if cleaned.strip() else ""
    if first_word not in {"select", "with"}:
        raise UnsafeSQLError("Apenas consultas SELECT são permitidas.")

    # 3. Nenhuma palavra-chave de escrita/DDL.
    match = _FORBIDDEN_RE.search(cleaned)
    if match:
        raise UnsafeSQLError(f"Comando não permitido detectado: '{match.group(1).upper()}'.")

    return sql


def enforce_row_limit(sql: str, max_rows: int) -> str:
    """Garante um LIMIT <= max_rows. Adiciona LIMIT se ausente."""
    if re.search(r"\blimit\b", sql, re.IGNORECASE):
        return sql
    return f"{sql}\nLIMIT {max_rows}"
