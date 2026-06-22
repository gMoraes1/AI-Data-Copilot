"""Geração da resposta em linguagem natural a partir dos resultados da consulta."""

import json
from typing import Any

from app.services.llm.base import LLMProvider
from app.services.llm.prompts import ANSWER_GENERATION_TEMPLATE, ANSWER_SYSTEM_PROMPT


class ResultAnalyzer:
    """Usa o LLM para transformar linhas de dados em uma resposta amigável."""

    def __init__(self, llm: LLMProvider) -> None:
        self._llm = llm

    def analyze(self, question: str, sql: str, rows: list[dict[str, Any]]) -> str:
        if not rows:
            return "Não encontrei nenhum resultado para essa pergunta."

        prompt = ANSWER_GENERATION_TEMPLATE.format(
            question=question,
            sql=sql,
            rows=json.dumps(rows, ensure_ascii=False, default=str),
        )
        return self._llm.complete(prompt, system=ANSWER_SYSTEM_PROMPT)
