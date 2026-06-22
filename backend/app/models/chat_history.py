"""Histórico de perguntas/respostas do Copilot (funcionalidade do MVP)."""

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ChatMessage(Base, TimestampMixin):
    __tablename__ = "chat_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Quem fez a pergunta (auditoria; base para multi-tenant no futuro).
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    generated_sql: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 'success' | 'rejected' | 'error' — facilita auditoria/observabilidade.
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="success")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    row_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
