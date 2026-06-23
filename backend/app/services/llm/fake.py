"""Provider determinístico para testes e desenvolvimento sem Ollama.

Não usa IA: aplica heurísticas simples sobre o prompt para devolver um SQL
plausível ou uma resposta em linguagem natural. Permite rodar a aplicação e a
suíte de testes ponta a ponta sem depender de um modelo externo.
"""

import re

from app.services.llm.base import LLMProvider

# Detecta se estamos na fase de geração de SQL ou de análise de resultado,
# com base em marcadores presentes nos prompts (ver prompts.py).
_SQL_MARKER = "Gere uma única consulta SQL"
_ANSWER_MARKER = "Resultado da consulta"


class FakeLLMProvider(LLMProvider):
    """Implementação simulada do LLMProvider (sem rede)."""

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        if _SQL_MARKER in prompt:
            return self._fake_sql(prompt)
        if _ANSWER_MARKER in prompt:
            return self._fake_answer(prompt)
        return "Resposta simulada."

    def _fake_sql(self, prompt: str) -> str:
        lowered = prompt.lower()
        if "cliente" in lowered and ("mais" in lowered or "top" in lowered):
            return (
                "SELECT c.nome, SUM(p.valor_total) AS total\n"
                "FROM clientes c\n"
                "JOIN pedidos p ON p.cliente_id = c.id\n"
                "GROUP BY c.nome\n"
                "ORDER BY total DESC\n"
                "LIMIT 10;"
            )
        if "faturamento" in lowered or "receita" in lowered:
            return (
                "SELECT date_trunc('month', data_pedido) AS mes, SUM(valor_total) AS total\n"
                "FROM pedidos\n"
                "GROUP BY mes\n"
                "ORDER BY mes;"
            )
        if "atrasad" in lowered:
            return "SELECT COUNT(*) AS pedidos_atrasados FROM pedidos WHERE status = 'atrasado';"
        return "SELECT COUNT(*) AS total_pedidos FROM pedidos;"

    def _fake_answer(self, prompt: str) -> str:
        # Extrai o primeiro número que aparecer no bloco de resultados, se houver.
        match = re.search(r"(\d[\d.,]*)", prompt.split(_ANSWER_MARKER, 1)[-1])
        numero = match.group(1) if match else "alguns"
        return f"Com base nos dados, o resultado encontrado foi {numero}."
