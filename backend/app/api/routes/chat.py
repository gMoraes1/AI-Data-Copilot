"""Rotas de chat: fazer perguntas e consultar o histórico (protegidas por JWT)."""

from fastapi import APIRouter

from app.api.deps import ChatRepositoryDep, ChatServiceDep, CurrentUser
from app.schemas.chat import ChatRequest, ChatResponse, HistoryItem

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse, summary="Perguntar ao Copilot")
def ask(payload: ChatRequest, service: ChatServiceDep, current_user: CurrentUser) -> ChatResponse:
    """Recebe uma pergunta em linguagem natural e devolve a resposta + SQL gerado."""
    # O tenant vem SEMPRE do usuário autenticado (nunca do payload) -> isolamento.
    return service.ask(
        payload.question, user_id=current_user.id, tenant_id=current_user.tenant_id
    )


@router.get("/history", response_model=list[HistoryItem], summary="Histórico de perguntas")
def history(
    repository: ChatRepositoryDep, current_user: CurrentUser, limit: int = 20
) -> list[HistoryItem]:
    # Cada usuário vê apenas o próprio histórico.
    messages = repository.list_recent(user_id=current_user.id, limit=limit)
    return [HistoryItem.model_validate(m) for m in messages]
