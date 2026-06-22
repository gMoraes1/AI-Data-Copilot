"""Repositório do histórico de chat (padrão Repository).

Isola a persistência: a camada de serviço não conhece SQLAlchemy, apenas este
contrato. Facilita testes (pode ser mockado) e troca de storage no futuro.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chat_history import ChatMessage


class ChatRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, message: ChatMessage) -> ChatMessage:
        self._session.add(message)
        self._session.commit()
        self._session.refresh(message)
        return message

    def list_recent(self, user_id: int | None = None, limit: int = 20) -> list[ChatMessage]:
        stmt = select(ChatMessage).order_by(ChatMessage.created_at.desc()).limit(limit)
        if user_id is not None:
            stmt = stmt.where(ChatMessage.user_id == user_id)
        return list(self._session.scalars(stmt).all())
