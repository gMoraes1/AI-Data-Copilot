"""Geração de SQL a partir da pergunta do usuário e do schema do banco."""

from app.db.schema_inspector import format_schema_for_prompt
from app.services.llm.base import LLMProvider
from app.services.llm.prompts import SQL_GENERATION_TEMPLATE, SQL_SYSTEM_PROMPT
from app.services.sql import validator


class SQLGenerator:
    """Orquestra o LLM para produzir um SELECT seguro e validado."""

    def __init__(self, llm: LLMProvider, max_rows: int) -> None:
        self._llm = llm
        self._max_rows = max_rows

    def generate(self, question: str, schema: dict[str, list[str]]) -> str:
        prompt = SQL_GENERATION_TEMPLATE.format(
            schema=format_schema_for_prompt(schema),
            question=question,
            max_rows=self._max_rows,
        )
        raw = self._llm.complete(prompt, system=SQL_SYSTEM_PROMPT)

        sql = validator.sanitize_and_validate(raw)
        sql = validator.enforce_row_limit(sql, self._max_rows)
        return sql
