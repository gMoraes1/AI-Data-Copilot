"""DTOs (Pydantic) da API de chat — contrato de entrada/saída do endpoint /chat."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Pergunta do usuário em linguagem natural.",
        examples=["Quais foram os 10 clientes que mais compraram este mês?"],
    )


class ChatResponse(BaseModel):
    """Resposta do Copilot, incluindo dados de transparência (SQL e linhas)."""

    answer: str = Field(..., description="Resposta em linguagem natural.")
    sql: str = Field(..., description="SQL gerado e executado (transparência/auditoria).")
    rows: list[dict[str, Any]] = Field(default_factory=list, description="Resultado da consulta.")
    row_count: int = 0
    latency_ms: int = 0


class HistoryItem(BaseModel):
    id: int
    user_id: int | None = None
    question: str
    generated_sql: str | None
    answer: str | None
    status: str
    row_count: int
    latency_ms: int
    created_at: datetime

    model_config = {"from_attributes": True}
