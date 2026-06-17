"""Dependencies do FastAPI — montam os serviços por request (injeção de dependência)."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.exceptions import AuthError
from app.core.security import decode_access_token
from app.db.session import engine, get_session, readonly_engine
from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.repositories.tenant_repository import TenantRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.chat_service import ChatService
from app.services.llm.base import LLMProvider
from app.services.llm.factory import get_llm_provider

SessionDep = Annotated[Session, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
LLMDep = Annotated[LLMProvider, Depends(get_llm_provider)]

# tokenUrl aponta para a rota de login (usado pelo botão "Authorize" do Swagger).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
TokenDep = Annotated[str, Depends(oauth2_scheme)]


def get_chat_repository(session: SessionDep) -> ChatRepository:
    return ChatRepository(session)


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(UserRepository(session), TenantRepository(session))


def get_current_user(token: TokenDep, session: SessionDep) -> User:
    """Resolve o usuário autenticado a partir do token JWT (Bearer)."""
    email = decode_access_token(token)
    if not email:
        raise AuthError("Token inválido ou expirado.")
    user = UserRepository(session).get_by_email(email)
    if not user or not user.is_active:
        raise AuthError("Usuário não encontrado ou inativo.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_chat_service(
    session: SessionDep,
    settings: SettingsDep,
    llm: LLMDep,
) -> ChatService:
    return ChatService(
        engine=engine,
        readonly_engine=readonly_engine,
        llm=llm,
        repository=ChatRepository(session),
        settings=settings,
    )


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
ChatRepositoryDep = Annotated[ChatRepository, Depends(get_chat_repository)]
